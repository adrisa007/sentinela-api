#!/usr/bin/env python3
"""
Script de teste para a API Sentinela
Testa os principais endpoints da API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)

def test_health():
    print_header("1. Testando Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200

def test_login():
    print_header("2. Testando Login")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "admin@sentinela.app",
            "senha": "admin123"
        }
    )
    print_response(response)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"\n✅ Token obtido: {token[:50]}...")
        return token
    return None

def test_me(token):
    print_header("3. Testando /auth/me")
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response)
    return response.status_code == 200

def test_list_usuarios(token):
    print_header("4. Testando GET /usuarios")
    response = requests.get(
        f"{BASE_URL}/usuarios",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response)
    return response.status_code == 200

def test_list_entidades(token):
    print_header("5. Testando GET /entidades")
    response = requests.get(
        f"{BASE_URL}/entidades",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response)
    return response.status_code == 200

def test_create_fornecedor(token):
    print_header("6. Testando POST /fornecedores")
    response = requests.post(
        f"{BASE_URL}/fornecedores",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "entidade_id": 1,
            "cnpj": "12345678000190",
            "razao_social": "Empresa Teste Ltda",
            "nome_fantasia": "Empresa Teste"
        }
    )
    print_response(response)
    
    if response.status_code in [200, 201]:
        return response.json().get("id")
    return None

def test_list_fornecedores(token):
    print_header("7. Testando GET /fornecedores")
    response = requests.get(
        f"{BASE_URL}/fornecedores",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response)
    return response.status_code == 200

def main():
    print("\n" + "🚀 INICIANDO TESTES DA API SENTINELA" + "\n")
    
    results = []
    
    # 1. Health Check
    results.append(("Health Check", test_health()))
    
    # 2. Login
    token = test_login()
    if not token:
        print("\n❌ Falha no login. Encerrando testes.")
        return
    results.append(("Login", True))
    
    # 3. Auth Me
    results.append(("Auth Me", test_me(token)))
    
    # 4. List Usuários
    results.append(("List Usuários", test_list_usuarios(token)))
    
    # 5. List Entidades
    results.append(("List Entidades", test_list_entidades(token)))
    
    # 6. Create Fornecedor
    fornecedor_id = test_create_fornecedor(token)
    results.append(("Create Fornecedor", fornecedor_id is not None))
    
    # 7. List Fornecedores
    results.append(("List Fornecedores", test_list_fornecedores(token)))
    
    # Resumo
    print_header("📊 RESUMO DOS TESTES")
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed} testes")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️  {failed} teste(s) falharam")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante os testes: {e}")
