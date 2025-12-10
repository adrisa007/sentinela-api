from app.celery_app import celery_app
from app.core.database import get_session
from app.services.pncp_service import PNCPService
from app.models.fornecedor import Fornecedor
from app.models.contrato import Contrato
from app.models.auditoria_global import AuditoriaGlobal
from sqlmodel import Session, select
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def backup_diario(self):
    """
    Lógica de backup do banco de dados ou arquivos
    """
    try:
        logger.info("Iniciando backup diário")
        # Lógica de backup aqui
        logger.info("Backup diário executado com sucesso!")
    except Exception as exc:
        logger.error(f"Erro no backup diário: {str(exc)}")
        raise self.retry(countdown=300, exc=exc)

@celery_app.task(bind=True)
def enviar_alertas(self):
    """
    Lógica para enviar alertas automáticos
    """
    try:
        logger.info("Enviando alertas automáticos")
        # Lógica de alertas aqui
        logger.info("Alertas enviados com sucesso!")
    except Exception as exc:
        logger.error(f"Erro ao enviar alertas: {str(exc)}")
        raise self.retry(countdown=120, exc=exc)

@celery_app.task(bind=True)
def sync_pncp_fornecedor(self, fornecedor_id: int, usuario_id: int):
    """
    Sincroniza dados de um fornecedor específico com o PNCP
    """
    try:
        logger.info(f"Sincronizando fornecedor {fornecedor_id} com PNCP")

        with next(get_session()) as session:
            # Busca fornecedor
            fornecedor = session.get(Fornecedor, fornecedor_id)
            if not fornecedor or not fornecedor.cnpj:
                logger.warning(f"Fornecedor {fornecedor_id} não encontrado ou sem CNPJ")
                return

            # Valida fornecedor no PNCP
            dados_pncp = await PNCPService.validar_fornecedor(fornecedor.cnpj)

            if dados_pncp.get("validado"):
                # Atualiza dados do fornecedor
                fornecedor.situacao_cadastral = dados_pncp.get("situacao_cadastral", "ATIVO")
                fornecedor.regularidade_geral = dados_pncp.get("regularidade_geral", "REGULAR")
                fornecedor.total_certidoes_vencidas = dados_pncp.get("certidoes_vencidas", 0)
                fornecedor.data_ultima_verificacao = datetime.utcnow()

                # Verifica impedimentos
                impedimentos = dados_pncp.get("impedimentos", [])
                if impedimentos:
                    fornecedor.data_impedimento = datetime.utcnow()
                    fornecedor.motivo_impedimento = "; ".join(impedimentos[:3])  # Top 3 impedimentos
                else:
                    fornecedor.data_impedimento = None
                    fornecedor.motivo_impedimento = None

                session.commit()

                # Registra auditoria
                auditoria = AuditoriaGlobal(
                    entidade_id=fornecedor.entidade_id,
                    usuario_id=usuario_id,
                    tabela_afetada="fornecedor",
                    registro_afetado_id=fornecedor.id,
                    acao="UPDATE",
                    descricao=f"Sincronização PNCP - Fornecedor {fornecedor.cnpj}",
                    dados_antes=None,
                    dados_depois=dados_pncp
                )
                session.add(auditoria)
                session.commit()

                logger.info(f"Fornecedor {fornecedor_id} sincronizado com sucesso")
            else:
                logger.warning(f"Falha na validação PNCP do fornecedor {cnpj}")

    except Exception as exc:
        logger.error(f"Erro ao sincronizar fornecedor {fornecedor_id}: {str(exc)}")
        raise self.retry(countdown=600, exc=exc)  # Retry em 10 minutos

