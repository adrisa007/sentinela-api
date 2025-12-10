#!/usr/bin/env python3
"""Script simples para testar a API"""
import sys
sys.path.insert(0, '/workspaces/sentinela-api')

from app.core.security import create_access_token, decode_access_token
from datetime import datetime, timezone

# Cria token
data = {"sub": 1, "email": "admin@sentinela.app", "perfil": "ROOT", "entidade_id": 1}
token = create_access_token(data)

print("✅ Token criado:", token[:50] + "...")

# Decodifica token
try:
    decoded = decode_access_token(token)
    if decoded:
        print("✅ Token decodificado com sucesso!")
        print(f"   User ID: {decoded.get('sub')}")
        print(f"   Email: {decoded.get('email')}")
        print(f"   Expira: {datetime.fromtimestamp(decoded.get('exp'), tz=timezone.utc)}")
    else:
        print("❌ Erro ao decodificar token - retornou None")
except Exception as e:
    print(f"❌ Exceção ao decodificar token: {e}")
