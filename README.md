# 🚀 VisualFlow - Sistema de Automação Visual

## 📋 Índice
- [Visão Geral](#visão-geral)
- [Instalação e Configuração](#instalação-e-configuração)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [API Backend - Rotas e Funcionalidades](#api-backend---rotas-e-funcionalidades)
- [Frontend - Interface Visual](#frontend---interface-visual)
- [Blocos de Automação - Guia Completo](#blocos-de-automação---guia-completo)
- [Exemplos Práticos](#exemplos-práticos)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **VisualFlow** é uma plataforma completa que permite criar automações web complexas através de uma interface visual drag-and-drop, similar ao N8N ou Zapier, mas focada em automação web com Selenium e processamento de dados com Pandas.

# VisualFlow

**Visual Workflow Builder for Web Automation & Data Processing**

VisualFlow abstracts the complexity of Selenium and Pandas into a drag-and-drop interface. Build automation workflows visually—like n8n or Scratch—without writing code.

![VisualFlow Demo](docs/demo.gif)

## Quick Start (Docker)

```bash
# Clone and run
git clone https://github.com/yourrepo/visualflow.git
cd visualflow
docker-compose up --build
```

**Access at: http://localhost:8164**

## Features

- 🖱️ **Drag & Drop** block-based workflow builder
- 🌐 **Web Automation** via Selenium (login, click, scrape tables)
- 📊 **Data Processing** via Pandas (read/write Excel, group, transform)
- 🔄 **Control Flow** with loops and conditions
- 💾 **Save & Load** workflows as JSON
- 🐳 **Docker Ready** with Chrome pre-installed

## Documentation

| Document | Description |
|----------|-------------|
| [USER_MANUAL.md](USER_MANUAL.md) | How to use the application |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Architecture & contribution |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues & fixes |

## Data Persistence

All files (downloads, spreadsheets, workflows) are saved to:
- **Docker**: `./visualflow_data` (mapped to `/app/data`)
- **Local**: `./visualflow_data`

## License

MIT

---

## 🛠️ Instalação e Configuração

### Pré-requisitos

- **Python 3.8+**
- **Node.js 16+** 
- **Google Chrome** (para Selenium)
- **Git**

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd visualflow
```

### 2. Configuração do Backend

```bash
cd backend

# Instalar dependências
pip install -r requirements.txt

# Testar configuração
python test_setup.py

# Iniciar servidor
python start.py
```

**Backend estará disponível em**: `http://localhost:8000`

### 3. Configuração do Frontend

```bash
cd frontend  # ou raiz do projeto

# Instalar dependências
npm install
# ou
bun install

# Iniciar desenvolvimento
npm run dev
# ou
bun dev
```

**Frontend estará disponível em**: `http://localhost:3000`

### 4. Verificação da Instalação

1. Acesse `http://localhost:3000`
2. Verifique se os blocos aparecem na sidebar
3. Teste criando um workflow simples
4. Acesse `http://localhost:8000/docs` para ver a documentação da API

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico

**Frontend:**
- React 18 + TypeScript
- React Flow (canvas visual)
- Tailwind CSS (estilização)
- Lucide React (ícones)
- Vite (build tool)

**Backend:**
- FastAPI (API REST)
- Selenium 4.15+ (automação web)
- Pandas 2.1+ (processamento de dados)
- Pydantic (validação de dados)
- Uvicorn (servidor ASGI)

### Fluxo de Dados

```
Frontend (React) → API REST → Backend (FastAPI) → Selenium/Pandas → Execução
     ↓                ↓              ↓                    ↓
Interface Visual → JSON Workflow → Python Code → Automação Web
```

---

## 🔌 API Backend - Rotas e Funcionalidades

### Base URL: `http://localhost:8000`

### 📊 Execução de Workflows

#### `POST /api/execute-flow`
Executa um workflow de automação.

**Request Body:**
```json
{
  "metadata": {
    "name": "Meu Workflow",
    "createdAt": "2024-01-01T10:00:00Z",
    "version": "1.0.0",
    "totalSteps": 3
  },
  "executionOrder": [
    {
      "id": "node_1",
      "type": "login",
      "label": "Login no Sistema",
      "inputs": {
        "url": "https://exemplo.com/login",
        "username_selector": "input[name='username']",
        "username_value": "usuario@email.com"
      },
      "position": {"x": 100, "y": 100}
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

#### `GET /api/execution/{execution_id}`
Consulta status de uma execução.

**Response:**
```json
{
  "id": "uuid-da-execucao",
  "status": "running",
  "started_at": "2024-01-01T10:00:00Z",
  "flow_name": "Meu Workflow",
  "total_steps": 3,
  "current_step": 2,
  "logs": [
    "Iniciando execução...",
    "Passo 1 concluído: Login realizado",
    "Executando passo 2..."
  ],
  "results": {}
}
```

#### `DELETE /api/execution/{execution_id}`
Cancela uma execução em andamento.

### 💾 Gerenciamento de Workflows

#### `POST /api/workflows`
Salva um novo workflow.

**Request Body:**
```json
{
  "flow_data": { /* dados do workflow */ },
  "name": "Automação de Cadastros",
  "description": "Processa planilha de clientes",
  "tags": ["cadastro", "planilha", "clientes"],
  "is_template": false
}
```

#### `GET /api/workflows`
Lista todos os workflows salvos.

**Query Parameters:**
- `include_templates`: boolean (padrão: true)

#### `GET /api/workflows/{workflow_id}`
Carrega um workflow específico.

#### `PUT /api/workflows/{workflow_id}`
Atualiza um workflow existente.

#### `DELETE /api/workflows/{workflow_id}`
Deleta um workflow.

#### `GET /api/workflows/search`
Busca workflows por nome, descrição ou tags.

**Query Parameters:**
- `q`: string (termo de busca)
- `tags`: string (tags separadas por vírgula)

#### `GET /api/workflows/stats`
Retorna estatísticas dos workflows.

**Response:**
```json
{
  "total_workflows": 15,
  "regular_workflows": 12,
  "templates": 3,
  "most_used_tags": [["automacao", 8], ["planilha", 5]],
  "storage_size_mb": 2.5
}
```

### 🔍 Validação

#### `POST /api/validate-flow`
Valida um workflow sem executar.

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Passo 3: Timeout muito baixo"]
}
```

---

## 🎨 Frontend - Interface Visual

### Componentes Principais

#### 1. **Header (Barra Superior)**
- **Workflows**: Abre gerenciador de workflows
- **Salvar**: Salva workflow atual
- **Carregar**: Carrega workflow de arquivo
- **Limpar**: Remove todos os blocos
- **Gerar Código**: Cria código Python
- **Executar Remoto**: Executa no backend
- **Logs**: Mostra painel de execução

#### 2. **Sidebar (Barra Lateral Esquerda)**
Contém todos os blocos de automação organizados por categoria:

**🌐 Navegação e Interação:**
- Login/Navegação
- Clicar Elemento  
- Inserir Texto/Dados
- Aguardar Elemento
- Pausa (Sleep)

**📊 Dados e Planilhas:**
- Planilha (Excel/CSV)
- Variável

**🔄 Controle de Fluxo:**
- Loop For (Repetir)
- Loop While (Enquanto)
- Condição (If/Else)

**⏰ Agendamento:**
- Agendamento

#### 3. **Canvas Central**
Área de trabalho onde você:
- Arrasta blocos da sidebar
- Conecta blocos criando fluxos
- Reposiciona elementos
- Faz zoom in/out
- Seleciona blocos para configurar

#### 4. **Painel de Configuração (Direita)**
Aparece ao clicar em um bloco, mostrando:
- Campos de configuração específicos
- Preview do código Python gerado
- Validação em tempo real

#### 5. **Painel de Execução**
Mostra durante execução:
- Progresso atual
- Logs em tempo real
- Controles de pausa/cancelamento

### Atalhos do Teclado

- **Ctrl + S**: Salvar workflow
- **Ctrl + O**: Abrir workflow
- **Ctrl + N**: Novo workflow
- **Delete**: Remover bloco selecionado
- **Ctrl + Z**: Desfazer (limitado)

---

## 🧩 Blocos de Automação - Guia Completo

### 🌐 1. Login/Navegação

**Função**: Navega para uma URL e realiza login em sistemas web.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **URL** | texto | ✅ | Endereço da página | `https://sistema.com/login` |
| **Tipo Seletor Usuário** | seleção | ✅ | Como localizar campo usuário | `ID`, `CSS Selector`, `XPath` |
| **Seletor Campo Usuário** | texto | ✅ | Seletor do campo usuário | `#username`, `input[name="user"]` |
| **Valor do Usuário** | texto | ✅ | Nome de usuário ou email | `usuario@email.com` |
| **Tipo Seletor Senha** | seleção | ✅ | Como localizar campo senha | `ID`, `CSS Selector`, `XPath` |
| **Seletor Campo Senha** | texto | ✅ | Seletor do campo senha | `#password`, `input[type="password"]` |
| **Valor da Senha** | senha | ✅ | Senha do usuário | `minhasenha123` |
| **Tipo Seletor Botão** | seleção | ✅ | Como localizar botão login | `ID`, `CSS Selector`, `XPath` |
| **Seletor Botão Login** | texto | ✅ | Seletor do botão | `#login-btn`, `button[type="submit"]` |
| **Tempo de Espera (s)** | número | ❌ | Timeout para elementos | `10` |

**Exemplo de Uso:**
```
URL: https://meusite.com/admin
Usuário: admin@site.com
Senha: senha123
Seletor Usuário: #email
Seletor Senha: #password  
Seletor Botão: button[type="submit"]
```

**Código Python Gerado:**
```python
driver.get("https://meusite.com/admin")
username_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#email"))
)
username_field.send_keys("admin@site.com")
password_field = driver.find_element(By.CSS_SELECTOR, "#password")
password_field.send_keys("senha123")
login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
login_button.click()
```

---

### 🖱️ 2. Clicar Elemento

**Função**: Clica em botões, links ou qualquer elemento da página.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **Tipo de Seletor** | seleção | ✅ | Como localizar elemento | `ID`, `CSS Selector`, `XPath` |
| **Valor do Seletor** | texto | ✅ | Seletor do elemento | `#btn-salvar`, `.button-primary` |
| **Condição de Espera** | seleção | ❌ | Quando elemento estará pronto | `Elemento Clicável`, `Elemento Visível` |
| **Timeout (s)** | número | ❌ | Tempo limite de espera | `10` |
| **Rolar até Elemento** | checkbox | ❌ | Fazer scroll se necessário | ✅ |
| **Duplo Clique** | checkbox | ❌ | Executar duplo clique | ❌ |
| **Pausa Após Clique (s)** | número | ❌ | Aguardar após clicar | `1` |

**Exemplo de Uso:**
```
Seletor: button.btn-primary
Condição: Elemento Clicável
Rolar até Elemento: ✅
Pausa Após: 2 segundos
```

**Código Python Gerado:**
```python
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary"))
)
driver.execute_script("arguments[0].scrollIntoView();", element)
element.click()
time.sleep(2)
```

---

### ✏️ 3. Inserir Texto/Dados

**Função**: Preenche campos de texto, textareas e inputs.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **Tipo de Seletor** | seleção | ✅ | Como localizar campo | `ID`, `Name`, `CSS Selector` |
| **Valor do Seletor** | texto | ✅ | Seletor do campo | `#nome`, `input[name="cliente"]` |
| **Texto a Inserir** | texto | ✅ | Conteúdo a digitar | `João Silva` ou `${nome_cliente}` |
| **Limpar Campo Antes** | checkbox | ❌ | Apagar conteúdo existente | ✅ |
| **Condição de Espera** | seleção | ❌ | Quando campo estará pronto | `Elemento Presente` |
| **Timeout (s)** | número | ❌ | Tempo limite | `10` |
| **Pressionar Enter** | checkbox | ❌ | Enviar formulário | ❌ |
| **Pausa Após (s)** | número | ❌ | Aguardar após inserir | `0.5` |

**💡 Uso de Variáveis:**
Você pode usar variáveis de planilhas ou outras fontes:
- `${nome_cliente}` - Valor da variável nome_cliente
- `${linha_atual.Nome}` - Coluna "Nome" da linha atual da planilha
- `Texto fixo + ${variavel}` - Combinação de texto e variável

**Exemplo de Uso:**
```
Seletor: #campo-nome
Texto: ${linha_atual.Nome}
Limpar Campo: ✅
Pressionar Enter: ❌
```

---

### ⏱️ 4. Aguardar Elemento

**Função**: Pausa execução até elemento aparecer ou condição ser atendida.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **Tipo de Espera** | seleção | ✅ | O que aguardar | `Tempo Fixo`, `Aguardar Elemento` |
| **Duração (s)** | número | ✅* | Tempo fixo de espera | `5` |
| **Tipo de Seletor** | seleção | ✅* | Como localizar elemento | `ID`, `CSS Selector` |
| **Valor do Seletor** | texto | ✅* | Seletor do elemento | `#loading`, `.spinner` |
| **Condição de Espera** | seleção | ❌ | Estado esperado | `Elemento Presente`, `Elemento Invisível` |
| **Timeout Máximo (s)** | número | ❌ | Tempo limite total | `30` |
| **Texto Esperado** | texto | ❌ | Texto que deve aparecer | `Carregamento concluído` |
| **Tentativas de Retry** | número | ❌ | Quantas tentativas | `3` |

*Obrigatório dependendo do tipo de espera

**Exemplo de Uso:**
```
Tipo: Aguardar Elemento
Seletor: .loading-spinner
Condição: Elemento Invisível
Timeout: 30 segundos
```

**Código Python Gerado:**
```python
WebDriverWait(driver, 30).until(
    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading-spinner"))
)
```

---

### 😴 5. Pausa (Sleep)

**Função**: Pausa simples por tempo determinado.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **Duração (segundos)** | número | ✅ | Tempo de pausa | `2.5` |
| **Descrição** | texto | ❌ | Comentário sobre a pausa | `Aguardar carregamento` |

**Exemplo de Uso:**
```
Duração: 3 segundos
Descrição: Aguardar processamento do servidor
```

**Código Python Gerado:**
```python
time.sleep(3)  # Aguardar processamento do servidor
```

---

### 📊 6. Planilha (Excel/CSV)

**Função**: Manipula arquivos Excel e CSV usando Pandas.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **Operação** | seleção | ✅ | Ação a executar | `Ler Planilha`, `Criar Planilha`, `Salvar` |
| **Caminho do Arquivo** | texto | ✅ | Local do arquivo | `C:/dados/clientes.xlsx` |
| **Nome da Aba** | texto | ❌ | Aba do Excel | `Sheet1`, `Clientes` |
| **Nome da Variável** | texto | ✅ | Como referenciar | `df_clientes` |
| **Colunas** | texto | ❌* | Colunas para criar | `Nome, Email, Telefone` |
| **Coluna para Filtrar** | texto | ❌ | Filtrar dados | `Status` |
| **Valor do Filtro** | texto | ❌ | Valor do filtro | `Ativo` |

*Obrigatório para operação "Criar Planilha"

**Operações Disponíveis:**

#### 📖 Ler Planilha
```
Operação: Ler Planilha
Arquivo: C:/dados/clientes.xlsx
Aba: Clientes
Variável: df_clientes
```

#### 📝 Criar Planilha
```
Operação: Criar Planilha
Variável: df_novo
Colunas: Nome, Email, Status, Data
```

#### 💾 Salvar Planilha
```
Operação: Salvar Planilha
Arquivo: C:/resultados/processados.xlsx
Variável: df_clientes
Aba: Resultados
```

**Código Python Gerado:**
```python
# Ler planilha
df_clientes = pd.read_excel("C:/dados/clientes.xlsx", sheet_name="Clientes")
print(f"Planilha carregada: {len(df_clientes)} linhas")

# Criar planilha
df_novo = pd.DataFrame(columns=["Nome", "Email", "Status", "Data"])

# Salvar planilha
df_clientes.to_excel("C:/resultados/processados.xlsx", sheet_name="Resultados", index=False)
```

---

### 🔄 7. Loop For (Repetir)

**Função**: Executa blocos repetidamente para cada item de uma coleção.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **Tipo de Loop** | seleção | ✅ | O que iterar | `Linhas da Planilha`, `Intervalo Numérico` |
| **Variável da Planilha** | texto | ✅* | Nome da planilha | `df_clientes` |
| **Variável da Linha Atual** | texto | ✅* | Nome para linha atual | `linha_atual` |
| **Valor Inicial** | número | ✅* | Início do intervalo | `0` |
| **Valor Final** | número | ✅* | Fim do intervalo | `10` |
| **Incremento** | número | ❌ | Passo do loop | `1` |
| **Lista de Valores** | texto | ✅* | Valores separados por vírgula | `A, B, C` |
| **Máximo de Iterações** | número | ❌ | Limite de segurança | `1000` |

*Obrigatório dependendo do tipo de loop

**Tipos de Loop:**

#### 📊 Linhas da Planilha
Processa cada linha de uma planilha:
```
Tipo: Linhas da Planilha
Planilha: df_clientes
Linha Atual: linha_atual
Máximo: 1000
```

#### 🔢 Intervalo Numérico
Loop de números:
```
Tipo: Intervalo Numérico
Início: 1
Fim: 100
Incremento: 1
```

#### 📝 Lista de Valores
Itera sobre lista personalizada:
```
Tipo: Lista de Valores
Valores: Janeiro, Fevereiro, Março, Abril
```

**Código Python Gerado:**
```python
# Loop por linhas da planilha
for index, linha_atual in df_clientes.iterrows():
    print(f"Processando linha {index + 1}")
    # Blocos dentro do loop serão executados aqui
    
# Loop numérico
for i in range(1, 100, 1):
    print(f"Iteração: {i}")
    
# Loop por lista
for item in ["Janeiro", "Fevereiro", "Março"]:
    print(f"Processando: {item}")
```

---

### 🔢 8. Variável

**Função**: Cria, modifica e obtém valores de variáveis.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **Operação** | seleção | ✅ | Ação com variável | `Definir Valor`, `Obter Célula` |
| **Nome da Variável** | texto | ✅ | Identificador | `nome_cliente` |
| **Valor** | texto | ✅* | Valor a definir | `João Silva` |
| **Variável da Planilha** | texto | ✅* | Planilha de origem | `df_clientes` |
| **Variável da Linha** | texto | ✅* | Linha atual | `linha_atual` |
| **Nome da Coluna** | texto | ✅* | Coluna da planilha | `Nome` |
| **Valor do Incremento** | número | ✅* | Quanto somar | `1` |
| **Texto para Concatenar** | texto | ✅* | Texto a adicionar | ` - processado` |

*Obrigatório dependendo da operação

**Operações Disponíveis:**

#### 📝 Definir Valor
```
Operação: Definir Valor
Variável: status_processamento
Valor: Em andamento
```

#### 📊 Obter Célula da Planilha
```
Operação: Obter Célula da Planilha
Variável: nome_cliente
Planilha: df_clientes
Linha: linha_atual
Coluna: Nome
```

#### ➕ Incrementar
```
Operação: Incrementar
Variável: contador
Incremento: 1
```

#### 🔗 Concatenar Texto
```
Operação: Concatenar Texto
Variável: nome_completo
Texto: - PROCESSADO
```

**Código Python Gerado:**
```python
# Definir valor
status_processamento = "Em andamento"

# Obter célula
nome_cliente = linha_atual["Nome"]

# Incrementar
contador = contador + 1

# Concatenar
nome_completo = nome_completo + "- PROCESSADO"
```

---

### ⏰ 9. Agendamento

**Função**: Define quando e com que frequência executar o workflow.

**Campos de Configuração:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| **Tipo de Agendamento** | seleção | ✅ | Frequência | `Diário`, `Semanal`, `Mensal` |
| **Horário (HH:MM)** | texto | ✅ | Hora de execução | `09:00`, `14:30` |
| **Dias da Semana** | seleção | ✅* | Quais dias | `Segunda-feira`, `Sexta-feira` |
| **Dias do Mês** | texto | ✅* | Dias específicos | `1,15,30` |
| **Intervalo (minutos)** | número | ✅* | Frequência em minutos | `60`, `120` |
| **Expressão Cron** | texto | ✅* | Cron personalizado | `0 9 * * 1-5` |
| **Fuso Horário** | texto | ❌ | Timezone | `America/Sao_Paulo` |
| **Data de Início** | texto | ❌ | Quando começar | `2024-01-01` |
| **Data de Fim** | texto | ❌ | Quando parar | `2024-12-31` |
| **Máximo de Execuções** | número | ❌ | Limite total | `100` |

*Obrigatório dependendo do tipo

**Tipos de Agendamento:**

#### 📅 Diário
Executa todos os dias no horário especificado:
```
Tipo: Diário
Horário: 09:00
Fuso: America/Sao_Paulo
```

#### 📆 Semanal
Executa em dias específicos da semana:
```
Tipo: Semanal
Horário: 08:30
Dias: Segunda-feira, Quarta-feira, Sexta-feira
```

#### 🗓️ Mensal
Executa em dias específicos do mês:
```
Tipo: Mensal
Horário: 10:00
Dias do Mês: 1,15,30
```

#### ⏱️ Intervalo
Executa a cada X minutos:
```
Tipo: Intervalo
Intervalo: 120 minutos
```

#### 🔧 Expressão Cron
Agendamento personalizado:
```
Tipo: Expressão Cron
Cron: 0 9 * * 1-5  # 9h, segunda a sexta
```

**Exemplos de Cron:**
- `0 9 * * *` - Todos os dias às 9h
- `0 9 * * 1-5` - Segunda a sexta às 9h  
- `0 */2 * * *` - A cada 2 horas
- `0 9 1 * *` - Todo dia 1 do mês às 9h
- `0 9 * * 1` - Toda segunda-feira às 9h

---

## 🎓 Exemplos Práticos

### 📊 Exemplo 1: Processar Planilha de Clientes

**Cenário**: Você tem uma planilha com dados de clientes e precisa cadastrá-los em um sistema web.

**Estrutura da Planilha** (`clientes.xlsx`):
```
| Nome          | Email                | Telefone     | Status |
|---------------|---------------------|--------------|--------|
| João Silva    | joao@email.com      | 11999999999  | Ativo  |
| Maria Santos  | maria@email.com     | 11888888888  | Ativo  |
```

**Workflow:**

1. **📊 Planilha** - Ler dados
   ```
   Operação: Ler Planilha
   Arquivo: C:/dados/clientes.xlsx
   Variável: df_clientes
   ```

2. **🌐 Login** - Acessar sistema
   ```
   URL: https://sistema.com/login
   Usuário: admin@sistema.com
   Senha: minhasenha
   ```

3. **🔄 Loop For** - Processar cada cliente
   ```
   Tipo: Linhas da Planilha
   Planilha: df_clientes
   Linha Atual: cliente
   ```

4. **🔢 Variável** - Obter nome do cliente
   ```
   Operação: Obter Célula da Planilha
   Variável: nome
   Planilha: df_clientes
   Linha: cliente
   Coluna: Nome
   ```

5. **🔢 Variável** - Obter email do cliente
   ```
   Operação: Obter Célula da Planilha
   Variável: email
   Planilha: df_clientes
   Linha: cliente
   Coluna: Email
   ```

6. **✏️ Inserir Texto** - Preencher nome
   ```
   Seletor: #campo-nome
   Texto: ${nome}
   ```

7. **✏️ Inserir Texto** - Preencher email
   ```
   Seletor: #campo-email
   Texto: ${email}
   ```

8. **🖱️ Clicar** - Salvar cadastro
   ```
   Seletor: #btn-salvar
   ```

9. **😴 Pausa** - Aguardar processamento
   ```
   Duração: 2 segundos
   ```

### 🕐 Exemplo 2: Automação Agendada

**Cenário**: Executar relatório diário às 9h da manhã.

**Workflow:**

1. **⏰ Agendamento**
   ```
   Tipo: Diário
   Horário: 09:00
   Fuso: America/Sao_Paulo
   ```

2. **🌐 Login** - Acessar sistema
3. **🖱️ Clicar** - Menu relatórios
4. **🖱️ Clicar** - Gerar relatório
5. **⏱️ Aguardar** - Processamento
6. **🖱️ Clicar** - Download

### 🔄 Exemplo 3: Loop com Condições

**Cenário**: Processar apenas clientes ativos.

**Workflow:**

1. **📊 Planilha** - Carregar dados
2. **🔄 Loop For** - Para cada linha
3. **🔢 Variável** - Obter status
   ```
   Coluna: Status
   Variável: status_cliente
   ```
4. **🌿 Condição** - Se cliente ativo
   ```
   Tipo: Comparar Variável
   Variável: status_cliente
   Operador: Igual (==)
   Valor: Ativo
   ```
5. **✏️ Inserir Texto** - Processar apenas se ativo

---

## 🔧 Troubleshooting

### ❌ Problemas Comuns

#### 1. **ChromeDriver não encontrado**
```
Erro: Unable to obtain driver for chrome
```
**Solução:**
```bash
cd backend
python fix_selenium_service.py
```

#### 2. **Planilha não encontrada**
```
Erro: FileNotFoundError: dados.xlsx
```
**Soluções:**
- Verificar caminho completo: `C:/Users/Usuario/Desktop/dados.xlsx`
- Usar barras normais `/` em vez de `\`
- Verificar se arquivo existe

#### 3. **Elemento não encontrado**
```
Erro: NoSuchElementException
```
**Soluções:**
- Verificar seletor CSS/XPath
- Adicionar bloco "Aguardar Elemento" antes
- Usar seletores mais específicos
- Verificar se página carregou completamente

#### 4. **Timeout na execução**
```
Erro: TimeoutException
```
**Soluções:**
- Aumentar timeout nos blocos
- Adicionar pausas entre ações
- Verificar velocidade da internet
- Usar condições de espera apropriadas

#### 5. **Variável não encontrada**
```
Erro: KeyError: 'nome_cliente'
```
**Soluções:**
- Verificar nome da variável
- Certificar que bloco "Variável" foi executado antes
- Verificar nome da coluna na planilha

### 🛠️ Comandos Úteis

#### Backend
```bash
# Testar configuração
python backend/test_setup.py

# Verificar logs
python backend/start.py

# Reinstalar dependências
pip install -r backend/requirements.txt --force-reinstall
```

#### Frontend
```bash
# Limpar cache
npm run build
rm -rf node_modules
npm install

# Verificar erros
npm run dev
```

### 📞 Suporte

Para problemas não listados:

1. **Verificar logs** no painel de execução
2. **Testar com dados menores** (1-2 linhas)
3. **Validar workflow** antes de executar
4. **Usar modo debug** com pausas entre passos

---

## 🚀 Próximos Passos

Agora que você conhece o sistema completo:

1. **Comece simples**: Crie um workflow com 2-3 blocos
2. **Teste com dados pequenos**: Use planilhas com poucas linhas
3. **Incremente gradualmente**: Adicione mais complexidade
4. **Use templates**: Salve workflows como templates
5. **Monitore execuções**: Acompanhe logs e resultados

**Boa automação! 🎉**