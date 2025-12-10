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
                razao_social="Fornecedor Ocorrencia Ltda",
                nome_fantasia="Fornecedor Ocorrencia",
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
                numero_contrato="CT-OCOR-001",
                numero_processo="PROC-OCOR-001/2025",
                objeto="Contrato para testes de ocorrências",
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
        # Cria fiscal designado se não existir
        fiscal_designado = session.exec(select(FiscalDesignado).where(FiscalDesignado.id == 1)).first()
        if not fiscal_designado:
            fiscal_designado = FiscalDesignado(
                id=1,
                contrato_id=1,
                usuario_id=2,  # ID do usuário fiscal
                tipo_fiscal="TITULAR",
                data_designacao=datetime.utcnow().date(),
                portaria="PORT-OCOR-001/2025",
                ativo=True
            )
            session.add(fiscal_designado)
            session.commit()
            session.refresh(fiscal_designado)
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

def test_ocorrencias_list():
    """Testa listagem de ocorrências"""
    token = get_auth_token()
    response = client.get("/ocorrencias-fiscalizacao/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_ocorrencias_create():
    """Testa criação de ocorrência"""
    token = get_auth_token()
    ocorrencia_data = {
        "contrato_id": 1,
        "fiscal_id": 2,  # ID do usuário fiscal
        "data_ocorrencia": "2025-12-10T10:00:00",
        "tipo_ocorrencia": "VISTORIA",
        "descricao": "Vistoria de rotina no local da obra",
        "geolocalizacao": "-23.550520,-46.633308",
        "assinatura_contratada": False
    }
    response = client.post("/ocorrencias-fiscalizacao/", json=ocorrencia_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["contrato_id"] == ocorrencia_data["contrato_id"]
    assert data["fiscal_id"] == ocorrencia_data["fiscal_id"]
    assert data["tipo_ocorrencia"] == ocorrencia_data["tipo_ocorrencia"]

def test_ocorrencias_read():
    """Testa leitura de ocorrência específica"""
    token = get_auth_token()
    # Primeiro cria uma ocorrência
    ocorrencia_data = {
        "contrato_id": 1,
        "fiscal_id": 2,
        "data_ocorrencia": "2025-12-10T14:30:00",
        "tipo_ocorrencia": "MEDICAO",
        "descricao": "Medição de serviços executados",
        "geolocalizacao": "-22.906847,-43.172896",
        "assinatura_contratada": True
    }
    create_response = client.post("/ocorrencias-fiscalizacao/", json=ocorrencia_data, headers={"Authorization": f"Bearer {token}"})
    assert create_response.status_code == 200
    ocorrencia_id = create_response.json()["id"]

    # Agora lê a ocorrência
    response = client.get(f"/ocorrencias-fiscalizacao/{ocorrencia_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ocorrencia_id
    assert data["tipo_ocorrencia"] == ocorrencia_data["tipo_ocorrencia"]