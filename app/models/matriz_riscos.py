from typing import Optional
from sqlmodel import SQLModel, Field

class MatrizRiscos(SQLModel, table=True):
    __tablename__ = "matriz_riscos"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    contrato_id: int = Field(foreign_key="contrato.id", nullable=False)
    risco_descricao: Optional[str] = Field(default=None)
    probabilidade: Optional[int] = Field(default=None)  # 1 a 5
    impacto: Optional[int] = Field(default=None)  # 1 a 5
    nivel_risco: Optional[str] = Field(default=None, max_length=20)
    medida_mitigacao: Optional[str] = Field(default=None)
    responsavel_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    status: str = Field(default="ATIVO", max_length=20)

class MatrizRiscosCreate(SQLModel):
    contrato_id: int
    risco_descricao: Optional[str] = None
    probabilidade: Optional[int] = None
    impacto: Optional[int] = None
    medida_mitigacao: Optional[str] = None
    responsavel_id: Optional[int] = None

class MatrizRiscosUpdate(SQLModel):
    probabilidade: Optional[int] = None
    impacto: Optional[int] = None
    medida_mitigacao: Optional[str] = None
    status: Optional[str] = None

class MatrizRiscosRead(SQLModel):
    id: int
    contrato_id: int
    risco_descricao: Optional[str]
    probabilidade: Optional[int]
    impacto: Optional[int]
    nivel_risco: Optional[str]
    medida_mitigacao: Optional[str]
    responsavel_id: Optional[int]
    status: str
