# 📊 API de Auditoria - Documentação

## Visão Geral

A API de Auditoria fornece endpoints completos para visualização e análise dos logs de todas as operações realizadas no sistema. Apenas usuários com perfis **ROOT**, **GESTOR** ou **AUDITOR** têm acesso.

## 🔐 Autenticação

Todos os endpoints requerem autenticação via JWT Bearer Token.

```bash
Authorization: Bearer <seu_token_jwt>
```

## 📋 Endpoints Disponíveis

### 1. Listar Registros de Auditoria

**GET** `/auditoria`

Lista registros de auditoria com filtros avançados.

**Query Parameters:**
- `skip` (int, padrão: 0) - Registros para pular (paginação)
- `limit` (int, padrão: 100, max: 1000) - Quantidade de registros
- `entidade_id` (int, opcional) - Filtrar por entidade
- `usuario_id` (int, opcional) - Filtrar por usuário
- `tabela_afetada` (string, opcional) - Filtrar por tabela
- `acao` (string, opcional) - Filtrar por ação (busca parcial)
- `data_inicio` (date, opcional) - Data início (YYYY-MM-DD)
- `data_fim` (date, opcional) - Data fim (YYYY-MM-DD)

**Exemplo:**
```bash
curl "http://localhost:8000/auditoria?limit=10&tabela_afetada=usuarios" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:**
```json
[
  {
    "id": 1,
    "entidade_id": 1,
    "usuario_id": 1,
    "acao": "POST /usuarios",
    "tabela_afetada": "usuarios",
    "registro_id": 2,
    "timestamp": "2025-12-10T19:00:00"
  }
]
```

---

### 2. Obter Detalhes de Auditoria

**GET** `/auditoria/{auditoria_id}`

Retorna detalhes completos de um registro, incluindo dados antes e depois da alteração.

**Exemplo:**
```bash
curl "http://localhost:8000/auditoria/1" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:**
```json
{
  "id": 1,
  "entidade_id": 1,
  "usuario_id": 1,
  "acao": "PUT /usuarios/2",
  "tabela_afetada": "usuarios",
  "registro_id": 2,
  "dados_antes": {
    "nome": "João Silva",
    "ativo": true
  },
  "dados_depois": {
    "nome": "João Silva Santos",
    "ativo": true
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2025-12-10T19:00:00"
}
```

---

### 3. Auditoria por Usuário

**GET** `/auditoria/usuario/{usuario_id}`

Lista todas as ações realizadas por um usuário específico.

**Query Parameters:**
- `skip` (int, padrão: 0)
- `limit` (int, padrão: 100, max: 500)

**Exemplo:**
```bash
curl "http://localhost:8000/auditoria/usuario/1?limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Uso:** Rastrear atividades de um usuário específico para auditoria de segurança.

---

### 4. Auditoria por Tabela

**GET** `/auditoria/tabela/{tabela_nome}`

Lista alterações em uma tabela específica.

**Query Parameters:**
- `skip` (int, padrão: 0)
- `limit` (int, padrão: 100, max: 500)
- `registro_id` (int, opcional) - Histórico de um registro específico

**Exemplo 1 - Todas as alterações na tabela:**
```bash
curl "http://localhost:8000/auditoria/tabela/contratos" \
  -H "Authorization: Bearer $TOKEN"
```

**Exemplo 2 - Histórico de um registro específico:**
```bash
curl "http://localhost:8000/auditoria/tabela/contratos?registro_id=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Uso:** Ver todo o histórico de alterações de um contrato específico.

---

### 5. Estatísticas de Auditoria

**GET** `/auditoria/estatisticas/resumo`

Retorna estatísticas agregadas sobre as auditorias.

**Query Parameters:**
- `entidade_id` (int, opcional)
- `data_inicio` (date, opcional)
- `data_fim` (date, opcional)

**Exemplo:**
```bash
curl "http://localhost:8000/auditoria/estatisticas/resumo" \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta:**
```json
{
  "total_registros": 1547,
  "usuarios_ativos": 12,
  "tabelas_afetadas": 8,
  "acoes_mais_comuns": [
    {
      "acao": "POST /auth/login",
      "quantidade": 456
    },
    {
      "acao": "GET /contratos",
      "quantidade": 234
    },
    {
      "acao": "PUT /fornecedores",
      "quantidade": 189
    }
  ]
}
```

**Uso:** Dashboards gerenciais e relatórios de atividade do sistema.

---

## 🔒 Controle de Acesso

### Perfis com Acesso
- **ROOT**: Acesso total a todas as auditorias
- **GESTOR**: Acesso às auditorias da própria entidade
- **AUDITOR**: Acesso às auditorias da própria entidade

### Perfis sem Acesso
- FISCAL_TECNICO
- FISCAL_ADM
- APOIO

---

## 📊 Casos de Uso

### 1. Rastreamento de Atividades Suspeitas
```bash
# Ver todas as ações de um usuário em uma data específica
curl "http://localhost:8000/auditoria/usuario/5?data_inicio=2025-12-10&data_fim=2025-12-10" \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Auditoria de Compliance
```bash
# Ver todas as alterações em contratos nos últimos 30 dias
curl "http://localhost:8000/auditoria/tabela/contratos?data_inicio=2025-11-10" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Histórico de Alterações de um Registro
```bash
# Ver todo o histórico de um contrato específico
curl "http://localhost:8000/auditoria/tabela/contratos?registro_id=42" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Relatório de Atividades Mensais
```bash
# Estatísticas do mês
curl "http://localhost:8000/auditoria/estatisticas/resumo?data_inicio=2025-12-01&data_fim=2025-12-31" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Identificar Usuários Mais Ativos
```bash
# Ver quais ações foram mais realizadas
curl "http://localhost:8000/auditoria/estatisticas/resumo" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📝 Informações Registradas

Cada registro de auditoria contém:

| Campo | Descrição |
|-------|-----------|
| `id` | ID único do registro |
| `entidade_id` | ID da entidade (se aplicável) |
| `usuario_id` | ID do usuário que realizou a ação |
| `acao` | Descrição da ação (ex: "POST /usuarios") |
| `tabela_afetada` | Tabela que foi modificada |
| `registro_id` | ID do registro modificado |
| `dados_antes` | Estado anterior (JSON) |
| `dados_depois` | Estado posterior (JSON) |
| `ip_address` | IP de onde veio a requisição |
| `user_agent` | Navegador/cliente usado |
| `timestamp` | Data e hora da ação |

---

## 🎯 Boas Práticas

1. **Paginação**: Use sempre `limit` para evitar sobrecarga
2. **Filtros**: Combine filtros para buscas mais precisas
3. **Períodos**: Limite buscas por data para melhor performance
4. **Backups**: Considere exportar auditorias antigas periodicamente
5. **Retenção**: Defina política de retenção de logs

---

## 🚨 Alertas Automáticos (Futuro)

Possíveis implementações futuras:
- Alertas para ações sensíveis (exclusões, alterações de perfil)
- Detecção de padrões anormais
- Relatórios automáticos por email
- Integração com SIEM

---

## ✅ Testes

Todos os endpoints foram testados e estão funcionando:
- ✅ Listagem com paginação
- ✅ Filtros por entidade, usuário, tabela
- ✅ Filtros por data
- ✅ Detalhes de registro individual
- ✅ Histórico por usuário
- ✅ Histórico por tabela/registro
- ✅ Estatísticas agregadas
- ✅ Controle de acesso por perfil

---

**Status**: ✅ Implementado e testado
**Versão**: 1.0.0
**Data**: 10 de Dezembro de 2025
