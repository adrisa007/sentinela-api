# 🛡️ Sistema de Guards - Sentinela API

## Visão Geral

Sistema completo de guards para controle de acesso multi-tenant e por perfil.

---

## 📦 Guards Disponíveis

### 1. TenantGuard
Controla isolamento de dados por entidade (multi-tenant)

### 2. RootGuard
Operações exclusivas para ROOT

### 3. GestorGuard
Operações para ROOT e GESTOR

### 4. OwnerGuard
Verifica propriedade de recursos

### 5. AuditorGuard
Controle de acesso a auditorias

### 6. FiscalGuard
Operações de fiscalização

---

## 🎯 TenantGuard - Multi-Tenant

### Filtrar Query por Entidade
```python
from app.core.guards import TenantGuard, apply_tenant_filter

# Em uma rota
@router.get("/contratos")
async def list_contratos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    # Cria query base
    statement = select(Contrato)
    
    # Aplica filtro de tenant
    statement = TenantGuard.filter_by_tenant(
        statement, 
        Contrato, 
        current_user,
        tenant_field="entidade_id"
    )
    
    # Ou usar atalho:
    statement = apply_tenant_filter(statement, Contrato, current_user)
    
    contratos = session.exec(statement).all()
    return contratos
```

**Comportamento:**
- ✅ ROOT: vê contratos de todas as entidades
- ✅ Outros: vê apenas contratos da própria entidade

### Verificar Acesso ao Editar
```python
from app.core.guards import check_tenant_access

@router.put("/contratos/{id}")
async def update_contrato(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    contrato = session.get(Contrato, id)
    if not contrato:
        raise HTTPException(404, "Contrato não encontrado")
    
    # Verifica se tem acesso
    check_tenant_access(contrato, current_user)
    
    # Se chegou aqui, pode editar
    # ... lógica de atualização
```

### Validar ao Criar
```python
from app.core.guards import TenantGuard

@router.post("/contratos")
async def create_contrato(
    data: ContratoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    # Converte para dict
    data_dict = data.model_dump()
    
    # Valida e força entidade_id
    data_dict = TenantGuard.validate_tenant_on_create(
        data_dict,
        current_user,
        tenant_field="entidade_id"
    )
    
    contrato = Contrato(**data_dict)
    session.add(contrato)
    session.commit()
    return contrato
```

**Comportamento:**
- ✅ ROOT: pode informar qualquer entidade_id
- ✅ Outros: sempre usa entidade_id do usuário

---

## 👑 RootGuard - Operações ROOT

### Exigir ROOT
```python
from app.core.guards import require_root

@router.delete("/entidades/{id}")
async def delete_entidade(
    id: int,
    current_user: Usuario = Depends(get_current_user)
):
    # Só ROOT pode deletar entidades
    require_root(current_user)
    
    # ... lógica de exclusão
```

### Verificar se é ROOT
```python
from app.core.guards import RootGuard

@router.get("/entidades")
async def list_entidades(
    current_user: Usuario = Depends(get_current_user)
):
    if RootGuard.is_root(current_user):
        # ROOT vê todas
        statement = select(Entidade)
    else:
        # Outros veem só a própria
        statement = select(Entidade).where(
            Entidade.id == current_user.entidade_id
        )
    
    # ...
```

---

## 🏢 GestorGuard - ROOT ou GESTOR

### Exigir GESTOR ou ROOT
```python
from app.core.guards import require_gestor_or_root

@router.post("/usuarios")
async def create_usuario(
    data: UsuarioCreate,
    current_user: Usuario = Depends(get_current_user)
):
    # Apenas GESTOR ou ROOT podem criar usuários
    require_gestor_or_root(current_user)
    
    # ... lógica de criação
```

### Verificar se é GESTOR ou ROOT
```python
from app.core.guards import GestorGuard

@router.put("/contratos/{id}")
async def update_contrato(
    id: int,
    current_user: Usuario = Depends(get_current_user)
):
    if GestorGuard.is_gestor_or_root(current_user):
        # Pode alterar qualquer campo
        # ...
    else:
        # Pode alterar apenas campos específicos
        # ...
```

