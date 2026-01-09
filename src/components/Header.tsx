import React from 'react';
import { Play, Download, Upload, Zap, Server, Eye, FolderOpen, Code, X } from 'lucide-react';

interface HeaderProps {
  onExecuteFlow: () => void;
  onExecuteRemote: () => void;
  onSaveFlow: () => void;
  onLoadFlow: () => void;
  onClearFlow: () => void;
  onToggleExecutionPanel: () => void;
  onOpenWorkflowManager: () => void;
  isExecuting?: boolean;
  showExecutionPanel?: boolean;
  workflowName?: string;
  onViewCode: () => void;
}

/**
 * Componente de Cabeçalho
 * Contém os controles principais da aplicação como Executar, Salvar, Carregar e Gerenciar Workflows
 */
const Header: React.FC<HeaderProps> = ({ 
  onExecuteFlow,
  onExecuteRemote, 
  onSaveFlow, 
  onLoadFlow, 
  onClearFlow,
  onToggleExecutionPanel,
  onOpenWorkflowManager,
  isExecuting = false,
  showExecutionPanel = false,
  workflowName,
  onViewCode
}) => {
  return (
    <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Zap className="text-blue-500" size={24} />
            <h1 className="text-xl font-bold text-white">VisualFlow</h1>
          </div>
          <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">v2.0</span>
          {workflowName && (
            <div className="flex items-center space-x-2 ml-4">
              <span className="text-sm text-gray-400">Workflow:</span>
              <span className="text-sm text-white font-medium">{workflowName}</span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenWorkflowManager}
            className="flex items-center space-x-2 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            <FolderOpen size={16} />
            <span className="text-sm">Workflows</span>
          </button>

          <button
            onClick={onSaveFlow}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            <Download size={16} />
            <span className="text-sm">Download</span>
          </button>

          <button
            onClick={onLoadFlow}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            <Upload size={16} />
            <span className="text-sm">Carregar</span>
          </button>

          <button
            onClick={onClearFlow}
            className="flex items-center space-x-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            <X size={16} />
            <span className="text-sm">Limpar</span>
          </button>

          <div className="w-px h-6 bg-gray-600"></div>

          <button
            onClick={onExecuteFlow}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium"
          >
            <Play size={16} />
            <span>Gerar Código</span>
          </button>

          <button
            onClick={onExecuteRemote}
            disabled={isExecuting}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors font-medium ${
              isExecuting 
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            <Server size={16} />
            <span>{isExecuting ? 'Executando...' : 'Executar Remoto'}</span>
          </button>

          <button
            onClick={onToggleExecutionPanel}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
              showExecutionPanel 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 hover:bg-gray-600 text-white'
            }`}
          >
            <Eye size={16} />
            <span className="text-sm">Logs</span>
          </button>
          
          <button
            onClick={onViewCode}
            className="flex items-center space-x-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            <Code size={16} />
            <span className="text-sm">Ver Código</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;