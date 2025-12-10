from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.models.cronograma_fisico_fin import CronogramaFisicoFin, CronogramaFisicoFinCreate, CronogramaFisicoFinUpdate, CronogramaFisicoFinRead
from app.models.contrato import Contrato
from app.models.usuario import Usuario
from datetime import datetime

router = APIRouter(prefix="/cronogramas", tags=["Cronogramas Físico-Financeiro"])

@router.post("", response_model=CronogramaFisicoFinRead)
async def create_cronograma(
    cronograma_data: CronogramaFisicoFinCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Cria etapa do cronograma físico-financeiro"""
    
    # Verifica se contrato existe
    contrato = session.get(Contrato, cronograma_data.contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil == "GESTOR" and current_user.entidade_id != contrato.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar cronograma neste contrato"
        )
    
    cronograma = CronogramaFisicoFin(**cronograma_data.model_dump())
    session.add(cronograma)
    session.commit()
    session.refresh(cronograma)
    
    return cronograma

@router.get("", response_model=List[CronogramaFisicoFinRead])
async def list_cronogramas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    contrato_id: Optional[int] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista etapas do cronograma"""
    
    statement = select(CronogramaFisicoFin)
    
    if contrato_id:
        statement = statement.where(CronogramaFisicoFin.contrato_id == contrato_id)
    
    if status:
        statement = statement.where(CronogramaFisicoFin.status == status)
    
    statement = statement.offset(skip).limit(limit)
    cronogramas = session.exec(statement).all()
    
    return cronogramas

@router.get("/{cronograma_id}", response_model=CronogramaFisicoFinRead)
async def get_cronograma(
    cronograma_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém etapa do cronograma por ID"""
    
    cronograma = session.get(CronogramaFisicoFin, cronograma_id)
    if not cronograma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etapa do cronograma não encontrada"
        )
    
    return cronograma

@router.put("/{cronograma_id}", response_model=CronogramaFisicoFinRead)
async def update_cronograma(
    cronograma_id: int,
    cronograma_data: CronogramaFisicoFinUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "FISCAL_TECNICO"))
):
    """Atualiza etapa do cronograma"""
    
    cronograma = session.get(CronogramaFisicoFin, cronograma_id)
    if not cronograma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etapa do cronograma não encontrada"
        )
    
    update_data = cronograma_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cronograma, key, value)
    
    session.add(cronograma)
    session.commit()
    session.refresh(cronograma)
    
    return cronograma
