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
from scheduler_service import scheduler_service
from scheduler_storage import ScheduleConfig, ScheduleData

from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    # Startup
    print("🚀 Iniciando VisualFlow Backend...")
    scheduler_service.set_executions_store(executions)
    await scheduler_service.start()
    yield
    # Shutdown
    print("🛑 Encerrando VisualFlow Backend...")
    await scheduler_service.stop()

app = FastAPI(
    title="VisualFlow Backend API", 
    version="2.0.0", 
    description="API para execução de fluxos de automação VisualFlow",
    lifespan=lifespan
)

# Configurar CORS para permitir comunicação com o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir tudo no mode 'single container'
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminho para os arquivos estáticos do frontend (React build)
# Espera-se que o build esteja em '../dist' relativo a este arquivo ou em '/app/dist' no Docker
FRONTEND_DIST_DIR = os.getenv("FRONTEND_DIST_DIR", "/app/dist")

# Diretório de dados (mesma lógica do start.py)
DATA_DIR = os.getenv("DATA_DIR")
if not DATA_DIR:
    # Fallback local se não definido
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(project_root, "visualflow_data")

SHEETS_DIR = os.path.join(DATA_DIR, "workflows", "sheets")
os.makedirs(SHEETS_DIR, exist_ok=True)

try:
    if os.path.exists(FRONTEND_DIST_DIR):
        # Montar arquivos estáticos (JS, CSS, Imagens)
        app.mount("/assets", StaticFiles(directory=f"{FRONTEND_DIST_DIR}/assets"), name="assets")
        print(f"✅ Serving frontend assets from {FRONTEND_DIST_DIR}")
    else:
        print(f"⚠️ Frontend dist dir not found at {FRONTEND_DIST_DIR}. Running in API-only mode.")
    
    # Montar diretório de planilhas para acesso externo (Power BI, etc)
    # Acessível em http://host:port/api/data/sheets/nome_arquivo.xlsx
    app.mount("/api/data/sheets", StaticFiles(directory=SHEETS_DIR), name="sheets")
    print(f"✅ Serving sheets from {SHEETS_DIR} at /api/data/sheets")

