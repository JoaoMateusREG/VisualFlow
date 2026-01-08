import { Node, Edge } from 'reactflow';

export enum NodeType {
  LOGIN = 'login',
  CLICK_BUTTON = 'clickButton',
  EXTRACT_TABLE = 'extractTable',
  WAIT = 'wait',
  SLEEP = 'sleep',
  SPREADSHEET = 'spreadsheet',
  LOOP_FOR = 'loopFor',
  LOOP_WHILE = 'loopWhile',
  VARIABLE = 'variable',
  CONDITION = 'condition',
  SCHEDULE = 'schedule'
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
}

export interface NodeConfig {
  label: string;
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