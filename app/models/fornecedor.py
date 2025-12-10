from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Index

class Fornecedor(SQLModel, table=True):
    __tablename__ = "fornecedor"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    entidade_id: int = Field(foreign_key="entidade.id", nullable=False)
    cnpj: Optional[str] = Field(default=None, max_length=14, index=True)
    cpf: Optional[str] = Field(default=None, max_length=11)
    razao_social: str = Field(max_length=255, nullable=False)
    nome_fantasia: Optional[str] = Field(default=None, max_length=255)
    situacao_cadastral: str = Field(default="ATIVO", max_length=20)
    regularidade_geral: str = Field(default="REGULAR", max_length=20)
    data_ultima_verificacao: Optional[datetime] = Field(default=None)
    total_certidoes_vencidas: int = Field(default=0)
    data_impedimento: Optional[datetime] = Field(default=None)
    motivo_impedimento: Optional[str] = Field(default=None)
    ativo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_fornecedor_entidade_cnpj', 'entidade_id', 'cnpj', unique=True),
        Index('idx_fornecedor_cnpj', 'cnpj'),
    )

class FornecedorCreate(SQLModel):
    entidade_id: int
    cnpj: Optional[str] = None
    cpf: Optional[str] = None
    razao_social: str
    nome_fantasia: Optional[str] = None

class FornecedorUpdate(SQLModel):
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    situacao_cadastral: Optional[str] = None
    regularidade_geral: Optional[str] = None
    ativo: Optional[bool] = None

class FornecedorRead(SQLModel):
    id: int
    entidade_id: int
    cnpj: Optional[str]
    cpf: Optional[str]
    razao_social: str
    nome_fantasia: Optional[str]
    situacao_cadastral: str
    regularidade_geral: str
    total_certidoes_vencidas: int
    ativo: bool
    created_at: datetime
