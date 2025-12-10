from typing import List
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.auth import get_current_user
from app.core.totp import generate_totp_secret, generate_totp_uri, generate_qr_code, verify_totp
from app.core.config import settings
from app.models.usuario import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioRead, UsuarioLogin
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login")
async def login(login_data: UsuarioLogin, session: Session = Depends(get_session)):
    """Autentica usuário e retorna token JWT"""
    
    # Busca usuário por email
    statement = select(Usuario).where(Usuario.email == login_data.email)
    usuario = session.exec(statement).first()
    
    if not usuario or not verify_password(login_data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Verifica TOTP se habilitado
    if usuario.totp_enabled:
        if not login_data.totp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código TOTP necessário"
            )
        
        if not verify_totp(usuario.totp_secret, login_data.totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código TOTP inválido"
            )
    
    # Atualiza último login
    usuario.ultimo_login = datetime.utcnow()
    session.add(usuario)
    session.commit()
    
    # Cria token
    access_token = create_access_token(
        data={
            "sub": str(usuario.id),
            "email": usuario.email,
            "perfil": usuario.perfil,
            "entidade_id": usuario.entidade_id
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": UsuarioRead.model_validate(usuario)
    }

@router.post("/register", response_model=UsuarioRead)
async def register(usuario_data: UsuarioCreate, session: Session = Depends(get_session)):
    """Registra novo usuário"""
    
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
    
    # Cria usuário
    usuario = Usuario(
        **usuario_data.model_dump(exclude={"senha"}),
        senha_hash=get_password_hash(usuario_data.senha)
    )
    
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    
    return usuario

@router.get("/me", response_model=UsuarioRead)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    """Retorna dados do usuário autenticado"""
    return current_user

@router.post("/totp/setup")
async def setup_totp(
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Configura TOTP (2FA) para o usuário"""
    
    # Gera secret temporário
    secret = generate_totp_secret()
    uri = generate_totp_uri(secret, current_user.email)
    qr_code = generate_qr_code(uri)
    
    # Salva secret temporário
    current_user.totp_temp_secret = secret
    session.add(current_user)
    session.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "uri": uri
    }

@router.post("/totp/verify")
async def verify_totp_setup(
    totp_code: str,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Verifica e ativa TOTP"""
    
    if not current_user.totp_temp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP não foi configurado"
        )
    
    if not verify_totp(current_user.totp_temp_secret, totp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código TOTP inválido"
        )
    
    # Ativa TOTP
    current_user.totp_secret = current_user.totp_temp_secret
    current_user.totp_temp_secret = None
    current_user.totp_enabled = True
    
    session.add(current_user)
    session.commit()
    
    return {"message": "TOTP ativado com sucesso"}

@router.post("/totp/disable")
async def disable_totp(
    senha: str,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Desativa TOTP"""
    
    if not verify_password(senha, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )
    
    current_user.totp_enabled = False
    current_user.totp_secret = None
    
    session.add(current_user)
    session.commit()
    
    return {"message": "TOTP desativado com sucesso"}
