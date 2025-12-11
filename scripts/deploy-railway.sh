#!/bin/bash

# Script de deploy para Railway
# Uso: ./deploy-railway.sh [backend|frontend|all]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT"
FRONTEND_DIR="$PROJECT_ROOT/frontend/frontend"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        log_error "Railway CLI não está instalado."
        log_info "Instalando Railway CLI..."
        if command -v npm &> /dev/null; then
            npm install -g @railway/cli
            log_success "Railway CLI instalado com sucesso!"
        else
            log_error "NPM não encontrado. Instale o Node.js e npm primeiro."
            log_info "Ou instale manualmente: npm install -g @railway/cli"
            exit 1
        fi
    fi
}

login() {
    log_info "🔐 Fazendo login no Railway..."
    railway login
    if [ $? -eq 0 ]; then
        log_success "Login realizado com sucesso!"
    else
        log_error "Falha no login. Tente novamente."
        exit 1
    fi
}

check_login() {
    # Tentar executar um comando que requer autenticação
    if ! railway projects list &> /dev/null; then
        log_error "Você não está logado no Railway."
        log_info "Execute: railway login"
        log_info "Após fazer login, execute novamente: $0 $1"
        exit 1
    fi
}

deploy_backend() {
    log_info "🚀 Fazendo deploy do backend..."

    cd "$BACKEND_DIR"

    # Verificar se projeto já existe
    if [ ! -f "railway.toml" ]; then
        log_error "Arquivo railway.toml não encontrado no backend"
        exit 1
    fi

    # Fazer deploy
    railway up

    log_success "Backend deployado com sucesso!"
}

deploy_frontend() {
    log_info "🎨 Fazendo deploy do frontend..."

    cd "$FRONTEND_DIR"

    # Verificar se projeto já existe
    if [ ! -f "railway.toml" ]; then
        log_error "Arquivo railway.toml não encontrado no frontend"
        exit 1
    fi

    # Fazer deploy
    railway up

    log_success "Frontend deployado com sucesso!"
}

setup_backend_env() {
    log_info "🔧 Configurando variáveis de ambiente do backend..."

    cd "$BACKEND_DIR"

    # Verificar se já existem variáveis
    if railway variables get DATABASE_URL &> /dev/null; then
        log_warning "Variáveis de ambiente já configuradas. Pulando..."
        return
    fi

    log_info "Configure as seguintes variáveis no Railway:"
    echo "  DATABASE_URL=postgresql://..."
    echo "  SECRET_KEY=sua-chave-secreta-aqui"
    echo "  ALGORITHM=HS256"
    echo "  ACCESS_TOKEN_EXPIRE_MINUTES=30"
    echo "  TOTP_ISSUER=Sentinela API"
    echo "  ENVIRONMENT=production"

    log_info "Ou execute os comandos:"
    echo "  railway variables set DATABASE_URL=postgresql://..."
    echo "  railway variables set SECRET_KEY=sua-chave-secreta-aqui"
    echo "  # ... outras variáveis"
}

setup_frontend_env() {
    log_info "🔧 Configurando variáveis de ambiente do frontend..."

    cd "$FRONTEND_DIR"

    # Verificar se já existem variáveis
    if railway variables get VITE_API_URL &> /dev/null; then
        log_warning "Variáveis de ambiente já configuradas. Pulando..."
        return
    fi

    log_info "Configure a seguinte variável no Railway:"
    echo "  VITE_API_URL=https://seu-backend.railway.app"

    log_info "Ou execute o comando:"
    echo "  railway variables set VITE_API_URL=https://seu-backend.railway.app"
}

init_projects() {
    log_info "📦 Inicializando projetos no Railway..."

    # Backend
    log_info "Inicializando backend..."
    cd "$BACKEND_DIR"
    railway init --name "sentinela-api-backend"

    # Frontend
    log_info "Inicializando frontend..."
    cd "$FRONTEND_DIR"
    railway init --name "sentinela-api-frontend"

    log_success "Projetos inicializados!"
}

show_help() {
    echo "🚂 Script de deploy para Railway - Sentinela API"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  init      - Inicializar projetos no Railway"
    echo "  backend   - Deploy apenas do backend"
    echo "  frontend  - Deploy apenas do frontend"
    echo "  all       - Deploy de backend e frontend"
    echo "  env       - Configurar variáveis de ambiente"
    echo "  login     - Verificar e fazer login no Railway"
    echo "  help      - Mostrar esta ajuda"
    echo ""
    echo "Pré-requisitos:"
    echo "  - Node.js e npm instalados"
    echo "  - Conta no Railway (https://railway.app)"
    echo ""
    echo "Fluxo recomendado:"
    echo "  1. $0 login    # Fazer login no Railway"
    echo "  2. $0 init     # Inicializar projetos"
    echo "  3. $0 env      # Configurar variáveis"
    echo "  4. $0 backend  # Deploy do backend"
    echo "  5. $0 frontend # Deploy do frontend"
    echo ""
    echo "Exemplos:"
    echo "  $0 init"
    echo "  $0 backend"
    echo "  $0 all"
}

main() {
    local command="$1"

    check_railway_cli

    case "$command" in
        "login")
            login
            ;;
        "init")
            check_login
            init_projects
            ;;
        "backend")
            check_login
            deploy_backend
            ;;
        "frontend")
            check_login
            deploy_frontend
            ;;
        "all")
            check_login
            deploy_backend
            deploy_frontend
            ;;
        "env")
            check_login
            setup_backend_env
            setup_frontend_env
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            log_error "Comando desconhecido: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"