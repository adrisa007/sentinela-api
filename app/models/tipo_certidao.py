from typing import Optional
from sqlmodel import SQLModel, Field

class TipoCertidao(SQLModel, table=True):
    __tablename__ = "tipo_certidao"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(max_length=30, unique=True, nullable=False)
    nome: str = Field(max_length=150, nullable=False)
    obrigatoria_licitacao: bool = Field(default=True)
    obrigatoria_contratacao: bool = Field(default=True)
    prazo_validade_dias: int = Field(default=180)
    api_disponivel: bool = Field(default=False)

class TipoCertidaoCreate(SQLModel):
    codigo: str
    nome: str
    obrigatoria_licitacao: bool = True
    obrigatoria_contratacao: bool = True
    prazo_validade_dias: int = 180
    api_disponivel: bool = False

class TipoCertidaoRead(SQLModel):
    id: int
    codigo: str
    nome: str
    obrigatoria_licitacao: bool
    obrigatoria_contratacao: bool
    prazo_validade_dias: int
    api_disponivel: bool
