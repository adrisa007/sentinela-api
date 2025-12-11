#!/bin/bash

echo "🧪 VALIDAÇÃO DE ENDPOINTS - SENTINELA API"
echo "=========================================="
echo ""

TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sentinela.app","senha":"admin123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "✅ Token obtido"
echo ""

# Endpoints corretos
declare -A endpoints=(
  ["/auth/me"]="Autenticação"
  ["/entidades"]="Entidades"
  ["/usuarios"]="Usuários"
  ["/fornecedores"]="Fornecedores"
  ["/contratos"]="Contratos"
  ["/tipo-certidoes"]="Tipos de Certidão"
  ["/certidoes-fornecedor"]="Certidões"
  ["/fiscais-designados"]="Fiscais"
  ["/ocorrencias-fiscalizacao"]="Ocorrências"
  ["/cronogramas"]="Cronogramas"
  ["/penalidades"]="Penalidades"
  ["/matriz-riscos"]="Matriz de Riscos"
  ["/auditoria"]="Auditoria"
)

success=0
failed=0

for endpoint in "${!endpoints[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8000$endpoint" \
    -H "Authorization: Bearer $TOKEN")
  
  if [ "$status" = "200" ]; then
    echo "✅ ${endpoints[$endpoint]} ($endpoint) - OK"
    ((success++))
  else
    echo "❌ ${endpoints[$endpoint]} ($endpoint) - Status: $status"
    ((failed++))
  fi
done

echo ""
echo "📊 RESULTADO: $success sucessos, $failed falhas"
echo ""
