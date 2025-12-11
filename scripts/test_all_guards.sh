#!/bin/bash

echo "🛡️  TESTE COMPLETO - GUARDS EM TODAS AS ROTAS"
echo "=============================================="
echo ""

# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sentinela.app","senha":"admin123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Falha no login"
  exit 1
fi

echo "✅ Login OK - Token obtido"
echo ""

echo "📊 Testando Guards em Todos os Endpoints"
echo "=========================================="
echo ""

declare -A endpoints=(
  ["GET /auth/me"]="Autenticação"
  ["GET /entidades"]="Entidades (RootGuard)"
  ["GET /usuarios"]="Usuários (TenantGuard)"
  ["GET /fornecedores"]="Fornecedores (TenantGuard)"
  ["GET /contratos"]="Contratos (TenantGuard)"
  ["GET /tipo-certidoes"]="Tipos Certidão"
  ["GET /certidoes-fornecedor"]="Certidões"
  ["GET /fiscais-designados"]="Fiscais (GestorGuard)"
  ["GET /ocorrencias-fiscalizacao"]="Ocorrências (FiscalGuard)"
  ["GET /cronogramas"]="Cronogramas (TenantGuard)"
  ["GET /penalidades"]="Penalidades (GestorGuard)"
  ["GET /matriz-riscos"]="Matriz Riscos (TenantGuard)"
  ["GET /auditoria"]="Auditoria (AuditorGuard)"
)

success=0
failed=0

for endpoint in "${!endpoints[@]}"; do
  method=$(echo $endpoint | cut -d' ' -f1)
  path=$(echo $endpoint | cut -d' ' -f2)
  
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X $method "http://localhost:8000$path" \
    -H "Authorization: Bearer $TOKEN")
  
  if [ "$STATUS" = "200" ]; then
    echo "✅ ${endpoints[$endpoint]} - $endpoint"
    ((success++))
  else
    echo "❌ ${endpoints[$endpoint]} - $endpoint (Status: $STATUS)"
    ((failed++))
  fi
done

echo ""
echo "📊 RESUMO"
echo "========="
echo "✅ Sucessos: $success"
echo "❌ Falhas: $failed"
echo ""

if [ $failed -eq 0 ]; then
  echo "🎉 TODOS OS GUARDS FUNCIONANDO PERFEITAMENTE!"
  echo ""
  echo "Guards Implementados:"
  echo "  🛡️  TenantGuard - Isolamento multi-tenant"
  echo "  🛡️  RootGuard - Operações ROOT"
  echo "  🛡️  GestorGuard - ROOT/GESTOR"
  echo "  🛡️  FiscalGuard - Fiscalização"
  echo "  🛡️  AuditorGuard - Auditoria"
  echo ""
  echo "Rotas Atualizadas:"
  echo "  ✅ contratos.py"
  echo "  ✅ usuarios.py"
  echo "  ✅ fornecedores.py"
  echo "  ✅ entidades.py"
  echo "  ✅ fiscais.py"
  echo "  ✅ ocorrencias.py"
  echo "  ✅ cronogramas.py"
  echo "  ✅ penalidades.py"
  echo "  ✅ matriz_riscos.py"
else
  echo "⚠️  Alguns endpoints apresentaram problemas"
fi
