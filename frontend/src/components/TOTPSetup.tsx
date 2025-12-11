import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Shield, QrCode, CheckCircle } from 'lucide-react';

const TOTPSetup: React.FC = () => {
  const { setupTOTP, verifyTOTPSetup } = useAuth();
  const [step, setStep] = useState<'setup' | 'verify' | 'success'>('setup');
  const [qrCode, setQrCode] = useState<string>('');
  const [totpCode, setTotpCode] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSetup = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await setupTOTP();
      setQrCode(response.qr_code);
      setStep('verify');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao configurar TOTP');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!totpCode || totpCode.length !== 6) {
      setError('Código TOTP deve ter 6 dígitos');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await verifyTOTPSetup(totpCode);
      if (response.success) {
        setStep('success');
      } else {
        setError('Código TOTP inválido');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao verificar código');
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 'setup') {
    return (
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <div className="text-center mb-6">
          <Shield className="mx-auto h-12 w-12 text-blue-600 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900">
            Configurar Autenticação de Dois Fatores
          </h2>
          <p className="text-gray-600 mt-2">
            Adicione uma camada extra de segurança à sua conta
          </p>
        </div>

        <button
          onClick={handleSetup}
          disabled={isLoading}
          className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {isLoading ? 'Configurando...' : 'Iniciar Configuração'}
        </button>

        {error && (
          <div className="mt-4 text-red-600 text-sm text-center">
            {error}
          </div>
        )}
      </div>
    );
  }

  if (step === 'verify') {
    return (
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <div className="text-center mb-6">
          <QrCode className="mx-auto h-12 w-12 text-blue-600 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900">
            Escaneie o Código QR
          </h2>
          <p className="text-gray-600 mt-2">
            Use um aplicativo autenticador como Google Authenticator
          </p>
        </div>

        {qrCode && (
          <div className="mb-6 text-center">
            <img
              src={`data:image/png;base64,${qrCode}`}
              alt="QR Code TOTP"
              className="mx-auto border rounded-lg"
            />
          </div>
        )}

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Código de Verificação
          </label>
          <input
            type="text"
            value={totpCode}
            onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            placeholder="000000"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-center text-lg tracking-widest"
            maxLength={6}
          />
        </div>

        <button
          onClick={handleVerify}
          disabled={isLoading || totpCode.length !== 6}
          className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        >
          {isLoading ? 'Verificando...' : 'Verificar Código'}
        </button>

        {error && (
          <div className="mt-4 text-red-600 text-sm text-center">
            {error}
          </div>
        )}

        <button
          onClick={() => setStep('setup')}
          className="w-full mt-4 text-sm text-gray-600 hover:text-gray-800"
        >
          ← Voltar
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="text-center">
        <CheckCircle className="mx-auto h-12 w-12 text-green-600 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          TOTP Configurado com Sucesso!
        </h2>
        <p className="text-gray-600">
          Sua conta agora está protegida com autenticação de dois fatores.
        </p>
      </div>
    </div>
  );
};

export default TOTPSetup;