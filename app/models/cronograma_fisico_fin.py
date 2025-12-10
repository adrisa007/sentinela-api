from typing import Optional
from datetime import date
from decimal import Decimal
from sqlmodel import SQLModel, Field

class CronogramaFisicoFin(SQLModel, table=True):
    __tablename__ = "cronograma_fisico_fin"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    contrato_id: int = Field(foreign_key="contrato.id", nullable=False)
    etapa: Optional[str] = Field(default=None, max_length=255)
    percentual_planejado: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    percentual_executado: Decimal = Field(default=Decimal("0.00"), max_digits=5, decimal_places=2)
    data_prevista: Optional[date] = Field(default=None)
    data_realizada: Optional[date] = Field(default=None)
    status: Optional[str] = Field(default=None, max_length=20)

class CronogramaFisicoFinCreate(SQLModel):
    contrato_id: int
    etapa: Optional[str] = None
    percentual_planejado: Optional[Decimal] = None
    data_prevista: Optional[date] = None
    status: Optional[str] = None

class CronogramaFisicoFinUpdate(SQLModel):
    percentual_executado: Optional[Decimal] = None
    data_realizada: Optional[date] = None
    status: Optional[str] = None

class CronogramaFisicoFinRead(SQLModel):
    id: int
    contrato_id: int
    etapa: Optional[str]
    percentual_planejado: Optional[Decimal]
    percentual_executado: Decimal
    data_prevista: Optional[date]
    data_realizada: Optional[date]
    status: Optional[str]
