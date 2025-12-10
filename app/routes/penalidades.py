from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.models.penalidade import Penalidade, PenalidadeCreate, PenalidadeUpdate, PenalidadeRead
from app.models.contrato import Contrato
from app.models.usuario import Usuario

router = APIRouter(prefix="/penalidades", tags=["Penalidades"])

@router.post("", response_model=PenalidadeRead)
async def create_penalidade(
    penalidade_data: PenalidadeCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Registra nova penalidade"""
    
    # Verifica se contrato existe
    contrato = session.get(Contrato, penalidade_data.contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil == "GESTOR" and current_user.entidade_id != contrato.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para registrar penalidade neste contrato"
        )
    
    penalidade = Penalidade(**penalidade_data.model_dump())
    session.add(penalidade)
    session.commit()
    session.refresh(penalidade)
    
    return penalidade

@router.get("", response_model=List[PenalidadeRead])
async def list_penalidades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    contrato_id: Optional[int] = None,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista penalidades"""
    
    statement = select(Penalidade)
    
    if contrato_id:
        statement = statement.where(Penalidade.contrato_id == contrato_id)
    
    if tipo:
        statement = statement.where(Penalidade.tipo == tipo)
    
    if status:
        statement = statement.where(Penalidade.status == status)
    
    statement = statement.offset(skip).limit(limit).order_by(Penalidade.created_at.desc())
    penalidades = session.exec(statement).all()
    
    return penalidades

@router.get("/{penalidade_id}", response_model=PenalidadeRead)
async def get_penalidade(
    penalidade_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém penalidade por ID"""
    
    penalidade = session.get(Penalidade, penalidade_id)
    if not penalidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penalidade não encontrada"
        )
    
    return penalidade

@router.put("/{penalidade_id}", response_model=PenalidadeRead)
async def update_penalidade(
    penalidade_id: int,
    penalidade_data: PenalidadeUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Atualiza penalidade"""
    
    penalidade = session.get(Penalidade, penalidade_id)
    if not penalidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penalidade não encontrada"
        )
    
    update_data = penalidade_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(penalidade, key, value)
    
    session.add(penalidade)
    session.commit()
    session.refresh(penalidade)
    
    return penalidade
