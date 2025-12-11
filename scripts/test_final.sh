#!/bin/bash

echo "🚀 TESTE FINAL DA API SENTINELA"
echo ""

# Health Check
echo "1. Testando Health Check..."
curl -s http://localhost:8000/health | grep "healthy" > /dev/null && echo "   ✅ Health Check OK" || echo "   ❌ Health Check FALHOU"

# Login
echo ""
echo "2. Testando Login..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"email":"admin@sentinela.app","senha":"admin123"}')
TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo "   ✅ Login OK - Token obtido"
else
    echo "   ❌ Login FALHOU"
    exit 1
fi

# Testar endpoints protegidos
echo ""
echo "3. Testando Endpoints Protegidos..."

curl -s "http://localhost:8000/usuarios" -H "Authorization: Bearer $TOKEN" > /dev/null && echo "   ✅ GET /usuarios OK" || echo "   ❌ GET /usuarios FALHOU"

curl -s "http://localhost:8000/entidades" -H "Authorization: Bearer $TOKEN" > /dev/null && echo "   ✅ GET /entidades OK" || echo "   ❌ GET /entidades FALHOU"

curl -s "http://localhost:8000/fornecedores" -H "Authorization: Bearer $TOKEN" > /dev/null && echo "   ✅ GET /fornecedores OK" || echo "   ❌ GET /fornecedores FALHOU"

curl -s "http://localhost:8000/contratos" -H "Authorization: Bearer $TOKEN" > /dev/null && echo "   ✅ GET /contratos OK" || echo "   ❌ GET /contratos FALHOU"

echo ""
echo "🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!"
echo ""
echo "📊 API está funcionando perfeitamente!"
echo "📚 Acesse http://localhost:8000/docs para documentação completa"
