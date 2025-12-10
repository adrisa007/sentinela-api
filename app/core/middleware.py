from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlmodel import Session
from app.core.database import engine
from app.models.auditoria_global import AuditoriaGlobal
import json

class AuditoriaMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar todas as operações no sistema"""
    
    async def dispatch(self, request: Request, call_next):
        # Ignora rotas de documentação e health check
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
        
        # Captura informações da requisição
        user_id = None
        entidade_id = None
        
        # Tenta extrair user_id do token se disponível
        if "authorization" in request.headers:
            try:
                from app.core.security import decode_access_token
                token = request.headers["authorization"].replace("Bearer ", "")
                payload = decode_access_token(token)
                if payload:
                    user_id = payload.get("sub")
                    entidade_id = payload.get("entidade_id")
            except:
                pass
        
        # Processa a requisição
        response = await call_next(request)
        
        # Registra auditoria para operações de modificação
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            try:
                with Session(engine) as session:
                    auditoria = AuditoriaGlobal(
                        entidade_id=entidade_id,
                        usuario_id=user_id,
                        acao=f"{request.method} {request.url.path}",
                        tabela_afetada=self._extract_table_from_path(request.url.path),
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent"),
                    )
                    session.add(auditoria)
                    session.commit()
            except Exception as e:
                # Não falha a requisição se a auditoria falhar
                print(f"Erro ao registrar auditoria: {e}")
        
        return response
    
    def _extract_table_from_path(self, path: str) -> str:
        """Extrai o nome da tabela do path da URL"""
        parts = path.strip("/").split("/")
        if len(parts) > 0:
            return parts[0]
        return "unknown"
