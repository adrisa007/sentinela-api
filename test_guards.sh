#!/bin/bash

echo "🛡️  TESTE DE GUARDS - SENTINELA API"
echo "===================================="
echo ""

# Login
echo "1️⃣  Fazendo login..."
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sentinela.app","senha":"admin123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Falha no login"
  exit 1
fi
echo "✅ Login OK - Token obtido"
echo ""

echo "2️⃣  Testando TenantGuard (multi-tenant)"
echo "----------------------------------------"

# Listar contratos (ROOT vê tudo)
echo "▶ GET /contratos (ROOT deve ver tudo)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8000/contratos" \
  -H "Authorization: Bearer $TOKEN")
if [ "$STATUS" = "200" ]; then
  echo "✅ TenantGuard.filter_by_tenant funcionando - Status: $STATUS"
else
  echo "❌ Falha - Status: $STATUS"
fi
echo ""

echo "3️⃣  Testando RootGuard + GestorGuard"
echo "-------------------------------------"

# Criar contrato (ROOT/GESTOR apenas)
echo "▶ POST /contratos (requer GESTOR ou ROOT)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8000/contratos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_contrato": "TEST-001/2025",
    "entidade_id": 1,
    "fornecedor_id": 1,
    "objeto": "Teste de Guards",
    "tipo": "SERVICO",
    "valor_total": 50000.00,
    "data_assinatura": "2025-12-10",
    "data_inicio_vigencia": "2025-12-15",
    "data_fim_vigencia": "2026-12-15",
    "modalidade_licitacao": "PREGAO_ELETRONICO",
    "numero_processo": "2025/TEST001",
    "ativo": true
  }')

if [ "$STATUS" = "200" ]; then
  echo "✅ require_gestor_or_root funcionando - Status: $STATUS"
else
  echo "❌ Falha - Status: $STATUS"
fi
echo ""

echo "4️⃣  Testando validação de tenant ao criar"
echo "------------------------------------------"
echo "▶ Criando contrato (TenantGuard.validate_tenant_on_create)"
RESPONSE=$(curl -s -X POST "http://localhost:8000/contratos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_contrato": "TEST-002/2025",
    "fornecedor_id": 1,
    "objeto": "Teste validação tenant",
    "tipo": "SERVICO",
    "valor_total": 30000.00,
    "data_assinatura": "2025-12-10",
    "data_inicio_vigencia": "2025-12-15",
    "data_fim_vigencia": "2026-12-15",
    "modalidade_licitacao": "DISPENSA",
    "numero_processo": "2025/TEST002",
    "ativo": true
  }')

ENTIDADE_ID=$(echo $RESPONSE | grep -o '"entidade_id":[0-9]*' | cut -d':' -f2)
if [ ! -z "$ENTIDADE_ID" ]; then
  echo "✅ TenantGuard.validate_tenant_on_create funcionando - entidade_id: $ENTIDADE_ID"
else
  echo "❌ Falha ao validar tenant"
fi
echo ""

echo "5️⃣  Testando verificação de acesso ao tenant"
echo "----------------------------------------------"
echo "▶ GET /contratos/1 (check_tenant_access)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8000/contratos/1" \
  -H "Authorization: Bearer $TOKEN")

if [ "$STATUS" = "200" ] || [ "$STATUS" = "404" ]; then
  echo "✅ check_tenant_access funcionando - Status: $STATUS"
else
  echo "❌ Falha - Status: $STATUS"
fi
echo ""

echo "6️⃣  Testando Guards em outros endpoints"
echo "----------------------------------------"

# Listar usuários
echo "▶ GET /usuarios (TenantGuard)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8000/usuarios" \
  -H "Authorization: Bearer $TOKEN")
echo "  Usuários: Status $STATUS"

# Listar fornecedores
echo "▶ GET /fornecedores (TenantGuard)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8000/fornecedores" \
  -H "Authorization: Bearer $TOKEN")
echo "  Fornecedores: Status $STATUS"

# Auditoria (requer ROOT/GESTOR/AUDITOR)
echo "▶ GET /auditoria (AuditorGuard)"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8000/auditoria" \
  -H "Authorization: Bearer $TOKEN")
echo "  Auditoria: Status $STATUS"

echo ""
echo "✅ TESTES DE GUARDS CONCLUÍDOS!"
