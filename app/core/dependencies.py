from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.usuario import Usuario
from app.models.entidade import Entidade
from app.core.auth import get_current_user
from app.core.guards import require_root


def require_active_entidade(
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Entidade:
    """
    Garante que o usuário está vinculado a uma entidade ativa.
    Lança HTTPException se não houver entidade ou se estiver inativa.
    """
    if not current_user.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não vinculado a nenhuma entidade."
        )
    entidade = session.exec(
        select(Entidade).where(Entidade.id == current_user.entidade_id)
    ).first()
    if not entidade or not entidade.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Entidade inativa ou não encontrada."
        )
    return entidade


def require_root_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Garante que o usuário autenticado é ROOT.
    Lança HTTPException se não for ROOT.
    """
    require_root(current_user)
    return current_user
