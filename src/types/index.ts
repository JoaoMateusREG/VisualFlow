import { Node, Edge } from 'reactflow';

/**
 * Tipos de nós suportados na aplicação VisualFlow
 * Cada tipo corresponde a uma ação ou bloco lógico específico
 */
export enum NodeType {
  LOGIN = 'login',           // Realiza login no sistema
  OPEN_SITE = 'openSite',    // Navega para URL pública
  CLICK_BUTTON = 'clickButton', // Clica em elementos
  EXTRACT_TABLE = 'extractTable', // Insere texto (Input) - NOME LEGADO
  CAPTURE_TABLE = 'captureTable', // Extrai tabelas HTML
  WAIT = 'wait',             // Aguarda condições/tempo
  SLEEP = 'sleep',           // Pausa fixa
  SPREADSHEET = 'spreadsheet', // Leitura/Escrita de Excel/CSV
  LOOP_FOR = 'loopFor',      // Repetição For
  LOOP_WHILE = 'loopWhile',  // Repetição While
  VARIABLE = 'variable',     // Manipulação de variáveis
  CONDITION = 'condition',   // Lógica If/Else
  SCHEDULE = 'schedule',     // Agendamento de execução
  EXECUTE_SCRIPT = 'executeScript', // Executa JS no navegador
  EXTRACT_TEXT = 'extractText', // Extrai texto de elementos (com Regex)
  TRANSFORM_COLUMN = 'transformColumn', // Transforma dados de planilhas
  GROUP_DATA = 'groupData',  // Agrupa dados (GroupBy)
  EXECUTE_PYTHON = 'executePython', // Executa código Python arbitrário
  CLOSE_BROWSER = 'closeBrowser' // Fecha instância do navegador
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface NodeInput {
  name: string;
  label: string;
  type: 'text' | 'password' | 'number' | 'select' | 'checkbox';
  placeholder: string;
  options?: SelectOption[];
  helpText?: string;
  required?: boolean;
}

export interface NodeConfig {
  label: string;
  description?: string;
  icon: string;
  color: string;
  inputs: NodeInput[];
}

export interface CustomNodeData {
  type: NodeType;
  label: string;
  inputs: Record<string, string>;
  onDataChange?: (nodeId: string, inputName: string, value: string) => void;
}

export interface CustomNode extends Node<CustomNodeData> {
  data: CustomNodeData;
}

export interface FlowExecutionStep {
  id: string;
  type: NodeType;
  label: string;
  inputs: Record<string, string>;
  position: { x: number; y: number };
}

export interface FlowValidation {
  isValid: boolean;
  errors: string[];
}

export interface FlowMetadata {
  name: string;
  createdAt: string;
  version: string;
  totalSteps: number;
}

export interface FlowData {
  metadata: FlowMetadata;
  validation: FlowValidation;
  executionOrder: FlowExecutionStep[];
  rawData: {
    nodes: Node<CustomNodeData>[];
    edges: Edge[];
  };
}