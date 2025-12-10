from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy import Index

class AuditoriaGlobal(SQLModel, table=True):
    __tablename__ = "auditoria_global"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    entidade_id: Optional[int] = Field(default=None, foreign_key="entidade.id")
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    acao: Optional[str] = Field(default=None, max_length=100)
    tabela_afetada: Optional[str] = Field(default=None, max_length=100)
    registro_id: Optional[int] = Field(default=None)
    dados_antes: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    dados_depois: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_auditoria_entidade_timestamp', 'entidade_id', 'timestamp'),
        Index('idx_auditoria_usuario', 'usuario_id'),
    )

class AuditoriaGlobalCreate(SQLModel):
    entidade_id: Optional[int] = None
    usuario_id: Optional[int] = None
    acao: str
    tabela_afetada: str
    registro_id: Optional[int] = None
    dados_antes: Optional[dict] = None
    dados_depois: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditoriaGlobalRead(SQLModel):
    id: int
    entidade_id: Optional[int]
    usuario_id: Optional[int]
    acao: Optional[str]
    tabela_afetada: Optional[str]
    registro_id: Optional[int]
    timestamp: datetime
