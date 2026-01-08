import { Edge, Node } from 'reactflow';
import { CustomNodeData, FlowExecutionStep, FlowData, FlowValidation } from '../types';

export const generateExecutionOrder = (nodes: Node<CustomNodeData>[], edges: Edge[]): FlowExecutionStep[] => {
  // Criar um mapa de adjacência para representar o grafo
  const adjacencyMap = new Map<string, string[]>();
  const inDegree = new Map<string, number>();
  
  // Inicializar todos os nodes
  nodes.forEach(node => {
    adjacencyMap.set(node.id, []);
    inDegree.set(node.id, 0);
  });
  
  // Construir o grafo baseado nas edges
  edges.forEach(edge => {
    const sourceNeighbors = adjacencyMap.get(edge.source) || [];
    sourceNeighbors.push(edge.target);
    adjacencyMap.set(edge.source, sourceNeighbors);
    
    const currentInDegree = inDegree.get(edge.target) || 0;
    inDegree.set(edge.target, currentInDegree + 1);
  });
  
  // Algoritmo de ordenação topológica (Kahn's algorithm)
  const queue: string[] = [];
  const executionOrder: FlowExecutionStep[] = [];
  
  // Encontrar todos os nodes sem dependências (grau de entrada = 0)
  inDegree.forEach((degree, nodeId) => {
    if (degree === 0) {
      queue.push(nodeId);
    }
  });
  
  // Processar a fila
  while (queue.length > 0) {
    const currentNodeId = queue.shift()!;
    const currentNode = nodes.find(n => n.id === currentNodeId);
    
    if (currentNode) {
      executionOrder.push({
        id: currentNodeId,
        type: currentNode.data.type,
        label: currentNode.data.label || currentNode.data.type,
        inputs: currentNode.data.inputs || {},
        position: currentNode.position
      });
    }
    
    // Reduzir o grau de entrada dos nodes adjacentes
    const neighbors = adjacencyMap.get(currentNodeId) || [];
    neighbors.forEach(neighborId => {
      const currentInDegree = inDegree.get(neighborId) || 0;
      inDegree.set(neighborId, currentInDegree - 1);
      
      // Se o grau de entrada chegou a 0, adicionar à fila
      if (inDegree.get(neighborId) === 0) {
        queue.push(neighborId);
      }
    });
  }
  
  // Verificar se há ciclos
  if (executionOrder.length !== nodes.length) {
    throw new Error('Ciclo detectado no fluxo! Verifique as conexões entre os blocos.');
  }
  
  return executionOrder;
};

export const validateFlow = (nodes: Node<CustomNodeData>[], edges: Edge[]): FlowValidation => {
  const errors: string[] = [];
  
  // Verificar se há pelo menos um node
  if (nodes.length === 0) {
    errors.push('O fluxo deve conter pelo menos um bloco.');
    return { isValid: false, errors };
  }
  
  // Verificar se todos os nodes têm configurações necessárias
  nodes.forEach(node => {
    const config = node.data;
    if (!config.inputs || Object.keys(config.inputs).length === 0) {
      errors.push(`O bloco "${config.label || config.type}" não está configurado.`);
    }
  });
  
  // Verificar se há nodes órfãos (exceto o primeiro)
  const connectedNodes = new Set<string>();
  edges.forEach(edge => {
    connectedNodes.add(edge.source);
    connectedNodes.add(edge.target);
  });
  
  const orphanNodes = nodes.filter(node => 
    !connectedNodes.has(node.id) && nodes.length > 1
  );
  
  if (orphanNodes.length > 0) {
    errors.push(`Existem blocos desconectados: ${orphanNodes.map(n => n.data.label || n.data.type).join(', ')}`);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const exportFlowAsJSON = (nodes: Node<CustomNodeData>[], edges: Edge[], workflowName?: string): FlowData => {
  try {
    const executionOrder = generateExecutionOrder(nodes, edges);
    const validation = validateFlow(nodes, edges);
    
    const flowData: FlowData = {
      metadata: {
        name: workflowName || 'Fluxo VisualFlow',
        createdAt: new Date().toISOString(),
        version: '1.0.0',
        totalSteps: executionOrder.length
      },
      validation,
      executionOrder,
      rawData: {
        nodes: nodes.map(node => ({
          ...node,
          data: {
            ...node.data
          }
        })),
        edges: edges.map(edge => ({
          ...edge
        }))
      }
    };
    
    return flowData;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
    
    return {
      metadata: {
        name: workflowName || 'Fluxo de Automação',
        createdAt: new Date().toISOString(),
        version: '1.0.0',
        totalSteps: 0
      },
      validation: {
        isValid: false,
        errors: [errorMessage]
      },
      executionOrder: [],
      rawData: { nodes, edges }
    };
  }
};