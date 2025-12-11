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
from app.models.contrato import Contrato
from app.models.fiscal_designado import FiscalDesignado
from app.core.security import get_password_hash
from sqlmodel import Session, select
from app.core.database import engine
from decimal import Decimal
from datetime import datetime

client = TestClient(app)

def setup_module(module):
    create_db_and_tables()
    # Cria usuário admin de teste
    with Session(engine) as session:
        # Cria entidade fictícia se não existir
        entidade = session.exec(select(Entidade).where(Entidade.id == 1)).first()
        if not entidade:
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
                razao_social="Fornecedor Fiscal Ltda",
                nome_fantasia="Fornecedor Fiscal",
                situacao_cadastral="ATIVO",
                regularidade_geral="REGULAR",
                ativo=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(fornecedor)
            session.commit()
            session.refresh(fornecedor)
        # Cria contrato de teste se não existir
        contrato = session.exec(select(Contrato).where(Contrato.id == 1)).first()
        if not contrato:
            contrato = Contrato(
                id=1,
                entidade_id=1,
                numero_contrato="CT-FISCAL-001",
                numero_processo="PROC-FISCAL-001/2025",
                objeto="Contrato para testes de fiscais",
                fornecedor_id=1,
                valor_global=Decimal("100000.00"),
                valor_executado=Decimal("0.00"),
                data_assinatura=datetime.utcnow().date(),
                data_inicio=datetime.utcnow().date(),
                data_termino=(datetime.utcnow().replace(year=datetime.utcnow().year + 1)).date(),
                vigencia_meses=12,
                modalidade="Pregão",
                tipo_contrato="Serviços",
                status="VIGENTE",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(contrato)
            session.commit()
            session.refresh(contrato)
        # Cria segundo contrato de teste se não existir
        contrato2 = session.exec(select(Contrato).where(Contrato.id == 2)).first()
        if not contrato2:
            contrato2 = Contrato(
                id=2,
                entidade_id=1,
                numero_contrato="CT-FISCAL-002",
                numero_processo="PROC-FISCAL-002/2025",
                objeto="Segundo contrato para testes de fiscais",
                fornecedor_id=1,
                valor_global=Decimal("200000.00"),
                valor_executado=Decimal("0.00"),
                data_assinatura=datetime.utcnow().date(),
                data_inicio=datetime.utcnow().date(),
                data_termino=(datetime.utcnow().replace(year=datetime.utcnow().year + 1)).date(),
                vigencia_meses=12,
                modalidade="Pregão",
                tipo_contrato="Serviços",
                status="VIGENTE",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(contrato2)
            session.commit()
            session.refresh(contrato2)
        # Cria terceiro contrato de teste se não existir
        contrato3 = session.exec(select(Contrato).where(Contrato.id == 3)).first()
        if not contrato3:
            contrato3 = Contrato(
                id=3,
                entidade_id=1,
                numero_contrato="CT-FISCAL-003",
                numero_processo="PROC-FISCAL-003/2025",
                objeto="Terceiro contrato para testes de fiscais",
                fornecedor_id=1,
                valor_global=Decimal("300000.00"),
                valor_executado=Decimal("0.00"),
                data_assinatura=datetime.utcnow().date(),
                data_inicio=datetime.utcnow().date(),
                data_termino=(datetime.utcnow().replace(year=datetime.utcnow().year + 1)).date(),
                vigencia_meses=12,
                modalidade="Pregão",
                tipo_contrato="Serviços",
                status="VIGENTE",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(contrato3)
            session.commit()
            session.refresh(contrato3)
        # Cria usuário fiscal se não existir
        fiscal = session.exec(select(Usuario).where(Usuario.email == "fiscal@sentinela.app")).first()
        if not fiscal:
            fiscal = Usuario(
                nome="Fiscal Teste",
                email="fiscal@sentinela.app",
                cpf="11111111111",
                senha_hash=get_password_hash("fiscal123"),
                perfil="FISCAL_TECNICO",
                ativo=True,
                entidade_id=entidade.id,
                totp_enabled=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(fiscal)
            session.commit()
            session.refresh(fiscal)
        # Cria segundo usuário fiscal se não existir
        fiscal2 = session.exec(select(Usuario).where(Usuario.email == "fiscal2@sentinela.app")).first()
        if not fiscal2:
            fiscal2 = Usuario(
                nome="Fiscal Teste 2",
                email="fiscal2@sentinela.app",
                cpf="22222222222",
                senha_hash=get_password_hash("fiscal123"),
                perfil="FISCAL_TECNICO",
                ativo=True,
                entidade_id=entidade.id,
                totp_enabled=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(fiscal2)
            session.commit()
            session.refresh(fiscal2)
        # Cria terceiro usuário fiscal se não existir
        fiscal3 = session.exec(select(Usuario).where(Usuario.email == "fiscal3@sentinela.app")).first()
        if not fiscal3:
            fiscal3 = Usuario(
                nome="Fiscal Teste 3",
                email="fiscal3@sentinela.app",
                cpf="33333333333",
                senha_hash=get_password_hash("fiscal123"),
                perfil="FISCAL_TECNICO",
                ativo=True,
                entidade_id=entidade.id,
                totp_enabled=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(fiscal3)
            session.commit()
            session.refresh(fiscal3)
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

def test_fiscais_list():
    """Testa listagem de fiscais"""
    token = get_auth_token()
    response = client.get("/fiscais-designados/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_fiscais_create():
    """Testa criação de fiscal"""
    token = get_auth_token()
    # Primeiro, vamos verificar quais usuários existem
    users_response = client.get("/usuarios/", headers={"Authorization": f"Bearer {token}"})
    users = users_response.json()
    fiscal_users = [u for u in users if u["perfil"] == "FISCAL_TECNICO"]
    
    # Usar o último usuário fiscal disponível
    fiscal_user = fiscal_users[-1] if fiscal_users else None
    assert fiscal_user, "Nenhum usuário fiscal encontrado"
    
    fiscal_data = {
        "contrato_id": 1,  # Primeiro contrato
        "usuario_id": fiscal_user["id"],  # Usar ID real do usuário fiscal
        "tipo_fiscal": "SUPLENTE",
        "data_designacao": "2025-01-15",
        "portaria": f"PORT-CREATE-{int(datetime.utcnow().timestamp())}/2025"  # Portaria única
    }
    response = client.post("/fiscais-designados/", json=fiscal_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["tipo_fiscal"] == fiscal_data["tipo_fiscal"]
    assert data["portaria"] == fiscal_data["portaria"]

def test_fiscais_read():
    """Testa leitura de fiscal específico"""
    token = get_auth_token()
    # Usa o fiscal criado no setup (ID 1)
    fiscal_id = 1
    response = client.get(f"/fiscais-designados/{fiscal_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == fiscal_id
    assert data["tipo_fiscal"] == "SUPLENTE"

def test_fiscais_delete():
    """Testa exclusão de fiscal"""
    token = get_auth_token()
    # Cria um fiscal específico para teste de delete
    fiscal_data = {
        "contrato_id": 2,  # Segundo contrato
        "usuario_id": 2,  # Primeiro usuário fiscal
        "tipo_fiscal": "TITULAR",
        "data_designacao": "2025-01-05",
        "portaria": f"PORT-DELETE-{int(datetime.utcnow().timestamp())}/2025"  # Portaria única
    }
    create_response = client.post("/fiscais-designados/", json=fiscal_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == 200
    fiscal_id = create_response.json()["id"]

    # Exclui o fiscal
    response = client.delete(f"/fiscais-designados/{fiscal_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Verifica se foi desativado (soft delete)
    read_response = client.get(f"/fiscais-designados/{fiscal_id}", headers={"Authorization": f"Bearer {token}"})
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["ativo"] == False