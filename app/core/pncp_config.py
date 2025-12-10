# Configurações do PNCP (Portal Nacional de Contratações Públicas)

# URLs da API do PNCP
PNCP_BASE_URL = "https://pncp.gov.br/api"
PNCP_FORNECEDORES_URL = f"{PNCP_BASE_URL}/fornecedores"
PNCP_CONTRATOS_URL = f"{PNCP_BASE_URL}/contratos"
PNCP_ORGAOS_URL = f"{PNCP_BASE_URL}/orgaos"

# Configurações de timeout e retry
PNCP_TIMEOUT = 30  # segundos
PNCP_MAX_RETRIES = 3
PNCP_RETRY_DELAY = 5  # segundos

# Configurações de paginação
PNCP_DEFAULT_PAGE_SIZE = 50
PNCP_MAX_PAGE_SIZE = 100

# Configurações de cache (em segundos)
PNCP_CACHE_FORNECEDOR = 3600  # 1 hora
PNCP_CACHE_CONTRATO = 1800    # 30 minutos
PNCP_CACHE_CERTIDOES = 7200   # 2 horas

# Status de contratos no PNCP
PNCP_STATUS_CONTRATOS = [
    "EM_ANDAMENTO",
    "CONCLUIDO",
    "CANCELADO",
    "SUSPENSO",
    "ANULADO"
]

# Modalidades de contratação
PNCP_MODALIDADES = [
    "PREGAO_ELETRONICO",
    "TOMADA_DE_PRECO",
    "CONCORRENCIA",
    "CONVITE",
    "LEILAO",
    "RDC",
    "DISPENSA",
    "INEXIGIBILIDADE",
    "CREDENCIAMENTO"
]

# Tipos de certidões
PNCP_TIPOS_CERTIDOES = [
    "CERTIDAO_FGTS",
    "CERTIDAO_TRABALHO_INFANCIL",
    "CERTIDAO_TRABALHO_ESCRAVO",
    "CERTIDAO_FEDERAL",
    "CERTIDAO_ESTADUAL",
    "CERTIDAO_MUNICIPAL",
    "CERTIDAO_INSS",
    "CERTIDAO_RECEITA_FEDERAL"
]