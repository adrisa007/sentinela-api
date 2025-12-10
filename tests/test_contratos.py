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
from app.models.fornecedor import Fornecedor
from app.core.security import get_password_hash
from sqlmodel import Session, select
from app.core.database import engine
from decimal import Decimal

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
        # Cria fornecedor de teste se não existir
        fornecedor = session.exec(select(Fornecedor).where(Fornecedor.id == 1)).first()
        if not fornecedor:
            fornecedor = Fornecedor(
                id=1,
                entidade_id=1,
                cnpj="99999999000199",
                razao_social="Fornecedor Contrato Ltda",
                nome_fantasia="Fornecedor Contrato",
                situacao_cadastral="ATIVO",
                regularidade_geral="REGULAR",
                ativo=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(fornecedor)
            session.commit()
            session.refresh(fornecedor)
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

def test_contratos_list():
    """Testa listagem de contratos"""
    token = get_auth_token()
    response = client.get("/contratos/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_contratos_create():
    """Testa criação de contrato"""
    token = get_auth_token()
    import time
    numero_contrato = f"CT-{int(time.time())}"
    contrato_data = {
        "entidade_id": 1,
        "numero_contrato": numero_contrato,
        "numero_processo": "PROC-001/2025",
        "objeto": "Prestação de serviços de consultoria",
        "fornecedor_id": 1,
        "valor_global": "150000.00",
        "data_assinatura": "2025-01-15",
        "data_inicio": "2025-02-01",
        "data_termino": "2025-12-31",
        "vigencia_meses": 12,
        "modalidade": "Pregão Eletrônico",
        "tipo_contrato": "Serviços"
    }
    response = client.post("/contratos/", json=contrato_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["numero_contrato"] == contrato_data["numero_contrato"]
    assert data["objeto"] == contrato_data["objeto"]
    assert data["valor_global"] == contrato_data["valor_global"]

def test_contratos_read():
    """Testa leitura de contrato específico"""
    token = get_auth_token()
    # Primeiro cria um contrato
    import time
    numero_contrato = f"CT-READ-{int(time.time() * 1000)}"
    contrato_data = {
        "entidade_id": 1,
        "numero_contrato": numero_contrato,
        "numero_processo": "PROC-002/2025",
        "objeto": "Aquisição de equipamentos",
        "fornecedor_id": 1,
        "valor_global": "50000.00",
        "data_assinatura": "2025-01-20",
        "data_inicio": "2025-02-01",
        "data_termino": "2025-06-30",
        "vigencia_meses": 6,
        "modalidade": "Dispensa",
        "tipo_contrato": "Compra"
    }
    create_response = client.post("/contratos/", json=contrato_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == 200
    contrato_id = create_response.json()["id"]

    # Agora lê o contrato
    response = client.get(f"/contratos/{contrato_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contrato_id
    assert data["numero_contrato"] == contrato_data["numero_contrato"]

def test_contratos_update():
    """Testa atualização de contrato"""
    token = get_auth_token()
    # Primeiro cria um contrato
    import time
    numero_contrato = f"CT-UPD-{int(time.time() * 1000 + 1)}"
    contrato_data = {
        "entidade_id": 1,
        "numero_contrato": numero_contrato,
        "numero_processo": "PROC-003/2025",
        "objeto": "Serviços de manutenção",
        "fornecedor_id": 1,
        "valor_global": "75000.00",
        "data_assinatura": "2025-01-10",
        "data_inicio": "2025-02-01",
        "data_termino": "2025-08-31",
        "vigencia_meses": 8,
        "modalidade": "Concorrência",
        "tipo_contrato": "Serviços"
    }
    create_response = client.post("/contratos/", json=contrato_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == 200
    contrato_id = create_response.json()["id"]

    # Atualiza o contrato
    update_data = {
        "objeto": "Serviços de manutenção atualizados",
        "valor_global": "85000.00",
        "status": "EM_EXECUCAO"
    }
    response = client.put(f"/contratos/{contrato_id}", json=update_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["objeto"] == update_data["objeto"]
    assert data["valor_global"] == update_data["valor_global"]
    assert data["status"] == update_data["status"]

def test_contratos_delete():
    """Testa exclusão de contrato"""
    token = get_auth_token()
    # Primeiro cria um contrato
    import time
    numero_contrato = f"CT-DEL-{int(time.time() * 1000 + 2)}"
    contrato_data = {
        "entidade_id": 1,
        "numero_contrato": numero_contrato,
        "numero_processo": "PROC-004/2025",
        "objeto": "Contrato para exclusão",
        "fornecedor_id": 1,
        "valor_global": "25000.00",
        "data_assinatura": "2025-01-05",
        "data_inicio": "2025-02-01",
        "data_termino": "2025-04-30",
        "vigencia_meses": 4,
        "modalidade": "Inexigibilidade",
        "tipo_contrato": "Serviços"
    }
    create_response = client.post("/contratos/", json=contrato_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == 200
    contrato_id = create_response.json()["id"]

    # Exclui o contrato
    response = client.delete(f"/contratos/{contrato_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Verifica se foi cancelado (soft delete)
    read_response = client.get(f"/contratos/{contrato_id}", headers={"Authorization": f"Bearer {token}"})
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["status"] == "CANCELADO"