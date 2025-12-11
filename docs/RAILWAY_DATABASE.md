# 🗄️ Configuração do Banco de Dados no Railway

## PostgreSQL no Railway

O Railway oferece PostgreSQL como um serviço integrado. Para configurar:

### 1. Adicionar PostgreSQL ao projeto

No dashboard do Railway, clique em "Add" > "Database" > "PostgreSQL"

### 2. Configurar variável de ambiente

Após criar o banco, copie a `DATABASE_URL` gerada automaticamente e configure:

```bash
railway variables set DATABASE_URL=postgresql://...
```

### 3. Migrações do banco

As migrações serão executadas automaticamente quando a aplicação iniciar, graças ao código em `main.py`:

```python
# Criar tabelas se não existirem
create_db_and_tables()
```

### 4. Verificar conexão

Você pode verificar se a conexão está funcionando através dos logs da aplicação:

```bash
railway logs
```

## 🔧 Variáveis de Ambiente Necessárias

### Backend
- `DATABASE_URL`: URL de conexão com PostgreSQL
- `SECRET_KEY`: Chave secreta para JWT (gere uma segura)
- `ALGORITHM`: Algoritmo de criptografia (padrão: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiração do token (padrão: 30)
- `TOTP_ISSUER`: Emissor do TOTP (padrão: "Sentinela API")
- `ENVIRONMENT`: Ambiente (padrão: "production")

### Frontend
- `VITE_API_URL`: URL da API do backend (ex: https://sentinela-api-backend.railway.app)

## 🚀 Ordem de Deploy

1. **Backend primeiro**: Configure o banco e faça deploy do backend
2. **Pegue a URL**: Anote a URL gerada para o backend
3. **Frontend**: Configure `VITE_API_URL` com a URL do backend e faça deploy

## 📊 Monitoramento

### Health Check
A aplicação tem um endpoint `/health` para verificar se está funcionando:

```bash
curl https://sua-app.railway.app/health
```

### Logs
```bash
railway logs --tail
```

### Status
```bash
railway status
```