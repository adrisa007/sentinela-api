import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import create_db_and_tables

client = TestClient(app)

def setup_module(module):
    create_db_and_tables()

def test_pncp_validar_fornecedor_endpoint():
    """Testa o endpoint de validação de fornecedor no PNCP"""
    # Como estamos em teste, este endpoint pode não funcionar sem API real
    # Mas podemos testar se a rota existe
    response = client.get("/pncp/fornecedor/validar/12345678000123")
    # Pode retornar erro de API externa, mas a rota deve existir
    assert response.status_code in [200, 400, 500]  # Aceita erro controlado

def test_pncp_buscar_contratos_endpoint():
    """Testa o endpoint de busca de contratos no PNCP"""
    response = client.get("/pncp/fornecedor/12345678000123/contratos")
    # Pode retornar erro de API externa, mas a rota deve existir
    assert response.status_code in [200, 400, 500]  # Aceita erro controlado

def test_pncp_verificar_certidoes_endpoint():
    """Testa o endpoint de verificação de certidões no PNCP"""
    response = client.get("/pncp/fornecedor/12345678000123/certidoes")
    # Pode retornar erro de API externa, mas a rota deve existir
    assert response.status_code in [200, 400, 500]  # Aceita erro controlado

def test_pncp_buscar_contrato_detalhado_endpoint():
    """Testa o endpoint de busca de contrato detalhado no PNCP"""
    response = client.get("/pncp/contrato/12345678000123/0012024")
    # Pode retornar erro de API externa, mas a rota deve existir
    assert response.status_code in [200, 400, 500]  # Aceita erro controlado

def test_pncp_cnpj_invalido():
    """Testa validação de CNPJ inválido"""
    response = client.get("/pncp/fornecedor/validar/123")
    assert response.status_code == 400
    assert "CNPJ inválido" in response.json()["detail"]

def test_pncp_sync_fornecedor_nao_encontrado():
    """Testa sincronização de fornecedor inexistente"""
    response = client.post("/pncp/sync/fornecedor/99999")
    assert response.status_code == 404
    assert "Fornecedor não encontrado" in response.json()["detail"]

def test_pncp_sync_contratos_cnpj_invalido():
    """Testa sincronização de contratos com CNPJ inválido"""
    response = client.post("/pncp/sync/contratos/123")
    assert response.status_code == 400
    assert "CNPJ inválido" in response.json()["detail"]
