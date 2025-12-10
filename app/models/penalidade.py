from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field

class Penalidade(SQLModel, table=True):
    __tablename__ = "penalidade"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    contrato_id: int = Field(foreign_key="contrato.id", nullable=False)
    tipo: str = Field(max_length=30, nullable=False)
    valor_multa: Optional[Decimal] = Field(default=None, max_digits=18, decimal_places=2)
    data_aplicacao: Optional[date] = Field(default=None)
    processo_administrativo: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="APLICADA", max_length=20)
    justificativa: Optional[str] = Field(default=None)
    recurso_apresentado: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PenalidadeCreate(SQLModel):
    contrato_id: int
    tipo: str
    valor_multa: Optional[Decimal] = None
    data_aplicacao: Optional[date] = None
    processo_administrativo: Optional[str] = None
    justificativa: Optional[str] = None

class PenalidadeUpdate(SQLModel):
    status: Optional[str] = None
    recurso_apresentado: Optional[bool] = None

class PenalidadeRead(SQLModel):
    id: int
    contrato_id: int
    tipo: str
    valor_multa: Optional[Decimal]
    data_aplicacao: Optional[date]
    status: str
    recurso_apresentado: bool
    created_at: datetime
