from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.models.usuario import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioRead
from app.core.security import get_password_hash
from datetime import datetime

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.post("", response_model=UsuarioRead)
async def create_usuario(
    usuario_data: UsuarioCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Cria novo usuário"""
    
    # Verifica permissões
    if current_user.perfil == "GESTOR":
        if usuario_data.entidade_id != current_user.entidade_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para criar usuário em outra entidade"
            )
        if usuario_data.perfil == "ROOT":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para criar usuário ROOT"
            )
    
    # Verifica se email já existe
    statement = select(Usuario).where(Usuario.email == usuario_data.email)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verifica se CPF já existe
    statement = select(Usuario).where(Usuario.cpf == usuario_data.cpf)
    if session.exec(statement).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    usuario = Usuario(
        **usuario_data.model_dump(exclude={"senha"}),
        senha_hash=get_password_hash(usuario_data.senha)
    )
    
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    
    return usuario

@router.get("", response_model=List[UsuarioRead])
async def list_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    entidade_id: Optional[int] = None,
    perfil: Optional[str] = None,
    ativo: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista usuários"""
    
    statement = select(Usuario)
    
    # Filtros
    if entidade_id:
        statement = statement.where(Usuario.entidade_id == entidade_id)
    
    if perfil:
        statement = statement.where(Usuario.perfil == perfil)
    
    if ativo is not None:
        statement = statement.where(Usuario.ativo == ativo)
    
    # Se não for ROOT, mostra apenas usuários da mesma entidade
    if current_user.perfil != "ROOT" and current_user.entidade_id:
        statement = statement.where(Usuario.entidade_id == current_user.entidade_id)
    
    statement = statement.offset(skip).limit(limit)
    usuarios = session.exec(statement).all()
    
    return usuarios

@router.get("/{usuario_id}", response_model=UsuarioRead)
async def get_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtém usuário por ID"""
    
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil not in ["ROOT", "GESTOR"]:
        if current_user.id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar este usuário"
            )
    elif current_user.perfil == "GESTOR":
        if current_user.entidade_id != usuario.entidade_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar este usuário"
            )
    
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioRead)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza usuário"""
    
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil not in ["ROOT", "GESTOR"]:
        if current_user.id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para atualizar este usuário"
            )
    elif current_user.perfil == "GESTOR":
        if current_user.entidade_id != usuario.entidade_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para atualizar este usuário"
            )
    
    update_data = usuario_data.model_dump(exclude_unset=True)
    
    # Hash da senha se fornecida
    if "senha" in update_data and update_data["senha"]:
        update_data["senha_hash"] = get_password_hash(update_data.pop("senha"))
    
    for key, value in update_data.items():
        setattr(usuario, key, value)
    
    usuario.updated_at = datetime.utcnow()
    
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    
    return usuario

@router.delete("/{usuario_id}")
async def delete_usuario(
    usuario_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """Desativa usuário"""
    
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica permissão
    if current_user.perfil == "GESTOR" and current_user.entidade_id != usuario.entidade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para desativar este usuário"
        )
    
    usuario.ativo = False
    usuario.updated_at = datetime.utcnow()
    
    session.add(usuario)
    session.commit()
    
    return {"message": "Usuário desativado com sucesso"}
