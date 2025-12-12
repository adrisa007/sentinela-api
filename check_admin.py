import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from app.core.config import settings
os.environ["DATABASE_URL"] = settings.DATABASE_URL

from app.core.database import create_db_and_tables, engine
from sqlmodel import Session, select
from app.models.usuario import Usuario
from app.core.security import get_password_hash

create_db_and_tables()
with Session(engine) as session:
    admin_email = "admin@sentinela.app"
    admin = session.exec(select(Usuario).where(Usuario.email == admin_email)).first()
    if admin:
        print(f"Admin encontrado: {admin.email}, senha_hash: {admin.senha_hash[:20]}...")
    else:
        # Cria admin padrão
        admin = Usuario(
            nome="Administrador",
            email=admin_email,
            cpf="00000000000",
            senha_hash=get_password_hash("admin123"),
            perfil="ROOT",
            ativo=True
        )
        session.add(admin)
        session.commit()
        print(f"Admin criado: {admin.email} | senha: admin123")