import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.core.database import create_db_and_tables, engine
from sqlmodel import Session, select
from app.models.usuario import Usuario

create_db_and_tables()
with Session(engine) as session:
    admin = session.exec(select(Usuario).where(Usuario.email == "admin@sentinela.app")).first()
    if admin:
        print(f"Admin encontrado: {admin.email}, senha_hash: {admin.senha_hash[:20]}...")
    else:
        print("Admin não encontrado")