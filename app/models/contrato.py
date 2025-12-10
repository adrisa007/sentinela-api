from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field
from sqlalchemy import Index

class Contrato(SQLModel, table=True):
    __tablename__ = "contrato"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    entidade_id: int = Field(foreign_key="entidade.id", nullable=False)
    numero_contrato: str = Field(max_length=50, nullable=False)
    numero_processo: Optional[str] = Field(default=None, max_length=50)
    objeto: str = Field(nullable=False)
    fornecedor_id: int = Field(foreign_key="fornecedor.id", nullable=False)
    valor_global: Decimal = Field(max_digits=18, decimal_places=2, nullable=False)
    valor_executado: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2)
    data_assinatura: Optional[date] = Field(default=None)
    data_inicio: Optional[date] = Field(default=None)
    data_termino: Optional[date] = Field(default=None)
    vigencia_meses: Optional[int] = Field(default=None)
    modalidade: Optional[str] = Field(default=None, max_length=50)
    tipo_contrato: Optional[str] = Field(default=None, max_length=50)
    gestor_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    status: str = Field(default="VIGENTE", max_length=30)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_contrato_entidade_numero', 'entidade_id', 'numero_contrato', unique=True),
        Index('idx_contrato_entidade_status', 'entidade_id', 'status'),
    )

class ContratoCreate(SQLModel):
    entidade_id: int
    numero_contrato: str
    numero_processo: Optional[str] = None
    objeto: str
    fornecedor_id: int
    valor_global: Decimal
    data_assinatura: Optional[date] = None
    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None
    vigencia_meses: Optional[int] = None
    modalidade: Optional[str] = None
    tipo_contrato: Optional[str] = None
    gestor_id: Optional[int] = None

class ContratoUpdate(SQLModel):
    objeto: Optional[str] = None
    valor_global: Optional[Decimal] = None
    valor_executado: Optional[Decimal] = None
    data_termino: Optional[date] = None
    status: Optional[str] = None
    gestor_id: Optional[int] = None

class ContratoRead(SQLModel):
    id: int
    entidade_id: int
    numero_contrato: str
    numero_processo: Optional[str]
    objeto: str
    fornecedor_id: int
    valor_global: Decimal
    valor_executado: Decimal
    data_assinatura: Optional[date]
    data_inicio: Optional[date]
    data_termino: Optional[date]
    status: str
    created_at: datetime
