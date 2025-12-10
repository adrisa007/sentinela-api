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

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_auth_login():
    response = client.post("/auth/login", json={"email": "admin@sentinela.app", "senha": "admin123"})
    print("LOGIN RESPONSE:", response.status_code, response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()

# Adicione mais testes para guards, auditoria, PNCP conforme necessário