---

## 👤 OwnerGuard - Proprietário do Recurso

### Verificar Propriedade
```python
from app.core.guards import OwnerGuard

@router.put("/usuarios/{id}")
async def update_usuario(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(404)
    
    # Verifica se é o próprio usuário, ROOT ou GESTOR
    OwnerGuard.check_owner_access(
        usuario, 
        current_user, 
        owner_field="id"  # Compara usuario.id com current_user.id
    )
    
    # Pode atualizar
```

### Verificar se é Dono
```python
from app.core.guards import OwnerGuard

@router.get("/ocorrencias/{id}")
async def get_ocorrencia(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    ocorrencia = session.get(Ocorrencia, id)
    
    # Verifica se criou a ocorrência
    is_owner = OwnerGuard.is_owner(
        ocorrencia, 
        current_user, 
        owner_field="fiscal_id"
    )
    
    if is_owner or current_user.perfil in ["ROOT", "GESTOR"]:
        # Mostra dados completos
        return ocorrencia
    else:
        # Mostra dados reduzidos
        return {"id": ocorrencia.id, "status": ocorrencia.status}
```

---

## 📊 AuditorGuard - Acesso a Auditorias

### Exigir Acesso de Auditor
```python
from app.core.guards import require_auditor_access

@router.get("/auditoria")
async def list_auditoria(
    current_user: Usuario = Depends(get_current_user)
):
    # Apenas ROOT, GESTOR ou AUDITOR
    require_auditor_access(current_user)
    
    # ... buscar auditorias
```

### Verificar Acesso
```python
from app.core.guards import AuditorGuard

@router.get("/dashboard")
async def dashboard(
    current_user: Usuario = Depends(get_current_user)
):
    # Mostra diferentes widgets baseado no perfil
    if AuditorGuard.has_auditor_access(current_user):
        # Inclui estatísticas de auditoria
        # ...
    
    # Retorna dashboard
```

---

## 👮 FiscalGuard - Operações de Fiscalização

### Exigir Acesso de Fiscal
```python
from app.core.guards import require_fiscal_access

@router.post("/ocorrencias")
async def create_ocorrencia(
    data: OcorrenciaCreate,
    current_user: Usuario = Depends(get_current_user)
):
    # Fiscais, gestores ou ROOT
    require_fiscal_access(current_user)
    
    # ... criar ocorrência
```

### Exigir Fiscal Técnico
```python
from app.core.guards import FiscalGuard

@router.post("/ocorrencias/tecnicas")
async def create_ocorrencia_tecnica(
    current_user: Usuario = Depends(get_current_user)
):
    # Apenas fiscal técnico, gestor ou ROOT
    FiscalGuard.require_fiscal_tecnico(current_user)
    
    # ... criar ocorrência técnica
```

### Exigir Fiscal Administrativo
```python
from app.core.guards import FiscalGuard

@router.post("/ocorrencias/administrativas")
async def create_ocorrencia_adm(
    current_user: Usuario = Depends(get_current_user)
):
    # Apenas fiscal administrativo, gestor ou ROOT
    FiscalGuard.require_fiscal_adm(current_user)
    
    # ... criar ocorrência administrativa
```

---

## 🔄 Exemplo Completo - CRUD com Guards

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user
from app.core.guards import (
    apply_tenant_filter,
    check_tenant_access,
    require_gestor_or_root,
    TenantGuard
)
from app.models.contrato import Contrato, ContratoCreate, ContratoRead
from app.models.usuario import Usuario

router = APIRouter(prefix="/contratos", tags=["Contratos"])

# LIST - Aplica filtro de tenant
@router.get("", response_model=list[ContratoRead])
async def list_contratos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    statement = select(Contrato)
    
    # ROOT vê tudo, outros veem só da entidade
    statement = apply_tenant_filter(statement, Contrato, current_user)
    
    contratos = session.exec(statement).all()
    return contratos

