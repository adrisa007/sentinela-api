from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.models.tipo_certidao import TipoCertidao, TipoCertidaoCreate, TipoCertidaoRead
from app.models.usuario import Usuario

router = APIRouter(prefix="/tipo-certidoes", tags=["Tipos de Certidão"])

@router.post("", response_model=TipoCertidaoRead)
async def create_tipo_certidao(
    tipo_data: TipoCertidaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Cria novo tipo de certidão"""
    
    # Verifica se código já existe
    statement = select(TipoCertidao).where(TipoCertidao.codigo == tipo_data.codigo)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de certidão com este código já existe"
        )
    
    tipo_certidao = TipoCertidao(**tipo_data.model_dump())
    session.add(tipo_certidao)
    session.commit()
    session.refresh(tipo_certidao)
    
    return tipo_certidao

@router.get("", response_model=List[TipoCertidaoRead])
async def list_tipos_certidao(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    obrigatoria_licitacao: Optional[bool] = None,
    obrigatoria_contratacao: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista tipos de certidão"""
    
    statement = select(TipoCertidao)
    
    if obrigatoria_licitacao is not None:
        statement = statement.where(TipoCertidao.obrigatoria_licitacao == obrigatoria_licitacao)
    
    if obrigatoria_contratacao is not None:
        statement = statement.where(TipoCertidao.obrigatoria_contratacao == obrigatoria_contratacao)
    
    statement = statement.offset(skip).limit(limit)
    tipos = session.exec(statement).all()
    
    return tipos

@router.get("/{tipo_id}", response_model=TipoCertidaoRead)
async def get_tipo_certidao(
    tipo_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém tipo de certidão por ID"""
    
    tipo_certidao = session.get(TipoCertidao, tipo_id)
    if not tipo_certidao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de certidão não encontrado"
        )
    
    return tipo_certidao
