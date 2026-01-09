import React, { useState, useEffect } from 'react';
import { 
  Save, 
  FolderOpen, 
  Search, 
  Trash2, 
  Copy, 
  Download, 
  Upload,
  Clock,
  Tag,
  X
} from 'lucide-react';
import { useWorkflows } from '../hooks/useWorkflows';
import { FlowData } from '../types';
import { WorkflowMetadata } from '../services/workflowService';

interface WorkflowManagerProps {
  isOpen: boolean;
  onClose: () => void;
  currentFlowData: FlowData;
  onLoadWorkflow: (flowData: FlowData) => void;
}

/**
 * Gerenciador de Workflows
 * Interface completa para CRUD (Listar, Criar, Salvar, Deletar) de workflows
 * Permite também Exportar/Importar arquivos e filtrar por tags
 */
const WorkflowManager: React.FC<WorkflowManagerProps> = ({
  isOpen,
  onClose,
  currentFlowData,
  onLoadWorkflow
}) => {
  const {
    workflows,
    stats,
    isLoading,
    error,
    saveWorkflow,
    loadWorkflow,
    deleteWorkflow,
    duplicateWorkflow,
    refreshWorkflows,
    exportWorkflow,
    importWorkflow,
    downloadWorkflow
  } = useWorkflows();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [filteredWorkflows, setFilteredWorkflows] = useState<WorkflowMetadata[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [saveForm, setSaveForm] = useState({
    name: '',
    description: '',
    tags: ''
  });

  // Drag and drop handlers for workflow import
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleFileDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        try {
          const text = await file.text();
          const flowData = JSON.parse(text);
          
          // Try different formats
          let parsedFlowData = null;
          if (flowData.flow_data) {
            parsedFlowData = flowData.flow_data;
          } else if (flowData.rawData) {
            parsedFlowData = flowData;
          } else if (flowData.nodes && flowData.edges) {
            parsedFlowData = { rawData: flowData };
          }
          
          if (parsedFlowData) {
            onLoadWorkflow(parsedFlowData);
            onClose();
            alert('Workflow importado com sucesso via drag & drop!');
          } else {
            alert('Formato de workflow não reconhecido.');
          }
        } catch (err) {
          alert('Erro ao processar arquivo: ' + (err instanceof Error ? err.message : 'Erro desconhecido'));
        }
      } else {
        alert('Por favor, arraste um arquivo .json');
      }
    }
  };

  // Filtrar workflows
  useEffect(() => {
    let filtered = workflows;

    if (searchQuery) {
      filtered = filtered.filter(w => 
        w.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        w.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedTags.length > 0) {
      filtered = filtered.filter(w => 
        selectedTags.some(tag => w.tags.includes(tag))
      );
    }

    setFilteredWorkflows(filtered);
  }, [workflows, searchQuery, selectedTags]);

  // Obter todas as tags únicas
  const allTags = Array.from(new Set(workflows.flatMap(w => w.tags))).sort();

  const handleSaveWorkflow = async () => {
    try {
      const tags = saveForm.tags.split(',').map(t => t.trim()).filter(t => t);
      
      await saveWorkflow(
        currentFlowData,
        saveForm.name,
        saveForm.description,
        tags,
        false
      );

      setShowSaveDialog(false);
      setSaveForm({ name: '', description: '', tags: '' });
      
      alert('Workflow salvo com sucesso!');
    } catch (err) {
      alert(`Erro ao salvar: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
    }
  };

  const handleLoadWorkflow = async (workflowId: string) => {
    try {
      const workflow = await loadWorkflow(workflowId);
      onLoadWorkflow(workflow.flow_data);
      onClose();
      alert('Workflow carregado com sucesso!');
    } catch (err) {
      alert(`Erro ao carregar: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
    }
  };

  const handleDeleteWorkflow = async (workflowId: string, name: string) => {
    if (window.confirm(`Tem certeza que deseja deletar o workflow "${name}"?`)) {
      try {
        await deleteWorkflow(workflowId);
        alert('Workflow deletado com sucesso!');
      } catch (err) {
        alert(`Erro ao deletar: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
      }
    }
  };

  const handleDuplicateWorkflow = async (workflowId: string, name: string) => {
    try {
      await duplicateWorkflow(workflowId, `${name} (Cópia)`);
      alert('Workflow duplicado com sucesso!');
    } catch (err) {
      alert(`Erro ao duplicar: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
    }
  };

  const handleImportWorkflow = async () => {
    try {
      const flowData = await importWorkflow();
      onLoadWorkflow(flowData);
      onClose();
      alert('Workflow importado com sucesso!');
    } catch (err) {
      alert(`Erro ao importar: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg w-full max-w-6xl h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">Gerenciar Workflows</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>

        {/* Toolbar */}
        <div className="p-4 border-b border-gray-700 space-y-4">
          {/* Ações principais */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setShowSaveDialog(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              <Save size={16} />
              Salvar Atual
            </button>
            
            <button
              onClick={handleImportWorkflow}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              <Upload size={16} />
              Importar
            </button>
            
            <button
              onClick={() => exportWorkflow(currentFlowData)}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            >
              <Download size={16} />
              Exportar Atual
            </button>

            <button
              onClick={refreshWorkflows}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              <FolderOpen size={16} />
              Atualizar
            </button>
          </div>

          {/* Busca e filtros */}
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <input
                type="text"
                placeholder="Buscar workflows..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              />
            </div>

            {/* Filtro por tags */}
            {allTags.length > 0 && (
              <div className="flex gap-2 flex-wrap">
                {allTags.slice(0, 5).map(tag => (
                  <button
                    key={tag}
                    onClick={() => {
                      setSelectedTags(prev => 
                        prev.includes(tag) 
                          ? prev.filter(t => t !== tag)
                          : [...prev, tag]
                      );
                    }}
                    className={`px-3 py-1 rounded text-sm ${
                      selectedTags.includes(tag)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <Tag size={12} className="inline mr-1" />
                    {tag}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Estatísticas */}
          {stats && (
            <div className="flex gap-6 text-sm text-gray-400">
              <span>Total: {stats.total_workflows}</span>
              <span>Armazenamento: {stats.storage_size_mb} MB</span>
            </div>
          )}
        </div>

        {/* Lista de workflows */}
        <div 
          className={`flex-1 overflow-y-auto p-4 transition-colors ${isDragOver ? 'bg-blue-900/30 border-2 border-dashed border-blue-500' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleFileDrop}
        >
          {/* Drop Zone Indicator */}
          {isDragOver && (
            <div className="text-center text-blue-400 py-8 mb-4 flex flex-col items-center gap-2">
              <Upload size={48} />
              <span className="text-lg">Solte o arquivo .json aqui para importar</span>
            </div>
          )}

          {isLoading && (
            <div className="text-center text-gray-400 py-8">
              Carregando workflows...
            </div>
          )}

          {error && (
            <div className="text-center text-red-400 py-8">
              Erro: {error}
            </div>
          )}

          {!isLoading && !error && filteredWorkflows.length === 0 && !isDragOver && (
            <div className="text-center text-gray-400 py-8">
              <p>Nenhum workflow encontrado</p>
              <p className="text-sm mt-2">Arraste um arquivo .json aqui para importar</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredWorkflows.map(workflow => (
              <div
                key={workflow.id}
                className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-colors"
              >
                {/* Header do card */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-white mb-1">
                      {workflow.name}
                    </h3>
                    <p className="text-sm text-gray-300 line-clamp-2">
                      {workflow.description || 'Sem descrição'}
                    </p>
                  </div>
                </div>

                {/* Tags */}
                {workflow.tags.length > 0 && (
                  <div className="flex gap-1 flex-wrap mb-3">
                    {workflow.tags.slice(0, 3).map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-600 text-xs text-gray-300 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                    {workflow.tags.length > 3 && (
                      <span className="px-2 py-1 bg-gray-600 text-xs text-gray-300 rounded">
                        +{workflow.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}

                {/* Metadados */}
                <div className="text-xs text-gray-400 mb-3 space-y-1">
                  <div className="flex items-center gap-1">
                    <Clock size={12} />
                    Criado: {formatDate(workflow.created_at)}
                  </div>
                  {workflow.updated_at !== workflow.created_at && (
                    <div className="flex items-center gap-1">
                      <Clock size={12} />
                      Atualizado: {formatDate(workflow.updated_at)}
                    </div>
                  )}
                </div>

                {/* Ações */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleLoadWorkflow(workflow.id)}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                  >
                    <FolderOpen size={14} className="inline mr-1" />
                    Carregar
                  </button>
                  
                  <button
                    onClick={() => downloadWorkflow(workflow.id)}
                    className="px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-500"
                    title="Baixar workflow como arquivo .json"
                  >
                    <Download size={14} />
                  </button>
                  
                  <button
                    onClick={() => handleDuplicateWorkflow(workflow.id, workflow.name)}
                    className="px-3 py-2 bg-gray-600 text-white text-sm rounded hover:bg-gray-500"
                    title="Duplicar workflow"
                  >
                    <Copy size={14} />
                  </button>
                  
                  <button
                    onClick={() => handleDeleteWorkflow(workflow.id, workflow.name)}
                    className="px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                    title="Deletar workflow"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Dialog de salvamento */}
        {showSaveDialog && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold text-white mb-4">Salvar Workflow</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Nome *
                  </label>
                  <input
                    type="text"
                    value={saveForm.name}
                    onChange={(e) => setSaveForm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="Nome do workflow"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Descrição
                  </label>
                  <textarea
                    value={saveForm.description}
                    onChange={(e) => setSaveForm(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="Descrição do workflow"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Tags (separadas por vírgula)
                  </label>
                  <input
                    type="text"
                    value={saveForm.tags}
                    onChange={(e) => setSaveForm(prev => ({ ...prev, tags: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="automação, login, teste"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSaveWorkflow}
                  disabled={!saveForm.name.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
                >
                  Salvar
                </button>
                <button
                  onClick={() => setShowSaveDialog(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowManager;