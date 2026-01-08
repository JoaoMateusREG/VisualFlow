from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import asyncio
from datetime import datetime
import json

# Tentar importar executor principal, se falhar usar fallback
try:
    from selenium_executor import SeleniumExecutor
    print("✅ Usando SeleniumExecutor principal")
except Exception as e:
    print(f"⚠️ SeleniumExecutor principal falhou: {e}")
    try:
        from selenium_executor_fallback import SeleniumExecutorFallback as SeleniumExecutor
        print("✅ Usando SeleniumExecutor com fallback")
    except Exception as e2:
        print(f"❌ Ambos executores falharam: {e2}")
        raise e2

from models import FlowData, ExecutionStatus, ExecutionResult
from workflow_storage import workflow_storage, WorkflowMetadata, SavedWorkflow

app = FastAPI(title="VisualFlow Backend API", version="2.0.0", description="API para execução de fluxos de automação VisualFlow")

# Configurar CORS para permitir comunicação com o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # URLs do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenar execuções em memória (em produção, usar banco de dados)
executions: Dict[str, ExecutionResult] = {}

# Modelos para requests de workflow
class SaveWorkflowRequest(BaseModel):
    flow_data: FlowData
    name: str
    description: str = ""
    tags: List[str] = []
    is_template: bool = False

class UpdateWorkflowRequest(BaseModel):
    flow_data: Optional[FlowData] = None
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

@app.get("/")
async def root():
    return {"message": "Selenium Flow Executor API", "version": "1.0.0"}

@app.post("/api/execute-flow")
async def execute_flow(flow_data: FlowData, background_tasks: BackgroundTasks):
    """
    Recebe um fluxo do frontend e inicia a execução em background
    """
    try:
        # Gerar ID único para a execução
        execution_id = str(uuid.uuid4())
        
        # Criar resultado inicial
        execution_result = ExecutionResult(
            id=execution_id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(),
            flow_name=flow_data.metadata.name,
            total_steps=len(flow_data.executionOrder),
            current_step=0,
            logs=[f"Iniciando execução do fluxo: {flow_data.metadata.name}"],
            results={}
        )
        
        # Armazenar no dicionário
        executions[execution_id] = execution_result
        
        # Executar em background
        background_tasks.add_task(run_selenium_flow, execution_id, flow_data)
        
        return {
            "execution_id": execution_id,
            "status": "started",
            "message": "Execução iniciada com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar execução: {str(e)}")

@app.get("/api/execution/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Retorna o status atual de uma execução
    """
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    
    return executions[execution_id]

@app.get("/api/executions")
async def list_executions():
    """
    Lista todas as execuções
    """
    return list(executions.values())

@app.delete("/api/execution/{execution_id}")
async def stop_execution(execution_id: str):
    """
    Para uma execução em andamento
    """
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    
    execution = executions[execution_id]
    if execution.status == ExecutionStatus.RUNNING:
        execution.status = ExecutionStatus.CANCELLED
        execution.finished_at = datetime.now()
        execution.logs.append("Execução cancelada pelo usuário")
    
    return {"message": "Execução cancelada"}

@app.post("/api/validate-flow")
async def validate_flow(flow_data: FlowData):
    """
    Valida um fluxo sem executar
    """
    try:
        executor = SeleniumExecutor()
        validation_result = executor.validate_flow(flow_data)
        
        return {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"],
            "warnings": validation_result["warnings"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na validação: {str(e)}")

# ==================== ROTAS DE WORKFLOW STORAGE ====================

@app.post("/api/workflows")
async def save_workflow(request: SaveWorkflowRequest):
    """
    Salva um novo workflow
    """
    try:
        saved_workflow = workflow_storage.save_workflow(
            flow_data=request.flow_data,
            name=request.name,
            description=request.description,
            tags=request.tags,
            is_template=request.is_template
        )
        
        return {
            "id": saved_workflow.metadata.id,
            "message": "Workflow salvo com sucesso",
            "metadata": saved_workflow.metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar workflow: {str(e)}")

@app.get("/api/workflows")
async def list_workflows(include_templates: bool = True):
    """
    Lista todos os workflows salvos
    """
    try:
        workflows = workflow_storage.list_workflows(include_templates=include_templates)
        return workflows
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar workflows: {str(e)}")

@app.get("/api/workflows/stats")
async def get_workflow_stats():
    """
    Retorna estatísticas dos workflows
    """
    try:
        stats = workflow_storage.get_workflow_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """
    Carrega um workflow específico
    """
    try:
        workflow = workflow_storage.load_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        return workflow
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar workflow: {str(e)}")

@app.put("/api/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, request: UpdateWorkflowRequest):
    """
    Atualiza um workflow existente
    """
    try:
        updated_workflow = workflow_storage.update_workflow(
            workflow_id=workflow_id,
            flow_data=request.flow_data,
            name=request.name,
            description=request.description,
            tags=request.tags
        )
        
        if not updated_workflow:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        return {
            "message": "Workflow atualizado com sucesso",
            "metadata": updated_workflow.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar workflow: {str(e)}")

@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """
    Deleta um workflow
    """
    try:
        success = workflow_storage.delete_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        return {"message": "Workflow deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar workflow: {str(e)}")

@app.get("/api/workflows/search")
async def search_workflows(q: str = "", tags: str = ""):
    """
    Busca workflows por nome, descrição ou tags
    """
    try:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else None
        workflows = workflow_storage.search_workflows(query=q, tags=tag_list)
        return workflows
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")

@app.post("/api/workflows/{workflow_id}/duplicate")
async def duplicate_workflow(workflow_id: str, name: str = None):
    """
    Duplica um workflow existente
    """
    try:
        # Carregar workflow original
        original = workflow_storage.load_workflow(workflow_id)
        if not original:
            raise HTTPException(status_code=404, detail="Workflow não encontrado")
        
        # Criar nome para a cópia
        copy_name = name or f"{original.metadata.name} (Cópia)"
        
        # Salvar como novo workflow
        duplicated = workflow_storage.save_workflow(
            flow_data=original.flow_data,
            name=copy_name,
            description=f"Cópia de: {original.metadata.description}",
            tags=original.metadata.tags,
            is_template=False
        )
        
        return {
            "id": duplicated.metadata.id,
            "message": "Workflow duplicado com sucesso",
            "metadata": duplicated.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao duplicar workflow: {str(e)}")

async def run_selenium_flow(execution_id: str, flow_data: FlowData):
    """
    Executa o fluxo Selenium em background
    """
    execution = executions[execution_id]
    
    try:
        # Criar executor
        executor = SeleniumExecutor()
        
        # Executar fluxo
        async for update in executor.execute_flow_async(flow_data, execution_id):
            # Atualizar status da execução
            execution.current_step = update.get("current_step", execution.current_step)
            execution.logs.extend(update.get("logs", []))
            execution.results.update(update.get("results", {}))
            
            if update.get("error"):
                execution.status = ExecutionStatus.ERROR
                execution.error = update["error"]
                execution.finished_at = datetime.now()
                break
        
        # Se chegou até aqui sem erro, execução foi bem-sucedida
        if execution.status == ExecutionStatus.RUNNING:
            execution.status = ExecutionStatus.COMPLETED
            execution.finished_at = datetime.now()
            execution.logs.append("Execução concluída com sucesso!")
            
    except Exception as e:
        execution.status = ExecutionStatus.ERROR
        execution.error = str(e)
        execution.finished_at = datetime.now()
        execution.logs.append(f"Erro na execução: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)