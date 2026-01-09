import React, { useState, useCallback, useRef } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
  Connection,
  ReactFlowInstance,
  NodeTypes,
  DefaultEdgeOptions,
  Node,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';

import Sidebar from './components/Sidebar';
import Header from './components/Header';
import CustomNode from './components/CustomNode';
import ConfigPanel from './components/ConfigPanel';
import ExecutionPanel from './components/ExecutionPanel';
import WorkflowManager from './components/WorkflowManager';
import WorkflowNameDialog from './components/WorkflowNameDialog';
import { NodeType, CustomNodeData } from './types';
import { getNodeConfig } from './types/nodeTypes';
import { exportFlowAsJSON } from './utils/flowExecution';
import { useExecution } from './hooks/useExecution';

type CustomNodeType = Node<CustomNodeData>;

const nodeTypes: NodeTypes = {
  [NodeType.LOGIN]: CustomNode,
  [NodeType.OPEN_SITE]: CustomNode,
  [NodeType.CLICK_BUTTON]: CustomNode,
  [NodeType.EXTRACT_TABLE]: CustomNode,
  [NodeType.CAPTURE_TABLE]: CustomNode,
  [NodeType.WAIT]: CustomNode,
  [NodeType.SLEEP]: CustomNode,
  [NodeType.SPREADSHEET]: CustomNode,
  [NodeType.LOOP_FOR]: CustomNode,
  [NodeType.LOOP_WHILE]: CustomNode,
  [NodeType.VARIABLE]: CustomNode,
  [NodeType.CONDITION]: CustomNode,
  [NodeType.SCHEDULE]: CustomNode,
  [NodeType.EXECUTE_SCRIPT]: CustomNode,
  [NodeType.EXTRACT_TEXT]: CustomNode,
  [NodeType.TRANSFORM_COLUMN]: CustomNode,
  [NodeType.GROUP_DATA]: CustomNode,
  [NodeType.EXECUTE_PYTHON]: CustomNode,
};

const defaultEdgeOptions: DefaultEdgeOptions = {
  animated: true,
  style: { stroke: '#6b7280', strokeWidth: 2 },
  markerEnd: {
    type: MarkerType.ArrowClosed,
    color: '#6b7280',
  },
};

let nodeId = 0;
const getId = (): string => `node_${nodeId++}`;

