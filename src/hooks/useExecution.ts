import { useState, useCallback, useEffect, useRef } from 'react';
import { apiService, ExecutionStatus } from '../services/api';
import { FlowData } from '../types';

export interface UseExecutionReturn {
  // Estado
  isExecuting: boolean;
  executionStatus: ExecutionStatus | null;
  error: string | null;
  
  // Ações
  executeFlow: (flowData: FlowData) => Promise<void>;
  cancelExecution: () => Promise<void>;
  clearExecution: () => void;
  
  // Dados
  logs: string[];
  progress: number;
  currentStep: string;
}

export const useExecution = (): UseExecutionReturn => {
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  
  const executionIdRef = useRef<string | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Função para fazer polling do status da execução
  const pollExecutionStatus = useCallback(async (executionId: string) => {
    try {
      const status = await apiService.getExecutionStatus(executionId);
      setExecutionStatus(status);
      setLogs(status.logs);
      
      // Se a execução terminou (sucesso, erro ou cancelada), parar o polling
      if (['completed', 'error', 'cancelled'].includes(status.status)) {
        setIsExecuting(false);
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
        
        if (status.status === 'error') {
          setError(status.error || 'Erro desconhecido na execução');
        }
      }
    } catch (err) {
      console.error('Erro ao consultar status da execução:', err);
      setError(err instanceof Error ? err.message : 'Erro ao consultar status');
      setIsExecuting(false);
      
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }
  }, []);

  // Iniciar execução
  const executeFlow = useCallback(async (flowData: FlowData) => {
    try {
      setError(null);
      setIsExecuting(true);
      setExecutionStatus(null);
      setLogs(['Iniciando execução...']);

      // Validar fluxo primeiro
      const validation = await apiService.validateFlow(flowData);
      if (!validation.valid) {
        throw new Error(`Fluxo inválido: ${validation.errors.join(', ')}`);
      }

      if (validation.warnings.length > 0) {
        setLogs(prev => [...prev, ...validation.warnings.map(w => `⚠️ ${w}`)]);
      }

      // Iniciar execução
      const response = await apiService.executeFlow(flowData);
      executionIdRef.current = response.execution_id;
      
      setLogs(prev => [...prev, `✅ ${response.message}`, `🆔 ID da execução: ${response.execution_id}`]);

      // Iniciar polling do status
      pollingIntervalRef.current = setInterval(() => {
        if (executionIdRef.current) {
          pollExecutionStatus(executionIdRef.current);
        }
      }, 1000); // Polling a cada 1 segundo

      // Fazer primeira consulta imediatamente
      if (executionIdRef.current) {
        await pollExecutionStatus(executionIdRef.current);
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      setIsExecuting(false);
      setLogs(prev => [...prev, `❌ Erro: ${errorMessage}`]);
    }
  }, [pollExecutionStatus]);

  // Cancelar execução
  const cancelExecution = useCallback(async () => {
    if (!executionIdRef.current) return;

    try {
      await apiService.cancelExecution(executionIdRef.current);
      setLogs(prev => [...prev, '🛑 Execução cancelada pelo usuário']);
      
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
      
      setIsExecuting(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao cancelar execução';
      setError(errorMessage);
      setLogs(prev => [...prev, `❌ Erro ao cancelar: ${errorMessage}`]);
    }
  }, []);

  // Limpar estado da execução
  const clearExecution = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    
    setIsExecuting(false);
    setExecutionStatus(null);
    setError(null);
    setLogs([]);
    executionIdRef.current = null;
  }, []);

  // Cleanup ao desmontar componente
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Calcular progresso
  const progress = executionStatus 
    ? Math.round((executionStatus.current_step / executionStatus.total_steps) * 100)
    : 0;

  // Passo atual
  const currentStep = executionStatus 
    ? `${executionStatus.current_step}/${executionStatus.total_steps}`
    : '0/0';

  return {
    isExecuting,
    executionStatus,
    error,
    executeFlow,
    cancelExecution,
    clearExecution,
    logs,
    progress,
    currentStep,
  };
};