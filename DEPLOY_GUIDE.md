# 🚀 Sentinela API - Pronto para Produção!

## ✅ Status do Deploy

**API está ONLINE e funcionando!**

- 🌐 **URL**: http://localhost:8000
- 📚 **Documentação (Swagger)**: http://localhost:8000/docs
- 📖 **Documentação (ReDoc)**: http://localhost:8000/redoc
- 🔍 **Health Check**: http://localhost:8000/health

## 🔐 Credenciais de Acesso

**Usuário ROOT criado:**
- **Email**: `admin@sentinela.app`
- **Senha**: `admin123`
- ⚠️ **IMPORTANTE**: Altere a senha em produção!

## 🧪 Testando a API

### 1. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sentinela.app",
    "senha": "admin123"
  }'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "nome": "Administrador",
    "email": "admin@sentinela.app",
    "perfil": "ROOT",
    ...
  }
}
```

### 2. Usar o token para acessar recursos protegidos

```bash
# Salve o token
TOKEN="seu_token_aqui"

# Liste usuários
curl -X GET "http://localhost:8000/usuarios" \
  -H "Authorization: Bearer $TOKEN"

# Liste entidades
curl -X GET "http://localhost:8000/entidades" \
  -H "Authorization: Bearer $TOKEN"

# Liste fornecedores
curl -X GET "http://localhost:8000/fornecedores" \
  -H "Authorization: Bearer $TOKEN"

# Liste contratos
curl -X GET "http://localhost:8000/contratos" \
  -H "Authorization: Bearer $TOKEN"
```

## 🗄️ Banco de Dados

**PostgreSQL (Neon.tech)** - ✅ Configurado e Rodando

**Tabelas criadas:**
- ✅ entidade
- ✅ usuario
- ✅ fornecedor
- ✅ tipo_certidao (6 tipos pré-cadastrados)
- ✅ certidao_fornecedor
- ✅ contrato
- ✅ fiscal_designado
- ✅ ocorrencia_fiscalizacao
- ✅ cronograma_fisico_fin
- ✅ penalidade
- ✅ matriz_riscos
- ✅ auditoria_global

## 📦 Funcionalidades Implementadas

### ✅ Autenticação e Segurança
- Login com JWT
- Autenticação de dois fatores (TOTP/2FA)
- Hash de senhas com bcrypt
- Middleware de autenticação
- Controle de perfis de acesso

### ✅ Gestão de Entidades
- CRUD completo
- Status (ATIVA, INATIVA, SUSPENSA)
- Configurações personalizadas (JSON)

### ✅ Gestão de Usuários
- CRUD completo
- 6 perfis: ROOT, GESTOR, FISCAL_TECNICO, FISCAL_ADM, APOIO, AUDITOR
- Controle de acesso por perfil
- 2FA opcional

### ✅ Gestão de Fornecedores
- CRUD completo
- Suporte para CNPJ e CPF
- Controle de regularidade
- Certificados e certidões

### ✅ Gestão de Contratos
- CRUD completo
- Vinculação com fornecedores
- Gestores e fiscais
- Cronograma físico-financeiro
- Penalidades
- Matriz de riscos

### ✅ Fiscalização
- Registro de ocorrências
- Geolocalização
- Fotos (JSON)
- Assinaturas digitais

### ✅ Auditoria Global
- Log automático de todas as operações
- IP e User-Agent
- Dados antes/depois das alterações

## 🛠️ Comandos Úteis

### Iniciar o servidor
```bash
cd /workspaces/sentinela-api
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Iniciar com reload (desenvolvimento)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Reinicializar banco de dados
```bash
python init_db.py
```

### Docker
```bash
# Build
docker build -t sentinela-api .

# Run
docker run -p 8000:8000 --env-file .env sentinela-api

# Docker Compose
docker-compose up -d
```

## 🚀 Deploy em Produção

### Opção 1: Render.com
1. Faça push do código para GitHub
2. Conecte o repositório no Render
3. Configure as variáveis de ambiente (.env)
4. Deploy automático!

### Opção 2: Railway.app
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

### Opção 3: Fly.io
```bash
fly launch
fly secrets set SECRET_KEY=sua_chave
fly deploy
```

### Opção 4: Heroku
```bash
heroku create sentinela-api
heroku config:set DATABASE_URL=...
heroku config:set SECRET_KEY=...
git push heroku main
```

## 📊 Monitoramento

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs do servidor
O Uvicorn exibe logs em tempo real no terminal.

## 🔒 Segurança em Produção

**IMPORTANTE! Antes de colocar em produção:**

1. ✅ Alterar `SECRET_KEY` no `.env`
2. ✅ Alterar senha do usuário ROOT
3. ✅ Configurar HTTPS
4. ✅ Configurar CORS apenas para domínios confiáveis
5. ✅ Ativar rate limiting
6. ✅ Configurar backup do banco de dados
7. ✅ Monitorar logs e auditoria

## 📝 Estrutura do Projeto

```
sentinela-api/
├── app/
│   ├── core/           # Configurações, auth, database
│   ├── models/         # Modelos SQLModel
│   ├── routes/         # Rotas/Endpoints
│   ├── services/       # Lógica de negócio
│   └── schemas/        # Schemas Pydantic
├── main.py             # Aplicação principal
├── init_db.py          # Script de inicialização
├── requirements.txt    # Dependências
├── Dockerfile          # Docker
├── docker-compose.yml  # Docker Compose
└── .env                # Variáveis de ambiente
```

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `/docs`
2. Consulte os logs do servidor
3. Revise a tabela `auditoria_global` no banco

## 🎉 Sucesso!

Sua API está pronta para uso! Acesse http://localhost:8000/docs para explorar todos os endpoints disponíveis.

---
Desenvolvido com ❤️ usando FastAPI + SQLModel + PostgreSQL
