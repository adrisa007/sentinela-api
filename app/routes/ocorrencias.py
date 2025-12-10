from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user
from app.core.guards import check_tenant_access, require_fiscal_access
from app.models.ocorrencia_fiscalizacao import OcorrenciaFiscalizacao, OcorrenciaFiscalizacaoCreate, OcorrenciaFiscalizacaoRead
from app.models.contrato import Contrato
from app.models.usuario import Usuario

router = APIRouter(prefix="/ocorrencias-fiscalizacao", tags=["Ocorrências de Fiscalização"])

@router.post("", response_model=OcorrenciaFiscalizacaoRead)
async def create_ocorrencia(
    ocorrencia_data: OcorrenciaFiscalizacaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Registra nova ocorrência de fiscalização"""
    
    # Verifica permissão (fiscais, gestor ou ROOT)
    require_fiscal_access(current_user)
    
    # Verifica se contrato existe
    contrato = session.get(Contrato, ocorrencia_data.contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verifica acesso ao tenant
    check_tenant_access(contrato, current_user)
    
    ocorrencia = OcorrenciaFiscalizacao(**ocorrencia_data.model_dump())
    session.add(ocorrencia)
    session.commit()
    session.refresh(ocorrencia)
    
    return ocorrencia

@router.get("", response_model=List[OcorrenciaFiscalizacaoRead])
async def list_ocorrencias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    contrato_id: Optional[int] = None,
    fiscal_id: Optional[int] = None,
    tipo_ocorrencia: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista ocorrências de fiscalização"""
    
    statement = select(OcorrenciaFiscalizacao)
    
    if contrato_id:
        statement = statement.where(OcorrenciaFiscalizacao.contrato_id == contrato_id)
    
    if fiscal_id:
        statement = statement.where(OcorrenciaFiscalizacao.fiscal_id == fiscal_id)
    
    if tipo_ocorrencia:
        statement = statement.where(OcorrenciaFiscalizacao.tipo_ocorrencia == tipo_ocorrencia)
    
    if data_inicio:
        statement = statement.where(OcorrenciaFiscalizacao.data_ocorrencia >= data_inicio)
    
    if data_fim:
        statement = statement.where(OcorrenciaFiscalizacao.data_ocorrencia <= data_fim)
    
    statement = statement.offset(skip).limit(limit).order_by(OcorrenciaFiscalizacao.data_ocorrencia.desc())
    ocorrencias = session.exec(statement).all()
    
    return ocorrencias

@router.get("/{ocorrencia_id}", response_model=OcorrenciaFiscalizacaoRead)
async def get_ocorrencia(
    ocorrencia_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém ocorrência por ID"""
    
    ocorrencia = session.get(OcorrenciaFiscalizacao, ocorrencia_id)
    if not ocorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada"
        )
    
    return ocorrencia
