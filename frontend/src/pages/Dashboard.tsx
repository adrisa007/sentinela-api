import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';
import {
  Building,
  Users,
  FileText,
  Shield,
  CheckCircle,
  Clock
} from 'lucide-react';

interface DashboardStats {
  entidades: number;
  usuarios: number;
  contratos: number;
  fornecedores: number;
  auditoria: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    entidades: 0,
    usuarios: 0,
    contratos: 0,
    fornecedores: 0,
    auditoria: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [entidades, usuarios, contratos, fornecedores, auditoria] = await Promise.all([
          apiService.getEntidades(),
          apiService.getUsuarios(),
          apiService.getContratos(),
          apiService.getFornecedores(),
          apiService.getEntidades(), // Temporário, depois implementar endpoint de auditoria
        ]);

        setStats({
          entidades: entidades?.length || 0,
          usuarios: usuarios?.length || 0,
          contratos: contratos?.length || 0,
          fornecedores: fornecedores?.length || 0,
          auditoria: auditoria?.length || 0,
        });
      } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, []);

  const statCards = [
    {
      name: 'Entidades',
      value: stats.entidades,
      icon: Building,
      color: 'bg-blue-500',
    },
    {
      name: 'Usuários',
      value: stats.usuarios,
      icon: Users,
      color: 'bg-green-500',
    },
    {
      name: 'Contratos',
      value: stats.contratos,
      icon: FileText,
      color: 'bg-purple-500',
    },
    {
      name: 'Fornecedores',
      value: stats.fornecedores,
      icon: Building,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Bem-vindo, {user?.nome}!
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Sistema de Gestão de Contratos e Fiscalização
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`p-3 rounded-md ${stat.color}`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {isLoading ? '...' : stat.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Ações Rápidas
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <CheckCircle className="h-8 w-8 text-green-500 mr-3" />
            <div className="text-left">
              <p className="text-sm font-medium text-gray-900">Validar Fornecedor</p>
              <p className="text-xs text-gray-500">Verificar PNCP</p>
            </div>
          </button>

          <button className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <FileText className="h-8 w-8 text-blue-500 mr-3" />
            <div className="text-left">
              <p className="text-sm font-medium text-gray-900">Novo Contrato</p>
              <p className="text-xs text-gray-500">Cadastrar contrato</p>
            </div>
          </button>

          <button className="flex items-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Shield className="h-8 w-8 text-purple-500 mr-3" />
            <div className="text-left">
              <p className="text-sm font-medium text-gray-900">Auditoria</p>
              <p className="text-xs text-gray-500">Ver logs do sistema</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Atividade Recente
        </h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <Clock className="h-5 w-5 text-gray-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-900">
                Sistema inicializado com sucesso
              </p>
              <p className="text-xs text-gray-500">
                Agora mesmo
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;