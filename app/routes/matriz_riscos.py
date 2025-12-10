from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.models.matriz_riscos import MatrizRiscos, MatrizRiscosCreate, MatrizRiscosUpdate, MatrizRiscosRead
from app.models.contrato import Contrato
from app.models.usuario import Usuario

router = APIRouter(prefix="/matriz-riscos", tags=["Matriz de Riscos"])

@router.post("", response_model=MatrizRiscosRead)
async def create_risco(
    risco_data: MatrizRiscosCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Registra novo risco na matriz"""
    
    # Verifica se contrato existe
    contrato = session.get(Contrato, risco_data.contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil == "GESTOR" and current_user.entidade_id != contrato.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para registrar risco neste contrato"
        )
    
    risco = MatrizRiscos(**risco_data.model_dump())
    
    # Calcula nível de risco se probabilidade e impacto forem fornecidos
    if risco.probabilidade and risco.impacto:
        nivel = risco.probabilidade * risco.impacto
        if nivel <= 5:
            risco.nivel_risco = "BAIXO"
        elif nivel <= 15:
            risco.nivel_risco = "MÉDIO"
        else:
            risco.nivel_risco = "ALTO"
    
    session.add(risco)
    session.commit()
    session.refresh(risco)
    
    return risco

@router.get("", response_model=List[MatrizRiscosRead])
async def list_riscos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    contrato_id: Optional[int] = None,
    nivel_risco: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista riscos da matriz"""
    
    statement = select(MatrizRiscos)
    
    if contrato_id:
        statement = statement.where(MatrizRiscos.contrato_id == contrato_id)
    
    if nivel_risco:
        statement = statement.where(MatrizRiscos.nivel_risco == nivel_risco)
    
    if status:
        statement = statement.where(MatrizRiscos.status == status)
    
    statement = statement.offset(skip).limit(limit)
    riscos = session.exec(statement).all()
    
    return riscos

@router.get("/{risco_id}", response_model=MatrizRiscosRead)
async def get_risco(
    risco_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém risco por ID"""
    
    risco = session.get(MatrizRiscos, risco_id)
    if not risco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risco não encontrado"
        )
    
    return risco

@router.put("/{risco_id}", response_model=MatrizRiscosRead)
async def update_risco(
    risco_id: int,
    risco_data: MatrizRiscosUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Atualiza risco"""
    
    risco = session.get(MatrizRiscos, risco_id)
    if not risco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risco não encontrado"
        )
    
    update_data = risco_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(risco, key, value)
    
    # Recalcula nível de risco se probabilidade ou impacto mudaram
    if risco.probabilidade and risco.impacto:
        nivel = risco.probabilidade * risco.impacto
        if nivel <= 5:
            risco.nivel_risco = "BAIXO"
        elif nivel <= 15:
            risco.nivel_risco = "MÉDIO"
        else:
            risco.nivel_risco = "ALTO"
    
    session.add(risco)
    session.commit()
    session.refresh(risco)
    
    return risco
