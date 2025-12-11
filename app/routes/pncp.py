from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user, require_perfil
from app.services.pncp_service import PNCPService
from app.models.fornecedor import Fornecedor, FornecedorRead
from app.models.contrato import Contrato, ContratoRead
from app.models.usuario import Usuario
from datetime import datetime

router = APIRouter(prefix="/pncp", tags=["PNCP - Portal Nacional de Contratações Públicas"])

@router.get("/fornecedor/validar/{cnpj}")
async def validar_fornecedor_pncp(
    cnpj: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR", "APOIO"))
):
    """
    Valida um fornecedor através do PNCP (Portal Nacional de Contratações Públicas).
    Verifica situação cadastral, regularidade e certidões.
    """
    # Valida CNPJ
    if not cnpj or len(cnpj.replace(".", "").replace("-", "").replace("/", "")) != 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ inválido. Deve conter 14 dígitos."
        )

    # Faz validação no PNCP
    resultado = await PNCPService.validar_fornecedor(cnpj)

    if not resultado.get("validado", False):
        return {
            "status": "erro",
            "cnpj": cnpj,
            "validado": False,
            "erro": resultado.get("erro", "Erro desconhecido"),
            "fonte": "PNCP"
        }

    # Verifica se fornecedor já existe no sistema
    cnpj_limpo = cnpj.replace(".", "").replace("-", "").replace("/", "")
    fornecedor_existente = session.exec(
        select(Fornecedor).where(
            Fornecedor.cnpj == cnpj_limpo,
            Fornecedor.entidade_id == current_user.entidade_id
        )
    ).first()

    # Agenda sincronização em background se fornecedor existir
    if fornecedor_existente:
        # TODO: Implementar sincronização em background
        # background_tasks.add_task(
        #     sync_pncp_fornecedor,
        #     fornecedor_existente.id,
        #     current_user.id
        # )
        pass

    return {
        "status": "sucesso",
        "cnpj": cnpj,
        "validado": True,
        "dados": {
            "razao_social": resultado.get("razao_social", ""),
            "nome_fantasia": resultado.get("nome_fantasia", ""),
            "situacao_cadastral": resultado.get("situacao_cadastral", "ATIVO"),
            "regularidade_geral": resultado.get("regularidade_geral", "REGULAR"),
            "certidoes_vencidas": resultado.get("certidoes_vencidas", 0),
            "impedimentos": resultado.get("impedimentos", [])
        },
        "fornecedor_existente": fornecedor_existente.id if fornecedor_existente else None,
        "fonte": "PNCP"
    }

