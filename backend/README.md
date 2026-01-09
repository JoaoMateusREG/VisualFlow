# Backend - VisualFlow Executor

Backend Python com FastAPI para executar fluxos de automação VisualFlow criados no frontend.

## 🚀 Instalação

### 1. Instalar Python 3.8+
Certifique-se de ter Python 3.8 ou superior instalado.

### 2. Criar ambiente virtual (recomendado)
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Iniciar servidor
```bash
python start.py
```

O servidor estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## 📡 Endpoints da API

### `POST /api/execute-flow`
Executa um fluxo de automação Selenium.

**Request Body:**
```json
{
  "metadata": {
    "name": "Meu Fluxo",
    "createdAt": "2024-01-08T10:00:00Z",
    "version": "1.0.0",
    "totalSteps": 3
  },
  "executionOrder": [
    {
      "id": "node_1",
      "type": "login",
      "label": "Login",
      "inputs": {
        "url": "https://exemplo.com",
        "username_selector_type": "id",
        "username_selector": "usuario",
        "username_value": "meu_usuario"
      }
    }
  ]
}
```

**Response:**
```json
{
  "execution_id": "uuid-da-execucao",
  "status": "started",
  "message": "Execução iniciada com sucesso"
}
```

### `GET /api/execution/{execution_id}`
Consulta o status de uma execução.

**Response:**
```json
{
  "id": "uuid-da-execucao",
  "status": "running",
  "started_at": "2024-01-08T10:00:00Z",
  "flow_name": "Meu Fluxo",
  "total_steps": 3,
  "current_step": 2,
  "logs": [
    "Iniciando execução...",
    "Navegou para: https://exemplo.com",
    "Preencheu campo usuário: usuario"
  ],
  "results": {}
}
```

### `GET /api/executions`
Lista todas as execuções.

### `DELETE /api/execution/{execution_id}`
Cancela uma execução em andamento.

### `POST /api/validate-flow`
Valida um fluxo sem executar.

## 📁 Acesso a Dados (Planilhas)

### `GET /api/data/list-files`
Lista recursivamente todos os arquivos na pasta de planilhas.
Útil para integração com ferramentas externas.

**Query Params:**
- `path`: (opcional) subpasta para listar
- `recursive`: (opcional, default=true) listar subpastas

**Response:**
```json
[
  {
    "name": "vendas.xlsx",
    "folder": ".",
    "relative_path": "vendas.xlsx",
    "url": "http://.../api/data/sheets/vendas.xlsx",
    "size": 1024,
    "updated_at": "2024-01-08T10:00:00"
  }
]
```

### `GET /api/data/sheets/{caminho_arquivo}`
Baixa um arquivo de planilha específico.
Exemplo: `/api/data/sheets/pasta1/dados.xlsx`

## 🔧 Configuração

### Selenium Config
```python
{
  "headless": false,          # Executar sem interface gráfica
  "window_size": "1920,1080", # Tamanho da janela
  "timeout": 30,              # Timeout padrão
  "implicit_wait": 10,        # Espera implícita
  "page_load_timeout": 30     # Timeout de carregamento
}
```

## 🎯 Tipos de Passos Suportados

### 1. Login/Navegação (`login`)
- Navega para URL
- Preenche campos de usuário e senha
- Clica no botão de login

### 2. Clicar Elemento (`clickButton`)
- Aguarda elemento estar disponível
- Clica ou duplo-clica
- Suporte a scroll automático

### 3. Inserir Texto (`extractTable`)
- Aguarda campo estar disponível
- Limpa campo (opcional)
- Insere texto
- Pressiona Enter (opcional)

### 4. Aguardar (`wait`)
- Espera por tempo fixo
- Aguarda elemento aparecer
- Aguarda condições específicas

## 🔍 Seletores Suportados

- **ID**: `By.ID`
- **Name**: `By.NAME`
- **Class Name**: `By.CLASS_NAME`
- **Tag Name**: `By.TAG_NAME`
- **XPath**: `By.XPATH`
- **CSS Selector**: `By.CSS_SELECTOR`
- **Link Text**: `By.LINK_TEXT`
- **Partial Link Text**: `By.PARTIAL_LINK_TEXT`

## ⏳ Condições de Espera

- `presence_of_element_located`
- `visibility_of_element_located`
- `element_to_be_clickable`
- `invisibility_of_element_located`
- `text_to_be_present_in_element`
- `element_to_be_selected`

## 📝 Logs e Monitoramento

O backend fornece logs detalhados em tempo real:
- Status de cada passo
- Elementos encontrados/não encontrados
- Erros e exceções
- Tempo de execução

## 🐛 Tratamento de Erros

- **TimeoutException**: Elemento não encontrado no tempo limite
- **NoSuchElementException**: Elemento não existe
- **StaleElementReferenceException**: Elemento não é mais válido
- **UnexpectedAlertPresentException**: Alerta inesperado

## 🔄 Execução Assíncrona

As execuções rodam em background, permitindo:
- Múltiplas execuções simultâneas
- Monitoramento em tempo real
- Cancelamento de execuções
- Histórico de execuções

## 📊 Exemplo de Uso

```python
# Exemplo de integração direta
from selenium_executor import SeleniumExecutor
from models import FlowData

executor = SeleniumExecutor()
flow_data = FlowData(...)  # Dados do frontend

async for update in executor.execute_flow_async(flow_data, "exec_id"):
    print(f"Status: {update}")
```