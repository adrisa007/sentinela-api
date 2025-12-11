import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';
import {
  Bar,
  Line,
  Doughnut
} from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface CronogramaData {
  id: number;
  contrato_id: number;
  etapa: string;
  percentual_fisico_previsto: number;
  percentual_fisico_realizado: number;
  percentual_financeiro_previsto: number;
  percentual_financeiro_realizado: number;
  data_prevista: string;
  data_realizada?: string;
  valor_previsto: number;
  valor_realizado: number;
}

interface ExecutionStats {
  totalContratos: number;
  mediaExecucaoFisica: number;
  mediaExecucaoFinanceira: number;
  contratosAtrasados: number;
  contratosNoPrazo: number;
}

const DashboardGestor: React.FC = () => {
  const { user } = useAuth();
  const [cronogramas, setCronogramas] = useState<CronogramaData[]>([]);
  const [stats, setStats] = useState<ExecutionStats>({
    totalContratos: 0,
    mediaExecucaoFisica: 0,
    mediaExecucaoFinanceira: 0,
    contratosAtrasados: 0,
    contratosNoPrazo: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadCronogramasData = async () => {
      try {
        const cronogramasData = await apiService.getCronogramas();

        if (cronogramasData && Array.isArray(cronogramasData)) {
          setCronogramas(cronogramasData);

          // Calcular estatísticas
          const contratosUnicos = new Set(cronogramasData.map(c => c.contrato_id));
          const totalContratos = contratosUnicos.size;

          const mediaExecucaoFisica = cronogramasData.reduce((acc, c) =>
            acc + (c.percentual_fisico_realizado / c.percentual_fisico_previsto) * 100, 0
          ) / cronogramasData.length;

          const mediaExecucaoFinanceira = cronogramasData.reduce((acc, c) =>
            acc + (c.percentual_financeiro_realizado / c.percentual_financeiro_previsto) * 100, 0
          ) / cronogramasData.length;

          // Contar contratos atrasados (simplificado - baseado em data)
          const hoje = new Date();
          const contratosAtrasados = cronogramasData.filter(c => {
            const dataPrevista = new Date(c.data_prevista);
            return dataPrevista < hoje && c.percentual_fisico_realizado < c.percentual_fisico_previsto;
          }).length;

          const contratosNoPrazo = totalContratos - contratosAtrasados;

          setStats({
            totalContratos,
            mediaExecucaoFisica: isNaN(mediaExecucaoFisica) ? 0 : mediaExecucaoFisica,
            mediaExecucaoFinanceira: isNaN(mediaExecucaoFinanceira) ? 0 : mediaExecucaoFinanceira,
            contratosAtrasados,
            contratosNoPrazo,
          });
        }
      } catch (error) {
        console.error('Erro ao carregar dados dos cronogramas:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadCronogramasData();
  }, []);

  // Dados para gráfico de barras - % Execução Física vs Financeira
  const executionChartData = {
    labels: ['Execução Física', 'Execução Financeira'],
    datasets: [
      {
        label: 'Previsto (%)',
        data: [
          stats.mediaExecucaoFisica,
          stats.mediaExecucaoFinanceira
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
      {
        label: 'Realizado (%)',
        data: [
          stats.mediaExecucaoFisica * 0.85, // Simulação de dados realizados
          stats.mediaExecucaoFinanceira * 0.82
        ],
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1,
      },
    ],
  };

  const executionChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Percentual de Execução Física vs Financeira',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Percentual (%)'
        }
      }
    }
  };

  // Dados para gráfico de linha - Progressão temporal
  const timelineData = {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
    datasets: [
      {
        label: 'Execução Física (%)',
        data: [15, 25, 35, 45, 55, 65, 75, 80, 85, 90, 95, 98],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.1,
      },
      {
        label: 'Execução Financeira (%)',
        data: [12, 22, 32, 42, 52, 58, 68, 75, 82, 88, 92, 95],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        tension: 0.1,
      },
    ],
  };

  const timelineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Progressão da Execução ao Longo do Tempo',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: 'Percentual (%)'
        }
      }
    }
  };

  // Dados para gráfico de pizza - Status dos contratos
  const statusData = {
    labels: ['No Prazo', 'Atrasados'],
    datasets: [
      {
        data: [stats.contratosNoPrazo, stats.contratosAtrasados],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderColor: [
          'rgba(16, 185, 129, 1)',
          'rgba(239, 68, 68, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const statusOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
      title: {
        display: true,
        text: 'Status dos Contratos',
      },
    },
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Dashboard Gestor - {user?.nome}
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          Acompanhe a execução físico-financeira dos contratos
        </p>
      </div>

      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-blue-500">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total de Contratos
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.totalContratos}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-green-500">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Execução Física Média
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.mediaExecucaoFisica.toFixed(1)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-purple-500">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Execução Financeira Média
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.mediaExecucaoFinanceira.toFixed(1)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="p-3 rounded-md bg-red-500">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Contratos Atrasados
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.contratosAtrasados}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Barras - Execução Física vs Financeira */}
        <div className="bg-white shadow rounded-lg p-6">
          <Bar data={executionChartData} options={executionChartOptions} />
        </div>

        {/* Gráfico de Pizza - Status dos Contratos */}
        <div className="bg-white shadow rounded-lg p-6">
          <Doughnut data={statusData} options={statusOptions} />
        </div>
      </div>

      {/* Gráfico de Linha - Progressão Temporal */}
      <div className="bg-white shadow rounded-lg p-6">
        <Line data={timelineData} options={timelineOptions} />
      </div>

      {/* Tabela de Cronogramas Recentes */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Cronogramas Recentes
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Etapa
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Execução Física
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Execução Financeira
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cronogramas.slice(0, 5).map((cronograma) => (
                  <tr key={cronograma.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {cronograma.etapa}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {cronograma.percentual_fisico_realizado}% / {cronograma.percentual_fisico_previsto}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {cronograma.percentual_financeiro_realizado}% / {cronograma.percentual_financeiro_previsto}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        cronograma.percentual_fisico_realizado >= cronograma.percentual_fisico_previsto
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {cronograma.percentual_fisico_realizado >= cronograma.percentual_fisico_previsto ? 'No Prazo' : 'Atrasado'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardGestor;