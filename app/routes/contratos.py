from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user
from app.models.contrato import Contrato, ContratoCreate, ContratoUpdate, ContratoRead
from app.models.usuario import Usuario
from datetime import datetime

router = APIRouter(prefix="/contratos", tags=["Contratos"])

@router.post("", response_model=ContratoRead)
async def create_contrato(
    contrato_data: ContratoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria novo contrato"""
    
    # Verifica permissão
    if current_user.perfil not in ["ROOT", "GESTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar contrato"
        )
    
    # Verifica se número do contrato já existe para a entidade
    statement = select(Contrato).where(
        Contrato.entidade_id == contrato_data.entidade_id,
        Contrato.numero_contrato == contrato_data.numero_contrato
    )
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contrato com este número já existe nesta entidade"
        )
    
    contrato = Contrato(**contrato_data.model_dump())
    session.add(contrato)
    session.commit()
    session.refresh(contrato)
    
    return contrato

@router.get("", response_model=List[ContratoRead])
async def list_contratos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    entidade_id: Optional[int] = None,
    fornecedor_id: Optional[int] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista contratos"""
    
    statement = select(Contrato)
    
    # Filtros
    if entidade_id:
        statement = statement.where(Contrato.entidade_id == entidade_id)
    elif current_user.perfil != "ROOT" and current_user.entidade_id:
        statement = statement.where(Contrato.entidade_id == current_user.entidade_id)
    
    if fornecedor_id:
        statement = statement.where(Contrato.fornecedor_id == fornecedor_id)
    
    if status:
        statement = statement.where(Contrato.status == status)
    
    statement = statement.offset(skip).limit(limit)
    contratos = session.exec(statement).all()
    
    return contratos

@router.get("/{contrato_id}", response_model=ContratoRead)
async def get_contrato(
    contrato_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém contrato por ID"""
    
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil != "ROOT" and current_user.entidade_id != contrato.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este contrato"
        )
    
    return contrato

@router.put("/{contrato_id}", response_model=ContratoRead)
async def update_contrato(
    contrato_id: int,
    contrato_data: ContratoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza contrato"""
    
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil not in ["ROOT", "GESTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar contrato"
        )
    
    if current_user.perfil != "ROOT" and current_user.entidade_id != contrato.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar este contrato"
        )
    
    update_data = contrato_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contrato, key, value)
    
    contrato.updated_at = datetime.utcnow()
    
    session.add(contrato)
    session.commit()
    session.refresh(contrato)
    
    return contrato

@router.delete("/{contrato_id}")
async def delete_contrato(
    contrato_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Cancela contrato"""
    
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil not in ["ROOT", "GESTOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para cancelar contrato"
        )
    
    if current_user.perfil != "ROOT" and current_user.entidade_id != contrato.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para cancelar este contrato"
        )
    
    contrato.status = "CANCELADO"
    contrato.updated_at = datetime.utcnow()
    
    session.add(contrato)
    session.commit()
    
    return {"message": "Contrato cancelado com sucesso"}