# GET - Verifica acesso ao tenant
@router.get("/{id}", response_model=ContratoRead)
async def get_contrato(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    contrato = session.get(Contrato, id)
    if not contrato:
        raise HTTPException(404, "Contrato não encontrado")
    
    # Verifica se tem acesso
    check_tenant_access(contrato, current_user)
    
    return contrato

# POST - Valida tenant ao criar, exige GESTOR ou ROOT
@router.post("", response_model=ContratoRead)
async def create_contrato(
    data: ContratoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    # Só GESTOR ou ROOT podem criar
    require_gestor_or_root(current_user)
    
    # Valida e força entidade_id
    data_dict = data.model_dump()
    data_dict = TenantGuard.validate_tenant_on_create(
        data_dict, 
        current_user
    )
    
    contrato = Contrato(**data_dict)
    session.add(contrato)
    session.commit()
    session.refresh(contrato)
    return contrato

# PUT - Verifica acesso, exige GESTOR ou ROOT
@router.put("/{id}", response_model=ContratoRead)
async def update_contrato(
    id: int,
    data: ContratoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    # Só GESTOR ou ROOT podem editar
    require_gestor_or_root(current_user)
    
    contrato = session.get(Contrato, id)
    if not contrato:
        raise HTTPException(404)
    
    # Verifica acesso ao tenant
    check_tenant_access(contrato, current_user)
    
    # Atualiza
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(contrato, key, value)
    
    session.add(contrato)
    session.commit()
    session.refresh(contrato)
    return contrato

# DELETE - Verifica acesso, exige GESTOR ou ROOT
@router.delete("/{id}")
async def delete_contrato(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    require_gestor_or_root(current_user)
    
    contrato = session.get(Contrato, id)
    if not contrato:
        raise HTTPException(404)
    
    check_tenant_access(contrato, current_user)
    
    session.delete(contrato)
    session.commit()
    return {"message": "Contrato excluído com sucesso"}
```

---

## 🎯 Casos de Uso por Perfil

### ROOT
```python
# Acessa tudo de todas as entidades
statement = select(Contrato)
statement = apply_tenant_filter(statement, Contrato, root_user)
# Retorna todos os contratos
```

### GESTOR
```python
# Acessa apenas da própria entidade
statement = select(Contrato)
statement = apply_tenant_filter(statement, Contrato, gestor_user)
# Retorna apenas contratos da entidade do gestor
```

### FISCAL
```python
# Acessa apenas da própria entidade
# Pode criar ocorrências e atualizar cronogramas
require_fiscal_access(fiscal_user)  # ✅ Passa
require_gestor_or_root(fiscal_user)  # ❌ Falha
```

### AUDITOR
```python
# Acessa auditorias da própria entidade
require_auditor_access(auditor_user)  # ✅ Passa
require_gestor_or_root(auditor_user)  # ❌ Falha
```

### APOIO
```python
# Acessa apenas da própria entidade
# Pode criar certidões e fornecedores
require_fiscal_access(apoio_user)  # ❌ Falha
```

---

## ✅ Benefícios

### Segurança
- ✅ Isolamento completo de dados por entidade
- ✅ Controle granular de permissões
- ✅ Previne vazamento de dados entre tenants

### Manutenção
- ✅ Código reutilizável
- ✅ Lógica centralizada
- ✅ Fácil de testar

### Escalabilidade
- ✅ Suporta múltiplas entidades
- ✅ Performance otimizada (filtro em query)
- ✅ Flexível para novos perfis

---

## 📝 Convenções

### Nomes de Campos
- `entidade_id` - Campo de tenant (padrão)
- `usuario_id` - Campo de proprietário (padrão)
- Personalizável via parâmetro `tenant_field` ou `owner_field`

### Hierarquia de Perfis
```
ROOT
  ↓
GESTOR
  ↓
FISCAL_TECNICO / FISCAL_ADM
  ↓
AUDITOR / APOIO
```

---

**Versão**: 1.0.0  
**Status**: ✅ Implementado  
**Data**: 10 de Dezembro de 2025
