import { Node, Edge } from 'reactflow';

export enum NodeType {
  LOGIN = 'login',
  OPEN_SITE = 'openSite',
  CLICK_BUTTON = 'clickButton',
  EXTRACT_TABLE = 'extractTable',
  CAPTURE_TABLE = 'captureTable',
  WAIT = 'wait',
  SLEEP = 'sleep',
  SPREADSHEET = 'spreadsheet',
  LOOP_FOR = 'loopFor',
  LOOP_WHILE = 'loopWhile',
  VARIABLE = 'variable',
  CONDITION = 'condition',
  SCHEDULE = 'schedule',
  EXECUTE_SCRIPT = 'executeScript',
  EXTRACT_TEXT = 'extractText',
  TRANSFORM_COLUMN = 'transformColumn',
  GROUP_DATA = 'groupData',
  EXECUTE_PYTHON = 'executePython',
  CLOSE_BROWSER = 'closeBrowser'
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