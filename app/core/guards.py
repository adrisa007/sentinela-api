"""
Guards para controle de acesso multi-tenant e root
"""
from typing import Optional, List
from fastapi import HTTPException, status
from sqlmodel import Session, select, col
from app.models.usuario import Usuario


class TenantGuard:
    """
    Guard para garantir isolamento de dados por entidade (multi-tenant)
    Usuários ROOT têm acesso a todas as entidades
    Outros perfis só acessam dados da própria entidade
    """
    
    @staticmethod
    def filter_by_tenant(
        statement,
        model_class,
        current_user: Usuario,
        tenant_field: str = "entidade_id"
    ):
        """
        Aplica filtro de tenant (entidade) na query
        
        Args:
            statement: Query SQLModel
            model_class: Classe do modelo
            current_user: Usuário autenticado
            tenant_field: Nome do campo de entidade no modelo
        
        Returns:
            Query com filtro aplicado (se não for ROOT)
        """
        # ROOT vê tudo
        if current_user.perfil == "ROOT":
            return statement
        
        # Outros perfis só veem dados da própria entidade
        if hasattr(model_class, tenant_field):
            return statement.where(
                getattr(model_class, tenant_field) == current_user.entidade_id
            )
        
        return statement
    
    @staticmethod
    def check_tenant_access(
        entity,
        current_user: Usuario,
        tenant_field: str = "entidade_id"
    ):
        """
        Verifica se usuário tem acesso a uma entidade específica
        
        Args:
            entity: Objeto do modelo
            current_user: Usuário autenticado
            tenant_field: Nome do campo de entidade
        
        Raises:
            HTTPException: Se não tiver acesso
        """
        # ROOT tem acesso a tudo
        if current_user.perfil == "ROOT":
            return
        
        # Verifica se a entidade pertence ao tenant do usuário
        entity_tenant_id = getattr(entity, tenant_field, None)
        
        if entity_tenant_id is None:
            # Se não tem campo de entidade, permite acesso
            return
        
        if entity_tenant_id != current_user.entidade_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: você não tem permissão para acessar dados de outra entidade"
            )
    
    @staticmethod
    def validate_tenant_on_create(
        data_dict: dict,
        current_user: Usuario,
        tenant_field: str = "entidade_id"
    ):
        """
        Valida e força entidade_id ao criar registro
        
        Args:
            data_dict: Dados do novo registro
            current_user: Usuário autenticado
            tenant_field: Nome do campo de entidade
        
        Returns:
            Dict com entidade_id validada
        """
        # ROOT pode criar em qualquer entidade
        if current_user.perfil == "ROOT":
            # Se não informou entidade_id, usa a do usuário ROOT
            if tenant_field not in data_dict or data_dict[tenant_field] is None:
                data_dict[tenant_field] = current_user.entidade_id
            return data_dict
        
        # Outros perfis só podem criar na própria entidade
        data_dict[tenant_field] = current_user.entidade_id
        return data_dict


class RootGuard:
    """
    Guard para operações que só ROOT pode executar
    """
    
    @staticmethod
    def require_root(current_user: Usuario):
        """
        Verifica se usuário é ROOT
        
        Args:
            current_user: Usuário autenticado
        
        Raises:
            HTTPException: Se não for ROOT
        """
        if current_user.perfil != "ROOT":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas usuários ROOT podem executar esta operação"
            )
    
    @staticmethod
    def is_root(current_user: Usuario) -> bool:
        """
        Verifica se usuário é ROOT (retorna boolean)
        
        Args:
            current_user: Usuário autenticado
        
        Returns:
            True se for ROOT, False caso contrário
        """
        return current_user.perfil == "ROOT"


class GestorGuard:
    """
    Guard para operações que ROOT ou GESTOR podem executar
    """
    
    @staticmethod
    def require_gestor_or_root(current_user: Usuario):
        """
        Verifica se usuário é ROOT ou GESTOR
        
        Args:
            current_user: Usuário autenticado
        
        Raises:
            HTTPException: Se não for ROOT nem GESTOR
        """
        if current_user.perfil not in ["ROOT", "GESTOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas ROOT ou GESTOR podem executar esta operação"
            )
    
    @staticmethod
    def is_gestor_or_root(current_user: Usuario) -> bool:
        """
        Verifica se usuário é ROOT ou GESTOR
        
        Args:
            current_user: Usuário autenticado
        
        Returns:
            True se for ROOT ou GESTOR
        """
        return current_user.perfil in ["ROOT", "GESTOR"]


class OwnerGuard:
    """
    Guard para verificar se usuário é dono do recurso
    """
    
    @staticmethod
    def check_owner_access(
        entity,
        current_user: Usuario,
        owner_field: str = "usuario_id"
    ):
        """
        Verifica se usuário é dono do recurso ou tem permissão superior
        
        Args:
            entity: Objeto do modelo
            current_user: Usuário autenticado
            owner_field: Nome do campo de usuário proprietário
        
        Raises:
            HTTPException: Se não for dono nem tiver permissão
        """
        # ROOT e GESTOR têm acesso a tudo
        if current_user.perfil in ["ROOT", "GESTOR"]:
            return
        
        # Verifica se é o dono
        owner_id = getattr(entity, owner_field, None)
        
        if owner_id is None:
            # Se não tem campo de dono, permite acesso
            return
        
        if owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: você não tem permissão para acessar este recurso"
            )
    
    @staticmethod
    def is_owner(entity, current_user: Usuario, owner_field: str = "usuario_id") -> bool:
        """
        Verifica se usuário é dono do recurso
        
        Args:
            entity: Objeto do modelo
            current_user: Usuário autenticado
            owner_field: Nome do campo de usuário proprietário
        
        Returns:
            True se for dono
        """
        owner_id = getattr(entity, owner_field, None)
        return owner_id == current_user.id


class AuditorGuard:
    """
    Guard para recursos de auditoria
    """
    
    @staticmethod
    def require_auditor_access(current_user: Usuario):
        """
        Verifica se usuário tem acesso a auditoria (ROOT, GESTOR ou AUDITOR)
        
        Args:
            current_user: Usuário autenticado
        
        Raises:
            HTTPException: Se não tiver permissão
        """
        if current_user.perfil not in ["ROOT", "GESTOR", "AUDITOR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas ROOT, GESTOR ou AUDITOR podem acessar auditorias"
            )
    
    @staticmethod
    def has_auditor_access(current_user: Usuario) -> bool:
        """
        Verifica se usuário tem acesso a auditoria
        
        Args:
            current_user: Usuário autenticado
        
        Returns:
            True se tiver acesso
        """
        return current_user.perfil in ["ROOT", "GESTOR", "AUDITOR"]


class FiscalGuard:
    """
    Guard para operações de fiscalização
    """
    
    @staticmethod
    def require_fiscal_access(current_user: Usuario):
        """
        Verifica se usuário é fiscal (qualquer tipo), gestor ou root
        
        Args:
            current_user: Usuário autenticado
        
        Raises:
            HTTPException: Se não tiver permissão
        """
        allowed_profiles = ["ROOT", "GESTOR", "FISCAL_TECNICO", "FISCAL_ADM"]
        
        if current_user.perfil not in allowed_profiles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas fiscais, gestores ou ROOT podem executar esta operação"
            )
    
    @staticmethod
    def is_fiscal(current_user: Usuario) -> bool:
        """
        Verifica se usuário é fiscal
        
        Args:
            current_user: Usuário autenticado
        
        Returns:
            True se for fiscal, gestor ou root
        """
        return current_user.perfil in ["ROOT", "GESTOR", "FISCAL_TECNICO", "FISCAL_ADM"]
    
    @staticmethod
    def require_fiscal_tecnico(current_user: Usuario):
        """
        Verifica se usuário é fiscal técnico, gestor ou root
        
        Args:
            current_user: Usuário autenticado
        
        Raises:
            HTTPException: Se não tiver permissão
        """
        if current_user.perfil not in ["ROOT", "GESTOR", "FISCAL_TECNICO"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas fiscal técnico, gestor ou ROOT podem executar esta operação"
            )
    
    @staticmethod
    def require_fiscal_adm(current_user: Usuario):
        """
        Verifica se usuário é fiscal administrativo, gestor ou root
        
        Args:
            current_user: Usuário autenticado
        
        Raises:
            HTTPException: Se não tiver permissão
        """
        if current_user.perfil not in ["ROOT", "GESTOR", "FISCAL_ADM"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: apenas fiscal administrativo, gestor ou ROOT podem executar esta operação"
            )


# Funções auxiliares para uso rápido
def apply_tenant_filter(statement, model_class, current_user: Usuario, tenant_field: str = "entidade_id"):
    """Atalho para aplicar filtro de tenant"""
    return TenantGuard.filter_by_tenant(statement, model_class, current_user, tenant_field)


def check_tenant_access(entity, current_user: Usuario, tenant_field: str = "entidade_id"):
    """Atalho para verificar acesso ao tenant"""
    TenantGuard.check_tenant_access(entity, current_user, tenant_field)


def require_root(current_user: Usuario):
    """Atalho para exigir ROOT"""
    RootGuard.require_root(current_user)


def require_gestor_or_root(current_user: Usuario):
    """Atalho para exigir GESTOR ou ROOT"""
    GestorGuard.require_gestor_or_root(current_user)


def require_fiscal_access(current_user: Usuario):
    """Atalho para exigir acesso de fiscal"""
    FiscalGuard.require_fiscal_access(current_user)


def require_auditor_access(current_user: Usuario):
    """Atalho para exigir acesso de auditor"""
    AuditorGuard.require_auditor_access(current_user)
