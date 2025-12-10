# 🎨 Guia de Integração Frontend - Sentinela API

## 📋 Informações Essenciais

### Base URL
```
http://localhost:8000
```

### Documentação Interativa
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### CORS Configurado
```javascript
// Origens permitidas:
- http://localhost:3000  // React/Next.js dev
- http://localhost:8000  // API
- https://sentinela.app  // Produção
```

---

## 🔐 Autenticação

### 1. Login
```javascript
POST /auth/login

// Request
{
  "email": "admin@sentinela.app",
  "senha": "admin123"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "usuario": {
    "id": 1,
    "nome": "Administrador",
    "email": "admin@sentinela.app",
    "perfil": "ROOT",
    "entidade_id": 1,
    "totp_habilitado": false,
    "ativo": true
  }
}
```

### 2. Usar Token
```javascript
// Headers em todas as requisições protegidas
Authorization: Bearer <seu_token_jwt>
```

### 3. Verificar Usuário Logado
```javascript
GET /auth/me

// Response
{
  "id": 1,
  "nome": "Administrador",
  "email": "admin@sentinela.app",
  "perfil": "ROOT",
  "entidade_id": 1
}
```

### 4. Configurar 2FA (Opcional)
```javascript
// Gerar QR Code
POST /auth/totp/setup
// Returns: qr_code_base64, secret

// Habilitar 2FA
POST /auth/totp/verify
{
  "codigo": "123456"
}

// Login com 2FA
POST /auth/login
{
  "email": "user@example.com",
  "senha": "password",
  "codigo_totp": "123456"  // Obrigatório se 2FA ativo
}
```

---

## 📊 Endpoints Disponíveis

### Perfis de Acesso
- **ROOT**: Acesso total
- **GESTOR**: Gestão da entidade
- **FISCAL_TECNICO**: Fiscalização técnica
- **FISCAL_ADM**: Fiscalização administrativa
- **APOIO**: Suporte operacional
- **AUDITOR**: Visualização de auditorias

---

## 🏢 1. Entidades

```javascript
// Listar
GET /entidades?skip=0&limit=100

// Buscar por ID
GET /entidades/1

// Criar (ROOT, GESTOR)
POST /entidades
{
  "nome": "Prefeitura Municipal",
  "sigla": "PM",
  "cnpj": "12345678000190",
  "tipo": "MUNICIPAL",
  "ativo": true
}

// Atualizar (ROOT, GESTOR)
PUT /entidades/1

// Deletar (ROOT)
DELETE /entidades/1
```

---

## 👥 2. Usuários

```javascript
// Listar
GET /usuarios?skip=0&limit=100

// Buscar por ID
GET /usuarios/1

// Buscar por entidade
GET /usuarios/entidade/1

// Buscar por perfil
GET /usuarios/perfil/GESTOR

// Criar (ROOT, GESTOR)
POST /usuarios
{
  "nome": "João Silva",
  "email": "joao@example.com",
  "senha": "senha123",
  "perfil": "FISCAL_TECNICO",
  "entidade_id": 1,
  "cpf": "12345678901",
  "telefone": "(11) 98765-4321",
  "ativo": true
}

// Atualizar (ROOT, GESTOR, próprio usuário)
PUT /usuarios/1

// Deletar (ROOT, GESTOR)
DELETE /usuarios/1
```

---

## 🏭 3. Fornecedores

```javascript
// Listar
GET /fornecedores?skip=0&limit=100&ativo=true

// Buscar por ID
GET /fornecedores/1

// Buscar por CNPJ/CPF
GET /fornecedores/cnpj/12345678000190

// Criar
POST /fornecedores
{
  "nome_razao_social": "Empresa XYZ Ltda",
  "nome_fantasia": "XYZ",
  "cnpj_cpf": "12345678000190",
  "tipo_pessoa": "JURIDICA",
  "email": "contato@xyz.com",
  "telefone": "(11) 3333-4444",
  "endereco": "Rua A, 123",
  "cidade": "São Paulo",
  "estado": "SP",
  "cep": "01234-567",
  "ativo": true
}

// Atualizar
PUT /fornecedores/1

// Deletar
DELETE /fornecedores/1
```

---

## 📜 4. Tipos de Certidão

```javascript
// Listar
GET /tipo-certidoes?skip=0&limit=100

// Buscar por ID
GET /tipo-certidoes/1

// Buscar por código
GET /tipo-certidoes/codigo/CND_FEDERAL

// Criar (ROOT, GESTOR)
POST /tipo-certidoes
{
  "codigo": "CND_MUNICIPAL",
  "nome": "Certidão Negativa Municipal",
  "obrigatoria_licitacao": true,
  "obrigatoria_contratacao": true,
  "prazo_validade_dias": 90,
  "api_disponivel": false
}

// Atualizar (ROOT, GESTOR)
PUT /tipo-certidoes/1

// Deletar (ROOT)
DELETE /tipo-certidoes/1
```

---

## 📄 5. Certidões de Fornecedor

