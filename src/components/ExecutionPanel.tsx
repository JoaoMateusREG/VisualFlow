import React from 'react';
import { 
  Square, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  Loader2,
  Terminal,
  X
} from 'lucide-react';
import { UseExecutionReturn } from '../hooks/useExecution';

interface ExecutionPanelProps {
  execution: UseExecutionReturn;
  isVisible: boolean;
  onClose: () => void;
}

/**
 * Painel de Logs de Execução
 * Exibe o status em tempo real da execução remota, incluindo logs, progresso e erros
 */
const ExecutionPanel: React.FC<ExecutionPanelProps> = ({ 
  execution, 
  isVisible, 
  onClose 
}) => {
  if (!isVisible) return null;

  const getStatusIcon = () => {
    if (execution.isExecuting) {
      return <Loader2 className="animate-spin text-blue-500" size={20} />;
    }
    
    if (execution.error) {
      return <XCircle className="text-red-500" size={20} />;
    }
    
    if (execution.executionStatus?.status === 'completed') {
      return <CheckCircle className="text-green-500" size={20} />;
    }
    
    if (execution.executionStatus?.status === 'cancelled') {
      return <Square className="text-yellow-500" size={20} />;
    }
    
    return <Clock className="text-gray-500" size={20} />;
  };

  const getStatusText = () => {
    if (execution.isExecuting) {
      return 'Executando...';
    }
    
    if (execution.error) {
      return 'Erro na execução';
    }
    
    switch (execution.executionStatus?.status) {
      case 'completed':
        return 'Concluído com sucesso';
      case 'cancelled':
        return 'Cancelado';
      case 'error':
        return 'Erro na execução';
      default:
        return 'Aguardando execução';
    }
  };

  const getStatusColor = () => {
    if (execution.isExecuting) return 'text-blue-400';
    if (execution.error) return 'text-red-400';
    
    switch (execution.executionStatus?.status) {
      case 'completed':
        return 'text-green-400';
      case 'cancelled':
        return 'text-yellow-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 shadow-lg z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <Terminal size={20} className="text-blue-400" />
          <h3 className="font-semibold text-white">Execução do Fluxo</h3>
          {getStatusIcon()}
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>
        
        <div className="flex items-center space-x-3">
          {execution.executionStatus && (
            <div className="text-sm text-gray-400">
              Passo {execution.currentStep}
            </div>
          )}
          
          {execution.isExecuting && (
            <button
              onClick={execution.cancelExecution}
              className="flex items-center space-x-1 px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
            >
              <Square size={14} />
              <span>Cancelar</span>
            </button>
          )}
          
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      {execution.executionStatus && (
        <div className="px-4 py-2 bg-gray-750">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
            <span>Progresso</span>
            <span>{execution.progress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${execution.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Logs */}
      <div className="p-4 max-h-48 overflow-y-auto">
        <div className="space-y-1">
          {execution.logs.length === 0 ? (
            <div className="text-gray-500 text-sm italic">
              Nenhum log disponível
            </div>
          ) : (
            execution.logs.map((log, index) => (
              <div 
                key={index} 
                className="text-sm font-mono text-gray-300 flex items-start space-x-2"
              >
                <span className="text-gray-500 text-xs mt-0.5 flex-shrink-0">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <span className="break-all">{log}</span>
              </div>
            ))
          )}
        </div>
        
        {/* Error Display */}
        {execution.error && (
          <div className="mt-3 p-3 bg-red-900/20 border border-red-700/30 rounded-lg">
            <div className="flex items-start space-x-2">
              <AlertTriangle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-red-400 font-medium text-sm mb-1">Erro:</div>
                <div className="text-red-300 text-sm font-mono break-all">
                  {execution.error}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Success Message */}
        {execution.executionStatus?.status === 'completed' && (
          <div className="mt-3 p-3 bg-green-900/20 border border-green-700/30 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle size={16} className="text-green-400" />
              <div className="text-green-400 font-medium text-sm">
                Fluxo executado com sucesso!
              </div>
            </div>
            {execution.executionStatus.results && Object.keys(execution.executionStatus.results).length > 0 && (
              <div className="mt-2 text-xs text-green-300">
                Resultados: {JSON.stringify(execution.executionStatus.results, null, 2)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExecutionPanel;