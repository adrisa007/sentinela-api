# Sentinela API

Sistema completo de fiscalização e gestão de contratos conforme a Lei 14.133/21, com integração ao Portal Nacional de Contratações Públicas (PNCP).

## 📋 Sobre o Projeto

O Sentinela API é uma solução robusta para gestão de contratos públicos, oferecendo:

- **Gestão Completa de Contratos**: Cadastro, acompanhamento e controle de contratos públicos
- **Fiscalização Integrada**: Sistema completo de designação de fiscais e registro de ocorrências
- **Integração PNCP**: Validação automática de fornecedores e consulta de contratos no Portal Nacional
- **Auditoria Total**: Rastreamento completo de todas as operações do sistema
- **Multi-tenant**: Isolamento completo por entidade com sistema de guards
- **Segurança Avançada**: Autenticação JWT, controle de acesso baseado em perfis e proteção CSRF

## 🚀 Funcionalidades Principais

### 📊 Gestão de Contratos
- Cadastro completo de contratos com validação automática
- Controle de cronogramas físico-financeiros
- Gestão de penalidades e ocorrências de fiscalização
- Matriz de riscos integrada

### 👥 Gestão de Usuários e Entidades
- Sistema multi-tenant com isolamento por entidade
- Perfis de usuário: ROOT, GESTOR, AUDITOR, APOIO
- Autenticação JWT com TOTP (2FA) opcional
- Controle granular de permissões

### 🔍 Integração PNCP
- **Validação de Fornecedores**: Verificação automática de regularidade cadastral
- **Busca de Contratos**: Consulta histórica de contratos por fornecedor
- **Verificação de Certidões**: Status atualizado de certidões obrigatórias
- **Sincronização em Background**: Processamento assíncrono com Celery

### 📈 Sistema de Auditoria
- Log completo de todas as operações
- Filtros avançados por entidade, usuário, tabela e período
- Estatísticas gerenciais
- Processamento em background para auditorias pesadas

### 🛡️ Segurança e Conformidade
- Middleware CSRF para proteção contra ataques
- Rate limiting para controle de carga
- Auditoria imutável de todas as operações
- Conformidade com Lei 14.133/21

## 🏗️ Arquitetura

### Tecnologias
- **Backend**: FastAPI (Python 3.12+)
- **Banco de Dados**: PostgreSQL
- **Cache/Message Broker**: Redis
- **Tarefas em Background**: Celery
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Autenticação**: JWT com bcrypt
- **Documentação**: OpenAPI/Swagger

### Estrutura do Projeto
```
sentinela-api/
├── app/
│   ├── core/           # Configurações centrais
│   │   ├── auth.py     # Autenticação JWT
│   │   ├── config.py   # Configurações da aplicação
│   │   ├── database.py # Conexão com banco
│   │   ├── guards.py   # Sistema de isolamento multi-tenant
│   │   ├── middleware.py # Middlewares customizados
│   │   ├── security.py # Utilitários de segurança
│   │   ├── celery_app.py # Configuração Celery
│   │   ├── pncp_config.py # Configurações PNCP
│   │   └── dependencies.py # Dependências compartilhadas
│   ├── models/         # Modelos de dados SQLModel
│   ├── routes/         # Endpoints da API
│   ├── schemas/        # Schemas Pydantic
│   ├── services/       # Lógica de negócio
│   └── tasks/          # Tarefas Celery
├── tests/              # Testes automatizados
├── alembic/            # Migrações de banco
├── docker-compose.yml  # Orquestração de containers
└── requirements.txt    # Dependências Python
```

## 🐳 Instalação e Execução

### Pré-requisitos
- Docker e Docker Compose
- Python 3.12+ (opcional, para desenvolvimento local)

### 1. Clonagem do Repositório
```bash
git clone https://github.com/adrisa007/sentinela-api.git
cd sentinela-api
```

### 2. Configuração do Ambiente
```bash
# Copiar arquivo de exemplo de variáveis de ambiente
cp .env.example .env

# Editar as variáveis conforme necessário
nano .env
```

