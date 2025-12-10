"""
Script de inicialização do banco de dados.
Popula dados iniciais como tipos de certidões.
"""
from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.models.tipo_certidao import TipoCertidao
from app.models.usuario import Usuario
from app.models.entidade import Entidade
from app.core.security import get_password_hash

def init_tipos_certidao():
    """Inicializa tipos de certidões"""
    tipos_certidao = [
        {
            "codigo": "CND_FEDERAL",
            "nome": "Certidão Negativa de Débitos Federais",
            "obrigatoria_licitacao": True,
            "obrigatoria_contratacao": True,
            "prazo_validade_dias": 180,
            "api_disponivel": True
        },
        {
            "codigo": "CND_ESTADUAL",
            "nome": "Certidão Negativa de Débitos Estaduais",
            "obrigatoria_licitacao": True,
            "obrigatoria_contratacao": True,
            "prazo_validade_dias": 180,
            "api_disponivel": False
        },
        {
            "codigo": "CND_MUNICIPAL",
            "nome": "Certidão Negativa de Débitos Municipais",
            "obrigatoria_licitacao": True,
            "obrigatoria_contratacao": True,
            "prazo_validade_dias": 180,
            "api_disponivel": False
        },
        {
            "codigo": "FGTS",
            "nome": "Certificado de Regularidade do FGTS",
            "obrigatoria_licitacao": True,
            "obrigatoria_contratacao": True,
            "prazo_validade_dias": 180,
            "api_disponivel": True
        },
        {
            "codigo": "TRABALHISTA",
            "nome": "Certidão Negativa de Débitos Trabalhistas",
            "obrigatoria_licitacao": True,
            "obrigatoria_contratacao": True,
            "prazo_validade_dias": 180,
            "api_disponivel": True
        },
        {
            "codigo": "INSS",
            "nome": "Certidão Negativa de Débitos do INSS",
            "obrigatoria_licitacao": True,
            "obrigatoria_contratacao": True,
            "prazo_validade_dias": 180,
            "api_disponivel": True
        },
    ]
    
    with Session(engine) as session:
        for tipo_data in tipos_certidao:
            # Verifica se já existe
            statement = select(TipoCertidao).where(TipoCertidao.codigo == tipo_data["codigo"])
            existing = session.exec(statement).first()
            
            if not existing:
                tipo = TipoCertidao(**tipo_data)
                session.add(tipo)
                print(f"✅ Tipo de certidão criado: {tipo_data['nome']}")
            else:
                print(f"⏭️  Tipo de certidão já existe: {tipo_data['nome']}")
        
        session.commit()

def create_root_user():
    """Cria usuário ROOT inicial"""
    with Session(engine) as session:
        # Verifica se já existe um usuário ROOT
        statement = select(Usuario).where(Usuario.perfil == "ROOT")
        existing = session.exec(statement).first()
        
        if not existing:
            # Verifica se entidade padrão já existe
            statement = select(Entidade).where(Entidade.cnpj == "00000000000000")
            entidade = session.exec(statement).first()
            
            if not entidade:
                # Cria entidade padrão
                entidade = Entidade(
                    cnpj="00000000000000",
                    razao_social="Sistema Sentinela",
                    nome_fantasia="Sentinela",
                    status="ATIVA"
                )
                session.add(entidade)
                session.commit()
                session.refresh(entidade)
            
            # Cria usuário ROOT
            root_user = Usuario(
                entidade_id=entidade.id,
                nome="Administrador",
                cpf="00000000000",
                email="admin@sentinela.app",
                senha_hash=get_password_hash("admin123"),
                perfil="ROOT",
                ativo=True
            )
            session.add(root_user)
            session.commit()
            
            print("✅ Usuário ROOT criado:")
            print("   Email: admin@sentinela.app")
            print("   Senha: admin123")
            print("   ⚠️  ALTERE A SENHA EM PRODUÇÃO!")
        else:
            print("⏭️  Usuário ROOT já existe")

def main():
    """Função principal de inicialização"""
    print("🚀 Iniciando banco de dados...")
    
    # Cria todas as tabelas
    create_db_and_tables()
    print("✅ Tabelas criadas")
    
    # Popula dados iniciais
    print("\n📦 Populando dados iniciais...")
    init_tipos_certidao()
    create_root_user()
    
    print("\n✅ Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    main()