const App: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState<CustomNodeData>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<CustomNodeType | null>(null);
  const [showExecutionPanel, setShowExecutionPanel] = useState(false);
  const [showWorkflowManager, setShowWorkflowManager] = useState(false);
  const [showNameDialog, setShowNameDialog] = useState(false);
  const [workflowName, setWorkflowName] = useState('Novo Workflow VisualFlow');
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  
  // Hook para gerenciar execuções remotas
  const execution = useExecution();

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const handleNodeDataChange = useCallback((nodeId: string, inputName: string, value: string) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          const updatedNode = {
            ...node,
            data: {
              ...node.data,
              inputs: {
                ...node.data.inputs,
                [inputName]: value,
              },
            },
          };
          
          // Atualizar o node selecionado se for o mesmo
          if (selectedNode && selectedNode.id === nodeId) {
            setSelectedNode(updatedNode);
          }
          
          return updatedNode;
        }
        return node;
      })
    );
  }, [setNodes, selectedNode]);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      // Check if a file is being dropped (workflow JSON import)
      const files = event.dataTransfer.files;
      if (files && files.length > 0) {
        const file = files[0];
        if (file.type === 'application/json' || file.name.endsWith('.json')) {
          const reader = new FileReader();
          reader.onload = (e) => {
            try {
              const result = e.target?.result as string;
              const flowData = JSON.parse(result);
              
              // Try to load from different workflow formats
              let nodesData = null;
              let edgesData = null;
              let name = 'Workflow Importado';
              
              // Format 1: Direct rawData (exported from app)
              if (flowData.rawData?.nodes && flowData.rawData?.edges) {
                nodesData = flowData.rawData.nodes;
                edgesData = flowData.rawData.edges;
                name = flowData.metadata?.name || name;
              }
              // Format 2: SavedWorkflow from backend
              else if (flowData.flow_data?.rawData?.nodes) {
                nodesData = flowData.flow_data.rawData.nodes;
                edgesData = flowData.flow_data.rawData.edges;
                name = flowData.metadata?.name || name;
              }
              // Format 3: Direct nodes/edges
              else if (flowData.nodes && flowData.edges) {
                nodesData = flowData.nodes;
                edgesData = flowData.edges;
              }
              
              if (nodesData && edgesData) {
                const restoredNodes: CustomNodeType[] = nodesData.map((node: CustomNodeType) => ({
                  ...node,
                  data: {
                    ...node.data,
                    onDataChange: handleNodeDataChange
                  }
                }));
                
                setNodes(restoredNodes);
                setEdges(edgesData);
                setWorkflowName(name);
                setSelectedNode(null);
                execution.clearExecution();
                alert(`Workflow "${name}" importado com sucesso!`);
              } else {
                alert('Arquivo de workflow inválido! Estrutura não reconhecida.');
              }
            } catch (error) {
              const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
              alert('Erro ao importar workflow: ' + errorMessage);
            }
          };
          reader.readAsText(file);
          return;
        }
      }

      // Handle node type drop from sidebar
      const type = event.dataTransfer.getData('application/reactflow') as NodeType;
      if (!type || !Object.values(NodeType).includes(type)) {
        return;
      }

      if (!reactFlowInstance) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const config = getNodeConfig(type);
      if (!config) return;

      const newNode: CustomNodeType = {
        id: getId(),
        type,
        position,
        data: {
          type,
          label: config.label,
          inputs: {},
          onDataChange: handleNodeDataChange,
        },
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [reactFlowInstance, setNodes, setEdges, handleNodeDataChange, execution]
  );


  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    const customNode = nodes.find(n => n.id === node.id);
    if (customNode) {
      setSelectedNode(customNode);
    }
  }, [nodes]);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  // Execução local (gerar código)
  const onExecuteFlow = useCallback(() => {
    const flowData = exportFlowAsJSON(nodes, edges, workflowName);
    
    console.group('🚀 Execução do Fluxo de Automação Selenium');
    console.log('📊 Dados Completos do Fluxo:', flowData);
    
    if (flowData.validation.isValid) {
      console.log('✅ Fluxo válido! Ordem de execução:');
      flowData.executionOrder.forEach((step, index) => {
        console.log(`${index + 1}. ${step.label}`, step);
      });
      
      // Gerar código Python/Selenium
      console.log('\n🐍 Código Python/Selenium gerado:');
      const pythonCode = generateSeleniumCode(flowData.executionOrder);
      console.log(pythonCode);
    } else {
      console.error('❌ Erros encontrados no fluxo:');
      flowData.validation.errors.forEach(error => console.error(`- ${error}`));
    }
    console.groupEnd();

    const message = flowData.validation.isValid 
      ? `Fluxo validado com ${flowData.executionOrder.length} passos! Código Selenium gerado no console.`
      : `Erros encontrados no fluxo! Verifique o console.`;
    
    alert(message);
  }, [nodes, edges, workflowName]);

  // Execução remota (backend)
  const onExecuteRemote = useCallback(async () => {
    const flowData = exportFlowAsJSON(nodes, edges, workflowName);
    
    if (!flowData.validation.isValid) {
      alert(`Fluxo inválido: ${flowData.validation.errors.join(', ')}`);
      return;
    }

    // Mostrar painel de execução
    setShowExecutionPanel(true);
    
    // Executar no backend
    await execution.executeFlow(flowData);
  }, [nodes, edges, execution, workflowName]);

  const generateSeleniumCode = (steps: any[]) => {
    let code = `import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

# Variáveis globais para armazenar dados
variables = {}
dataframes = {}

# Inicializar driver
driver = webdriver.Chrome()

try:
`;

    steps.forEach((step, index) => {
      code += `\n    # Passo ${index + 1}: ${step.label}\n`;
      const inputs = step.inputs;
      
      switch (step.type) {
        case 'login':
          code += `    driver.get("${inputs.url || 'URL'}")
    driver.maximize_window()
    
    username_field = WebDriverWait(driver, ${inputs.wait_time || 10}).until(
        EC.presence_of_element_located((By.${inputs.username_selector_type?.toUpperCase() || 'ID'}, "${inputs.username_selector || 'username'}"))
    )
    username_field.send_keys("${inputs.username_value || 'usuario'}")
    
    password_field = driver.find_element(By.${inputs.password_selector_type?.toUpperCase() || 'ID'}, "${inputs.password_selector || 'password'}")
    password_field.send_keys("${inputs.password_value || 'senha'}")
    
    login_button = driver.find_element(By.${inputs.login_button_selector_type?.toUpperCase() || 'ID'}, "${inputs.login_button_selector || 'login'}")
    login_button.click()
`;
          break;
          
        case 'clickButton':
          code += `    element = WebDriverWait(driver, ${inputs.wait_timeout || 10}).until(
        EC.${inputs.wait_condition || 'element_to_be_clickable'}((By.${inputs.selector_type?.toUpperCase() || 'ID'}, "${inputs.selector_value || 'button'}"))
    )
    ${inputs.scroll_to_element === 'true' ? 'driver.execute_script("arguments[0].scrollIntoView();", element)\n    ' : ''}${inputs.double_click === 'true' ? 'ActionChains(driver).double_click(element).perform()' : 'element.click()'}
    ${inputs.pause_after ? `time.sleep(${inputs.pause_after})` : ''}
`;
          break;
          
        case 'extractTable':
          code += `    element = WebDriverWait(driver, ${inputs.wait_timeout || 10}).until(
        EC.${inputs.wait_condition || 'presence_of_element_located'}((By.${inputs.selector_type?.toUpperCase() || 'ID'}, "${inputs.selector_value || 'input'}"))
    )
    ${inputs.clear_before === 'true' ? 'element.clear()\n    ' : ''}element.send_keys("${inputs.text_value || 'texto'}")
    ${inputs.press_enter === 'true' ? 'element.send_keys(Keys.RETURN)\n    ' : ''}${inputs.pause_after ? `time.sleep(${inputs.pause_after})` : ''}
`;
          break;
          
        case 'wait':
          if (inputs.wait_type === 'time') {
            code += `    time.sleep(${inputs.duration || 5})
`;
          } else {
            code += `    WebDriverWait(driver, ${inputs.timeout || 30}).until(
        EC.${inputs.wait_condition || 'presence_of_element_located'}((By.${inputs.selector_type?.toUpperCase() || 'ID'}, "${inputs.selector_value || 'element'}"))
    )
`;
          }
          break;
          
        case 'sleep':
          const sleepDuration = inputs.duration || '2';
          const sleepDescription = inputs.description ? ` # ${inputs.description}` : '';
          code += `    time.sleep(${sleepDuration})${sleepDescription}
`;
          break;
          
        case 'spreadsheet':
          const operation = inputs.operation || 'read';
          const filePath = inputs.file_path || 'dados.xlsx';
          const sheetName = inputs.sheet_name || 'Sheet1';
          const variableName = inputs.variable_name || 'df';
          
          switch (operation) {
            case 'read':
              if (filePath.endsWith('.csv')) {
                code += `    # Ler arquivo CSV
    ${variableName} = pd.read_csv("${filePath}")
    dataframes["${variableName}"] = ${variableName}
    print(f"Planilha carregada: {len(${variableName})} linhas")
`;
              } else {
                code += `    # Ler arquivo Excel
    ${variableName} = pd.read_excel("${filePath}", sheet_name="${sheetName}")
    dataframes["${variableName}"] = ${variableName}
    print(f"Planilha carregada: {len(${variableName})} linhas")
`;
              }
              break;
            case 'create':
              const columns = inputs.columns ? inputs.columns.split(',').map((c: string) => c.trim()) : ['Coluna1'];
              code += `    # Criar nova planilha
    ${variableName} = pd.DataFrame(columns=${JSON.stringify(columns)})
    dataframes["${variableName}"] = ${variableName}
`;
              break;
            case 'save':
              if (filePath.endsWith('.csv')) {
                code += `    # Salvar como CSV
    ${variableName}.to_csv("${filePath}", index=False)
    print(f"Planilha salva: ${filePath}")
`;
              } else {
                code += `    # Salvar como Excel
    ${variableName}.to_excel("${filePath}", sheet_name="${sheetName}", index=False)
    print(f"Planilha salva: ${filePath}")
`;
              }
              break;
          }
          break;
          
        case 'loopFor':
          const loopType = inputs.loop_type || 'range';
          const dfVariable = inputs.dataframe_variable || 'df';
          const rowVariable = inputs.row_variable || 'row';
          
          switch (loopType) {
            case 'dataframe_rows':
              code += `    # Loop pelas linhas da planilha
    for index, ${rowVariable} in ${dfVariable}.iterrows():
        variables["${rowVariable}"] = ${rowVariable}
        variables["row_index"] = index
        print(f"Processando linha {index + 1}")
        
        # === INÍCIO DO LOOP ===
`;
              break;
            case 'range':
              const startValue = inputs.start_value || '0';
              const endValue = inputs.end_value || '10';
              const stepValue = inputs.step_value || '1';
              code += `    # Loop numérico
    for i in range(${startValue}, ${endValue}, ${stepValue}):
        variables["i"] = i
        print(f"Iteração: {i}")
        
        # === INÍCIO DO LOOP ===
`;
              break;
            case 'list':
              const listValues = inputs.list_values ? inputs.list_values.split(',').map((v: string) => `"${v.trim()}"`) : ['"valor1"'];
              code += `    # Loop por lista de valores
    for item in ${JSON.stringify(listValues).replace(/"/g, '')}:
        variables["item"] = item
        print(f"Processando: {item}")
        
        # === INÍCIO DO LOOP ===
`;
              break;
          }
          break;
          
        case 'variable':
          const varOperation = inputs.operation || 'set';
          const varName = inputs.variable_name || 'variavel';
          
          switch (varOperation) {
            case 'set':
              const varValue = inputs.variable_value || '';
              code += `    # Definir variável
    variables["${varName}"] = "${varValue}"
    ${varName} = variables["${varName}"]
`;
              break;
            case 'get_cell':
              const rowVar = inputs.row_variable || 'row';
              const columnName = inputs.column_name || 'Coluna1';
              code += `    # Obter valor da célula
    ${varName} = variables["${rowVar}"]["${columnName}"]
    variables["${varName}"] = ${varName}
    print(f"${varName} = {${varName}}")
`;
              break;
            case 'increment':
              const incrementValue = inputs.increment_value || '1';
              code += `    # Incrementar variável
    variables["${varName}"] = variables.get("${varName}", 0) + ${incrementValue}
    ${varName} = variables["${varName}"]
`;
              break;
          }
          break;
      }
    });

    code += `
finally:
    driver.quit()
`;

    return code;
  };

  const onSaveFlow = useCallback(() => {
    if (!workflowName || workflowName === 'Novo Workflow VisualFlow') {
      setShowNameDialog(true);
      return;
    }
    
    const flowData = exportFlowAsJSON(nodes, edges, workflowName);
    const dataStr = JSON.stringify(flowData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    // Criar nome do arquivo com nome do workflow e data
    const sanitizedName = workflowName.replace(/[<>:"/\\|?*]/g, '_');
    const dateStr = new Date().toISOString().split('T')[0];
    const timeStr = new Date().toTimeString().split(' ')[0].replace(/:/g, '-');
    const exportFileDefaultName = `${sanitizedName}_${dateStr}_${timeStr}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }, [nodes, edges, workflowName]);

  const handleWorkflowNameSave = useCallback((name: string) => {
    setWorkflowName(name);
    // Após definir o nome, salvar automaticamente
    setTimeout(() => {
      const flowData = exportFlowAsJSON(nodes, edges, name);
      const dataStr = JSON.stringify(flowData, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const sanitizedName = name.replace(/[<>:"/\\|?*]/g, '_');
      const dateStr = new Date().toISOString().split('T')[0];
      const timeStr = new Date().toTimeString().split(' ')[0].replace(/:/g, '-');
      const exportFileDefaultName = `${sanitizedName}_${dateStr}_${timeStr}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    }, 100);
  }, [nodes, edges]);

  const onLoadFlow = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const result = e.target?.result as string;
            const flowData = JSON.parse(result);
            if (flowData.rawData && flowData.rawData.nodes && flowData.rawData.edges) {
              const restoredNodes: CustomNodeType[] = flowData.rawData.nodes.map((node: CustomNodeType) => ({
                ...node,
                data: {
                  ...node.data,
                  onDataChange: handleNodeDataChange
                }
              }));
              
              setNodes(restoredNodes);
              setEdges(flowData.rawData.edges);
              setSelectedNode(null);
              execution.clearExecution();
              alert('Fluxo carregado com sucesso!');
            } else {
              alert('Arquivo de fluxo inválido!');
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
            alert('Erro ao carregar o arquivo: ' + errorMessage);
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  }, [setNodes, setEdges, handleNodeDataChange, execution]);

  const onClearFlow = useCallback(() => {
    if (window.confirm('Tem certeza que deseja limpar todo o fluxo?')) {
      setNodes([]);
      setEdges([]);
      setSelectedNode(null);
      execution.clearExecution();
      nodeId = 0;
    }
  }, [setNodes, setEdges, execution]);

  const onToggleExecutionPanel = useCallback(() => {
    setShowExecutionPanel(prev => !prev);
  }, []);

  const onOpenWorkflowManager = useCallback(() => {
    setShowWorkflowManager(true);
  }, []);

  const onLoadWorkflowFromManager = useCallback((flowData: any) => {
    if (flowData.rawData && flowData.rawData.nodes && flowData.rawData.edges) {
      const restoredNodes: CustomNodeType[] = flowData.rawData.nodes.map((node: CustomNodeType) => ({
        ...node,
        data: {
          ...node.data,
          onDataChange: handleNodeDataChange
        }
      }));
      
      setNodes(restoredNodes);
      setEdges(flowData.rawData.edges);
      setSelectedNode(null);
      execution.clearExecution();
      
      // Definir nome do workflow
      if (flowData.metadata && flowData.metadata.name) {
        setWorkflowName(flowData.metadata.name);
      }
    } else if (flowData.nodes && flowData.edges) {
      // Formato direto do FlowData
      const restoredNodes: CustomNodeType[] = flowData.nodes.map((node: CustomNodeType) => ({
        ...node,
        data: {
          ...node.data,
          onDataChange: handleNodeDataChange
        }
      }));
      
      setNodes(restoredNodes);
      setEdges(flowData.edges);
      setSelectedNode(null);
      execution.clearExecution();
      
      // Definir nome do workflow
      if (flowData.metadata && flowData.metadata.name) {
        setWorkflowName(flowData.metadata.name);
      }
    }
  }, [setNodes, setEdges, handleNodeDataChange, execution]);

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      <Header 
        onExecuteFlow={onExecuteFlow}
        onExecuteRemote={onExecuteRemote}
        onSaveFlow={onSaveFlow}
        onLoadFlow={onLoadFlow}
        onClearFlow={onClearFlow}
        onToggleExecutionPanel={onToggleExecutionPanel}
        onOpenWorkflowManager={onOpenWorkflowManager}
        isExecuting={execution.isExecuting}
        showExecutionPanel={showExecutionPanel}
        workflowName={workflowName}
      />
      
      <div className="flex-1 flex">
        <Sidebar />
        
        <div className="flex-1" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            defaultEdgeOptions={defaultEdgeOptions}
            fitView
            className="bg-gray-900"
            deleteKeyCode={['Backspace', 'Delete']}
          >
            <Controls 
              className="bg-gray-800 border border-gray-600"
            />
            <Background 
              color="#4b5563" 
              gap={20} 
              size={1}
              variant={BackgroundVariant.Dots}
            />
          </ReactFlow>
        </div>

        <ConfigPanel 
          selectedNode={selectedNode}
          onClose={() => setSelectedNode(null)}
          onNodeUpdate={handleNodeDataChange}
        />
      </div>

      <ExecutionPanel 
        execution={execution}
        isVisible={showExecutionPanel}
        onClose={() => setShowExecutionPanel(false)}
      />

      <WorkflowManager
        isOpen={showWorkflowManager}
        onClose={() => setShowWorkflowManager(false)}
        currentFlowData={exportFlowAsJSON(nodes, edges, workflowName)}
        onLoadWorkflow={onLoadWorkflowFromManager}
      />

      <WorkflowNameDialog
        isOpen={showNameDialog}
        onClose={() => setShowNameDialog(false)}
        onSave={handleWorkflowNameSave}
        currentName={workflowName}
        title="Definir Nome do Workflow"
      />
    </div>
  );
};

export default App;