import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from app.core.config import settings

logger = logging.getLogger(__name__)

class PNCPService:
    """
    Serviço para integração com o Portal Nacional de Contratações Públicas (PNCP)
    """

    BASE_URL = "https://pncp.gov.br/api"
    TIMEOUT = 30

    @staticmethod
    async def _make_request(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Faz uma requisição para a API do PNCP
        """
        url = f"{PNCPService.BASE_URL}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=PNCPService.TIMEOUT) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Erro na requisição PNCP: {e}")
            raise Exception(f"Erro ao consultar PNCP: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado no PNCP: {e}")
            raise Exception(f"Erro inesperado: {str(e)}")

    @staticmethod
    async def validar_fornecedor(cnpj: str) -> Dict[str, Any]:
        """
        Valida um fornecedor através do PNCP
        """
        if not cnpj or len(cnpj.replace(".", "").replace("-", "").replace("/", "")) != 14:
            raise ValueError("CNPJ inválido")

        # Remove formatação do CNPJ
        cnpj_limpo = cnpj.replace(".", "").replace("-", "").replace("/", "")

        try:
            # Consulta fornecedores no PNCP
            endpoint = f"/fornecedores/{cnpj_limpo}"
            data = await PNCPService._make_request(endpoint)

            return {
                "cnpj": cnpj_limpo,
                "razao_social": data.get("razao_social", ""),
                "nome_fantasia": data.get("nome_fantasia", ""),
                "situacao_cadastral": data.get("situacao_cadastral", "ATIVO"),
                "regularidade_geral": data.get("regularidade_geral", "REGULAR"),
                "data_ultima_verificacao": datetime.utcnow(),
                "certidoes_vencidas": data.get("certidoes_vencidas", 0),
                "impedimentos": data.get("impedimentos", []),
                "validado": True,
                "fonte": "PNCP"
            }

        except Exception as e:
            logger.warning(f"Erro ao validar fornecedor {cnpj}: {e}")
            return {
                "cnpj": cnpj_limpo,
                "validado": False,
                "erro": str(e),
                "fonte": "PNCP"
            }

    @staticmethod
    async def buscar_contratos_fornecedor(cnpj: str, pagina: int = 1, tamanho_pagina: int = 50) -> Dict[str, Any]:
        """
        Busca contratos de um fornecedor no PNCP
        """
        if not cnpj or len(cnpj.replace(".", "").replace("-", "").replace("/", "")) != 14:
            raise ValueError("CNPJ inválido")

        cnpj_limpo = cnpj.replace(".", "").replace("-", "").replace("/", "")

        try:
            # Consulta contratos do fornecedor
            endpoint = f"/fornecedores/{cnpj_limpo}/contratos"
            params = {
                "pagina": pagina,
                "tamanhoPagina": tamanho_pagina
            }

            data = await PNCPService._make_request(endpoint, params)

            contratos = []
            for contrato in data.get("contratos", []):
                contratos.append({
                    "numero_contrato": contrato.get("numero_contrato", ""),
                    "numero_processo": contrato.get("numero_processo", ""),
                    "objeto": contrato.get("objeto", ""),
                    "orgao": contrato.get("orgao", ""),
                    "valor_global": contrato.get("valor_global", 0),
                    "valor_executado": contrato.get("valor_executado", 0),
                    "data_assinatura": contrato.get("data_assinatura"),
                    "data_inicio": contrato.get("data_inicio"),
                    "data_termino": contrato.get("data_termino"),
                    "status": contrato.get("status", "VIGENTE"),
                    "modalidade": contrato.get("modalidade"),
                    "fonte": "PNCP"
                })

            return {
                "cnpj": cnpj_limpo,
                "total_contratos": data.get("total", 0),
                "pagina": pagina,
                "tamanho_pagina": tamanho_pagina,
                "contratos": contratos,
                "fonte": "PNCP"
            }

        except Exception as e:
            logger.warning(f"Erro ao buscar contratos do fornecedor {cnpj}: {e}")
            return {
                "cnpj": cnpj_limpo,
                "erro": str(e),
                "contratos": [],
                "fonte": "PNCP"
            }

    @staticmethod
    async def buscar_contrato_por_numero(orgao_cnpj: str, numero_contrato: str) -> Dict[str, Any]:
        """
        Busca detalhes de um contrato específico
        """
        try:
            endpoint = f"/orgaos/{orgao_cnpj}/contratos/{numero_contrato}"
            data = await PNCPService._make_request(endpoint)

            return {
                "numero_contrato": numero_contrato,
                "orgao_cnpj": orgao_cnpj,
                "objeto": data.get("objeto", ""),
                "fornecedor_cnpj": data.get("fornecedor_cnpj", ""),
                "valor_global": data.get("valor_global", 0),
                "valor_executado": data.get("valor_executado", 0),
                "data_assinatura": data.get("data_assinatura"),
                "data_inicio": data.get("data_inicio"),
                "data_termino": data.get("data_termino"),
                "status": data.get("status", "VIGENTE"),
                "modalidade": data.get("modalidade"),
                "itens": data.get("itens", []),
                "aditivos": data.get("aditivos", []),
                "fonte": "PNCP"
            }

        except Exception as e:
            logger.warning(f"Erro ao buscar contrato {numero_contrato}: {e}")
            return {
                "numero_contrato": numero_contrato,
                "erro": str(e),
                "fonte": "PNCP"
            }

    @staticmethod
    async def verificar_certidoes_fornecedor(cnpj: str) -> Dict[str, Any]:
        """
        Verifica certidões de um fornecedor no PNCP
        """
        if not cnpj or len(cnpj.replace(".", "").replace("-", "").replace("/", "")) != 14:
            raise ValueError("CNPJ inválido")

        cnpj_limpo = cnpj.replace(".", "").replace("-", "").replace("/", "")

        try:
            endpoint = f"/fornecedores/{cnpj_limpo}/certidoes"
            data = await PNCPService._make_request(endpoint)

            certidoes = []
            for certidao in data.get("certidoes", []):
                certidoes.append({
                    "tipo": certidao.get("tipo", ""),
                    "numero": certidao.get("numero", ""),
                    "data_emissao": certidao.get("data_emissao"),
                    "data_validade": certidao.get("data_validade"),
                    "situacao": certidao.get("situacao", "VÁLIDA"),
                    "orgao_emissor": certidao.get("orgao_emissor", "")
                })

            # Conta certidões vencidas
            vencidas = sum(1 for c in certidoes
                          if c.get("data_validade") and
                          datetime.strptime(c["data_validade"], "%Y-%m-%d").date() < date.today())

            return {
                "cnpj": cnpj_limpo,
                "certidoes": certidoes,
                "total_certidoes": len(certidoes),
                "certidoes_vencidas": vencidas,
                "regularidade_geral": "IRREGULAR" if vencidas > 0 else "REGULAR",
                "fonte": "PNCP"
            }

        except Exception as e:
            logger.warning(f"Erro ao verificar certidões do fornecedor {cnpj}: {e}")
            return {
                "cnpj": cnpj_limpo,
                "erro": str(e),
                "certidoes": [],
                "fonte": "PNCP"
            }