# VisualFlow - Setup Completo

Guia para executar o VisualFlow completo com frontend React e backend Python.

## 🚀 Arquitetura do VisualFlow

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   Frontend      │ ──────────────► │   Backend       │
│   React + TS    │                 │   FastAPI       │
│   Port: 3001    │ ◄────────────── │   Port: 8000    │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │   Selenium      │
                                    │   WebDriver     │
                                    └─────────────────┘
```

## 📦 Instalação Completa

### 1. Frontend (React + TypeScript + Bun)

```bash
# Instalar dependências
bun install

# Executar frontend
bun run dev
```

**URL:** http://localhost:3001

### 2. Backend (Python + FastAPI)

```bash
# Navegar para pasta do backend
cd backend

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar backend
python start.py
```

**URLs:**
- API: http://localhost:8000
- Documentação: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## 🔄 Fluxo de Comunicação

### 1. **Criação do Fluxo (Frontend)**
- Usuário arrasta blocos no canvas
- Configura cada bloco na sidebar direita
- Conecta blocos para definir sequência

### 2. **Execução Local (Gerar Código)**
- Botão "Gerar Código" valida fluxo
- Gera código Python/Selenium no console
- Não executa, apenas mostra o código

### 3. **Execução Remota (Backend)**
- Botão "Executar Remoto" envia fluxo para backend
- Backend valida e executa com Selenium real
- Frontend monitora progresso em tempo real

## 📡 Endpoints da API

### `POST /api/execute-flow`
Executa fluxo no backend com Selenium.

**Request:**
```json
{
  "metadata": {
    "name": "Meu Fluxo",
    "totalSteps": 3
  },
  "executionOrder": [
    {
      "id": "node_1",
      "type": "login",
      "inputs": {
        "url": "https://exemplo.com",
        "username_selector": "usuario"
      }
    }
  ]
}
```

**Response:**
```json
{
  "execution_id": "uuid-da-execucao",
  "status": "started"
}
```

### `GET /api/execution/{execution_id}`
Consulta status da execução.

**Response:**
```json
{
  "id": "uuid",
  "status": "running",
  "current_step": 2,
  "total_steps": 5,
  "logs": ["Log 1", "Log 2"]
}
```

## 🎯 Funcionalidades Implementadas

### Frontend
- ✅ Canvas drag-and-drop
- ✅ Sidebar de configuração
- ✅ Geração de código Selenium
- ✅ Execução remota via API
- ✅ Monitoramento em tempo real
- ✅ Painel de logs e progresso

### Backend
- ✅ API REST com FastAPI
- ✅ Execução assíncrona
- ✅ Selenium WebDriver
- ✅ Todos os tipos de seletor
- ✅ Condições de espera
- ✅ Tratamento de erros
- ✅ Logs detalhados

## 🔧 Tipos de Blocos Suportados

### 1. **Navegação/Login**
- Navega para URL
- Preenche usuário/senha
- Clica botão login
- Suporte a todos seletores

### 2. **Clicar Elemento**
- Aguarda elemento
- Clique simples/duplo
- Scroll automático
- Pausa configurável

### 3. **Inserir Texto**
- Aguarda campo
- Limpa antes (opcional)
- Insere texto
- Pressiona Enter (opcional)

### 4. **Aguardar**
- Tempo fixo
- Aguardar elemento
- Condições específicas
- Retry automático

## 🎮 Como Usar

### 1. **Iniciar Serviços**
```bash
# Terminal 1 - Backend
cd backend
python start.py

# Terminal 2 - Frontend  
bun run dev
```

### 2. **Criar Fluxo**
1. Abra http://localhost:3001
2. Arraste blocos para o canvas
3. Conecte blocos na ordem desejada
4. Clique em cada bloco para configurar

### 3. **Configurar Blocos**
1. Selecione tipo de seletor (ID, XPath, etc.)
2. Digite valor do seletor
3. Configure timeouts e condições
4. Veja código gerado em tempo real

### 4. **Executar**
- **"Gerar Código"**: Valida e mostra código no console
- **"Executar Remoto"**: Executa no backend com Selenium
- **"Logs"**: Mostra painel de monitoramento

## 🐛 Troubleshooting

### Frontend não conecta com Backend
```bash
# Verificar se backend está rodando
curl http://localhost:8000

# Verificar CORS no backend (main.py)
allow_origins=["http://localhost:3001"]
```

### Selenium não funciona
```bash
# Instalar Chrome/Chromium
# Windows: Baixar do site oficial
# Linux: sudo apt install chromium-browser
# Mac: brew install --cask google-chrome

# Verificar webdriver-manager
pip install --upgrade webdriver-manager
```

### Erro de dependências
```bash
# Frontend
bun install --force

# Backend
pip install -r requirements.txt --force-reinstall
```

## 📊 Monitoramento

### Logs do Frontend
- Console do navegador (F12)
- Painel de execução (botão "Logs")
- Alertas de validação

### Logs do Backend
- Terminal onde rodou `python start.py`
- Logs detalhados do Selenium
- Status HTTP das requisições

## 🚀 Próximos Passos

1. **Persistência**: Banco de dados para execuções
2. **Autenticação**: Login de usuários
3. **Agendamento**: Execuções programadas
4. **Relatórios**: Dashboard de resultados
5. **Integração**: Webhooks e APIs externas

## 📝 Exemplo Completo

### Fluxo: Login no SISREG
1. **Navegação**: https://sisregiii.saude.gov.br/
2. **Login**: usuario/senha nos campos ID
3. **Aguardar**: Campo de busca aparecer
4. **Inserir**: CPF no campo "nu_cns"
5. **Clicar**: Botão "btn_pesquisar"
6. **Aguardar**: Resultado aparecer

Este fluxo será executado automaticamente pelo Selenium no backend! 🎉