# VisualFlow Developer Guide

## Architecture Overview

VisualFlow follows a **client-server architecture** with a React frontend and FastAPI backend.

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
               │ (web actions) │     │ (data ops)    │     │ (persistence) │
               └───────────────┘     └───────────────┘     └───────────────┘
```

## Project Structure

```
VisualFlow/
├── src/                    # React Frontend
│   ├── App.tsx             # Main application
│   ├── components/         # UI components
│   │   ├── Sidebar.tsx     # Block palette
│   │   ├── ConfigPanel.tsx # Property editor
│   │   ├── CustomNode.tsx  # Flow node renderer
│   │   └── ...
│   ├── services/           # API clients
│   └── types/              # TypeScript definitions
│
├── backend/                # Python Backend
│   ├── main.py             # FastAPI server & routes
│   ├── models.py           # Pydantic data models
│   ├── selenium_executor.py # Web automation engine
│   ├── pandas_executor.py  # Data processing engine
│   ├── workflow_storage.py # Save/load workflows
│   └── tools/              # Utility scripts (dev only)
│
├── Dockerfile              # Unified production image
├── docker-compose.yml      # Docker orchestration
└── visualflow_data/        # Persistent data volume
```

## Adding a New Block Type

### 1. Define the NodeType (Backend)

Edit `backend/models.py`:
```python
class NodeType(str, Enum):
    # ... existing types ...
    MY_NEW_BLOCK = "myNewBlock"
```

### 2. Implement the Executor Method (Backend)

In `selenium_executor.py` or `pandas_executor.py`:
```python
async def execute_step_my_new_block(self, step: FlowExecutionStep) -> Dict[str, Any]:
    inputs = step.inputs
    logs = []
    # Your logic here
    return {"success": True, "logs": logs}
```

Register in `_execute_step()`:
```python
elif step.type == NodeType.MY_NEW_BLOCK:
    return await self.execute_step_my_new_block(step)
```

### 3. Add UI Configuration (Frontend)

Edit `src/types/nodeTypes.ts`:
```typescript
[NodeType.MY_NEW_BLOCK]: {
  label: 'My New Block',
  icon: 'SomeIcon',
  color: '#hexcolor',
  description: 'What this block does',
  inputs: [
    { name: 'param1', label: 'Parameter 1', type: 'text', required: true }
  ]
}
```

### 4. Register in App.tsx

```typescript
const nodeTypes = {
  // ... existing ...
  [NodeType.MY_NEW_BLOCK]: CustomNode,
};
```

## Running Locally

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 start.py

# Frontend (separate terminal)
bun install  # or npm install
bun run dev
```

## Docker Deployment

```bash
docker-compose up --build
# Access at http://localhost:8164
```

## Data Directory

All files (downloaded, created, saved) are stored in:
- **Docker**: `/app/data` (mapped to `./visualflow_data`)
- **Local dev**: `./visualflow_data` (project root)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/execute` | POST | Execute workflow |
| `/api/validate-flow` | POST | Validate workflow |
| `/api/workflows` | GET | List saved workflows |
| `/api/workflows` | POST | Save new workflow |
| `/api/workflows/{id}` | GET | Load workflow |
| `/api/workflows/{id}` | DELETE | Delete workflow |