```javascript
// Listar
GET /certidoes-fornecedor?skip=0&limit=100

// Buscar por ID
GET /certidoes-fornecedor/1

// Buscar por fornecedor
GET /certidoes-fornecedor/fornecedor/1

// Buscar vencidas
GET /certidoes-fornecedor/vencidas

// Criar
POST /certidoes-fornecedor
{
  "fornecedor_id": 1,
  "tipo_certidao_id": 1,
  "numero_certidao": "123456789",
  "data_emissao": "2025-12-10",
  "data_validade": "2026-06-10",
  "arquivo_url": "https://storage.example.com/certidao.pdf",
  "observacoes": "Certidão válida"
}

// Atualizar
PUT /certidoes-fornecedor/1

// Deletar
DELETE /certidoes-fornecedor/1
```

---

## 📝 6. Contratos

```javascript
// Listar
GET /contratos?skip=0&limit=100&ativo=true

// Buscar por ID
GET /contratos/1

// Buscar por número
GET /contratos/numero/001/2025

// Buscar por fornecedor
GET /contratos/fornecedor/1

// Criar (ROOT, GESTOR)
POST /contratos
{
  "numero_contrato": "001/2025",
  "entidade_id": 1,
  "fornecedor_id": 1,
  "objeto": "Prestação de serviços de limpeza",
  "tipo": "SERVICO",
  "valor_total": 100000.00,
  "data_assinatura": "2025-01-01",
  "data_inicio_vigencia": "2025-01-15",
  "data_fim_vigencia": "2025-12-31",
  "modalidade_licitacao": "PREGAO_ELETRONICO",
  "numero_processo": "2024/12345",
  "ativo": true
}

// Atualizar (ROOT, GESTOR)
PUT /contratos/1

// Deletar (ROOT, GESTOR)
DELETE /contratos/1
```

---

## 👨‍💼 7. Fiscais Designados

```javascript
// Listar
GET /fiscais-designados?skip=0&limit=100

// Buscar por ID
GET /fiscais-designados/1

// Buscar por contrato
GET /fiscais-designados/contrato/1

// Buscar ativos
GET /fiscais-designados/ativos

// Criar (ROOT, GESTOR)
POST /fiscais-designados
{
  "contrato_id": 1,
  "usuario_id": 2,
  "tipo_fiscal": "TECNICO",
  "data_designacao": "2025-01-15",
  "portaria_numero": "001/2025",
  "ativo": true
}

// Atualizar (ROOT, GESTOR)
PUT /fiscais-designados/1

// Deletar (ROOT, GESTOR)
DELETE /fiscais-designados/1
```

---

## 🚨 8. Ocorrências de Fiscalização

```javascript
// Listar
GET /ocorrencias-fiscalizacao?skip=0&limit=100

// Buscar por ID
GET /ocorrencias-fiscalizacao/1

// Buscar por contrato
GET /ocorrencias-fiscalizacao/contrato/1

// Buscar por tipo
GET /ocorrencias-fiscalizacao/tipo/ATRASO

// Criar (Fiscais)
POST /ocorrencias-fiscalizacao
{
  "contrato_id": 1,
  "fiscal_id": 2,
  "tipo_ocorrencia": "ATRASO",
  "descricao": "Atraso na entrega do relatório mensal",
  "data_ocorrencia": "2025-12-10",
  "gravidade": "MEDIA",
  "status": "ABERTA"
}

// Atualizar (Fiscais)
PUT /ocorrencias-fiscalizacao/1

// Deletar (ROOT, GESTOR)
DELETE /ocorrencias-fiscalizacao/1
```

---

## 📅 9. Cronogramas Físico-Financeiro

```javascript
// Listar
GET /cronogramas?skip=0&limit=100

// Buscar por ID
GET /cronogramas/1

// Buscar por contrato
GET /cronogramas/contrato/1

// Criar (ROOT, GESTOR)
POST /cronogramas
{
  "contrato_id": 1,
  "mes_referencia": 1,
  "ano_referencia": 2025,
  "percentual_fisico_previsto": 10.0,
  "percentual_fisico_realizado": 8.5,
  "valor_previsto": 10000.00,
  "valor_realizado": 8500.00,
  "observacoes": "Atraso devido a condições climáticas"
}

// Atualizar (Fiscais)
PUT /cronogramas/1

// Deletar (ROOT, GESTOR)
DELETE /cronogramas/1
```

---

## ⚠️ 10. Penalidades

```javascript
// Listar
GET /penalidades?skip=0&limit=100

// Buscar por ID
GET /penalidades/1

// Buscar por contrato
GET /penalidades/contrato/1

// Buscar por tipo
GET /penalidades/tipo/MULTA

// Criar (ROOT, GESTOR)
POST /penalidades
{
  "contrato_id": 1,
  "tipo_penalidade": "MULTA",
  "motivo": "Atraso na execução",
  "valor": 5000.00,
  "data_aplicacao": "2025-12-10",
  "processo_numero": "2025/456",
  "status": "APLICADA"
}

// Atualizar (ROOT, GESTOR)
PUT /penalidades/1

// Deletar (ROOT)
DELETE /penalidades/1
```

