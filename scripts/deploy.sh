#!/bin/bash

echo "🚀 Iniciando deploy da Sentinela API..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verifica se .env existe
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo "Copie .env.example para .env e configure as variáveis"
    exit 1
fi

# Carrega variáveis de ambiente
source .env

# Verifica conexão com banco
echo -e "${YELLOW}📊 Verificando conexão com banco de dados...${NC}"
python -c "from app.core.database import engine; engine.connect()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Conexão com banco estabelecida${NC}"
else
    echo -e "${RED}❌ Erro ao conectar com banco de dados${NC}"
    exit 1
fi

# Inicializa banco de dados
echo -e "${YELLOW}📦 Inicializando banco de dados...${NC}"
python init_db.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Banco de dados inicializado${NC}"
else
    echo -e "${RED}❌ Erro ao inicializar banco de dados${NC}"
    exit 1
fi

# Build Docker (se necessário)
if command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 Construindo imagem Docker...${NC}"
    docker build -t sentinela-api .
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Imagem Docker criada${NC}"
    else
        echo -e "${RED}❌ Erro ao criar imagem Docker${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
echo ""
echo "Para iniciar a aplicação, execute:"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Ou com Docker:"
echo "  docker run -p 8000:8000 --env-file .env sentinela-api"
echo ""
echo "Ou com Docker Compose:"
echo "  docker-compose up -d"
