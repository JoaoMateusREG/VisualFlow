import { FlowData } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export interface WorkflowMetadata {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  version: string;
  tags: string[];
  author: string;
  is_template: boolean;
}

export interface SavedWorkflow {
  metadata: WorkflowMetadata;
  flow_data: FlowData;
  file_path: string;
}

export interface SaveWorkflowRequest {
  flow_data: FlowData;
  name: string;
  description?: string;
  tags?: string[];
  is_template?: boolean;
}

export interface UpdateWorkflowRequest {
  flow_data?: FlowData;
  name?: string;
  description?: string;
  tags?: string[];
}

export interface WorkflowStats {
  total_workflows: number;
  regular_workflows: number;
  templates: number;
  most_used_tags: [string, number][];
  storage_size_mb: number;
  oldest_workflow: string | null;
  newest_workflow: string | null;
}

class WorkflowService {
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
   * Salva um novo workflow
   */
  async saveWorkflow(request: SaveWorkflowRequest): Promise<{ id: string; message: string; metadata: WorkflowMetadata }> {
    return this.request<{ id: string; message: string; metadata: WorkflowMetadata }>('/api/workflows', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Lista todos os workflows
   */
  async listWorkflows(includeTemplates: boolean = true): Promise<WorkflowMetadata[]> {
    const params = new URLSearchParams({ include_templates: includeTemplates.toString() });
    return this.request<WorkflowMetadata[]>(`/api/workflows?${params}`);
  }

  /**
   * Carrega um workflow específico
   */
  async getWorkflow(workflowId: string): Promise<SavedWorkflow> {
    return this.request<SavedWorkflow>(`/api/workflows/${workflowId}`);
  }

  /**
   * Atualiza um workflow existente
   */
  async updateWorkflow(workflowId: string, request: UpdateWorkflowRequest): Promise<{ message: string; metadata: WorkflowMetadata }> {
    return this.request<{ message: string; metadata: WorkflowMetadata }>(`/api/workflows/${workflowId}`, {
      method: 'PUT',
      body: JSON.stringify(request),
    });
  }

  /**
   * Deleta um workflow
   */
  async deleteWorkflow(workflowId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/workflows/${workflowId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Busca workflows
   */
  async searchWorkflows(query: string = '', tags: string[] = []): Promise<WorkflowMetadata[]> {
    const params = new URLSearchParams({
      q: query,
      tags: tags.join(',')
    });
    return this.request<WorkflowMetadata[]>(`/api/workflows/search?${params}`);
  }

  /**
   * Obtém estatísticas dos workflows
   */
  async getWorkflowStats(): Promise<WorkflowStats> {
    return this.request<WorkflowStats>('/api/workflows/stats');
  }

  /**
   * Duplica um workflow
   */
  async duplicateWorkflow(workflowId: string, name?: string): Promise<{ id: string; message: string; metadata: WorkflowMetadata }> {
    const params = name ? new URLSearchParams({ name }) : '';
    return this.request<{ id: string; message: string; metadata: WorkflowMetadata }>(`/api/workflows/${workflowId}/duplicate?${params}`, {
      method: 'POST',
    });
  }

  /**
   * Salva workflow automaticamente no localStorage
   */
  saveToLocalStorage(key: string, flowData: FlowData): void {
    try {
      const data = {
        flowData,
        timestamp: new Date().toISOString(),
        version: '1.0'
      };
      localStorage.setItem(`workflow_${key}`, JSON.stringify(data));
    } catch (error) {
      console.error('Erro ao salvar no localStorage:', error);
    }
  }

  /**
   * Carrega workflow do localStorage
   */
  loadFromLocalStorage(key: string): { flowData: FlowData; timestamp: string; version: string } | null {
    try {
      const data = localStorage.getItem(`workflow_${key}`);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Erro ao carregar do localStorage:', error);
      return null;
    }
  }

  /**
   * Lista workflows salvos no localStorage
   */
  listLocalStorageWorkflows(): Array<{ key: string; name: string; timestamp: string }> {
    const workflows: Array<{ key: string; name: string; timestamp: string }> = [];
    
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('workflow_')) {
          const data = localStorage.getItem(key);
          if (data) {
            const parsed = JSON.parse(data);
            workflows.push({
              key: key.replace('workflow_', ''),
              name: parsed.flowData?.metadata?.name || 'Workflow sem nome',
              timestamp: parsed.timestamp
            });
          }
        }
      }
    } catch (error) {
      console.error('Erro ao listar workflows do localStorage:', error);
    }

    return workflows.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

  /**
   * Remove workflow do localStorage
   */
  removeFromLocalStorage(key: string): void {
    try {
      localStorage.removeItem(`workflow_${key}`);
    } catch (error) {
      console.error('Erro ao remover do localStorage:', error);
    }
  }

  /**
   * Salva automaticamente (auto-save)
   */
  autoSave(flowData: FlowData): void {
    this.saveToLocalStorage('autosave', flowData);
  }

  /**
   * Carrega auto-save
   */
  loadAutoSave(): { flowData: FlowData; timestamp: string; version: string } | null {
    return this.loadFromLocalStorage('autosave');
  }

  /**
   * Exporta workflow como arquivo JSON
   */
  exportAsFile(flowData: FlowData, filename?: string): void {
    const dataStr = JSON.stringify(flowData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = filename || `workflow-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }

  /**
   * Importa workflow de arquivo JSON
   */
  importFromFile(): Promise<FlowData> {
    return new Promise((resolve, reject) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.json';
      input.onchange = (e) => {
        const target = e.target as HTMLInputElement;
        const file = target.files?.[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (e) => {
            try {
              const result = e.target?.result as string;
              const flowData = JSON.parse(result);
              resolve(flowData);
            } catch (error) {
              reject(new Error('Arquivo JSON inválido'));
            }
          };
          reader.onerror = () => reject(new Error('Erro ao ler arquivo'));
          reader.readAsText(file);
        } else {
          reject(new Error('Nenhum arquivo selecionado'));
        }
      };
      input.click();
    });
  }
}

export const workflowService = new WorkflowService();