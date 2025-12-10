from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user
from app.models.certidao_fornecedor import CertidaoFornecedor, CertidaoFornecedorCreate, CertidaoFornecedorRead
from app.models.fornecedor import Fornecedor
from app.models.usuario import Usuario

router = APIRouter(prefix="/certidoes-fornecedor", tags=["Certidões de Fornecedor"])

@router.post("", response_model=CertidaoFornecedorRead)
async def create_certidao(
    certidao_data: CertidaoFornecedorCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria nova certidão de fornecedor"""
    
    # Verifica se fornecedor existe
    fornecedor = session.get(Fornecedor, certidao_data.fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil not in ["ROOT", "GESTOR", "APOIO"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar certidão"
        )
    
    if current_user.perfil != "ROOT" and current_user.entidade_id != fornecedor.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar certidão para este fornecedor"
        )
    
    certidao = CertidaoFornecedor(**certidao_data.model_dump())
    
    # Atualiza status baseado na data de validade
    if certidao.data_validade < date.today():
        certidao.situacao = "VENCIDA"
    
    session.add(certidao)
    session.commit()
    session.refresh(certidao)
    
    return certidao

@router.get("", response_model=List[CertidaoFornecedorRead])
async def list_certidoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    fornecedor_id: Optional[int] = None,
    tipo_certidao_id: Optional[int] = None,
    situacao: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista certidões de fornecedores"""
    
    statement = select(CertidaoFornecedor)
    
    if fornecedor_id:
        statement = statement.where(CertidaoFornecedor.fornecedor_id == fornecedor_id)
    
    if tipo_certidao_id:
        statement = statement.where(CertidaoFornecedor.tipo_certidao_id == tipo_certidao_id)
    
    if situacao:
        statement = statement.where(CertidaoFornecedor.situacao == situacao)
    
    statement = statement.offset(skip).limit(limit)
    certidoes = session.exec(statement).all()
    
    return certidoes

@router.get("/{certidao_id}", response_model=CertidaoFornecedorRead)
async def get_certidao(
    certidao_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém certidão por ID"""
    
    certidao = session.get(CertidaoFornecedor, certidao_id)
    if not certidao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certidão não encontrada"
        )
    
    return certidao

@router.get("/fornecedor/{fornecedor_id}/vencidas", response_model=List[CertidaoFornecedorRead])
async def get_certidoes_vencidas(
    fornecedor_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista certidões vencidas de um fornecedor"""
    
    statement = select(CertidaoFornecedor).where(
        CertidaoFornecedor.fornecedor_id == fornecedor_id,
        CertidaoFornecedor.data_validade < date.today()
    )
    
    certidoes = session.exec(statement).all()
    return certidoes
