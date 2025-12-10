from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, col
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.models.auditoria_global import AuditoriaGlobal, AuditoriaGlobalRead
from app.models.usuario import Usuario

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])

@router.get("", response_model=List[AuditoriaGlobalRead])
async def list_auditoria(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entidade_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    tabela_afetada: Optional[str] = None,
    acao: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Lista registros de auditoria com filtros avançados.
    Apenas usuários ROOT, GESTOR e AUDITOR têm acesso.
    """
    
    statement = select(AuditoriaGlobal)
    
    # Filtros
    if entidade_id:
        statement = statement.where(AuditoriaGlobal.entidade_id == entidade_id)
    elif current_user.perfil != "ROOT" and current_user.entidade_id:
        # Se não for ROOT, mostra apenas auditoria da própria entidade
        statement = statement.where(AuditoriaGlobal.entidade_id == current_user.entidade_id)
    
    if usuario_id:
        statement = statement.where(AuditoriaGlobal.usuario_id == usuario_id)
    
    if tabela_afetada:
        statement = statement.where(AuditoriaGlobal.tabela_afetada == tabela_afetada)
    
    if acao:
        statement = statement.where(col(AuditoriaGlobal.acao).ilike(f"%{acao}%"))
    
    if data_inicio:
        statement = statement.where(AuditoriaGlobal.timestamp >= datetime.combine(data_inicio, datetime.min.time()))
    
    if data_fim:
        statement = statement.where(AuditoriaGlobal.timestamp <= datetime.combine(data_fim, datetime.max.time()))
    
    # Ordena do mais recente para o mais antigo
    statement = statement.order_by(AuditoriaGlobal.timestamp.desc())
    statement = statement.offset(skip).limit(limit)
    
    auditorias = session.exec(statement).all()
    
    return auditorias

@router.get("/{auditoria_id}", response_model=AuditoriaGlobalRead)
async def get_auditoria(
    auditoria_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Obtém detalhes de um registro de auditoria específico.
    Inclui dados antes e depois da alteração.
    """
    
    auditoria = session.get(AuditoriaGlobal, auditoria_id)
    if not auditoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de auditoria não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil != "ROOT":
        if current_user.entidade_id != auditoria.entidade_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar este registro"
            )
    
    return auditoria

@router.get("/usuario/{usuario_id}", response_model=List[AuditoriaGlobalRead])
async def list_auditoria_por_usuario(
    usuario_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Lista todas as ações realizadas por um usuário específico.
    Útil para rastreamento de atividades.
    """
    
    statement = select(AuditoriaGlobal).where(AuditoriaGlobal.usuario_id == usuario_id)
    
    # Se não for ROOT, mostra apenas auditoria da própria entidade
    if current_user.perfil != "ROOT" and current_user.entidade_id:
        statement = statement.where(AuditoriaGlobal.entidade_id == current_user.entidade_id)
    
    statement = statement.order_by(AuditoriaGlobal.timestamp.desc())
    statement = statement.offset(skip).limit(limit)
    
    auditorias = session.exec(statement).all()
    
    return auditorias

@router.get("/tabela/{tabela_nome}", response_model=List[AuditoriaGlobalRead])
async def list_auditoria_por_tabela(
    tabela_nome: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    registro_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Lista alterações em uma tabela específica.
    Se registro_id for fornecido, mostra histórico de um registro específico.
    """
    
    statement = select(AuditoriaGlobal).where(AuditoriaGlobal.tabela_afetada == tabela_nome)
    
    if registro_id:
        statement = statement.where(AuditoriaGlobal.registro_id == registro_id)
    
    # Se não for ROOT, mostra apenas auditoria da própria entidade
    if current_user.perfil != "ROOT" and current_user.entidade_id:
        statement = statement.where(AuditoriaGlobal.entidade_id == current_user.entidade_id)
    
    statement = statement.order_by(AuditoriaGlobal.timestamp.desc())
    statement = statement.offset(skip).limit(limit)
    
    auditorias = session.exec(statement).all()
    
    return auditorias

@router.get("/estatisticas/resumo")
async def get_estatisticas_auditoria(
    entidade_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Retorna estatísticas sobre as auditorias.
    Útil para dashboards e relatórios gerenciais.
    """
    
    from sqlalchemy import func
    
    statement = select(
        func.count(AuditoriaGlobal.id).label("total_registros"),
        func.count(func.distinct(AuditoriaGlobal.usuario_id)).label("usuarios_ativos"),
        func.count(func.distinct(AuditoriaGlobal.tabela_afetada)).label("tabelas_afetadas")
    )
    
    # Filtros
    if entidade_id:
        statement = statement.where(AuditoriaGlobal.entidade_id == entidade_id)
    elif current_user.perfil != "ROOT" and current_user.entidade_id:
        statement = statement.where(AuditoriaGlobal.entidade_id == current_user.entidade_id)
    
    if data_inicio:
        statement = statement.where(AuditoriaGlobal.timestamp >= datetime.combine(data_inicio, datetime.min.time()))
    
    if data_fim:
        statement = statement.where(AuditoriaGlobal.timestamp <= datetime.combine(data_fim, datetime.max.time()))
    
    result = session.exec(statement).first()
    
    # Ações mais comuns
    statement_acoes = select(
        AuditoriaGlobal.acao,
        func.count(AuditoriaGlobal.id).label("quantidade")
    ).group_by(AuditoriaGlobal.acao).order_by(func.count(AuditoriaGlobal.id).desc()).limit(10)
    
    if entidade_id:
        statement_acoes = statement_acoes.where(AuditoriaGlobal.entidade_id == entidade_id)
    elif current_user.perfil != "ROOT" and current_user.entidade_id:
        statement_acoes = statement_acoes.where(AuditoriaGlobal.entidade_id == current_user.entidade_id)
    
    acoes_comuns = session.exec(statement_acoes).all()
    
    return {
        "total_registros": result[0] if result else 0,
        "usuarios_ativos": result[1] if result else 0,
        "tabelas_afetadas": result[2] if result else 0,
        "acoes_mais_comuns": [
            {"acao": acao, "quantidade": qtd}
            for acao, qtd in acoes_comuns
        ]
    }

# Importações para Celery
from app.tasks.tasks import process_audit_task
from celery.result import AsyncResult

@router.post("/processar/{audit_id}")
async def process_audit_background(
    audit_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Inicia o processamento de uma auditoria em background usando Celery.
    Retorna o ID da tarefa para acompanhar o progresso.
    """

    # Verificar se a auditoria existe
    audit = session.get(AuditoriaGlobal, audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auditoria não encontrada"
        )

    # Disparar tarefa em background
    task = process_audit_task.delay(audit_id)

    return {
        "message": "Processamento de auditoria iniciado em background",
        "task_id": task.id,
        "audit_id": audit_id,
        "status_url": f"/auditoria/task/{task.id}"
    }

@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Verifica o status de uma tarefa em background.
    """

    task_result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "current": task_result.current,
        "total": task_result.total,
        "info": task_result.info
    }

    if task_result.failed():
        response["error"] = str(task_result.result)

    return response
