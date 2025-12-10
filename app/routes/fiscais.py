from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.models.fiscal_designado import FiscalDesignado, FiscalDesignadoCreate, FiscalDesignadoRead
from app.models.contrato import Contrato
from app.models.usuario import Usuario

router = APIRouter(prefix="/fiscais-designados", tags=["Fiscais Designados"])

@router.post("", response_model=FiscalDesignadoRead)
async def create_fiscal_designado(
    fiscal_data: FiscalDesignadoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Designa fiscal para contrato"""
    
    # Verifica se contrato existe
    contrato = session.get(Contrato, fiscal_data.contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verifica se usuário existe
    usuario = session.get(Usuario, fiscal_data.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil == "GESTOR" and current_user.entidade_id != contrato.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para designar fiscal para este contrato"
        )
    
    # Verifica se já existe
    statement = select(FiscalDesignado).where(
        FiscalDesignado.contrato_id == fiscal_data.contrato_id,
        FiscalDesignado.usuario_id == fiscal_data.usuario_id
    )
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fiscal já designado para este contrato"
        )
    
    fiscal = FiscalDesignado(**fiscal_data.model_dump())
    session.add(fiscal)
    session.commit()
    session.refresh(fiscal)
    
    return fiscal

@router.get("", response_model=List[FiscalDesignadoRead])
async def list_fiscais_designados(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    contrato_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    tipo_fiscal: Optional[str] = None,
    ativo: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista fiscais designados"""
    
    statement = select(FiscalDesignado)
    
    if contrato_id:
        statement = statement.where(FiscalDesignado.contrato_id == contrato_id)
    
    if usuario_id:
        statement = statement.where(FiscalDesignado.usuario_id == usuario_id)
    
    if tipo_fiscal:
        statement = statement.where(FiscalDesignado.tipo_fiscal == tipo_fiscal)
    
    if ativo is not None:
        statement = statement.where(FiscalDesignado.ativo == ativo)
    
    statement = statement.offset(skip).limit(limit)
    fiscais = session.exec(statement).all()
    
    return fiscais

@router.get("/{fiscal_id}", response_model=FiscalDesignadoRead)
async def get_fiscal_designado(
    fiscal_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém fiscal designado por ID"""
    
    fiscal = session.get(FiscalDesignado, fiscal_id)
    if not fiscal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fiscal designado não encontrado"
        )
    
    return fiscal

@router.delete("/{fiscal_id}")
async def delete_fiscal_designado(
    fiscal_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Remove designação de fiscal"""
    
    fiscal = session.get(FiscalDesignado, fiscal_id)
    if not fiscal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fiscal designado não encontrado"
        )
    
    fiscal.ativo = False
    session.add(fiscal)
    session.commit()
    
    return {"message": "Designação removida com sucesso"}