### 3. Execução com Docker
```bash
# Construir e iniciar todos os serviços
docker-compose up -d

# Verificar se os containers estão rodando
docker-compose ps

# Ver logs dos serviços
docker-compose logs -f
```

### 4. Inicialização do Banco de Dados
```bash
# Executar dentro do container da aplicação
docker-compose exec api python init_db.py
```

### 5. Acesso à Aplicação
- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Autenticação

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -H "x-csrf-token: sentinela-csrf" \
  -d '{"email":"admin@sentinela.app","senha":"admin123"}'
```

### Usuário Padrão
Após a inicialização, é criado automaticamente:
- **Email**: admin@sentinela.app
- **Senha**: admin123
- **Perfil**: ROOT

⚠️ **IMPORTANTE**: Altere a senha padrão em produção!

## 📚 API Endpoints

### Autenticação
- `POST /auth/login` - Login do usuário
- `POST /auth/register` - Registro de novo usuário
- `GET /auth/me` - Dados do usuário autenticado
- `POST /auth/totp/setup` - Configurar 2FA
- `POST /auth/totp/verify` - Verificar configuração 2FA
- `POST /auth/totp/disable` - Desabilitar 2FA

### Gestão de Entidades
- `GET/POST /entidades` - Listar/Criar entidades
- `GET/PUT/DELETE /entidades/{id}` - Gerenciar entidade específica

### Gestão de Usuários
- `GET/POST /usuarios` - Listar/Criar usuários
- `GET/PUT/DELETE /usuarios/{id}` - Gerenciar usuário específico

### Gestão de Fornecedores
- `GET/POST /fornecedores` - Listar/Criar fornecedores
- `GET/PUT/DELETE /fornecedores/{id}` - Gerenciar fornecedor específico

### Gestão de Contratos
- `GET/POST /contratos` - Listar/Criar contratos
- `GET/PUT/DELETE /contratos/{id}` - Gerenciar contrato específico

### Gestão de Certidões
- `GET/POST /tipo-certidoes` - Listar/Criar tipos de certidão
- `GET/POST /certidoes-fornecedor` - Listar/Criar certidões de fornecedor
- `GET /certidoes-fornecedor/{id}` - Obter certidão específica
- `GET /certidoes-fornecedor/fornecedor/{id}/vencidas` - Certidões vencidas

### Fiscais e Fiscalização
- `GET/POST /fiscais-designados` - Listar/Designar fiscais
- `DELETE /fiscais-designados/{id}` - Remover designação
- `GET/POST /ocorrencias-fiscalizacao` - Listar/Registrar ocorrências
- `GET /ocorrencias-fiscalizacao/{id}` - Obter ocorrência específica

### Cronogramas e Penalidades
- `GET/POST /cronogramas` - Listar/Criar etapas do cronograma
- `GET/PUT /cronogramas/{id}` - Gerenciar etapa específica
- `GET/POST /penalidades` - Listar/Criar penalidades
- `GET/PUT /penalidades/{id}` - Gerenciar penalidade específica

### Matriz de Riscos
- `GET/POST /matriz-riscos` - Listar/Criar riscos
- `GET/PUT /matriz-riscos/{id}` - Gerenciar risco específico

### Sistema de Auditoria
- `GET /auditoria` - Listar registros de auditoria (com filtros)
- `GET /auditoria/{id}` - Detalhes de auditoria específica
- `GET /auditoria/usuario/{id}` - Auditoria por usuário
- `GET /auditoria/tabela/{nome}` - Auditoria por tabela
- `GET /auditoria/estatisticas/resumo` - Estatísticas de auditoria
- `POST /auditoria/processar/{id}` - Processar auditoria em background
- `GET /auditoria/task/{task_id}` - Status da tarefa

### Integração PNCP
- `GET /pncp/fornecedor/validar/{cnpj}` - Validar fornecedor no PNCP
- `GET /pncp/fornecedor/{cnpj}/contratos` - Buscar contratos do fornecedor
- `GET /pncp/contrato/{orgao_cnpj}/{numero_contrato}` - Detalhes de contrato
- `GET /pncp/fornecedor/{cnpj}/certidoes` - Verificar certidões do fornecedor
- `POST /pncp/sync/fornecedor/{id}` - Sincronizar fornecedor em background
- `POST /pncp/sync/contratos/{cnpj}` - Sincronizar contratos em background

### Utilitários
- `GET /health` - Health check simples
- `GET /ready` - Health check do banco de dados
- `GET /live` - Health check do Redis

## 🔍 Integração PNCP Detalhada

### Validação de Fornecedor
```bash
curl -H "Authorization: Bearer {token}" \
     -H "x-csrf-token: sentinela-csrf" \
     "http://localhost:8000/pncp/fornecedor/validar/12345678000123"
