import React, { useState, useEffect } from 'react';
import { X, Copy, Check } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeViewDialogProps {
  isOpen: boolean;
  onClose: () => void;
  code: string;
  workflowName?: string;
}

const CodeViewDialog: React.FC<CodeViewDialogProps> = ({ 
  isOpen, 
  onClose, 
  code,
  workflowName 
}) => {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setCopied(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-gray-800 border border-gray-700 rounded-xl shadow-2xl w-full max-w-4xl h-[80vh] flex flex-col animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div>
            <h2 className="text-lg font-semibold text-white">Código Python Gerado</h2>
            {workflowName && <p className="text-sm text-gray-400">{workflowName}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="flex-1 overflow-hidden relative group">
          <SyntaxHighlighter
            language="python"
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              padding: '1.5rem',
              height: '100%',
              fontSize: '14px',
              backgroundColor: '#1f2937' // gray-800
            }}
            showLineNumbers={true}
          >
            {code}
          </SyntaxHighlighter>
          
          <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleCopy}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg transition-all transform hover:scale-105"
            >
              {copied ? <Check size={16} /> : <Copy size={16} />}
              <span className="text-xs font-medium">{copied ? 'Copiado!' : 'Copiar'}</span>
            </button>
          </div>
        </div>
        
        <div className="p-4 border-t border-gray-700 bg-gray-900/50 rounded-b-xl flex justify-between items-center text-xs text-gray-400">
          <p>Este código pode ser executado em qualquer ambiente Python com Selenium e Pandas instalados.</p>
          <div className="flex space-x-2">
            <span className="px-2 py-1 bg-gray-800 rounded">selenium</span>
            <span className="px-2 py-1 bg-gray-800 rounded">pandas</span>
            <span className="px-2 py-1 bg-gray-800 rounded">python 3.8+</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeViewDialog;
