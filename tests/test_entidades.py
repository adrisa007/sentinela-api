import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import create_db_and_tables
from app.models.usuario import Usuario
from app.models.entidade import Entidade
from app.core.security import get_password_hash
from sqlmodel import Session, select
from app.core.database import engine

client = TestClient(app)

def setup_module(module):
    create_db_and_tables()
    # Cria usuário admin de teste
    with Session(engine) as session:
        # Cria entidade fictícia se não existir
        entidade = session.exec(select(Entidade).where(Entidade.id == 1)).first()
        if not entidade:
            from datetime import datetime
            entidade = Entidade(
                id=1,
                cnpj="12345678000199",
                razao_social="Entidade Teste Ltda",
                nome_fantasia="Entidade Teste",
                ug_codigo="UG123",
                status="ATIVA",
                data_status=datetime.utcnow(),
                motivo_status=None,
                root_user_id=None,
                logo_url=None,
                config_json=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(entidade)
            session.commit()
            session.refresh(entidade)
        # Cria usuário admin vinculado à entidade
        if not session.exec(select(Usuario).where(Usuario.email == "admin@sentinela.app")).first():
            admin = Usuario(
                nome="Admin Teste",
                email="admin@sentinela.app",
                cpf="00000000191",
                senha_hash=get_password_hash("admin123"),
                perfil="ROOT",
                ativo=True,
                entidade_id=entidade.id,
                totp_enabled=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)

def get_auth_token():
    """Obtém token de autenticação para testes"""
    response = client.post("/auth/login", json={"email": "admin@sentinela.app", "senha": "admin123"})
    return response.json()["access_token"]

def test_entidades_list():
    """Testa listagem de entidades"""
    token = get_auth_token()
    response = client.get("/entidades/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_entidades_create():
    """Testa criação de entidade"""
    token = get_auth_token()
    import time
    cnpj = f"{int(time.time()) % 100000000000000:014d}"
    entidade_data = {
        "cnpj": cnpj,
        "razao_social": "Nova Entidade Ltda",
        "nome_fantasia": "Nova Entidade",
        "ug_codigo": "UG456"
    }
    response = client.post("/entidades/", json=entidade_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["cnpj"] == entidade_data["cnpj"]
    assert data["razao_social"] == entidade_data["razao_social"]

def test_entidades_read():
    """Testa leitura de entidade específica"""
    token = get_auth_token()
    # Primeiro cria uma entidade
    import time
    cnpj = f"{int(time.time() * 1000) % 100000000000000:014d}"
    entidade_data = {
        "cnpj": cnpj,
        "razao_social": "Entidade Leitura Ltda",
        "nome_fantasia": "Entidade Leitura",
        "ug_codigo": "UG111"
    }
    create_response = client.post("/entidades/", json=entidade_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == 200
    entidade_id = create_response.json()["id"]

    # Agora lê a entidade
    response = client.get(f"/entidades/{entidade_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == entidade_id
    assert data["cnpj"] == entidade_data["cnpj"]

def test_entidades_update():
    """Testa atualização de entidade"""
    token = get_auth_token()
    # Primeiro cria uma entidade
    import time
    cnpj = f"{int(time.time() * 1000 + 1) % 100000000000000:014d}"
    entidade_data = {
        "cnpj": cnpj,
        "razao_social": "Entidade Update Ltda",
        "nome_fantasia": "Entidade Update",
        "ug_codigo": "UG222"
    }
    create_response = client.post("/entidades/", json=entidade_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == 200
    entidade_id = create_response.json()["id"]

    # Atualiza a entidade
    update_data = {
        "nome_fantasia": "Entidade Atualizada",
        "ug_codigo": "UG333"
    }
    response = client.put(f"/entidades/{entidade_id}", json=update_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["nome_fantasia"] == update_data["nome_fantasia"]
    assert data["ug_codigo"] == update_data["ug_codigo"]

def test_entidades_delete():
    """Testa exclusão de entidade"""
    token = get_auth_token()
    # Primeiro cria uma entidade
    import time
    cnpj = f"{int(time.time() * 1000 + 2) % 100000000000000:014d}"
    entidade_data = {
        "cnpj": cnpj,
        "razao_social": "Entidade Delete Ltda",
        "nome_fantasia": "Entidade Delete",
        "ug_codigo": "UG333"
    }
    create_response = client.post("/entidades/", json=entidade_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == 200
    entidade_id = create_response.json()["id"]

    # Exclui a entidade
    response = client.delete(f"/entidades/{entidade_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Verifica se foi desativada (soft delete)
    read_response = client.get(f"/entidades/{entidade_id}", headers={"Authorization": f"Bearer {token}"})
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["status"] == "INATIVA"