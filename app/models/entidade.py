from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy import Index

class Entidade(SQLModel, table=True):
    __tablename__ = "entidade"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    cnpj: str = Field(max_length=14, unique=True, nullable=False, index=True)
    razao_social: str = Field(max_length=255, nullable=False)
    nome_fantasia: Optional[str] = Field(default=None, max_length=255)
    ug_codigo: Optional[str] = Field(default=None, max_length=20)
    status: str = Field(default="ATIVA", max_length=20, index=True)
    data_status: datetime = Field(default_factory=datetime.utcnow)
    motivo_status: Optional[str] = Field(default=None)
    root_user_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    logo_url: Optional[str] = Field(default=None, max_length=500)
    config_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_entidade_cnpj', 'cnpj', unique=True),
        Index('idx_entidade_status', 'status'),
    )

class EntidadeCreate(SQLModel):
    cnpj: str = Field(max_length=14)
    razao_social: str = Field(max_length=255)
    nome_fantasia: Optional[str] = None
    ug_codigo: Optional[str] = None
    logo_url: Optional[str] = None
    config_json: Optional[dict] = None

class EntidadeUpdate(SQLModel):
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    ug_codigo: Optional[str] = None
    status: Optional[str] = None
    motivo_status: Optional[str] = None
    logo_url: Optional[str] = None
    config_json: Optional[dict] = None

class EntidadeRead(SQLModel):
    id: int
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str]
    ug_codigo: Optional[str]
    status: str
    data_status: datetime
    created_at: datetime
