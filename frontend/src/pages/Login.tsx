import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useRoleCheck } from '../hooks/useRoleCheck';
import { Shield, Eye, EyeOff, Info } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [requiresTOTP, setRequiresTOTP] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const { isUserBlocked } = useRoleCheck();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(email, senha, requiresTOTP ? totpCode : undefined);

      // Verificar se o usuário tem perfil bloqueado (ROOT ou GESTOR)
      if (isUserBlocked()) {
        // Fazer logout imediatamente
        const { logout } = useAuth();
        logout();
        setError('Acesso negado: Usuários com perfil ROOT ou GESTOR não podem acessar o sistema através desta interface.');
        return;
      }

      navigate(from, { replace: true });
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Erro ao fazer login';

      // Verifica se é erro de TOTP necessário
      if (errorMessage.includes('TOTP necessário') || errorMessage.includes('Código TOTP necessário')) {
        setRequiresTOTP(true);
        setError('Digite o código do seu aplicativo autenticador');
      } else {
        setError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 via-white to-blue-200 animate-gradient-x p-4">
      <div className="w-full max-w-md">
        <div className="bg-white/80 backdrop-blur-md border border-blue-100 rounded-2xl shadow-2xl p-8 md:p-10 transition-all duration-300">
          <div className="flex flex-col items-center mb-10">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-700 to-blue-500 shadow-lg rounded-full flex items-center justify-center mb-5">
              <Shield className="w-10 h-10 text-white drop-shadow-lg" />
            </div>
            <h1 className="text-4xl font-extrabold font-sans text-gray-900 mb-2 tracking-tight">Sentinela</h1>
            <p className="text-gray-500 text-lg text-center font-sans">Sistema de Gestão de Contratos e Fiscalização</p>
          </div>
          <form className="space-y-7" onSubmit={handleSubmit}>
            <div className="relative">
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <span className="absolute left-3 top-9 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 12H8m8 0a4 4 0 11-8 0 4 4 0 018 0zm0 0v1a4 4 0 01-8 0v-1" /></svg>
              </span>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full border border-gray-300 rounded-lg py-3 pl-10 pr-4 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/80 transition"
                placeholder="seu@email.com"
              />
            </div>
            <div className="relative">
              <label htmlFor="senha" className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
              <span className="absolute left-3 top-9 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m0-6v2m-6 4h12a2 2 0 002-2V7a2 2 0 00-2-2H6a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
              </span>
              <input
                id="senha"
                name="senha"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                required
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="block w-full border border-gray-300 rounded-lg py-3 pl-10 pr-10 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/80 transition"
                placeholder="••••••••"
              />
              <button
                type="button"
                className="absolute right-3 top-9 text-gray-400 hover:text-blue-700 focus:outline-none"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
              >
                {showPassword ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
            {requiresTOTP && (
              <div>
                <label htmlFor="totp" className="block text-sm font-medium text-gray-700 mb-1">Código TOTP</label>
                <input
                  id="totp"
                  name="totp"
                  type="text"
                  autoComplete="one-time-code"
                  required
                  value={totpCode}
                  onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  className="block w-full border border-gray-300 rounded-lg py-3 px-4 text-center text-lg font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/80 transition"
                  placeholder="000000"
                  maxLength={6}
                />
                <span className="block mt-1 text-xs text-gray-400">Digite o código de 6 dígitos do seu aplicativo autenticador</span>
              </div>
            )}
            {error && (
              <div className="bg-red-100 border border-red-300 text-red-700 rounded-lg px-3 py-2 text-sm text-center">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-blue-700 to-blue-500 text-white py-3 rounded-lg font-bold shadow-xl hover:from-blue-800 hover:to-blue-600 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {isLoading ? (
                <>
                  <span className="loading loading-spinner loading-xs mr-2"></span>
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </button>
          </form>
          <div className="mt-10">
            <div className="flex items-center gap-2 mb-3 text-blue-700">
              <Info className="w-5 h-5" />
              <span className="text-sm font-semibold">Credenciais de Teste</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-blue-50/80 border border-blue-100 rounded-lg p-4 text-center shadow-sm">
                <p className="font-semibold text-blue-700">Administrador:</p>
                <p className="font-mono text-sm text-gray-700 break-all">admin@sentinela.app</p>
                <p className="font-mono text-sm text-gray-700">admin123</p>
              </div>
              <div className="bg-blue-50/80 border border-blue-100 rounded-lg p-4 text-center shadow-sm">
                <p className="font-semibold text-blue-700">Gestor:</p>
                <p className="font-mono text-sm text-gray-700 break-all">gestor@entidade.com</p>
                <p className="font-mono text-sm text-gray-700">gestor123</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;