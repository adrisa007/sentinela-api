from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session
from app.core.database import engine
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.middleware import AuditoriaMiddleware
from app.routes import (
    auth, 
    entidades, 
    usuarios, 
    fornecedores, 
    contratos,
    tipo_certidao,
    certidoes,
    fiscais,
    ocorrencias,
    cronogramas,
    penalidades,
    matriz_riscos,
    auditoria,
    pncp
)

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    create_db_and_tables()
    print("✅ Banco de dados inicializado")
    yield
    # Shutdown (se necessário no futuro)
    print("🔴 Aplicação encerrada")


# Configuração do rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API completa para gestão de contratos e fiscalização",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Adiciona handler de rate limit exceeded
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)




# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware CSRF simples (exemplo, para POST/PUT/PATCH/DELETE)
class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        from app.core.config import settings
        if settings.ENVIRONMENT.lower() in ("test", "testing"):  # Ignora CSRF em testes
            return await call_next(request)
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            csrf_token = request.headers.get("x-csrf-token")
            # Aqui você pode validar o token conforme sua lógica
            if not csrf_token or csrf_token != "sentinela-csrf":
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=403, content={"detail": "CSRF token inválido ou ausente."})
        return await call_next(request)

# # app.add_middleware(CSRFMiddleware)
app.add_middleware(CSRFMiddleware)


# Middleware de auditoria
app.add_middleware(AuditoriaMiddleware)

# Rotas
app.include_router(auth.router)
app.include_router(entidades.router)
app.include_router(usuarios.router)
app.include_router(fornecedores.router)
app.include_router(contratos.router)
app.include_router(tipo_certidao.router)
app.include_router(certidoes.router)
app.include_router(fiscais.router)
app.include_router(ocorrencias.router)
app.include_router(cronogramas.router)
app.include_router(penalidades.router)
app.include_router(matriz_riscos.router)
app.include_router(auditoria.router)
app.include_router(pncp.router)


# Exemplo de uso de rate limit em endpoint
from slowapi.util import get_remote_address
from slowapi.util import get_remote_address
from slowapi import Limiter
def rate_limiter(limit):
    def decorator(func):
        return func
    return decorator

@app.get("/")
@rate_limiter("10/second")
def read_root(request: Request):
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
    """Health check simples"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

@app.get("/ready")
def ready_check():
    """Health check do banco de dados"""
    try:
        with Session(engine) as session:
            session.exec("SELECT 1")
        return {"status": "ready", "database": "ok"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unavailable", "database": "error", "detail": str(e)})

# Config Redis (ajuste conforme necessário)
REDIS_URL = "redis://localhost:6379/0"
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