@router.get("/fornecedor/{cnpj}/contratos")
async def buscar_contratos_fornecedor_pncp(
    cnpj: str,
    pagina: int = Query(1, ge=1),
    tamanho_pagina: int = Query(50, ge=1, le=100),
    background_tasks: BackgroundTasks = None,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Busca contratos de um fornecedor no PNCP.
    Retorna lista de contratos com informações detalhadas.
    """
    try:
        # Valida CNPJ
        if not cnpj or len(cnpj.replace(".", "").replace("-", "").replace("/", "")) != 14:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ inválido. Deve conter 14 dígitos."
            )

        # Busca contratos no PNCP
        resultado = await PNCPService.buscar_contratos_fornecedor(cnpj, pagina, tamanho_pagina)

        if "erro" in resultado:
            return {
                "status": "erro",
                "cnpj": cnpj,
                "erro": resultado["erro"],
                "contratos": [],
                "fonte": "PNCP"
            }

        # Verifica contratos existentes no sistema
        cnpj_limpo = cnpj.replace(".", "").replace("-", "").replace("/", "")
        contratos_sistema = session.exec(
            select(Contrato).where(
                Contrato.entidade_id == current_user.entidade_id
            ).join(Fornecedor).where(Fornecedor.cnpj == cnpj_limpo)
        ).all()

        contratos_existentes = {c.numero_contrato: c.id for c in contratos_sistema}

        # Marca contratos que já existem no sistema
        for contrato in resultado["contratos"]:
            numero = contrato.get("numero_contrato", "")
            contrato["contrato_existente_id"] = contratos_existentes.get(numero)

        # Agenda sincronização em background
        if background_tasks and contratos_sistema:
            # TODO: Implementar sincronização em background
            # background_tasks.add_task(
            #     sync_pncp_contratos,
            #     cnpj_limpo,
            #     current_user.entidade_id,
            #     current_user.id
            # )
            pass

        return {
            "status": "sucesso",
            "cnpj": cnpj,
            "total_contratos": resultado.get("total_contratos", 0),
            "pagina": pagina,
            "tamanho_pagina": tamanho_pagina,
            "contratos": resultado.get("contratos", []),
            "contratos_no_sistema": len(contratos_sistema),
            "fonte": "PNCP"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/contrato/{orgao_cnpj}/{numero_contrato}")
async def buscar_contrato_detalhado_pncp(
    orgao_cnpj: str,
    numero_contrato: str,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR"))
):
    """
    Busca detalhes completos de um contrato específico no PNCP.
    Inclui itens, aditivos e informações detalhadas.
    """
    try:
        # Busca contrato no PNCP
        resultado = await PNCPService.buscar_contrato_por_numero(orgao_cnpj, numero_contrato)

        if "erro" in resultado:
            return {
                "status": "erro",
                "orgao_cnpj": orgao_cnpj,
                "numero_contrato": numero_contrato,
                "erro": resultado["erro"],
                "fonte": "PNCP"
            }

        # Verifica se contrato já existe no sistema
        contrato_existente = session.exec(
            select(Contrato).where(
                Contrato.entidade_id == current_user.entidade_id,
                Contrato.numero_contrato == numero_contrato
            )
        ).first()

        return {
            "status": "sucesso",
            "orgao_cnpj": orgao_cnpj,
            "numero_contrato": numero_contrato,
            "contrato_existente_id": contrato_existente.id if contrato_existente else None,
            "dados": resultado,
            "fonte": "PNCP"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/fornecedor/{cnpj}/certidoes")
async def verificar_certidoes_fornecedor_pncp(
    cnpj: str,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR", "AUDITOR", "APOIO"))
):
    """
    Verifica todas as certidões de um fornecedor no PNCP.
    Retorna status de regularidade e lista detalhada de certidões.
    """
    try:
        # Valida CNPJ
        if not cnpj or len(cnpj.replace(".", "").replace("-", "").replace("/", "")) != 14:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ inválido. Deve conter 14 dígitos."
            )

        # Verifica certidões no PNCP
        resultado = await PNCPService.verificar_certidoes_fornecedor(cnpj)

        if "erro" in resultado:
            return {
                "status": "erro",
                "cnpj": cnpj,
                "erro": resultado["erro"],
                "certidoes": [],
                "fonte": "PNCP"
            }

        # Atualiza fornecedor no sistema se existir
        cnpj_limpo = cnpj.replace(".", "").replace("-", "").replace("/", "")
        fornecedor = session.exec(
            select(Fornecedor).where(
                Fornecedor.cnpj == cnpj_limpo,
                Fornecedor.entidade_id == current_user.entidade_id
            )
        ).first()

        if fornecedor:
            # Atualiza dados de regularidade
            fornecedor.regularidade_geral = resultado.get("regularidade_geral", "REGULAR")
            fornecedor.total_certidoes_vencidas = resultado.get("certidoes_vencidas", 0)
            fornecedor.data_ultima_verificacao = datetime.utcnow()
            session.commit()

        return {
            "status": "sucesso",
            "cnpj": cnpj,
            "fornecedor_atualizado": fornecedor.id if fornecedor else None,
            "dados": {
                "total_certidoes": resultado.get("total_certidoes", 0),
                "certidoes_vencidas": resultado.get("certidoes_vencidas", 0),
                "regularidade_geral": resultado.get("regularidade_geral", "REGULAR"),
                "certidoes": resultado.get("certidoes", [])
            },
            "fonte": "PNCP"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/sync/fornecedor/{fornecedor_id}")
async def sincronizar_fornecedor_pncp(
    fornecedor_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """
    Sincroniza dados de um fornecedor específico com o PNCP em background.
    """
    # Verifica se fornecedor existe
    fornecedor = session.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )

    # Verifica permissão de entidade
    if fornecedor.entidade_id != current_user.entidade_id and current_user.perfil != "ROOT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para sincronizar este fornecedor"
        )

    if not fornecedor.cnpj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fornecedor não possui CNPJ cadastrado"
        )

    # Agenda sincronização
    # TODO: Implementar sincronização em background
    # background_tasks.add_task(
    #     sync_pncp_fornecedor,
    #     fornecedor_id,
    #     current_user.id
    # )
    return {
        "status": "sincronizacao_agendada",
        "fornecedor_id": fornecedor_id,
        "cnpj": fornecedor.cnpj,
        "mensagem": "Sincronização com PNCP agendada (não implementada)"
    }

@router.post("/sync/contratos/{cnpj}")
async def sincronizar_contratos_fornecedor_pncp(
    cnpj: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_perfil("ROOT", "GESTOR"))
):
    """
    Sincroniza contratos de um fornecedor com o PNCP em background.
    """
    # Valida CNPJ
    if not cnpj or len(cnpj.replace(".", "").replace("-", "").replace("/", "")) != 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ inválido. Deve conter 14 dígitos."
        )

    cnpj_limpo = cnpj.replace(".", "").replace("-", "").replace("/", "")

    # Agenda sincronização
    # TODO: Implementar sincronização em background
    # background_tasks.add_task(
    #     sync_pncp_contratos,
    #     cnpj_limpo,
    #     current_user.entidade_id,
    #     current_user.id
    # )

    return {
        "status": "sincronizacao_agendada",
        "cnpj": cnpj,
        "entidade_id": current_user.entidade_id,
        "mensagem": "Sincronização de contratos com PNCP agendada (não implementada)"
    }