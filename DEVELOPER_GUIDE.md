# Guia do Desenvolvedor - VisualFlow

## Visão Geral da Arquitetura

O VisualFlow segue uma **arquitetura cliente-servidor** com frontend React e backend FastAPI.

```
┌────────────────┐     HTTP/WS      ┌─────────────────────┐
│  React Frontend │ ──────────────► │   FastAPI Backend   │
│  (ReactFlow UI) │ ◄────────────── │   (main.py)         │
└────────────────┘                  └─────────────────────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        ▼                     ▼                     ▼
               ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
               │ SeleniumExec  │     │ PandasExec    │     │ WorkflowStore │
               │ (ações web)   │     │ (ops dados)   │     │ (persistência)│
               └───────────────┘     └───────────────┘     └───────────────┘
```

## Estrutura do Projeto

```
VisualFlow/
├── src/                    # Frontend React
│   ├── App.tsx             # Aplicação principal
│   ├── components/         # Componentes UI
│   │   ├── Sidebar.tsx     # Paleta de blocos
│   │   ├── ConfigPanel.tsx # Editor de propriedades
│   │   ├── CustomNode.tsx  # Renderizador de nós
│   │   └── ...
│   ├── services/           # Clientes API
│   └── types/              # Definições TypeScript
│
├── backend/                # Backend Python
│   ├── main.py             # Servidor FastAPI e rotas
│   ├── models.py           # Modelos de dados Pydantic
│   ├── selenium_executor.py # Motor de automação web
│   ├── pandas_executor.py  # Motor de processamento de dados
│   ├── workflow_storage.py # Salvar/carregar workflows
│   └── tools/              # Scripts utilitários (dev apenas)
│
├── Dockerfile              # Imagem de produção unificada
├── docker-compose.yml      # Orquestração Docker
└── visualflow_data/        # Volume de dados persistente
```

## Adicionando um Novo Tipo de Bloco

### 1. Definir o NodeType (Backend)

Edite `backend/models.py`:
```python
class NodeType(str, Enum):
    # ... tipos existentes ...
    MEU_NOVO_BLOCO = "meuNovoBloco"
```

### 2. Implementar o Método Executor (Backend)

Em `selenium_executor.py` ou `pandas_executor.py`:
```python
async def execute_step_meu_novo_bloco(self, step: FlowExecutionStep) -> Dict[str, Any]:
    inputs = step.inputs
    logs = []
    # Sua lógica aqui
    return {"success": True, "logs": logs}
```

Registre em `_execute_step()`:
```python
elif step.type == NodeType.MEU_NOVO_BLOCO:
    return await self.execute_step_meu_novo_bloco(step)
```

### 3. Adicionar Configuração UI (Frontend)

Edite `src/types/nodeTypes.ts`:
```typescript
[NodeType.MEU_NOVO_BLOCO]: {
  label: 'Meu Novo Bloco',
  icon: 'AlgumIcone',
  color: '#hexcolor',
  description: 'O que este bloco faz',
  inputs: [
    { name: 'param1', label: 'Parâmetro 1', type: 'text', required: true }
  ]
}
```

### 4. Registrar em App.tsx

```typescript
const nodeTypes = {
  // ... existentes ...
  [NodeType.MEU_NOVO_BLOCO]: CustomNode,
};
```

## Executando Localmente

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 start.py

# Frontend (terminal separado)
bun install  # ou npm install
bun run dev
```

## Deploy com Docker

```bash
docker-compose up --build
# Acesse em http://localhost:8164
```

## Diretório de Dados

Todos os arquivos (baixados, criados, salvos) são armazenados em:
- **Docker**: `/app/data` (mapeado para `./visualflow_data`)
- **Dev local**: `./visualflow_data` (raiz do projeto)

## Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/execute` | POST | Executar workflow |
| `/api/validate-flow` | POST | Validar workflow |
| `/api/workflows` | GET | Listar workflows salvos |
| `/api/workflows` | POST | Salvar novo workflow |
| `/api/workflows/{id}` | GET | Carregar workflow |
| `/api/workflows/{id}` | DELETE | Deletar workflow |
