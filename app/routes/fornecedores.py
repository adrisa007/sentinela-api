from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user
from app.core.guards import (
    apply_tenant_filter,
    check_tenant_access,
    require_gestor_or_root,
    TenantGuard
)
from app.models.fornecedor import Fornecedor, FornecedorCreate, FornecedorUpdate, FornecedorRead
from app.models.usuario import Usuario
from datetime import datetime

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

@router.post("", response_model=FornecedorRead)
async def create_fornecedor(
    fornecedor_data: FornecedorCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria novo fornecedor"""
    
    # Verifica permissão (ROOT, GESTOR ou APOIO)
    if current_user.perfil not in ["ROOT", "GESTOR", "APOIO"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar fornecedor"
        )
    
    # Valida e força entidade_id
    data_dict = fornecedor_data.model_dump()
    data_dict = TenantGuard.validate_tenant_on_create(data_dict, current_user)
    
    # Verifica se CNPJ/CPF já existe para a entidade
    if fornecedor_data.cnpj:
        statement = select(Fornecedor).where(
            Fornecedor.entidade_id == data_dict["entidade_id"],
            Fornecedor.cnpj == fornecedor_data.cnpj
        )
        if session.exec(statement).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fornecedor com este CNPJ já cadastrado nesta entidade"
            )
    
    fornecedor = Fornecedor(**data_dict)
    session.add(fornecedor)
    session.commit()
    session.refresh(fornecedor)
    
    return fornecedor

@router.get("", response_model=List[FornecedorRead])
async def list_fornecedores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    entidade_id: Optional[int] = None,
    situacao_cadastral: Optional[str] = None,
    regularidade_geral: Optional[str] = None,
    ativo: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista fornecedores"""
    
    statement = select(Fornecedor)
    
    # Aplica filtro de tenant
    statement = apply_tenant_filter(statement, Fornecedor, current_user)
    
    # Filtros adicionais
    if entidade_id:
        statement = statement.where(Fornecedor.entidade_id == entidade_id)
    
    if situacao_cadastral:
        statement = statement.where(Fornecedor.situacao_cadastral == situacao_cadastral)
    
    if regularidade_geral:
        statement = statement.where(Fornecedor.regularidade_geral == regularidade_geral)
    
    if ativo is not None:
        statement = statement.where(Fornecedor.ativo == ativo)
    
    statement = statement.offset(skip).limit(limit)
    fornecedores = session.exec(statement).all()
    
    return fornecedores

@router.get("/{fornecedor_id}", response_model=FornecedorRead)
async def get_fornecedor(
    fornecedor_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém fornecedor por ID"""
    
    fornecedor = session.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil != "ROOT" and current_user.entidade_id != fornecedor.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este fornecedor"
        )
    
    return fornecedor

@router.put("/{fornecedor_id}", response_model=FornecedorRead)
async def update_fornecedor(
    fornecedor_id: int,
    fornecedor_data: FornecedorUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza fornecedor"""
    
    fornecedor = session.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil not in ["ROOT", "GESTOR", "APOIO"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar fornecedor"
        )
    
    if current_user.perfil != "ROOT" and current_user.entidade_id != fornecedor.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar este fornecedor"
        )
    
    update_data = fornecedor_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(fornecedor, key, value)
    
    fornecedor.updated_at = datetime.utcnow()
    
    session.add(fornecedor)
    session.commit()
    session.refresh(fornecedor)
    
    return fornecedor

@router.delete("/{fornecedor_id}")
async def delete_fornecedor(
    fornecedor_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Desativa fornecedor"""
    
    fornecedor = session.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil not in ["ROOT", "GESTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para desativar fornecedor"
        )
    
    if current_user.perfil != "ROOT" and current_user.entidade_id != fornecedor.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para desativar este fornecedor"
        )
    
    fornecedor.ativo = False
    fornecedor.updated_at = datetime.utcnow()
    
    session.add(fornecedor)
    session.commit()
    
    return {"message": "Fornecedor desativado com sucesso"}