---

## ⚡ 11. Matriz de Riscos

```javascript
// Listar
GET /matriz-riscos?skip=0&limit=100

// Buscar por ID
GET /matriz-riscos/1

// Buscar por contrato
GET /matriz-riscos/contrato/1

// Buscar por nível
GET /matriz-riscos/nivel/ALTO

// Criar (ROOT, GESTOR, Fiscais)
POST /matriz-riscos
{
  "contrato_id": 1,
  "categoria_risco": "OPERACIONAL",
  "descricao_risco": "Falta de mão de obra especializada",
  "probabilidade": "MEDIA",
  "impacto": "ALTO",
  "nivel_risco": "ALTO",
  "medidas_mitigacao": "Contratar empresa com equipe própria",
  "responsavel_monitoramento": "Fiscal Técnico",
  "status": "EM_MONITORAMENTO"
}

// Atualizar
PUT /matriz-riscos/1

// Deletar (ROOT, GESTOR)
DELETE /matriz-riscos/1
```

---

## 📊 12. Auditoria

```javascript
// Listar (ROOT, GESTOR, AUDITOR)
GET /auditoria?skip=0&limit=100&entidade_id=1

// Filtros avançados
GET /auditoria?usuario_id=1&tabela_afetada=contratos&acao=POST&data_inicio=2025-12-01&data_fim=2025-12-31

// Buscar por ID
GET /auditoria/1

// Histórico de usuário
GET /auditoria/usuario/1?limit=50

// Histórico de tabela
GET /auditoria/tabela/contratos?registro_id=5

// Estatísticas
GET /auditoria/estatisticas/resumo?entidade_id=1

// Response
{
  "total_registros": 1547,
  "usuarios_ativos": 12,
  "tabelas_afetadas": 8,
  "acoes_mais_comuns": [
    {
      "acao": "POST /auth/login",
      "quantidade": 456
    }
  ]
}
```

---

## 🔄 Exemplo de Integração React

### Setup Axios
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para adicionar token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para tratar erros
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Hook de Autenticação
```javascript
import { useState, useEffect } from 'react';
import api from './api';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, []);

  async function loadUser() {
    try {
      const { data } = await api.get('/auth/me');
      setUser(data);
    } catch (error) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  }

  async function login(email, senha, codigo_totp) {
    const { data } = await api.post('/auth/login', {
      email,
      senha,
      codigo_totp
    });
    localStorage.setItem('token', data.access_token);
    setUser(data.usuario);
    return data;
  }

  function logout() {
    localStorage.removeItem('token');
    setUser(null);
  }

  return { user, loading, login, logout };
}
```

### Exemplo de Componente
```javascript
import { useEffect, useState } from 'react';
import api from './api';

export function ContratosList() {
  const [contratos, setContratos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadContratos();
  }, []);

  async function loadContratos() {
    try {
      const { data } = await api.get('/contratos?ativo=true');
      setContratos(data);
    } catch (error) {
      console.error('Erro ao carregar contratos:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Carregando...</div>;

  return (
    <div>
      <h1>Contratos Ativos</h1>
      {contratos.map(contrato => (
        <div key={contrato.id}>
          <h3>{contrato.numero_contrato}</h3>
          <p>{contrato.objeto}</p>
          <p>Valor: R$ {contrato.valor_total.toLocaleString('pt-BR')}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 🎯 Recursos Importantes

### Paginação
```javascript
// Todas as listagens suportam paginação
GET /endpoint?skip=0&limit=50
```

### Filtros
```javascript
// Maioria dos endpoints tem filtros específicos
GET /contratos?ativo=true
GET /usuarios?perfil=GESTOR
GET /fornecedores?ativo=true
```

### Ordenação (via query params customizados)
```javascript
// Implementar no backend se necessário
GET /contratos?ordenar_por=data_assinatura&ordem=desc
```

---

## 🚨 Tratamento de Erros

### Códigos HTTP
- **200**: Sucesso
- **201**: Criado
- **400**: Dados inválidos
- **401**: Não autenticado
- **403**: Sem permissão
- **404**: Não encontrado
- **409**: Conflito (duplicado)
- **422**: Validação falhou
- **500**: Erro interno

### Formato de Erro
```javascript
{
  "detail": "Mensagem de erro descritiva"
}
```

---

## ✅ Checklist de Implementação

- [ ] Configurar axios/fetch com baseURL
- [ ] Implementar interceptor de autenticação
- [ ] Criar hook/context de autenticação
- [ ] Implementar tela de login
- [ ] Implementar logout
- [ ] Criar componentes CRUD para cada entidade
- [ ] Adicionar validação de formulários
- [ ] Implementar tratamento de erros
- [ ] Adicionar loading states
- [ ] Implementar paginação
- [ ] Adicionar filtros de busca
- [ ] Testar permissões por perfil
- [ ] Implementar 2FA (opcional)
- [ ] Dashboard de auditoria (opcional)

---

**Versão**: 1.0.0  
**Status**: ✅ Backend Pronto para Integração  
**Data**: 10 de Dezembro de 2025
