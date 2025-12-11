import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { AuthContextType, Usuario, TOTPSetupResponse, TOTPVerifyResponse } from '../types';
import { apiService } from '../services/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<Usuario | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');

      if (storedToken && storedUser) {
        try {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          // Verificar se o token ainda é válido
          await apiService.getCurrentUser();
        } catch (error) {
          // Token inválido, limpar dados
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, senha: string, totpCode?: string) => {
    try {
      const response = await apiService.login({ email, senha, totp_code: totpCode });
      const { access_token, usuario } = response;

      setToken(access_token);
      setUser(usuario);

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(usuario));
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const setupTOTP = async (): Promise<TOTPSetupResponse> => {
    try {
      return await apiService.setupTOTP();
    } catch (error) {
      throw error;
    }
  };

  const verifyTOTPSetup = async (totpCode: string): Promise<TOTPVerifyResponse> => {
    try {
      return await apiService.verifyTOTPSetup({ totp_code: totpCode });
    } catch (error) {
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    setupTOTP,
    verifyTOTPSetup,
    isAuthenticated: !!user && !!token,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};