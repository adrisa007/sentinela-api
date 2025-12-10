from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field
from sqlalchemy import Index

class FiscalDesignado(SQLModel, table=True):
    __tablename__ = "fiscal_designado"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    contrato_id: int = Field(foreign_key="contrato.id", nullable=False)
    usuario_id: int = Field(foreign_key="usuario.id", nullable=False)
    tipo_fiscal: str = Field(max_length=20, nullable=False)  # TITULAR | SUPLENTE
    data_designacao: date = Field(nullable=False)
    portaria: Optional[str] = Field(default=None, max_length=100)
    ativo: bool = Field(default=True)

    __table_args__ = (
        Index('idx_fiscal_contrato_usuario', 'contrato_id', 'usuario_id', unique=True),
    )

class FiscalDesignadoCreate(SQLModel):
    contrato_id: int
    usuario_id: int
    tipo_fiscal: str
    data_designacao: date
    portaria: Optional[str] = None

class FiscalDesignadoRead(SQLModel):
    id: int
    contrato_id: int
    usuario_id: int
    tipo_fiscal: str
    data_designacao: date
    portaria: Optional[str]
    ativo: bool
