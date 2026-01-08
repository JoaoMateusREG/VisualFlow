import { useState, useCallback, useEffect } from 'react';
import { workflowService, WorkflowMetadata, SavedWorkflow, WorkflowStats } from '../services/workflowService';
import { FlowData } from '../types';

export interface UseWorkflowsReturn {
  // Estado
  workflows: WorkflowMetadata[];
  currentWorkflow: SavedWorkflow | null;
  stats: WorkflowStats | null;
  isLoading: boolean;
  error: string | null;
  
  // Ações
  saveWorkflow: (flowData: FlowData, name: string, description?: string, tags?: string[], isTemplate?: boolean) => Promise<string>;
  loadWorkflow: (workflowId: string) => Promise<SavedWorkflow>;
  updateWorkflow: (workflowId: string, updates: { flowData?: FlowData; name?: string; description?: string; tags?: string[] }) => Promise<void>;
  deleteWorkflow: (workflowId: string) => Promise<void>;
  duplicateWorkflow: (workflowId: string, name?: string) => Promise<string>;
  searchWorkflows: (query: string, tags?: string[]) => Promise<WorkflowMetadata[]>;
  refreshWorkflows: () => Promise<void>;
  
  // Auto-save
  autoSave: (flowData: FlowData) => void;
  loadAutoSave: () => { flowData: FlowData; timestamp: string } | null;
  
  // Arquivo
  exportWorkflow: (flowData: FlowData, filename?: string) => void;
  importWorkflow: () => Promise<FlowData>;
  
  // Local storage
  saveToLocal: (key: string, flowData: FlowData) => void;
  loadFromLocal: (key: string) => { flowData: FlowData; timestamp: string } | null;
  listLocalWorkflows: () => Array<{ key: string; name: string; timestamp: string }>;
}

export const useWorkflows = (): UseWorkflowsReturn => {
  const [workflows, setWorkflows] = useState<WorkflowMetadata[]>([]);
  const [currentWorkflow, setCurrentWorkflow] = useState<SavedWorkflow | null>(null);
  const [stats, setStats] = useState<WorkflowStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Carregar workflows iniciais
  useEffect(() => {
    let mounted = true;
    
    const loadInitialData = async () => {
      if (mounted) {
        await refreshWorkflows();
        await loadStats();
      }
    };
    
    loadInitialData();
    
    return () => {
      mounted = false;
    };
  }, []);

  const refreshWorkflows = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const workflowList = await workflowService.listWorkflows();
      setWorkflows(workflowList);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar workflows';
      setError(errorMessage);
      console.error('Erro ao carregar workflows:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const workflowStats = await workflowService.getWorkflowStats();
      setStats(workflowStats);
    } catch (err) {
      // Não logar erro de stats como crítico, apenas avisar
      console.warn('Aviso: Não foi possível carregar estatísticas de workflows:', err);
      // Definir stats padrão
      setStats({
        total_workflows: 0,
        regular_workflows: 0,
        templates: 0,
        most_used_tags: [],
        storage_size_mb: 0,
        oldest_workflow: null,
        newest_workflow: null
      });
    }
  }, []);

  const saveWorkflow = useCallback(async (
    flowData: FlowData, 
    name: string, 
    description: string = '', 
    tags: string[] = [], 
    isTemplate: boolean = false
  ): Promise<string> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await workflowService.saveWorkflow({
        flow_data: flowData,
        name,
        description,
        tags,
        is_template: isTemplate
      });
      
      // Atualizar lista de workflows
      await refreshWorkflows();
      await loadStats();
      
      return response.id;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao salvar workflow';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [refreshWorkflows, loadStats]);

  const loadWorkflow = useCallback(async (workflowId: string): Promise<SavedWorkflow> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const workflow = await workflowService.getWorkflow(workflowId);
      setCurrentWorkflow(workflow);
      
      return workflow;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar workflow';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateWorkflow = useCallback(async (
    workflowId: string, 
    updates: { flowData?: FlowData; name?: string; description?: string; tags?: string[] }
  ): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      
      await workflowService.updateWorkflow(workflowId, updates);
      
      // Atualizar workflow atual se for o mesmo
      if (currentWorkflow && currentWorkflow.metadata.id === workflowId) {
        const updatedWorkflow = await workflowService.getWorkflow(workflowId);
        setCurrentWorkflow(updatedWorkflow);
      }
      
      // Atualizar lista
      await refreshWorkflows();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar workflow';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [currentWorkflow, refreshWorkflows]);

  const deleteWorkflow = useCallback(async (workflowId: string): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      
      await workflowService.deleteWorkflow(workflowId);
      
      // Limpar workflow atual se for o mesmo
      if (currentWorkflow && currentWorkflow.metadata.id === workflowId) {
        setCurrentWorkflow(null);
      }
      
      // Atualizar lista
      await refreshWorkflows();
      await loadStats();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao deletar workflow';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [currentWorkflow, refreshWorkflows, loadStats]);

  const duplicateWorkflow = useCallback(async (workflowId: string, name?: string): Promise<string> => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await workflowService.duplicateWorkflow(workflowId, name);
      
      // Atualizar lista
      await refreshWorkflows();
      await loadStats();
      
      return response.id;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao duplicar workflow';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [refreshWorkflows, loadStats]);

  const searchWorkflows = useCallback(async (query: string, tags: string[] = []): Promise<WorkflowMetadata[]> => {
    try {
      setError(null);
      const results = await workflowService.searchWorkflows(query, tags);
      return results;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro na busca';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  // Auto-save
  const autoSave = useCallback((flowData: FlowData) => {
    workflowService.autoSave(flowData);
  }, []);

  const loadAutoSave = useCallback(() => {
    return workflowService.loadAutoSave();
  }, []);

  // Arquivo
  const exportWorkflow = useCallback((flowData: FlowData, filename?: string) => {
    workflowService.exportAsFile(flowData, filename);
  }, []);

  const importWorkflow = useCallback(async (): Promise<FlowData> => {
    try {
      setError(null);
      return await workflowService.importFromFile();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao importar workflow';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  // Local storage
  const saveToLocal = useCallback((key: string, flowData: FlowData) => {
    workflowService.saveToLocalStorage(key, flowData);
  }, []);

  const loadFromLocal = useCallback((key: string) => {
    return workflowService.loadFromLocalStorage(key);
  }, []);

  const listLocalWorkflows = useCallback(() => {
    return workflowService.listLocalStorageWorkflows();
  }, []);

  return {
    workflows,
    currentWorkflow,
    stats,
    isLoading,
    error,
    saveWorkflow,
    loadWorkflow,
    updateWorkflow,
    deleteWorkflow,
    duplicateWorkflow,
    searchWorkflows,
    refreshWorkflows,
    autoSave,
    loadAutoSave,
    exportWorkflow,
    importWorkflow,
    saveToLocal,
    loadFromLocal,
    listLocalWorkflows,
  };
};