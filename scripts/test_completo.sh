#!/bin/bash

echo "🧪 TESTE COMPLETO DA API - SENTINELA"
echo "====================================="
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

# Teste endpoints
echo "2️⃣  Testando endpoints principais..."

endpoints=(
  "GET /auth/me"
  "GET /entidades"
  "GET /usuarios"
  "GET /fornecedores"
  "GET /contratos"
  "GET /tipo_certidao"
  "GET /certidoes"
  "GET /fiscais"
  "GET /ocorrencias"
  "GET /cronogramas"
  "GET /penalidades"
  "GET /matriz_riscos"
  "GET /auditoria"
)

for endpoint in "${endpoints[@]}"; do
  method=$(echo $endpoint | cut -d' ' -f1)
  path=$(echo $endpoint | cut -d' ' -f2)
  
  status=$(curl -s -o /dev/null -w "%{http_code}" -X $method "http://localhost:8000$path" \
    -H "Authorization: Bearer $TOKEN")
  
  if [ "$status" = "200" ]; then
    echo "✅ $endpoint - Status: $status"
  else
    echo "❌ $endpoint - Status: $status"
  fi
done

echo ""
echo "3️⃣  Testando estatísticas de auditoria..."
curl -s -X GET "http://localhost:8000/auditoria/estatisticas/resumo" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "✅ TESTES CONCLUÍDOS!"
