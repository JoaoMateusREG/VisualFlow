import React, { useCallback } from 'react';
import { X, Settings, Code, Info, HelpCircle } from 'lucide-react';
import { CustomNode, NodeInput } from '../types';
import { getNodeConfig } from '../types/nodeTypes';

interface ConfigPanelProps {
  selectedNode: CustomNode | null;
  onClose: () => void;
  onNodeUpdate: (nodeId: string, inputName: string, value: string) => void;
}

/**
 * Painel de Configuração de Nó
 * Exibe o formulário dinâmico para editar as propriedades do nó selecionado
 * Também gera e mostra o código Selenium correspondente em tempo real
 */
const ConfigPanel: React.FC<ConfigPanelProps> = ({ 
  selectedNode, 
  onClose, 
  onNodeUpdate 
}) => {
  const handleInputChange = useCallback((inputName: string, value: string) => {
    if (selectedNode) {
      onNodeUpdate(selectedNode.id, inputName, value);
    }
  }, [selectedNode, onNodeUpdate]);

  if (!selectedNode) {
    return (
      <div className="w-80 bg-gray-800 border-l border-gray-700 p-4 flex items-center justify-center">
        <div className="text-center text-gray-400">
          <Settings size={48} className="mx-auto mb-3 opacity-50" />
          <p className="text-sm">Selecione um bloco para configurar</p>
        </div>
      </div>
    );
  }

  const config = getNodeConfig(selectedNode.data.type);
  
  if (!config) {
    return (
      <div className="w-80 bg-gray-800 border-l border-gray-700 p-4">
        <div className="text-center text-red-400">
          <p className="text-sm">Configuração não encontrada</p>
        </div>
      </div>
    );
  }

  const renderInput = (input: NodeInput) => {
    const currentValue = selectedNode.data.inputs?.[input.name] || '';

    switch (input.type) {
      case 'select':
        return (
          <select
            value={currentValue}
            onChange={(e) => handleInputChange(input.name, e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="">Selecione...</option>
            {input.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'checkbox':
        return (
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={currentValue === 'true'}
              onChange={(e) => handleInputChange(input.name, e.target.checked.toString())}
              className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Ativado</span>
          </label>
        );

      case 'password':
        return (
          <input
            type="password"
            placeholder={input.placeholder}
            value={currentValue}
            onChange={(e) => handleInputChange(input.name, e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none"
          />
        );

      case 'number':
        return (
          <input
            type="number"
            placeholder={input.placeholder}
            value={currentValue}
            onChange={(e) => handleInputChange(input.name, e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none"
          />
        );

      default: // text
        return (
          <textarea
            placeholder={input.placeholder}
            value={currentValue}
            onChange={(e) => handleInputChange(input.name, e.target.value)}
            rows={input.name.includes('selector') ? 2 : 1}
            className="w-full h-40 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm placeholder-gray-400 focus:border-blue-500 focus:outline-none resize-none"
          />
        );
    }
  };

  const getSeleniumCode = () => {
    const inputs = selectedNode.data.inputs || {};
    
    switch (selectedNode.data.type) {
      case 'login':
        return `# Navegação e Login
driver.get("${inputs.url || 'URL'}")
driver.maximize_window()

# Campo usuário
username_field = WebDriverWait(driver, ${inputs.wait_time || 10}).until(
    EC.presence_of_element_located((By.${inputs.username_selector_type?.toUpperCase() || 'ID'}, "${inputs.username_selector || 'username'}"))
)
username_field.send_keys("${inputs.username_value || 'usuario'}")

# Campo senha
password_field = driver.find_element(By.${inputs.password_selector_type?.toUpperCase() || 'ID'}, "${inputs.password_selector || 'password'}")
password_field.send_keys("${inputs.password_value || 'senha'}")

# Botão login
login_button = driver.find_element(By.${inputs.login_button_selector_type?.toUpperCase() || 'ID'}, "${inputs.login_button_selector || 'login'}")
login_button.click()`;

      case 'clickButton':
        return `# Clicar elemento
element = WebDriverWait(driver, ${inputs.wait_timeout || 10}).until(
    EC.${inputs.wait_condition || 'element_to_be_clickable'}((By.${inputs.selector_type?.toUpperCase() || 'ID'}, "${inputs.selector_value || 'button'}"))
)
${inputs.scroll_to_element === 'true' ? 'driver.execute_script("arguments[0].scrollIntoView();", element)' : ''}
${inputs.double_click === 'true' ? 'ActionChains(driver).double_click(element).perform()' : 'element.click()'}
${inputs.pause_after ? `time.sleep(${inputs.pause_after})` : ''}`;

      case 'extractTable':
        return `# Inserir texto
element = WebDriverWait(driver, ${inputs.wait_timeout || 10}).until(
    EC.${inputs.wait_condition || 'presence_of_element_located'}((By.${inputs.selector_type?.toUpperCase() || 'ID'}, "${inputs.selector_value || 'input'}"))
)
${inputs.clear_before === 'true' ? 'element.clear()' : ''}
element.send_keys("${inputs.text_value || 'texto'}")
${inputs.press_enter === 'true' ? 'element.send_keys(Keys.RETURN)' : ''}
${inputs.pause_after ? `time.sleep(${inputs.pause_after})` : ''}`;

      case 'captureTable':
        return `# Capturar tabela HTML
table_element = WebDriverWait(driver, ${inputs.wait_timeout || 10}).until(
    EC.${inputs.wait_condition || 'presence_of_element_located'}((By.${inputs.selector_type?.toUpperCase() || 'XPATH'}, "${inputs.selector_value || '//table'}"))
)

# Extrair linhas e células
rows = table_element.find_elements(By.TAG_NAME, 'tr')
table_data = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, 'td')
    if not cells:
        cells = row.find_elements(By.TAG_NAME, 'th')
    row_data = [cell.text.strip() for cell in cells]
    ${inputs.skip_empty_rows === 'true' ? 'if any(row_data): table_data.append(row_data)' : 'table_data.append(row_data)'}

# Criar DataFrame
${inputs.variable_name || 'df_table'} = pd.DataFrame(table_data)
${inputs.include_headers === 'true' ? `\n# Usar primeira linha como cabeçalho\n${inputs.variable_name || 'df_table'}.columns = ${inputs.variable_name || 'df_table'}.iloc[0]\n${inputs.variable_name || 'df_table'} = ${inputs.variable_name || 'df_table'}[1:].reset_index(drop=True)` : ''}
print(f"Tabela capturada: {len(${inputs.variable_name || 'df_table'})} linhas x {len(${inputs.variable_name || 'df_table'}.columns)} colunas")`;

      case 'wait':
        if (inputs.wait_type === 'time') {
          return `# Espera por tempo fixo
time.sleep(${inputs.duration || 5})`;
        } else {
          return `# Aguardar elemento
element = WebDriverWait(driver, ${inputs.timeout || 30}).until(
    EC.${inputs.wait_condition || 'presence_of_element_located'}((By.${inputs.selector_type?.toUpperCase() || 'ID'}, "${inputs.selector_value || 'element'}"))
)`;
        }

      case 'sleep':
        const sleepDuration = inputs.duration || '2';
        const sleepDescription = inputs.description ? ` # ${inputs.description}` : '';
        return `# Pausa (Sleep)${sleepDescription}
time.sleep(${sleepDuration})`;

      case 'spreadsheet':
        const operation = inputs.operation || 'read';
        const filePath = inputs.file_path || 'dados.xlsx';
        const variableName = inputs.variable_name || 'df';
        
        switch (operation) {
          case 'read':
            return `# Ler planilha
${variableName} = pd.read_excel("${filePath}")
print(f"Planilha carregada: {len(${variableName})} linhas")`;
          case 'create':
            const columns = inputs.columns || 'Coluna1';
            return `# Criar nova planilha
${variableName} = pd.DataFrame(columns=[${columns.split(',').map(c => `"${c.trim()}"`).join(', ')}])`;
          case 'save':
            return `# Salvar planilha
${variableName}.to_excel("${filePath}", index=False)`;
          default:
            return `# Operação de planilha: ${operation}`;
        }

      case 'loopFor':
        const loopType = inputs.loop_type || 'range';
        if (loopType === 'dataframe_rows') {
          const dfVariable = inputs.dataframe_variable || 'df';
          const rowVariable = inputs.row_variable || 'row';
          return `# Loop pelas linhas da planilha
for index, ${rowVariable} in ${dfVariable}.iterrows():
    # Processar linha atual`;
        } else if (loopType === 'range') {
          const start = inputs.start_value || '0';
          const end = inputs.end_value || '10';
          return `# Loop numérico
for i in range(${start}, ${end}):
    # Processar iteração`;
        }
        return `# Loop for configurado`;

      case 'variable':
        const varOperation = inputs.operation || 'set';
        const varName = inputs.variable_name || 'variavel';
        
        switch (varOperation) {
          case 'set':
            const varValue = inputs.variable_value || '';
            return `# Definir variável
${varName} = "${varValue}"`;
          case 'get_cell':
            const columnName = inputs.column_name || 'Coluna1';
            const rowVar = inputs.row_variable || 'row';
            return `# Obter valor da célula
${varName} = ${rowVar}["${columnName}"]`;
          default:
            return `# Operação de variável: ${varOperation}`;
        }

      case 'executeScript':
        return `# Executar JavaScript
script = """
${inputs.script || 'return document.title;'}
"""
result = driver.execute_script(script)
${inputs.variable_name ? `variables["${inputs.variable_name}"] = result\nprint(f"Script executado. Resultado: {result}")` : 'print("Script executado")'}`;

      case 'extractText':
        return `# Extrair Texto com Regex
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
print(f"Texto extraído: {extracted_value}")`;

      case 'transformColumn':
        return `# Transformar Coluna
df = dataframes["${inputs.dataframe_variable || 'df'}"]
col = "${inputs.column_name || 'coluna'}"
new_col = "${inputs.new_column_name || inputs.column_name || 'coluna'}"

if "${inputs.transformation_type}" == "first_letter_upper":
    df[new_col] = df[col].astype(str).str.title()
elif "${inputs.transformation_type}" == "parse_list":
    # Exemplo: converte string "['a','b']" para lista real
    import ast
    df[new_col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
elif "${inputs.transformation_type}" == "limit_list":
    limit = ${inputs.limit || 4}
    df[new_col] = df[col].apply(lambda x: x[:limit] if isinstance(x, list) else x)
elif "${inputs.transformation_type}" == "to_string":
    df[new_col] = df[col].astype(str)

dataframes["${inputs.dataframe_variable || 'df'}"] = df`;

      case 'groupData':
        return `# Agrupar Dados
df = dataframes["${inputs.dataframe_variable || 'df'}"]
grouped = df.groupby("${inputs.group_by_column || 'coluna'}")
# Aplicar agregações (exemplo simplificado)
result = grouped.agg({
    # Mapear agregações do input...
})
variables["${inputs.output_variable || 'df_agrupado'}"] = result`;

      case 'executePython':
        return `# Executar Python Customizado
# Variáveis disponíveis: driver, variables, dataframes, pd, time, re
code = """
${inputs.code || '# Seu código aqui'}
"""
exec(code)`;

      case 'closeBrowser':
        return `# Fechar Navegador
if driver:
    driver.quit()
    print("Navegador encerrado")`;

      default:
        return '# Código será gerado baseado na configuração';
    }
  };

  return (
    <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${config.color.replace('bg-', 'bg-')}`}></div>
            <h3 className="font-semibold text-white">{config.label}</h3>
            {config.description && (
              <div className="group relative">
                <HelpCircle size={16} className="text-gray-400 cursor-help hover:text-white" />
                <div className="absolute z-50 right-0 mt-2 w-64 p-2 bg-gray-900 border border-gray-600 rounded shadow-lg text-xs text-gray-200 hidden group-hover:block whitespace-normal">
                  {config.description}
                </div>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-1">ID: {selectedNode.id}</p>
      </div>

      {/* Configurações */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        <div className="space-y-4 pb-20"> {/* pb-20 gives space for last items tooltip */}
          {config.inputs.map((input) => (
            <div key={input.name} className="space-y-2 relative hover:z-50">
              <div className="flex items-center space-x-2">
                <label className="block text-sm font-medium text-gray-300">
                  {input.label}
                  {input.required && <span className="text-red-500 ml-1" title="Obrigatório">*</span>}
                </label>
                {input.helpText && (
                  <div className="group">
                    <HelpCircle size={14} className="text-gray-500 cursor-help hover:text-blue-400" />
                    <div className="absolute z-50 right-0 top-7 w-56 p-2 bg-gray-900 border border-gray-600 rounded shadow-xl text-xs text-gray-200 hidden group-hover:block whitespace-normal">
                       {/* Positioned relative to the parent input container (div.relative), not the icon wrapper */}
                      {input.helpText}
                    </div>
                  </div>
                )}
              </div>
              {renderInput(input)}
              {input.placeholder && (
                <p className="text-xs text-gray-500">
                  Ex: {input.placeholder}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Código Selenium Gerado */}
        <div className="mt-6 pt-4 border-t border-gray-700">
          <div className="flex items-center space-x-2 mb-3">
            <Code size={16} className="text-blue-400" />
            <h4 className="text-sm font-medium text-white">Código Selenium</h4>
          </div>
          <div className="bg-gray-900 rounded-lg p-3 text-xs font-mono">
            <pre className="text-green-400 whitespace-pre-wrap overflow-x-auto">
              {getSeleniumCode()}
            </pre>
          </div>
        </div>

        {/* Dicas */}
        <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700/30 rounded-lg">
          <div className="flex items-start space-x-2">
            <Info size={14} className="text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-blue-300">
              <p className="font-medium mb-1">Dicas:</p>
              <ul className="space-y-1 text-blue-200">
                <li>• Use XPath para elementos complexos</li>
                <li>• ID é o seletor mais rápido</li>
                <li>• Sempre configure timeouts adequados</li>
                <li>• Teste seletores no DevTools do navegador</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfigPanel;