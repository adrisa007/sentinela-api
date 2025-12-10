from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.middleware import AuditoriaMiddleware
from app.routes import auth, entidades, usuarios, fornecedores, contratos

# Importar modelos para criar tabelas
from app.models.entidade import Entidade
from app.models.usuario import Usuario
from app.models.fornecedor import Fornecedor
from app.models.tipo_certidao import TipoCertidao
from app.models.certidao_fornecedor import CertidaoFornecedor
from app.models.contrato import Contrato
from app.models.fiscal_designado import FiscalDesignado
from app.models.ocorrencia_fiscalizacao import OcorrenciaFiscalizacao
from app.models.cronograma_fisico_fin import CronogramaFisicoFin
from app.models.penalidade import Penalidade
from app.models.matriz_riscos import MatrizRiscos
from app.models.auditoria_global import AuditoriaGlobal

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API completa para gestão de contratos e fiscalização",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de auditoria
app.add_middleware(AuditoriaMiddleware)

# Rotas
app.include_router(auth.router)
app.include_router(entidades.router)
app.include_router(usuarios.router)
app.include_router(fornecedores.router)
app.include_router(contratos.router)

@app.on_event("startup")
def on_startup():
    """Cria tabelas no banco de dados ao iniciar"""
    create_db_and_tables()
    print("✅ Banco de dados inicializado")

@app.get("/")
def read_root():
    """Endpoint raiz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }
