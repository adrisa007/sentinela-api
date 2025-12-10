from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.models.entidade import Entidade, EntidadeCreate, EntidadeUpdate, EntidadeRead
from app.models.usuario import Usuario
from datetime import datetime

router = APIRouter(prefix="/entidades", tags=["Entidades"])

@router.post("", response_model=EntidadeRead)
async def create_entidade(
    entidade_data: EntidadeCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT"))
):
    """Cria nova entidade"""
    
    # Verifica se CNPJ já existe
    statement = select(Entidade).where(Entidade.cnpj == entidade_data.cnpj)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado"
        )
    
    entidade = Entidade(**entidade_data.model_dump())
    session.add(entidade)
    session.commit()
    session.refresh(entidade)
    
    return entidade

@router.get("", response_model=List[EntidadeRead])
async def list_entidades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista entidades"""
    
    statement = select(Entidade)
    
    if status:
        statement = statement.where(Entidade.status == status)
    
    # Se não for ROOT, mostra apenas a entidade do usuário
    if current_user.perfil != "ROOT" and current_user.entidade_id:
        statement = statement.where(Entidade.id == current_user.entidade_id)
    
    statement = statement.offset(skip).limit(limit)
    entidades = session.exec(statement).all()
    
    return entidades

@router.get("/{entidade_id}", response_model=EntidadeRead)
async def get_entidade(
    entidade_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém entidade por ID"""
    
    entidade = session.get(Entidade, entidade_id)
    if not entidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entidade não encontrada"
        )
    
    # Verifica permissão
    if current_user.perfil != "ROOT" and current_user.entidade_id != entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar esta entidade"
        )
    
    return entidade

@router.put("/{entidade_id}", response_model=EntidadeRead)
async def update_entidade(
    entidade_id: int,
    entidade_data: EntidadeUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Atualiza entidade"""
    
    entidade = session.get(Entidade, entidade_id)
    if not entidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entidade não encontrada"
        )
    
    # Verifica permissão
    if current_user.perfil == "GESTOR" and current_user.entidade_id != entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar esta entidade"
        )
    
    update_data = entidade_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entidade, key, value)
    
    entidade.updated_at = datetime.utcnow()
    
    session.add(entidade)
    session.commit()
    session.refresh(entidade)
    
    return entidade

@router.delete("/{entidade_id}")
async def delete_entidade(
    entidade_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT"))
):
    """Desativa entidade"""
    
    entidade = session.get(Entidade, entidade_id)
    if not entidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entidade não encontrada"
        )
    
    entidade.status = "INATIVA"
    entidade.data_status = datetime.utcnow()
    entidade.updated_at = datetime.utcnow()
    
    session.add(entidade)
    session.commit()
    
    return {"message": "Entidade desativada com sucesso"}
