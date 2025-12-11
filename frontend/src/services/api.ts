import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import type { LoginRequest, LoginResponse, Usuario, TOTPSetupResponse, TOTPVerifyRequest, TOTPVerifyResponse } from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para adicionar token automaticamente
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor para tratamento de erros
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Autenticação
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.api.post('/auth/login', data);
    return response.data;
  }

  async getCurrentUser(): Promise<Usuario> {
    const response: AxiosResponse<Usuario> = await this.api.get('/auth/me');
    return response.data;
  }

  // TOTP/MFA
  async setupTOTP(): Promise<TOTPSetupResponse> {
    const response: AxiosResponse<TOTPSetupResponse> = await this.api.post('/auth/totp/setup');
    return response.data;
  }

  async verifyTOTPSetup(data: TOTPVerifyRequest): Promise<TOTPVerifyResponse> {
    const response: AxiosResponse<TOTPVerifyResponse> = await this.api.post('/auth/totp/verify', data);
    return response.data;
  }

  // Entidades
  async getEntidades() {
    const response = await this.api.get('/entidades');
    return response.data;
  }

  // Usuários
  async getUsuarios() {
    const response = await this.api.get('/usuarios');
    return response.data;
  }

  // Fornecedores
  async getFornecedores() {
    const response = await this.api.get('/fornecedores');
    return response.data;
  }

  // Contratos
  async getContratos() {
    const response = await this.api.get('/contratos');
    return response.data;
  }

  async getCronogramas() {
    const response = await this.api.get('/cronogramas');
    return response.data;
  }

  // PNCP
  async validarFornecedor(cnpj: string) {
    const response = await this.api.get(`/pncp/fornecedor/validar/${cnpj}`);
    return response.data;
  }

  async buscarContratosFornecedor(cnpj: string) {
    const response = await this.api.get(`/pncp/fornecedor/${cnpj}/contratos`);
    return response.data;
  }
}

export const apiService = new ApiService();