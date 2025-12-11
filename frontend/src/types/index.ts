// Tipos base da API Sentinela

export interface Usuario {
  id: number;
  nome: string;
  email: string;
  perfil: 'ROOT' | 'GESTOR' | 'FISCAL_TECNICO' | 'FISCAL_ADM' | 'APOIO' | 'AUDITOR';
  entidade_id: number | null;
  totp_habilitado: boolean;
  ativo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface LoginRequest {
  email: string;
  senha: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

export interface AuthContextType {
  user: Usuario | null;
  token: string | null;
  login: (email: string, senha: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export interface Entidade {
  id: number;
  nome: string;
  cnpj: string;
  endereco: string;
  telefone: string;
  email: string;
  ativo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Fornecedor {
  id: number;
  nome: string;
  cnpj: string;
  endereco: string;
  telefone: string;
  email: string;
  entidade_id: number;
  ativo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Contrato {
  id: number;
  numero: string;
  objeto: string;
  valor: number;
  data_inicio: string;
  data_fim: string;
  fornecedor_id: number;
  entidade_id: number;
  status: 'ATIVO' | 'SUSPENSO' | 'ENCERRADO';
  created_at?: string;
  updated_at?: string;
}