except Exception as e:
    print(f"⚠️ Failed to mount static files: {e}")

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
    if os.path.exists(f"{FRONTEND_DIST_DIR}/index.html"):
        from fastapi.responses import FileResponse
        return FileResponse(f"{FRONTEND_DIST_DIR}/index.html")
    return {"message": "Selenium Flow Executor API", "version": "1.0.0", "note": "Frontend not found"}



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
    Salva um novo workflow e configura agendamento automático se houver bloco de schedule
    """
    try:
        saved_workflow = workflow_storage.save_workflow(
            flow_data=request.flow_data,
            name=request.name,
            description=request.description,
            tags=request.tags,
            is_template=request.is_template
        )
        
        workflow_id = saved_workflow.metadata.id
        
        # Verificar se há bloco de agendamento no workflow
        schedule_block = None
        if request.flow_data.rawData and 'nodes' in request.flow_data.rawData:
            for node in request.flow_data.rawData['nodes']:
                if node.get('type') == 'schedule':
                    schedule_block = node.get('data', {}).get('inputs', {})
                    break
        
        # Se tem bloco de agendamento, criar/atualizar schedule
        if schedule_block:
            schedule_type = schedule_block.get('schedule_type', 'daily')
            time_str = schedule_block.get('time', '09:00')
            
            config = ScheduleConfig(
                schedule_type=schedule_type,
                time=time_str,
                timezone=schedule_block.get('timezone', 'America/Sao_Paulo'),
                days_of_week=[d.strip() for d in schedule_block.get('days_of_week', 'monday').split(',')] if schedule_block.get('days_of_week') else None,
                days_of_month=[int(d.strip()) for d in schedule_block.get('days_of_month', '1').split(',') if d.strip().isdigit()] if schedule_block.get('days_of_month') else None,
                interval_minutes=int(schedule_block.get('interval_minutes', 60)) if schedule_block.get('interval_minutes') else None,
                cron_expression=schedule_block.get('cron_expression'),
                start_date=schedule_block.get('start_date'),
                end_date=schedule_block.get('end_date'),
                max_executions=int(schedule_block.get('max_executions')) if schedule_block.get('max_executions') else None
            )
            
            await scheduler_service.add_schedule(workflow_id=workflow_id, config=config)
            
            return {
                "id": workflow_id,
                "message": "Workflow salvo e agendamento configurado!",
                "metadata": saved_workflow.metadata,
                "schedule_configured": True
            }
        else:
            # Se não tem bloco de agendamento, remover agendamento existente (se houver)
            existing_schedule = scheduler_service.get_schedule_by_workflow(workflow_id)
            if existing_schedule:
                await scheduler_service.remove_schedule(existing_schedule.id)
        
        return {
            "id": workflow_id,
            "message": "Workflow salvo com sucesso",
            "metadata": saved_workflow.metadata,
            "schedule_configured": False
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
    Atualiza um workflow existente e reconfigura agendamento se necessário
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
        
        # Verificar se há bloco de agendamento no workflow atualizado
        schedule_configured = False
        if request.flow_data and request.flow_data.rawData and 'nodes' in request.flow_data.rawData:
            schedule_block = None
            for node in request.flow_data.rawData['nodes']:
                if node.get('type') == 'schedule':
                    schedule_block = node.get('data', {}).get('inputs', {})
                    break
            
            if schedule_block:
                schedule_type = schedule_block.get('schedule_type', 'daily')
                time_str = schedule_block.get('time', '09:00')
                
                config = ScheduleConfig(
                    schedule_type=schedule_type,
                    time=time_str,
                    timezone=schedule_block.get('timezone', 'America/Sao_Paulo'),
                    days_of_week=[d.strip() for d in schedule_block.get('days_of_week', 'monday').split(',')] if schedule_block.get('days_of_week') else None,
                    days_of_month=[int(d.strip()) for d in schedule_block.get('days_of_month', '1').split(',') if d.strip().isdigit()] if schedule_block.get('days_of_month') else None,
                    interval_minutes=int(schedule_block.get('interval_minutes', 60)) if schedule_block.get('interval_minutes') else None,
                    cron_expression=schedule_block.get('cron_expression'),
                    start_date=schedule_block.get('start_date'),
                    end_date=schedule_block.get('end_date'),
                    max_executions=int(schedule_block.get('max_executions')) if schedule_block.get('max_executions') else None
                )
                
                await scheduler_service.add_schedule(workflow_id=workflow_id, config=config)
                schedule_configured = True
            else:
                # Se não tem bloco de agendamento, remover agendamento existente
                existing_schedule = scheduler_service.get_schedule_by_workflow(workflow_id)
                if existing_schedule:
                    await scheduler_service.remove_schedule(existing_schedule.id)
        
        message = "Workflow atualizado" + (" e agendamento configurado!" if schedule_configured else " com sucesso")
        return {
            "message": message,
            "metadata": updated_workflow.metadata,
            "schedule_configured": schedule_configured
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
        # Primeiro remover agendamentos associados
        await scheduler_service.on_workflow_deleted(workflow_id)
        
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

# ==================== ROTAS DE AGENDAMENTO ====================

class CreateScheduleRequest(BaseModel):
    workflow_id: str
    schedule_type: str  # daily, weekly, monthly, interval, cron
    time: str = "09:00"
    timezone: str = "America/Sao_Paulo"
    days_of_week: Optional[List[str]] = None
    days_of_month: Optional[List[int]] = None
    interval_minutes: Optional[int] = None
    cron_expression: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_executions: Optional[int] = None

class UpdateScheduleRequest(BaseModel):
    schedule_type: Optional[str] = None
    time: Optional[str] = None
    timezone: Optional[str] = None
    days_of_week: Optional[List[str]] = None
    days_of_month: Optional[List[int]] = None
    interval_minutes: Optional[int] = None
    cron_expression: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_executions: Optional[int] = None

@app.get("/api/schedules")
async def list_schedules():
    """
    Lista todos os agendamentos ativos
    """
    try:
        schedules = scheduler_service.list_schedules()
        return [
            {
                "id": s.id,
                "workflow_id": s.workflow_id,
                "workflow_name": s.workflow_name,
                "config": s.config.model_dump(),
                "is_active": s.is_active,
                "is_paused": s.is_paused,
                "next_run": s.next_run.isoformat() if s.next_run else None,
                "last_run": s.last_run.isoformat() if s.last_run else None,
                "execution_count": s.execution_count,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat()
            }
            for s in schedules
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar agendamentos: {str(e)}")

@app.post("/api/schedules")
async def create_schedule(request: CreateScheduleRequest):
    """
    Cria um novo agendamento para um workflow
    """
    try:
        config = ScheduleConfig(
            schedule_type=request.schedule_type,
            time=request.time,
            timezone=request.timezone,
            days_of_week=request.days_of_week,
            days_of_month=request.days_of_month,
            interval_minutes=request.interval_minutes,
            cron_expression=request.cron_expression,
            start_date=request.start_date,
            end_date=request.end_date,
            max_executions=request.max_executions
        )
        
        schedule = await scheduler_service.add_schedule(
            workflow_id=request.workflow_id,
            config=config
        )
        
        return {
            "id": schedule.id,
            "message": "Agendamento criado com sucesso",
            "next_run": schedule.next_run.isoformat() if schedule.next_run else None
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar agendamento: {str(e)}")

@app.get("/api/schedules/{schedule_id}")
async def get_schedule(schedule_id: str):
    """
    Retorna detalhes de um agendamento
    """
    schedule = scheduler_service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    return {
        "id": schedule.id,
        "workflow_id": schedule.workflow_id,
        "workflow_name": schedule.workflow_name,
        "config": schedule.config.model_dump(),
        "is_active": schedule.is_active,
        "is_paused": schedule.is_paused,
        "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
        "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
        "execution_count": schedule.execution_count,
        "execution_history": [
            {
                "executed_at": e.executed_at.isoformat(),
                "status": e.status,
                "error_message": e.error_message,
                "execution_id": e.execution_id
            }
            for e in schedule.execution_history[:10]
        ],
        "created_at": schedule.created_at.isoformat(),
        "updated_at": schedule.updated_at.isoformat()
    }

@app.put("/api/schedules/{schedule_id}")
async def update_schedule(schedule_id: str, request: UpdateScheduleRequest):
    """
    Atualiza um agendamento existente
    """
    try:
        existing = scheduler_service.get_schedule(schedule_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        
        # Mesclar com config existente
        current_config = existing.config.model_dump()
        update_data = request.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            if value is not None:
                current_config[key] = value
        
        new_config = ScheduleConfig(**current_config)
        
        schedule = await scheduler_service.update_schedule(schedule_id, config=new_config)
        
        return {
            "message": "Agendamento atualizado com sucesso",
            "next_run": schedule.next_run.isoformat() if schedule.next_run else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar agendamento: {str(e)}")

@app.delete("/api/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """
    Remove um agendamento
    """
    try:
        success = await scheduler_service.remove_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        
        return {"message": "Agendamento removido com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover agendamento: {str(e)}")

@app.post("/api/schedules/{schedule_id}/pause")
async def pause_schedule(schedule_id: str):
    """
    Pausa um agendamento
    """
    schedule = await scheduler_service.pause_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    return {"message": "Agendamento pausado com sucesso"}

@app.post("/api/schedules/{schedule_id}/resume")
async def resume_schedule(schedule_id: str):
    """
    Retoma um agendamento pausado
    """
    schedule = await scheduler_service.resume_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    return {
        "message": "Agendamento retomado com sucesso",
        "next_run": schedule.next_run.isoformat() if schedule.next_run else None
    }

@app.post("/api/schedules/{schedule_id}/run-now")
async def run_schedule_now(schedule_id: str):
    """
    Executa um workflow agendado imediatamente
    """
    try:
        workflow_id = await scheduler_service.run_now(schedule_id)
        return {
            "message": "Execução iniciada",
            "workflow_id": workflow_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar: {str(e)}")

@app.get("/api/workflows/{workflow_id}/schedule")
async def get_workflow_schedule(workflow_id: str):
    """
    Retorna o agendamento de um workflow específico
    """
    schedule = scheduler_service.get_schedule_by_workflow(workflow_id)
    if not schedule:
        return {"has_schedule": False}
    
    return {
        "has_schedule": True,
        "schedule": {
            "id": schedule.id,
            "config": schedule.config.model_dump(),
            "is_paused": schedule.is_paused,
            "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
            "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
            "execution_count": schedule.execution_count
        }
    }



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

@app.get("/api/data/list-files")
async def list_sheet_files(path: str = "", recursive: bool = True):
    """
    Lista arquivos na pasta de planilhas para consumo externo (ex: Power BI).
    Por padrão lista RECURSIVAMENTE (inclui subpastas).
    Retorna JSON com nome, caminho relativo e URL de download.
    """
    try:
        # Sanitizar path para evitar traversal
        target_dir = SHEETS_DIR
        if path:
            # Remove .. e barras iniciais
            clean_path = path.replace('..', '').lstrip('/\\')
            target_dir = os.path.join(SHEETS_DIR, clean_path)
            
        if not os.path.exists(target_dir):
            return []
            
        files_data = []
        base_url = "http://localhost:8000/api/data/sheets" # Ajustar se estiver atrás de proxy/docker
        
        # Usar os.walk para listar recursivamente
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.startswith('.'):
                    continue
                    
                full_path = os.path.join(root, file)
                
                # Calcular caminho relativo à pasta SHEETS_DIR para a URL correta
                # Ex: se o arquivo é .../sheets/sub/arquivo.xlsx, rel_path é "sub/arquivo.xlsx"
                rel_path_from_sheets = os.path.relpath(full_path, SHEETS_DIR).replace('\\', '/')
                
                # Caminho relativo ao target_dir (apenas para info de display se necessário)
                rel_path_from_search = os.path.relpath(full_path, target_dir).replace('\\', '/')
                
                files_data.append({
                    "name": file,
                    "folder": os.path.dirname(rel_path_from_sheets),
                    "relative_path": rel_path_from_sheets,
                    "url": f"{base_url}/{rel_path_from_sheets}",
                    "size": os.path.getsize(full_path),
                    "updated_at": datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat()
                })

        return files_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar arquivos: {str(e)}")

@app.get("/visualflow-icon.svg")
async def get_icon():
    """Serves the application icon"""
    icon_path = os.path.join(FRONTEND_DIST_DIR, "visualflow-icon.svg")
    if os.path.exists(icon_path):
        from fastapi.responses import FileResponse
        return FileResponse(icon_path)
    return HTTPException(status_code=404, detail="Icon not found")

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Se começar com api, deixa o FastAPI lidar (vai dar 404 se não existir rota definida)
    # Importante: Como esta é a última rota, qualquer requisição api/ que cair aqui
    # significa que não deu match em nenhuma rota anterior.
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    
    # Para qualquer outra rota, retorna o index.html (SPA routing)
    if os.path.exists(f"{FRONTEND_DIST_DIR}/index.html"):
        from fastapi.responses import FileResponse
        return FileResponse(f"{FRONTEND_DIST_DIR}/index.html")
    
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)