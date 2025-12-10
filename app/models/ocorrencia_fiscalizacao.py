from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON

class OcorrenciaFiscalizacao(SQLModel, table=True):
    __tablename__ = "ocorrencia_fiscalizacao"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    contrato_id: int = Field(foreign_key="contrato.id", nullable=False)
    fiscal_id: int = Field(foreign_key="usuario.id", nullable=False)
    data_ocorrencia: datetime = Field(nullable=False)
    tipo_ocorrencia: Optional[str] = Field(default=None, max_length=50)
    descricao: Optional[str] = Field(default=None)
    fotos: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    geolocalizacao: Optional[str] = Field(default=None)  # Formato: "lat,lng"
    assinatura_fiscal: Optional[str] = Field(default=None, max_length=500)
    assinatura_contratada: Optional[bool] = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OcorrenciaFiscalizacaoCreate(SQLModel):
    contrato_id: int
    fiscal_id: int
    data_ocorrencia: datetime
    tipo_ocorrencia: Optional[str] = None
    descricao: Optional[str] = None
    fotos: Optional[dict] = None
    geolocalizacao: Optional[str] = None
    assinatura_fiscal: Optional[str] = None
    assinatura_contratada: Optional[bool] = False

class OcorrenciaFiscalizacaoRead(SQLModel):
    id: int
    contrato_id: int
    fiscal_id: int
    data_ocorrencia: datetime
    tipo_ocorrencia: Optional[str]
    descricao: Optional[str]
    fotos: Optional[dict]
    geolocalizacao: Optional[str]
    created_at: datetime
