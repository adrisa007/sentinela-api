# 🚂 Deploy no Railway

Este guia explica como fazer deploy da aplicação Sentinela API no Railway.

## 📋 Pré-requisitos

1. Conta no [Railway.app](https://railway.app)
2. CLI do Railway instalado:
   ```bash
   npm install -g @railway/cli
   ```

## 🚀 Deploy do Backend

### 1. Login no Railway
```bash
railway login
```

### 2. Criar projeto
```bash
cd /workspaces/sentinela-api
railway init
```

### 3. Configurar variáveis de ambiente
```bash
railway variables set DATABASE_URL=postgresql://...
railway variables set SECRET_KEY=sua-chave-secreta-aqui
railway variables set ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables set TOTP_ISSUER="Sentinela API"
railway variables set ENVIRONMENT=production
```

### 4. Fazer deploy
```bash
railway up
```

## 🎨 Deploy do Frontend

### 1. Criar projeto separado
```bash
cd frontend/frontend
railway init
```

### 2. Configurar variável de ambiente
```bash
railway variables set VITE_API_URL=https://seu-backend.railway.app
```

### 3. Fazer deploy
```bash
railway up
```

## 🔧 Configurações

### Backend (railway.toml)
- **Builder:** Dockerfile
- **Porta:** `$PORT` (definida automaticamente pelo Railway)
- **Healthcheck:** `/health`
- **Banco:** PostgreSQL (via variável `DATABASE_URL`)

### Frontend (railway.toml)
- **Builder:** Nixpacks
- **Build:** `npm run build`
- **Start:** `npm run preview`
- **API URL:** Via variável `VITE_API_URL`

## 📊 Monitoramento

Após o deploy, você pode:

1. **Ver logs:** `railway logs`
2. **Verificar status:** `railway status`
3. **Acessar aplicação:** URL gerada automaticamente pelo Railway

## 🔄 Atualizações

Para atualizar a aplicação:
```bash
git add .
git commit -m "Atualização"
railway up
```

## 🐛 Troubleshooting

### Problemas comuns:

1. **Porta não configurada:** O Railway define automaticamente a porta via variável `$PORT`
2. **Banco não conectado:** Verifique se a variável `DATABASE_URL` está correta
3. **Frontend não consegue acessar API:** Configure `VITE_API_URL` com a URL do backend

### Logs de erro:
```bash
railway logs --tail
```

## 📞 Suporte

Para mais informações, consulte a [documentação do Railway](https://docs.railway.app/).