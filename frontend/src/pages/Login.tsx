import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useRoleCheck } from '../hooks/useRoleCheck';
import { Shield, Eye, EyeOff } from 'lucide-react';

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
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-base-100 to-secondary/5 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Container principal com card */}
        <div className="card bg-base-100 shadow-2xl border border-base-300">
          <div className="card-body p-8">
            {/* Logo e título */}
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-primary rounded-full flex items-center justify-center mb-4">
                <Shield className="w-8 h-8 text-primary-content" />
              </div>
              <h1 className="text-3xl font-bold text-base-content mb-2">
                Sentinela
              </h1>
              <p className="text-base-content/70 text-sm">
                Sistema de Gestão de Contratos e Fiscalização
              </p>
            </div>

            {/* Formulário */}
            <form className="space-y-6" onSubmit={handleSubmit}>
              {/* Campo Email */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium">Email</span>
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input input-bordered w-full focus:input-primary"
                  placeholder="seu@email.com"
                />
              </div>

              {/* Campo Senha */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium">Senha</span>
                </label>
                <div className="relative">
                  <input
                    id="senha"
                    name="senha"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={senha}
                    onChange={(e) => setSenha(e.target.value)}
                    className="input input-bordered w-full pr-12 focus:input-primary"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 btn btn-ghost btn-sm btn-circle"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Campo TOTP (condicional) */}
              {requiresTOTP && (
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-medium">Código TOTP</span>
                  </label>
                  <input
                    id="totp"
                    name="totp"
                    type="text"
                    autoComplete="one-time-code"
                    required
                    value={totpCode}
                    onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    className="input input-bordered w-full text-center text-lg font-mono tracking-widest focus:input-primary"
                    placeholder="000000"
                    maxLength={6}
                  />
                  <label className="label">
                    <span className="label-text-alt text-base-content/60">
                      Digite o código de 6 dígitos do seu aplicativo autenticador
                    </span>
                  </label>
                </div>
              )}

              {/* Mensagem de erro */}
              {error && (
                <div className="alert alert-error">
                  <span>{error}</span>
                </div>
              )}

              {/* Botão de login */}
              <button
                type="submit"
                disabled={isLoading}
                className="btn btn-primary w-full"
              >
                {isLoading ? (
                  <>
                    <span className="loading loading-spinner loading-sm"></span>
                    Entrando...
                  </>
                ) : (
                  'Entrar'
                )}
              </button>
            </form>

            {/* Credenciais de teste */}
            <div className="divider my-6">Credenciais de Teste</div>
            <div className="space-y-2 text-sm">
              <div className="bg-base-200 p-3 rounded-lg">
                <p className="font-semibold text-primary">Administrador:</p>
                <p className="text-base-content/70">admin@sentinela.app</p>
                <p className="text-base-content/70">admin123</p>
              </div>
              <div className="bg-base-200 p-3 rounded-lg">
                <p className="font-semibold text-primary">Gestor:</p>
                <p className="text-base-content/70">gestor@entidade.com</p>
                <p className="text-base-content/70">gestor123</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;