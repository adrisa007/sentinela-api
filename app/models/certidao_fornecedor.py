from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field
from sqlalchemy import Index

class CertidaoFornecedor(SQLModel, table=True):
    __tablename__ = "certidao_fornecedor"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    fornecedor_id: int = Field(foreign_key="fornecedor.id", nullable=False)
    tipo_certidao_id: int = Field(foreign_key="tipo_certidao.id", nullable=False)
    numero_protocolo: Optional[str] = Field(default=None, max_length=100)
    data_emissao: date = Field(nullable=False)
    data_validade: date = Field(nullable=False)
    situacao: str = Field(default="VÁLIDA", max_length=20, index=True)
    origem: Optional[str] = Field(default=None, max_length=30)
    arquivo_pdf: Optional[str] = Field(default=None, max_length=500)
    hash_arquivo: Optional[str] = Field(default=None, max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_certidao_fornecedor_validade', 'fornecedor_id', 'data_validade'),
        Index('idx_certidao_situacao', 'situacao'),
    )

class CertidaoFornecedorCreate(SQLModel):
    fornecedor_id: int
    tipo_certidao_id: int
    numero_protocolo: Optional[str] = None
    data_emissao: date
    data_validade: date
    situacao: str = "VÁLIDA"
    origem: Optional[str] = None
    arquivo_pdf: Optional[str] = None

class CertidaoFornecedorRead(SQLModel):
    id: int
    fornecedor_id: int
    tipo_certidao_id: int
    numero_protocolo: Optional[str]
    data_emissao: date
    data_validade: date
    situacao: str
    origem: Optional[str]
    created_at: datetime
