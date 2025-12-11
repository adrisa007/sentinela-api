import { useAuth } from '../contexts/AuthContext';

export const useRoleCheck = () => {
  const { user } = useAuth();

  const isBlockedRole = (perfil: string) => {
    return perfil === 'ROOT' || perfil === 'GESTOR';
  };

  const isUserBlocked = () => {
    return user ? isBlockedRole(user.perfil) : false;
  };

  const canAccess = (allowedRoles: string[]) => {
    if (!user) return false;
    return allowedRoles.includes(user.perfil);
  };

  return {
    isBlockedRole,
    isUserBlocked,
    canAccess,
    userPerfil: user?.perfil
  };
};