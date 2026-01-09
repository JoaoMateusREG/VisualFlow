import { Edge, Node } from 'reactflow';
import { CustomNodeData, FlowExecutionStep, FlowData, FlowValidation, NodeType } from '../types';

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
      // Ignorar validação simples, pois alguns blocos podem não ter inputs obrigatórios
      // errors.push(`O bloco "${config.label || config.type}" não está configurado.`);
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

export const generateSeleniumCode = (steps: FlowExecutionStep[]): string => {
  let code = `import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
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
      case NodeType.LOGIN:
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
        
      case NodeType.CLICK_BUTTON:
        code += `    element = WebDriverWait(driver, ${inputs.wait_timeout || 10}).until(
        EC.${inputs.wait_condition || 'element_to_be_clickable'}((By.${inputs.selector_type?.toUpperCase() || 'ID'}, "${inputs.selector_value || 'button'}"))
    )
    ${inputs.scroll_to_element === 'true' ? 'driver.execute_script("arguments[0].scrollIntoView();", element)\n    ' : ''}${inputs.double_click === 'true' ? 'ActionChains(driver).double_click(element).perform()' : 'element.click()'}
    ${inputs.pause_after ? `time.sleep(${inputs.pause_after})` : ''}
`;
        break;
        
      case NodeType.EXTRACT_TABLE: // Note: Legacy name, acts as InputText
        code += `    element = WebDriverWait(driver, ${inputs.wait_timeout || 10}).until(
        EC.${inputs.wait_condition || 'presence_of_element_located'}((By.${inputs.selector_type?.toUpperCase() || 'ID'}, "${inputs.selector_value || 'input'}"))
    )
    ${inputs.clear_before === 'true' ? 'element.clear()\n    ' : ''}element.send_keys("${inputs.text_value || 'texto'}")
    ${inputs.press_enter === 'true' ? 'element.send_keys(Keys.RETURN)\n    ' : ''}${inputs.pause_after ? `time.sleep(${inputs.pause_after})` : ''}
`;
        break;
        
      case NodeType.WAIT:
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
        
      case NodeType.SLEEP:
        const sleepDuration = inputs.duration || '2';
        const sleepDescription = inputs.description ? ` # ${inputs.description}` : '';
        code += `    time.sleep(${sleepDuration})${sleepDescription}
`;
        break;
        
      case NodeType.SPREADSHEET:
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
        
      case NodeType.LOOP_FOR:
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
        
      case NodeType.VARIABLE:
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
        
      case NodeType.EXTRACT_TEXT:
        code += `    # Extrair Texto
    element = WebDriverWait(driver, ${inputs.wait_timeout || 10}).until(
        EC.presence_of_element_located((By.${inputs.selector_type?.toUpperCase() || 'XPATH'}, "${inputs.selector_value || '//div'}"))
    )
    text_content = element.text
    extracted_value = text_content
    
    # Regex no elemento
    if "${inputs.regex_pattern}":
        match = re.search(r"${inputs.regex_pattern}", text_content)
        if match:
            extracted_value = match.group(1) if match.groups() else match.group(0)
    
    # Fallback no Body
    if ${inputs.fallback_to_body === 'true' ? 'True' : 'False'} and not extracted_value:
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        fallback_pattern = r"${inputs.fallback_regex_pattern || inputs.regex_pattern}"
        match = re.search(fallback_pattern, body_text)
        if match:
            extracted_value = match.group(1) if match.groups() else match.group(0)
            
    variables["${inputs.variable_name || 'texto_extraido'}"] = extracted_value
    print(f"Texto extraído: {extracted_value}")
`;
        break;
        
      case NodeType.EXECUTE_PYTHON:
        code += `    # Executar Python Customizado
    # Variáveis disponíveis: driver, variables, dataframes, pd, time, re
    code = """
${inputs.code || '# Seu código aqui'}
"""
    exec(code)
`;
        break;
        
      case NodeType.CLOSE_BROWSER:
        code += `    # Fechar navegador
    if driver:
        driver.quit()
        driver = None
        print("Navegador fechado via bloco")
`;
        break;
    }
  });

  code += `
finally:
    if 'driver' in locals() and driver:
        driver.quit()
`;

  return code;
};