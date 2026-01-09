import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { 
  LogIn, 
  MousePointer, 
  Type, 
  Clock, 
  Timer, 
  FileSpreadsheet, 
  RotateCw, 
  Repeat, 
  Hash, 
  GitBranch,
  Calendar,
  Table,
  LucideIcon 
} from 'lucide-react';
import { CustomNodeData } from '../types';
import { getNodeConfig } from '../types/nodeTypes';

const iconMap: Record<string, LucideIcon> = {
  LogIn,
  MousePointer,
  Type,
  Clock,
  Timer,
  FileSpreadsheet,
  RotateCw,
  Repeat,
  Hash,
  GitBranch,
  Calendar,
  Table
};

interface CustomNodeProps extends NodeProps {
  data: CustomNodeData;
}

const CustomNode: React.FC<CustomNodeProps> = ({ data, selected }) => {
  const config = getNodeConfig(data.type);

  if (!config) return null;

  const IconComponent = iconMap[config.icon] || iconMap['Hash']; // Fallback para Hash
  const hasConfiguration = Object.keys(data.inputs || {}).length > 0;

  return (
    <div className={`bg-gray-800 border-2 rounded-lg shadow-lg min-w-[180px] transition-all ${
      selected ? 'border-blue-500 shadow-blue-500/20' : 'border-gray-600'
    }`}>
      {/* Handle de entrada */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-gray-400 !border-2 !border-gray-600"
      />
      
      {/* Header do Node */}
      <div className={`${config.color} p-3 rounded-t-lg`}>
        <div className="flex items-center space-x-2 text-white">
          <IconComponent size={18} />
          <span className="font-medium text-sm">{config.label}</span>
        </div>
      </div>

      {/* Status de configuração */}
      <div className="px-3 py-2 bg-gray-750 rounded-b-lg">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">
            {hasConfiguration ? '✅ Configurado' : '⚙️ Clique para configurar'}
          </span>
          {hasConfiguration && (
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          )}
        </div>
      </div>

      {/* Handle de saída */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-gray-400 !border-2 !border-gray-600"
      />
    </div>
  );
};

export default CustomNode;