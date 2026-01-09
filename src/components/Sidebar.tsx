import React from 'react';
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
  Code,
  Search,
  Columns,
  Layers,
  Terminal,
  XCircle,
  LucideIcon 
} from 'lucide-react';
import { NodeType } from '../types';
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
  Hash, // Usar Hash em vez de Variable
  GitBranch,
  Calendar,
  Table,
  Code,
  Search,
  Columns,
  Layers,
  Terminal,
  XCircle
};

const Sidebar: React.FC = () => {
  const onDragStart = (event: React.DragEvent<HTMLDivElement>, nodeType: NodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const nodeTypes: NodeType[] = [
    NodeType.LOGIN,
    NodeType.OPEN_SITE,
    NodeType.CLICK_BUTTON,
    NodeType.EXTRACT_TABLE,
    NodeType.CAPTURE_TABLE,
    NodeType.WAIT,
    NodeType.SLEEP,
    NodeType.SPREADSHEET,
    NodeType.LOOP_FOR,
    NodeType.LOOP_WHILE,
    NodeType.VARIABLE,
    NodeType.CONDITION,
    NodeType.SCHEDULE,
    NodeType.EXECUTE_SCRIPT,
    NodeType.EXTRACT_TEXT,
    NodeType.TRANSFORM_COLUMN,
    NodeType.GROUP_DATA,
    NodeType.EXECUTE_PYTHON,
    NodeType.CLOSE_BROWSER
  ];

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col h-full">
      <div className="p-4 pb-2 shrink-0">
        <h2 className="text-lg font-semibold text-white">Blocos de Automação</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 pt-2 space-y-3 custom-scrollbar">
        {nodeTypes.map((nodeType) => {
          const config = getNodeConfig(nodeType);
          if (!config) return null;
          
          const IconComponent = iconMap[config.icon] || iconMap['Hash']; // Fallback para Hash
          
          return (
            <div
              key={nodeType}
              className={`${config.color} p-3 rounded-lg cursor-grab active:cursor-grabbing hover:opacity-80 transition-opacity`}
              draggable
              onDragStart={(event) => onDragStart(event, nodeType)}
            >
              <div className="flex items-center space-x-2 text-white">
                <IconComponent size={20} />
                <span className="font-medium">{config.label}</span>
              </div>
              <p className="text-xs text-gray-200 mt-1 opacity-75">
                Arraste para o canvas
              </p>
            </div>
          );
        })}
      </div>
      
      <div className="p-3 bg-gray-700 mx-4 mb-4 rounded-lg shrink-0">
        <h3 className="text-sm font-medium text-white mb-2">Como usar:</h3>
        <ul className="text-xs text-gray-300 space-y-1">
          <li>• Arraste blocos para o canvas</li>
          <li>• Conecte os blocos pelos pontos</li>
          <li>• Configure cada bloco</li>
          <li>• Execute o fluxo</li>
        </ul>
      </div>
    </div>
  );
};

export default Sidebar;