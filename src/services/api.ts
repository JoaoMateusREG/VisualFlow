import { FlowData } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export interface ExecutionResponse {
  execution_id: string;
  status: string;
  message: string;
}

export interface ExecutionStatus {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'cancelled';
  started_at: string;
  finished_at?: string;
  flow_name: string;
  total_steps: number;
  current_step: number;
  logs: string[];
  results: Record<string, any>;
  error?: string;
}

export interface ValidationResponse {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

class ApiService {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Executa um fluxo no backend
   */
  async executeFlow(flowData: FlowData): Promise<ExecutionResponse> {
    return this.request<ExecutionResponse>('/api/execute-flow', {
      method: 'POST',
      body: JSON.stringify(flowData),
    });
  }

  /**
   * Consulta o status de uma execução
   */
  async getExecutionStatus(executionId: string): Promise<ExecutionStatus> {
    return this.request<ExecutionStatus>(`/api/execution/${executionId}`);
  }

  /**
   * Lista todas as execuções
   */
  async listExecutions(): Promise<ExecutionStatus[]> {
    return this.request<ExecutionStatus[]>('/api/executions');
  }

  /**
   * Cancela uma execução
   */
  async cancelExecution(executionId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/execution/${executionId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Valida um fluxo sem executar
   */
  async validateFlow(flowData: FlowData): Promise<ValidationResponse> {
    return this.request<ValidationResponse>('/api/validate-flow', {
      method: 'POST',
      body: JSON.stringify(flowData),
    });
  }

  /**
   * Verifica se o backend está disponível
   */
  async healthCheck(): Promise<{ message: string; version: string }> {
    return this.request<{ message: string; version: string }>('/');
  }
}

export const apiService = new ApiService();