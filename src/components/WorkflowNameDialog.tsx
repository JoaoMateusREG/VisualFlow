import React, { useState } from 'react';
import { Save, X } from 'lucide-react';

interface WorkflowNameDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string) => void;
  currentName?: string;
  title?: string;
}

/**
 * Dialog para nomear/renomear workflows
 * Permite ao usuário definir o nome do arquivo/workflow antes de salvar
 */
const WorkflowNameDialog: React.FC<WorkflowNameDialogProps> = ({
  isOpen,
  onClose,
  onSave,
  currentName = '',
  title = 'Nome do Workflow'
}) => {
  const [workflowName, setWorkflowName] = useState(currentName);

  const handleSave = () => {
    if (workflowName.trim()) {
      onSave(workflowName.trim());
      onClose();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Nome do Workflow
            </label>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ex: Login no Sistema, Automação de Cadastro..."
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              autoFocus
            />
          </div>

          <div className="text-xs text-gray-400">
            <p>• O nome será usado para identificar o workflow</p>
            <p>• Arquivos salvos incluirão o nome e a data</p>
            <p>• Use nomes descritivos para facilitar a organização</p>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={handleSave}
            disabled={!workflowName.trim()}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
          >
            <Save size={16} />
            Salvar
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkflowNameDialog;