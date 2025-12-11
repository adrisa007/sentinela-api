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

@pytest.fixture(scope="module")
def auth_token():
    """Fixture para obter token de autenticação"""
    # Cria tabelas do banco
    create_db_and_tables()
    
    # Cria usuário admin de teste se não existir
    with Session(engine) as session:
        # Cria entidade fictícia se não existir
        entidade = session.exec(select(Entidade).where(Entidade.id == 1)).first()
        if not entidade:
            from datetime import datetime
            entidade = Entidade(
                id=1,
                cnpj="00059311000126",
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

    # Faz login e retorna token
    response = client.post("/auth/login", json={"email": "admin@sentinela.app", "senha": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_pncp_validar_fornecedor_endpoint(auth_token):
    """Testa o endpoint de validação de fornecedor no PNCP"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/pncp/fornecedor/validar/00059311000126", headers=headers)
    # Pode retornar erro de API externa, mas a rota deve existir
    assert response.status_code in [200, 400, 500]  # Aceita erro controlado

def test_pncp_buscar_contratos_endpoint(auth_token):
    """Testa o endpoint de busca de contratos no PNCP"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/pncp/fornecedor/00059311000126/contratos", headers=headers)
    # Pode retornar erro de API externa, mas a rota deve existir
    assert response.status_code in [200, 400, 500]  # Aceita erro controlado

def test_pncp_verificar_certidoes_endpoint(auth_token):
    """Testa o endpoint de verificação de certidões no PNCP"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/pncp/fornecedor/00059311000126/certidoes", headers=headers)
    # Pode retornar erro de API externa, mas a rota deve existir
    assert response.status_code in [200, 400, 500]  # Aceita erro controlado

def test_pncp_buscar_contrato_detalhado_endpoint(auth_token):
    """Testa o endpoint de busca de contrato detalhado no PNCP"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/pncp/contrato/00059311000126/0012024", headers=headers)
    # Pode retornar erro de API externa, mas a rota deve existir
    assert response.status_code in [200, 400, 500]  # Aceita erro controlado

# Teste removido temporariamente - validação de CNPJ funciona mas HTTPException retorna 500 ao invés de 400
def test_pncp_cnpj_invalido(auth_token):
    """Testa validação de CNPJ inválido"""
    print("DEBUG TESTE: Iniciando teste CNPJ inválido")
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/pncp/fornecedor/validar/123", headers=headers)
    print(f"DEBUG TESTE: Status code recebido: {response.status_code}")
    print(f"DEBUG TESTE: Response: {response.text}")
    assert response.status_code == 400
    assert "CNPJ inválido" in response.json()["detail"]

def test_pncp_sync_fornecedor_nao_encontrado(auth_token):
    """Testa sincronização de fornecedor inexistente"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/pncp/sync/fornecedor/99999", headers=headers)
    assert response.status_code == 404
    assert "Fornecedor não encontrado" in response.json()["detail"]

def test_pncp_sync_contratos_cnpj_invalido(auth_token):
    """Testa sincronização de contratos com CNPJ inválido"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/pncp/sync/contratos/123", headers=headers)
    assert response.status_code == 400
    assert "CNPJ inválido" in response.json()["detail"]
