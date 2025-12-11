import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';
import {
  Building,
  Users,
  FileText,
  Shield,
  CheckCircle,
  Clock,
  TrendingUp,
  Activity,
  Calendar,
  BarChart3
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
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
      description: 'Organizações cadastradas',
      trend: '+12%',
      trendUp: true,
    },
    {
      name: 'Usuários',
      value: stats.usuarios,
      icon: Users,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600',
      description: 'Usuários ativos',
      trend: '+8%',
      trendUp: true,
    },
    {
      name: 'Contratos',
      value: stats.contratos,
      icon: FileText,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600',
      description: 'Contratos vigentes',
      trend: '+15%',
      trendUp: true,
    },
    {
      name: 'Fornecedores',
      value: stats.fornecedores,
      icon: Building,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-600',
      description: 'Fornecedores ativos',
      trend: '+5%',
      trendUp: true,
    },
  ];

  const quickActions = [
    {
      title: 'Validar Fornecedor',
      description: 'Verificar PNCP',
      icon: CheckCircle,
      color: 'bg-green-500 hover:bg-green-600',
      action: () => console.log('Validar fornecedor'),
    },
    {
      title: 'Novo Contrato',
      description: 'Cadastrar contrato',
      icon: FileText,
      color: 'bg-blue-500 hover:bg-blue-600',
      action: () => console.log('Novo contrato'),
    },
    {
      title: 'Auditoria',
      description: 'Ver logs do sistema',
      icon: Shield,
      color: 'bg-purple-500 hover:bg-purple-600',
      action: () => console.log('Auditoria'),
    },
    {
      title: 'Relatórios',
      description: 'Análises e métricas',
      icon: BarChart3,
      color: 'bg-indigo-500 hover:bg-indigo-600',
      action: () => console.log('Relatórios'),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 px-6 py-8 sm:px-8">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div className="mb-4 sm:mb-0">
                  <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">
                    Olá, {user?.nome}! 👋
                  </h1>
                  <p className="text-blue-100 text-sm sm:text-base">
                    Bem-vindo ao Sistema Sentinela de Gestão de Contratos
                  </p>
                  <div className="flex items-center mt-3 text-blue-100 text-sm">
                    <Activity className="w-4 h-4 mr-2" />
                    Sistema online e operacional
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 sm:w-20 sm:h-20 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                    <Shield className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.name}
                className={`${stat.bgColor} rounded-xl p-6 border border-gray-100 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg bg-gradient-to-r ${stat.color} shadow-lg`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div className={`flex items-center text-sm font-medium ${stat.textColor}`}>
                    <TrendingUp className="w-4 h-4 mr-1" />
                    {stat.trend}
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-2xl font-bold text-gray-900">
                    {isLoading ? (
                      <div className="animate-pulse bg-gray-300 h-8 w-16 rounded"></div>
                    ) : (
                      stat.value.toLocaleString('pt-BR')
                    )}
                  </p>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-xs text-gray-500">{stat.description}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions & Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
              <div className="flex items-center mb-6">
                <div className="p-2 bg-blue-100 rounded-lg mr-3">
                  <Activity className="w-5 h-5 text-blue-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Ações Rápidas</h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.title}
                      onClick={action.action}
                      className={`${action.color} text-white p-4 rounded-xl transition-all duration-300 transform hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-4 focus:ring-opacity-50 focus:ring-blue-300`}
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <div className="flex items-start space-x-3">
                        <Icon className="w-6 h-6 mt-1 flex-shrink-0" />
                        <div className="text-left">
                          <p className="font-semibold text-sm">{action.title}</p>
                          <p className="text-xs opacity-90 mt-1">{action.description}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
              <div className="flex items-center mb-6">
                <div className="p-2 bg-green-100 rounded-lg mr-3">
                  <Clock className="w-5 h-5 text-green-600" />
                </div>
                <h2 className="text-xl font-bold text-gray-900">Atividade Recente</h2>
              </div>
              <div className="space-y-4">
                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-4 h-4 text-blue-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      Sistema inicializado com sucesso
                    </p>
                    <div className="flex items-center mt-1">
                      <Calendar className="w-3 h-3 text-gray-400 mr-1" />
                      <p className="text-xs text-gray-500">
                        Agora mesmo
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Users className="w-4 h-4 text-green-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      Novo usuário registrado
                    </p>
                    <div className="flex items-center mt-1">
                      <Calendar className="w-3 h-3 text-gray-400 mr-1" />
                      <p className="text-xs text-gray-500">
                        2 minutos atrás
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors duration-200">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <FileText className="w-4 h-4 text-purple-600" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      Contrato aprovado
                    </p>
                    <div className="flex items-center mt-1">
                      <Calendar className="w-3 h-3 text-gray-400 mr-1" />
                      <p className="text-xs text-gray-500">
                        5 minutos atrás
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="mt-8">
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg mr-3">
                  <Activity className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Status do Sistema</h3>
                  <p className="text-sm text-gray-600">Todos os serviços estão operacionais</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  <span className="text-sm font-medium text-green-600">Online</span>
                </div>
                <div className="text-sm text-gray-500">
                  Última atualização: {new Date().toLocaleTimeString('pt-BR')}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;