```

**Resposta**:
```json
{
  "status": "sucesso",
  "cnpj": "12345678000123",
  "validado": true,
  "dados": {
    "razao_social": "Empresa Exemplo Ltda",
    "situacao_cadastral": "ATIVA",
    "regularidade_geral": "REGULAR"
  }
}
```

### Busca de Contratos
```bash
curl -H "Authorization: Bearer {token}" \
     -H "x-csrf-token: sentinela-csrf" \
     "http://localhost:8000/pncp/fornecedor/12345678000123/contratos?pagina=1&tamanho_pagina=50"
```

### Sincronização em Background
```bash
# Sincronizar fornecedor
curl -X POST \
     -H "Authorization: Bearer {token}" \
     -H "x-csrf-token: sentinela-csrf" \
     "http://localhost:8000/pncp/sync/fornecedor/1"

# Verificar status da tarefa
curl -H "Authorization: Bearer {token}" \
     -H "x-csrf-token: sentinela-csrf" \
     "http://localhost:8000/auditoria/task/{task_id}"
```

## 🧪 Testes

### Executar Todos os Testes
```bash
# Dentro do container
docker-compose exec api python -m pytest tests/ -v

# Com cobertura
docker-compose exec api python -m pytest tests/ --cov=app --cov-report=html
```

### Testes Específicos
```bash
# Testes PNCP
docker-compose exec api python -m pytest tests/test_pncp.py -v

# Testes de autenticação
docker-compose exec api python -m pytest tests/test_api.py -v

# Testes de guards
docker-compose exec api python -m pytest tests/test_guards.py -v
```

## 🔧 Desenvolvimento

### Configuração do Ambiente Local
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação localmente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Migrações de Banco
```bash
# Criar nova migração
docker-compose exec api alembic revision --autogenerate -m "Descrição da migração"

# Aplicar migrações
docker-compose exec api alembic upgrade head

# Ver status das migrações
docker-compose exec api alembic current
```

### Trabalhando com Celery
```bash
# Iniciar worker
docker-compose exec api celery -A app.celery_app worker --loglevel=info

# Iniciar beat (agendador)
docker-compose exec api celery -A app.celery_app beat --loglevel=info

# Ou usar o script
./start_celery.sh
```

## 📊 Monitoramento

### Health Checks
- **Aplicação**: `GET /health`
- **Banco de Dados**: `GET /ready`
- **Redis**: `GET /live`

### Logs
```bash
# Logs da aplicação
docker-compose logs -f api

# Logs do banco
docker-compose logs -f postgres

# Logs do Redis
docker-compose logs -f redis

# Logs do Celery
docker-compose logs -f celery_worker
```

## 🔒 Segurança

### Headers CSRF
Todas as requisições `POST`, `PUT`, `PATCH` e `DELETE` requerem:
```
x-csrf-token: sentinela-csrf
```

### Perfis de Acesso
- **ROOT**: Acesso total ao sistema
- **GESTOR**: Gestão de contratos e usuários da entidade
- **AUDITOR**: Acesso apenas leitura e auditoria
- **APOIO**: Acesso limitado a funcionalidades específicas

### Rate Limiting
- Implementado via `slowapi`
- Configurado por endpoint e perfil de usuário

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação em `/docs`
- Verifique os logs da aplicação

---

**Desenvolvido com ❤️ para conformidade com a Lei 14.133/21**