@celery_app.task(bind=True)
def sync_pncp_contratos(self, cnpj: str, entidade_id: int, usuario_id: int):
    """
    Sincroniza contratos de um fornecedor com o PNCP
    """
    try:
        logger.info(f"Sincronizando contratos do CNPJ {cnpj} com PNCP")

        with next(get_session()) as session:
            # Busca contratos do PNCP
            dados_pncp = await PNCPService.buscar_contratos_fornecedor(cnpj, pagina=1, tamanho_pagina=100)

            if "erro" in dados_pncp:
                logger.warning(f"Erro ao buscar contratos PNCP para {cnpj}: {dados_pncp['erro']}")
                return

            contratos_pncp = dados_pncp.get("contratos", [])
            logger.info(f"Encontrados {len(contratos_pncp)} contratos no PNCP para {cnpj}")

            # Busca fornecedor no sistema
            fornecedor = session.exec(
                select(Fornecedor).where(
                    Fornecedor.cnpj == cnpj,
                    Fornecedor.entidade_id == entidade_id
                )
            ).first()

            if not fornecedor:
                logger.warning(f"Fornecedor com CNPJ {cnpj} não encontrado na entidade {entidade_id}")
                return

            contratos_criados = 0
            contratos_atualizados = 0

            for contrato_pncp in contratos_pncp:
                numero_contrato = contrato_pncp.get("numero_contrato", "").strip()
                if not numero_contrato:
                    continue

                # Verifica se contrato já existe
                contrato_existente = session.exec(
                    select(Contrato).where(
                        Contrato.numero_contrato == numero_contrato,
                        Contrato.entidade_id == entidade_id
                    )
                ).first()

                if contrato_existente:
                    # Atualiza contrato existente
                    contrato_existente.objeto = contrato_pncp.get("objeto", contrato_existente.objeto)
                    contrato_existente.valor_global = contrato_pncp.get("valor_global", contrato_existente.valor_global)
                    contrato_existente.valor_executado = contrato_pncp.get("valor_executado", contrato_existente.valor_executado)
                    contrato_existente.status = contrato_pncp.get("status", contrato_existente.status)
                    contrato_existente.modalidade = contrato_pncp.get("modalidade", contrato_existente.modalidade)
                    contrato_existente.updated_at = datetime.utcnow()

                    contratos_atualizados += 1
                else:
                    # Cria novo contrato
                    try:
                        from decimal import Decimal
                        novo_contrato = Contrato(
                            entidade_id=entidade_id,
                            numero_contrato=numero_contrato,
                            numero_processo=contrato_pncp.get("numero_processo"),
                            objeto=contrato_pncp.get("objeto", ""),
                            fornecedor_id=fornecedor.id,
                            valor_global=Decimal(str(contrato_pncp.get("valor_global", 0))),
                            valor_executado=Decimal(str(contrato_pncp.get("valor_executado", 0))),
                            status=contrato_pncp.get("status", "VIGENTE"),
                            modalidade=contrato_pncp.get("modalidade"),
                            tipo_contrato="PNCP"
                        )
                        session.add(novo_contrato)
                        contratos_criados += 1
                    except Exception as e:
                        logger.warning(f"Erro ao criar contrato {numero_contrato}: {str(e)}")
                        continue

            session.commit()

            # Registra auditoria
            auditoria = AuditoriaGlobal(
                entidade_id=entidade_id,
                usuario_id=usuario_id,
                tabela_afetada="contrato",
                acao="SYNC_PNCP",
                descricao=f"Sincronização PNCP - Contratos do fornecedor {cnpj}",
                dados_antes=None,
                dados_depois={
                    "cnpj": cnpj,
                    "contratos_pncp": len(contratos_pncp),
                    "contratos_criados": contratos_criados,
                    "contratos_atualizados": contratos_atualizados
                }
            )
            session.add(auditoria)
            session.commit()

            logger.info(f"Sincronização concluída: {contratos_criados} criados, {contratos_atualizados} atualizados")

    except Exception as exc:
        logger.error(f"Erro ao sincronizar contratos PNCP para {cnpj}: {str(exc)}")
        raise self.retry(countdown=600, exc=exc)  # Retry em 10 minutos

@celery_app.task(bind=True)
def sync_pncp(self):
    """
    Sincronização completa com o PNCP - executa validações e atualizações em lote
    """
    try:
        logger.info("Iniciando sincronização completa com PNCP")

        with next(get_session()) as session:
            # Busca todos os fornecedores com CNPJ
            fornecedores = session.exec(
                select(Fornecedor).where(Fornecedor.cnpj.isnot(None))
            ).all()

            logger.info(f"Encontrados {len(fornecedores)} fornecedores para sincronização")

            # Agenda sincronização individual para cada fornecedor
            from app.tasks.tasks import sync_pncp_fornecedor
            for fornecedor in fornecedores:
                sync_pncp_fornecedor.delay(fornecedor.id, 1)  # usuario_id = 1 (sistema)

            logger.info("Sincronização PNCP completa agendada com sucesso!")

    except Exception as exc:
        logger.error(f"Erro na sincronização PNCP completa: {str(exc)}")
        raise self.retry(countdown=1800, exc=exc)  # Retry em 30 minutos
