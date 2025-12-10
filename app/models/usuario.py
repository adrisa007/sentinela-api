from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Index

class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    entidade_id: Optional[int] = Field(default=None, foreign_key="entidade.id")
    nome: str = Field(max_length=150, nullable=False)
    cpf: str = Field(max_length=11, unique=True, nullable=False, index=True)
    email: str = Field(max_length=255, unique=True, nullable=False)
    senha_hash: str = Field(max_length=255, nullable=False)
    perfil: str = Field(max_length=30, nullable=False)  # ROOT | GESTOR | FISCAL_TECNICO | FISCAL_ADM | APOIO | AUDITOR
    ativo: bool = Field(default=True)
    totp_secret: Optional[str] = Field(default=None)
    totp_temp_secret: Optional[str] = Field(default=None)
    totp_enabled: bool = Field(default=False)
    ultimo_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_usuario_entidade_perfil', 'entidade_id', 'perfil'),
        Index('idx_usuario_cpf', 'cpf', unique=True),
    )

class UsuarioCreate(SQLModel):
    entidade_id: Optional[int] = None
    nome: str = Field(max_length=150)
    cpf: str = Field(max_length=11)
    email: str = Field(max_length=255)
    senha: str = Field(min_length=8)
    perfil: str

class UsuarioUpdate(SQLModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    perfil: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioRead(SQLModel):
    id: int
    entidade_id: Optional[int]
    nome: str
    cpf: str
    email: str
    perfil: str
    ativo: bool
    totp_enabled: bool
    ultimo_login: Optional[datetime]
    created_at: datetime

class UsuarioLogin(SQLModel):
    email: str
    senha: str
    totp_code: Optional[str] = None
