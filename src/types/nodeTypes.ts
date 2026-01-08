import { NodeType, NodeConfig } from './index';

export const NODE_TYPES = NodeType;

export const SELENIUM_SELECTORS = [
  { value: 'id', label: 'ID' },
  { value: 'name', label: 'Name' },
  { value: 'class_name', label: 'Class Name' },
  { value: 'tag_name', label: 'Tag Name' },
  { value: 'xpath', label: 'XPath' },
  { value: 'css_selector', label: 'CSS Selector' },
  { value: 'link_text', label: 'Link Text' },
  { value: 'partial_link_text', label: 'Partial Link Text' }
];

export const WAIT_CONDITIONS = [
  { value: 'presence_of_element_located', label: 'Elemento Presente' },
  { value: 'visibility_of_element_located', label: 'Elemento Visível' },
  { value: 'element_to_be_clickable', label: 'Elemento Clicável' },
  { value: 'invisibility_of_element_located', label: 'Elemento Invisível' },
  { value: 'text_to_be_present_in_element', label: 'Texto Presente no Elemento' },
  { value: 'element_to_be_selected', label: 'Elemento Selecionado' }
];

export const getNodeConfig = (type: NodeType): NodeConfig | null => {
  const configs: Record<NodeType, NodeConfig> = {
    [NodeType.LOGIN]: {
      label: 'Navegação/Login',
      icon: 'LogIn',
      color: 'bg-blue-600',
      inputs: [
        { name: 'url', label: 'URL', type: 'text', placeholder: 'https://exemplo.com' },
        { name: 'username_selector_type', label: 'Tipo Seletor Usuário', type: 'select', placeholder: '', options: SELENIUM_SELECTORS },
        { name: 'username_selector', label: 'Seletor do Campo Usuário', type: 'text', placeholder: 'usuario, #login, //input[@name="user"]' },
        { name: 'username_value', label: 'Valor do Usuário', type: 'text', placeholder: 'seu_usuario' },
        { name: 'password_selector_type', label: 'Tipo Seletor Senha', type: 'select', placeholder: '', options: SELENIUM_SELECTORS },
        { name: 'password_selector', label: 'Seletor do Campo Senha', type: 'text', placeholder: 'senha, #password, //input[@type="password"]' },
        { name: 'password_value', label: 'Valor da Senha', type: 'password', placeholder: 'sua_senha' },
        { name: 'login_button_selector_type', label: 'Tipo Seletor Botão', type: 'select', placeholder: '', options: SELENIUM_SELECTORS },
        { name: 'login_button_selector', label: 'Seletor do Botão Login', type: 'text', placeholder: 'btn_login, #submit, //input[@type="submit"]' },
        { name: 'wait_time', label: 'Tempo de Espera (s)', type: 'number', placeholder: '10' }
      ]
    },
    [NodeType.CLICK_BUTTON]: {
      label: 'Clicar Elemento',
      icon: 'MousePointer',
      color: 'bg-green-600',
      inputs: [
        { name: 'selector_type', label: 'Tipo de Seletor', type: 'select', placeholder: '', options: SELENIUM_SELECTORS },
        { name: 'selector_value', label: 'Valor do Seletor', type: 'text', placeholder: 'btn_pesquisar, #submit, //button[text()="Clique"]' },
        { name: 'wait_condition', label: 'Condição de Espera', type: 'select', placeholder: '', options: WAIT_CONDITIONS },
        { name: 'wait_timeout', label: 'Timeout (s)', type: 'number', placeholder: '10' },
        { name: 'scroll_to_element', label: 'Rolar até Elemento', type: 'checkbox', placeholder: '' },
        { name: 'double_click', label: 'Duplo Clique', type: 'checkbox', placeholder: '' },
        { name: 'pause_after', label: 'Pausa Após Clique (s)', type: 'number', placeholder: '1' }
      ]
    },
    [NodeType.EXTRACT_TABLE]: {
      label: 'Inserir Texto/Dados',
      icon: 'Type',
      color: 'bg-purple-600',
      inputs: [
        { name: 'selector_type', label: 'Tipo de Seletor', type: 'select', placeholder: '', options: SELENIUM_SELECTORS },
        { name: 'selector_value', label: 'Valor do Seletor', type: 'text', placeholder: 'nu_cns, #cpf, //input[@name="documento"]' },
        { name: 'text_value', label: 'Texto a Inserir', type: 'text', placeholder: 'Texto ou variável ${cpf}' },
        { name: 'clear_before', label: 'Limpar Campo Antes', type: 'checkbox', placeholder: '' },
        { name: 'wait_condition', label: 'Condição de Espera', type: 'select', placeholder: '', options: WAIT_CONDITIONS },
        { name: 'wait_timeout', label: 'Timeout (s)', type: 'number', placeholder: '10' },
        { name: 'press_enter', label: 'Pressionar Enter', type: 'checkbox', placeholder: '' },
        { name: 'pause_after', label: 'Pausa Após Inserção (s)', type: 'number', placeholder: '0.5' }
      ]
    },
    [NodeType.WAIT]: {
      label: 'Aguardar Elemento',
      icon: 'Clock',
      color: 'bg-orange-600',
      inputs: [
        { name: 'wait_type', label: 'Tipo de Espera', type: 'select', placeholder: '', options: [
          { value: 'time', label: 'Tempo Fixo' },
          { value: 'element', label: 'Aguardar Elemento' },
          { value: 'condition', label: 'Condição Específica' }
        ]},
        { name: 'duration', label: 'Duração (s)', type: 'number', placeholder: '5' },
        { name: 'selector_type', label: 'Tipo de Seletor', type: 'select', placeholder: '', options: SELENIUM_SELECTORS },
        { name: 'selector_value', label: 'Valor do Seletor', type: 'text', placeholder: 'elemento, #loading, //div[@class="result"]' },
        { name: 'wait_condition', label: 'Condição de Espera', type: 'select', placeholder: '', options: WAIT_CONDITIONS },
        { name: 'timeout', label: 'Timeout Máximo (s)', type: 'number', placeholder: '30' },
        { name: 'expected_text', label: 'Texto Esperado (opcional)', type: 'text', placeholder: 'Texto que deve aparecer' },
        { name: 'retry_attempts', label: 'Tentativas de Retry', type: 'number', placeholder: '3' }
      ]
    },
    [NodeType.SLEEP]: {
      label: 'Pausa (Sleep)',
      icon: 'Timer',
      color: 'bg-indigo-600',
      inputs: [
        { name: 'duration', label: 'Duração da Pausa (segundos)', type: 'number', placeholder: '2.5' },
        { name: 'description', label: 'Descrição (opcional)', type: 'text', placeholder: 'Aguardar carregamento da página' }
      ]
    },
    [NodeType.SPREADSHEET]: {
      label: 'Planilha (Excel/CSV)',
      icon: 'FileSpreadsheet',
      color: 'bg-emerald-600',
      inputs: [
        { name: 'operation', label: 'Operação', type: 'select', placeholder: '', options: [
          { value: 'read', label: 'Ler Planilha' },
          { value: 'create', label: 'Criar Planilha' },
          { value: 'write', label: 'Escrever Dados' },
          { value: 'save', label: 'Salvar Planilha' }
        ]},
        { name: 'file_path', label: 'Caminho do Arquivo', type: 'text', placeholder: 'C:/dados/planilha.xlsx ou dados.csv' },
        { name: 'sheet_name', label: 'Nome da Aba (Excel)', type: 'text', placeholder: 'Sheet1' },
        { name: 'variable_name', label: 'Nome da Variável', type: 'text', placeholder: 'df_dados' },
        { name: 'columns', label: 'Colunas (separadas por vírgula)', type: 'text', placeholder: 'Nome, Email, Telefone' },
        { name: 'filter_column', label: 'Coluna para Filtrar', type: 'text', placeholder: 'Status' },
        { name: 'filter_value', label: 'Valor do Filtro', type: 'text', placeholder: 'Ativo' }
      ]
    },
    [NodeType.LOOP_FOR]: {
      label: 'Loop For (Repetir)',
      icon: 'RotateCw',
      color: 'bg-cyan-600',
      inputs: [
        { name: 'loop_type', label: 'Tipo de Loop', type: 'select', placeholder: '', options: [
          { value: 'dataframe_rows', label: 'Linhas da Planilha' },
          { value: 'range', label: 'Intervalo Numérico' },
          { value: 'list', label: 'Lista de Valores' }
        ]},
        { name: 'dataframe_variable', label: 'Variável da Planilha', type: 'text', placeholder: 'df_dados' },
        { name: 'row_variable', label: 'Variável da Linha Atual', type: 'text', placeholder: 'linha_atual' },
        { name: 'start_value', label: 'Valor Inicial', type: 'number', placeholder: '0' },
        { name: 'end_value', label: 'Valor Final', type: 'number', placeholder: '10' },
        { name: 'step_value', label: 'Incremento', type: 'number', placeholder: '1' },
        { name: 'list_values', label: 'Lista de Valores', type: 'text', placeholder: 'valor1, valor2, valor3' },
        { name: 'max_iterations', label: 'Máximo de Iterações', type: 'number', placeholder: '1000' }
      ]
    },
    [NodeType.LOOP_WHILE]: {
      label: 'Loop While (Enquanto)',
      icon: 'Repeat',
      color: 'bg-teal-600',
      inputs: [
        { name: 'condition_type', label: 'Tipo de Condição', type: 'select', placeholder: '', options: [
          { value: 'variable_comparison', label: 'Comparar Variável' },
          { value: 'element_exists', label: 'Elemento Existe' },
          { value: 'custom', label: 'Condição Personalizada' }
        ]},
        { name: 'variable_name', label: 'Nome da Variável', type: 'text', placeholder: 'contador' },
        { name: 'comparison_operator', label: 'Operador', type: 'select', placeholder: '', options: [
          { value: '<', label: 'Menor que (<)' },
          { value: '<=', label: 'Menor ou igual (<=)' },
          { value: '>', label: 'Maior que (>)' },
          { value: '>=', label: 'Maior ou igual (>=)' },
          { value: '==', label: 'Igual (==)' },
          { value: '!=', label: 'Diferente (!=)' }
        ]},
        { name: 'comparison_value', label: 'Valor de Comparação', type: 'text', placeholder: '10' },
        { name: 'selector_type', label: 'Tipo de Seletor', type: 'select', placeholder: '', options: SELENIUM_SELECTORS },
        { name: 'selector_value', label: 'Seletor do Elemento', type: 'text', placeholder: '#loading, .spinner' },
        { name: 'custom_condition', label: 'Condição Python', type: 'text', placeholder: 'len(lista) > 0' },
        { name: 'max_iterations', label: 'Máximo de Iterações', type: 'number', placeholder: '100' }
      ]
    },
    [NodeType.VARIABLE]: {
      label: 'Variável',
      icon: 'Hash',
      color: 'bg-amber-600',
      inputs: [
        { name: 'operation', label: 'Operação', type: 'select', placeholder: '', options: [
          { value: 'set', label: 'Definir Valor' },
          { value: 'get_cell', label: 'Obter Célula da Planilha' },
          { value: 'increment', label: 'Incrementar' },
          { value: 'concatenate', label: 'Concatenar Texto' }
        ]},
        { name: 'variable_name', label: 'Nome da Variável', type: 'text', placeholder: 'minha_variavel' },
        { name: 'variable_value', label: 'Valor', type: 'text', placeholder: 'Valor inicial' },
        { name: 'dataframe_variable', label: 'Variável da Planilha', type: 'text', placeholder: 'df_dados' },
        { name: 'row_variable', label: 'Variável da Linha', type: 'text', placeholder: 'linha_atual' },
        { name: 'column_name', label: 'Nome da Coluna', type: 'text', placeholder: 'Nome' },
        { name: 'increment_value', label: 'Valor do Incremento', type: 'number', placeholder: '1' },
        { name: 'text_to_add', label: 'Texto para Concatenar', type: 'text', placeholder: ' - processado' }
      ]
    },
    [NodeType.CONDITION]: {
      label: 'Condição (If/Else)',
      icon: 'GitBranch',
      color: 'bg-rose-600',
      inputs: [
        { name: 'condition_type', label: 'Tipo de Condição', type: 'select', placeholder: '', options: [
          { value: 'variable_comparison', label: 'Comparar Variável' },
          { value: 'element_exists', label: 'Elemento Existe' },
          { value: 'text_contains', label: 'Texto Contém' },
          { value: 'custom', label: 'Condição Personalizada' }
        ]},
        { name: 'variable_name', label: 'Nome da Variável', type: 'text', placeholder: 'status' },
        { name: 'comparison_operator', label: 'Operador', type: 'select', placeholder: '', options: [
          { value: '==', label: 'Igual (==)' },
          { value: '!=', label: 'Diferente (!=)' },
          { value: '<', label: 'Menor que (<)' },
          { value: '<=', label: 'Menor ou igual (<=)' },
          { value: '>', label: 'Maior que (>)' },
          { value: '>=', label: 'Maior ou igual (>=)' },
          { value: 'in', label: 'Contém (in)' },
          { value: 'not in', label: 'Não contém (not in)' }
        ]},
        { name: 'comparison_value', label: 'Valor de Comparação', type: 'text', placeholder: 'Ativo' },
        { name: 'selector_type', label: 'Tipo de Seletor', type: 'select', placeholder: '', options: SELENIUM_SELECTORS },
        { name: 'selector_value', label: 'Seletor do Elemento', type: 'text', placeholder: '#success, .error' },
        { name: 'text_source', label: 'Fonte do Texto', type: 'text', placeholder: 'variavel_texto' },
        { name: 'search_text', label: 'Texto a Procurar', type: 'text', placeholder: 'sucesso' },
        { name: 'custom_condition', label: 'Condição Python', type: 'text', placeholder: 'variavel > 0 and status == "ok"' }
      ]
    },
    [NodeType.SCHEDULE]: {
      label: 'Agendamento',
      icon: 'Calendar',
      color: 'bg-violet-600',
      inputs: [
        { name: 'schedule_type', label: 'Tipo de Agendamento', type: 'select', placeholder: '', options: [
          { value: 'daily', label: 'Diário' },
          { value: 'weekly', label: 'Semanal' },
          { value: 'monthly', label: 'Mensal' },
          { value: 'interval', label: 'Intervalo' },
          { value: 'cron', label: 'Expressão Cron' }
        ]},
        { name: 'time', label: 'Horário (HH:MM)', type: 'text', placeholder: '09:00' },
        { name: 'days_of_week', label: 'Dias da Semana', type: 'select', placeholder: '', options: [
          { value: 'monday', label: 'Segunda-feira' },
          { value: 'tuesday', label: 'Terça-feira' },
          { value: 'wednesday', label: 'Quarta-feira' },
          { value: 'thursday', label: 'Quinta-feira' },
          { value: 'friday', label: 'Sexta-feira' },
          { value: 'saturday', label: 'Sábado' },
          { value: 'sunday', label: 'Domingo' }
        ]},
        { name: 'days_of_month', label: 'Dias do Mês (1-31)', type: 'text', placeholder: '1,15,30' },
        { name: 'interval_minutes', label: 'Intervalo (minutos)', type: 'number', placeholder: '60' },
        { name: 'cron_expression', label: 'Expressão Cron', type: 'text', placeholder: '0 9 * * 1-5' },
        { name: 'timezone', label: 'Fuso Horário', type: 'text', placeholder: 'America/Sao_Paulo' },
        { name: 'start_date', label: 'Data de Início', type: 'text', placeholder: '2024-01-01' },
        { name: 'end_date', label: 'Data de Fim (opcional)', type: 'text', placeholder: '2024-12-31' },
        { name: 'max_executions', label: 'Máximo de Execuções', type: 'number', placeholder: '100' }
      ]
    }
  };
  
  return configs[type] || null;
};