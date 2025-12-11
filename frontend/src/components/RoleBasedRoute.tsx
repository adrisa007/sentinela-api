import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useRoleCheck } from '../hooks/useRoleCheck';

interface RoleBasedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  blockedRoles?: string[];
}

const RoleBasedRoute: React.FC<RoleBasedRouteProps> = ({
  children,
  allowedRoles = [],
  blockedRoles = []
}) => {
  const { isAuthenticated, isLoading } = useAuth();
  const { canAccess, userPerfil } = useRoleCheck();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Verificar se o usuário tem um perfil bloqueado
  if (blockedRoles.length > 0 && blockedRoles.includes(userPerfil || '')) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-red-100 px-4">
        <div className="max-w-md w-full space-y-8">
          <div className="bg-white py-8 px-6 shadow-xl rounded-lg text-center">
            <div className="mx-auto h-16 w-16 bg-red-600 rounded-full flex items-center justify-center mb-4">
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Acesso Restrito
            </h2>
            <p className="text-gray-600 mb-4">
              Usuários com perfil <strong>{userPerfil}</strong> não têm permissão para acessar esta área do sistema.
            </p>
            <p className="text-sm text-gray-500">
              Entre em contato com o administrador do sistema para obter acesso.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Verificar se o usuário tem um dos perfis permitidos (se especificado)
  if (allowedRoles.length > 0 && !canAccess(allowedRoles)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-yellow-50 to-yellow-100 px-4">
        <div className="max-w-md w-full space-y-8">
          <div className="bg-white py-8 px-6 shadow-xl rounded-lg text-center">
            <div className="mx-auto h-16 w-16 bg-yellow-600 rounded-full flex items-center justify-center mb-4">
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Acesso Negado
            </h2>
            <p className="text-gray-600 mb-4">
              Seu perfil <strong>{userPerfil}</strong> não tem permissão para acessar esta página.
            </p>
            <p className="text-sm text-gray-500">
              Você será redirecionado para o dashboard.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default RoleBasedRoute;