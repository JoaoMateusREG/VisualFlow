#!/usr/bin/env python3
"""
Serviço de agendamento de workflows usando APScheduler
Executa workflows automaticamente nos horários configurados
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
import pytz

from scheduler_storage import scheduler_storage, ScheduleConfig, ScheduleData
from workflow_storage import workflow_storage
from models import FlowData, ExecutionStatus, ExecutionResult

logger = logging.getLogger(__name__)


class SchedulerService:
    """Serviço de agendamento de workflows"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            timezone=pytz.timezone('America/Sao_Paulo')
        )
        self._executor = None
        self._executions: Dict[str, ExecutionResult] = {}
        self._is_running = False
    
    def set_executions_store(self, executions: Dict[str, ExecutionResult]):
        """Define o dicionário de execuções compartilhado com main.py"""
        self._executions = executions
    
    async def start(self):
        """Inicia o scheduler e restaura agendamentos"""
        if self._is_running:
            logger.info("⚠️ Scheduler já está rodando")
            return
        
        logger.info("🚀 Iniciando serviço de agendamento...")
        
        try:
            self.scheduler.start()
            self._is_running = True
            logger.info("✅ Scheduler iniciado com sucesso")
            
            # Restaurar agendamentos salvos
            await self._restore_schedules()
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar scheduler: {e}")
            raise
    
    async def stop(self):
        """Para o scheduler graciosamente"""
        if self._is_running:
            logger.info("🛑 Parando serviço de agendamento...")
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("✅ Scheduler parado")
    
    async def _restore_schedules(self):
        """Restaura agendamentos salvos após reinício"""
        schedules = scheduler_storage.list_schedules()
        restored_count = 0
        
        for schedule in schedules:
            if schedule.is_active and not schedule.is_paused:
                try:
                    # Verificar se o workflow ainda existe
                    workflow = workflow_storage.load_workflow(schedule.workflow_id)
                    if not workflow:
                        logger.warning(f"⚠️ Workflow {schedule.workflow_id} não encontrado, desativando agendamento")
                        scheduler_storage.deactivate_schedule(schedule.id)
                        continue
                    
                    # Adicionar job
                    self._add_job_for_schedule(schedule)
                    restored_count += 1
                    logger.info(f"✅ Agendamento restaurado: {schedule.workflow_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao restaurar agendamento {schedule.id}: {e}")
        
        logger.info(f"📅 {restored_count} agendamentos restaurados")
    
    def _create_trigger(self, config: ScheduleConfig):
        """Cria o trigger apropriado baseado na configuração"""
        tz = pytz.timezone(config.timezone or 'America/Sao_Paulo')
        
        # Extrair hora e minuto
        hour, minute = 9, 0
        if config.time:
            try:
                parts = config.time.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
            except:
                pass
        
        if config.schedule_type == 'daily':
            return CronTrigger(hour=hour, minute=minute, timezone=tz)
        
        elif config.schedule_type == 'weekly':
            days = config.days_of_week or ['monday']
            # Converter nomes para números (0=monday)
            day_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2,
                'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
            }
            day_numbers = [str(day_map.get(d.lower(), 0)) for d in days]
            return CronTrigger(
                day_of_week=','.join(day_numbers),
                hour=hour,
                minute=minute,
                timezone=tz
            )
        
        elif config.schedule_type == 'monthly':
            days = config.days_of_month or [1]
            return CronTrigger(
                day=','.join(str(d) for d in days),
                hour=hour,
                minute=minute,
                timezone=tz
            )
        
        elif config.schedule_type == 'interval':
            minutes = config.interval_minutes or 60
            return IntervalTrigger(minutes=minutes, timezone=tz)
        
        elif config.schedule_type == 'cron':
            # Parse expressão cron: minuto hora dia mês dia_semana
            expr = config.cron_expression or '0 9 * * *'
            parts = expr.split()
            if len(parts) >= 5:
                return CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4],
                    timezone=tz
                )
        
        # Default: diário às 9h
        return CronTrigger(hour=9, minute=0, timezone=tz)
    
    def _add_job_for_schedule(self, schedule: ScheduleData):
        """Adiciona um job no scheduler para um agendamento"""
        job_id = f"schedule_{schedule.id}"
        
        # Remover job existente se houver
        existing_job = self.scheduler.get_job(job_id)
        if existing_job:
            self.scheduler.remove_job(job_id)
        
        # Criar trigger
        trigger = self._create_trigger(schedule.config)
        
        # Adicionar job
        job = self.scheduler.add_job(
            self._execute_scheduled_workflow,
            trigger=trigger,
            id=job_id,
            args=[schedule.id, schedule.workflow_id],
            name=f"Workflow: {schedule.workflow_name}",
            replace_existing=True,
            misfire_grace_time=300  # 5 minutos de tolerância
        )
        
        # Atualizar próxima execução
        if job.next_run_time:
            scheduler_storage.update_schedule(
                schedule.id,
                next_run=job.next_run_time.replace(tzinfo=None)
            )
        
        logger.info(f"📅 Job adicionado: {schedule.workflow_name} - Próxima: {job.next_run_time}")
    
    async def _execute_scheduled_workflow(self, schedule_id: str, workflow_id: str):
        """Executa um workflow agendado"""
        logger.info(f"⏰ Executando workflow agendado: {workflow_id}")
        
        try:
            # Carregar workflow
            workflow = workflow_storage.load_workflow(workflow_id)
            if not workflow:
                logger.error(f"❌ Workflow {workflow_id} não encontrado")
                scheduler_storage.record_execution(
                    schedule_id, 
                    status='error', 
                    error_message='Workflow não encontrado'
                )
                # Desativar agendamento se workflow não existe
                scheduler_storage.deactivate_schedule(schedule_id)
                self.scheduler.remove_job(f"schedule_{schedule_id}")
                return
            
            # Importar executor aqui para evitar import circular
            from selenium_executor import SeleniumExecutor
            
            flow_data = workflow.flow_data
            
            # Gerar ID de execução
            import uuid
            execution_id = str(uuid.uuid4())
            
            # Criar resultado de execução
            execution_result = ExecutionResult(
                id=execution_id,
                status=ExecutionStatus.RUNNING,
                started_at=datetime.now(),
                flow_name=flow_data.metadata.name,
                total_steps=len(flow_data.executionOrder),
                current_step=0,
                logs=[f"[AGENDADO] Iniciando execução do fluxo: {flow_data.metadata.name}"],
                results={}
            )
            
            # Armazenar execução
            self._executions[execution_id] = execution_result
            
            logger.info(f"🚀 Execução iniciada: {execution_id}")
            
            # Executar workflow
            executor = SeleniumExecutor()
            
            async for update in executor.execute_flow_async(flow_data, execution_id):
                execution_result.current_step = update.get("current_step", execution_result.current_step)
                execution_result.logs.extend(update.get("logs", []))
                execution_result.results.update(update.get("results", {}))
                
                if update.get("error"):
                    execution_result.status = ExecutionStatus.ERROR
                    execution_result.error = update["error"]
                    execution_result.finished_at = datetime.now()
                    break
            
            # Finalizar
            if execution_result.status == ExecutionStatus.RUNNING:
                execution_result.status = ExecutionStatus.COMPLETED
                execution_result.finished_at = datetime.now()
                execution_result.logs.append("Execução agendada concluída com sucesso!")
            
            # Registrar execução
            status = 'success' if execution_result.status == ExecutionStatus.COMPLETED else 'error'
            scheduler_storage.record_execution(
                schedule_id,
                status=status,
                error_message=execution_result.error,
                execution_id=execution_id
            )
            
            # Atualizar próxima execução
            job = self.scheduler.get_job(f"schedule_{schedule_id}")
            if job and job.next_run_time:
                scheduler_storage.update_schedule(
                    schedule_id,
                    next_run=job.next_run_time.replace(tzinfo=None)
                )
            
            logger.info(f"✅ Execução agendada finalizada: {status}")
            
        except Exception as e:
            logger.error(f"❌ Erro na execução agendada: {e}")
            scheduler_storage.record_execution(
                schedule_id,
                status='error',
                error_message=str(e)
            )
    
    async def add_schedule(
        self,
        workflow_id: str,
        config: ScheduleConfig
    ) -> ScheduleData:
        """Adiciona um novo agendamento"""
        # Verificar se workflow existe
        workflow = workflow_storage.load_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} não encontrado")
        
        # Verificar se já existe agendamento para este workflow
        existing = scheduler_storage.get_schedule_by_workflow(workflow_id)
        if existing:
            # Atualizar existente
            schedule = scheduler_storage.save_schedule(
                workflow_id=workflow_id,
                workflow_name=workflow.metadata.name,
                config=config,
                schedule_id=existing.id
            )
        else:
            # Criar novo
            schedule = scheduler_storage.save_schedule(
                workflow_id=workflow_id,
                workflow_name=workflow.metadata.name,
                config=config
            )
        
        # Adicionar job
        self._add_job_for_schedule(schedule)
        
        logger.info(f"✅ Agendamento criado/atualizado: {schedule.workflow_name}")
        return schedule
    
    async def update_schedule(
        self,
        schedule_id: str,
        config: ScheduleConfig
    ) -> Optional[ScheduleData]:
        """Atualiza um agendamento existente"""
        schedule = scheduler_storage.get_schedule(schedule_id)
        if not schedule:
            return None
        
        # Atualizar storage
        schedule = scheduler_storage.update_schedule(schedule_id, config=config)
        
        # Atualizar job
        if schedule and not schedule.is_paused:
            self._add_job_for_schedule(schedule)
        
        return schedule
    
    async def remove_schedule(self, schedule_id: str) -> bool:
        """Remove um agendamento"""
        # Remover job
        job_id = f"schedule_{schedule_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Remover do storage
        return scheduler_storage.delete_schedule(schedule_id)
    
    async def pause_schedule(self, schedule_id: str) -> Optional[ScheduleData]:
        """Pausa um agendamento"""
        schedule = scheduler_storage.update_schedule(schedule_id, is_paused=True)
        if schedule:
            job_id = f"schedule_{schedule_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.pause_job(job_id)
            logger.info(f"⏸️ Agendamento pausado: {schedule.workflow_name}")
        return schedule
    
    async def resume_schedule(self, schedule_id: str) -> Optional[ScheduleData]:
        """Retoma um agendamento pausado"""
        schedule = scheduler_storage.update_schedule(schedule_id, is_paused=False)
        if schedule:
            job_id = f"schedule_{schedule_id}"
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.resume_job(job_id)
            else:
                # Job não existe, recriar
                self._add_job_for_schedule(schedule)
            logger.info(f"▶️ Agendamento retomado: {schedule.workflow_name}")
        return schedule
    
    async def run_now(self, schedule_id: str) -> str:
        """Executa um workflow agendado imediatamente"""
        schedule = scheduler_storage.get_schedule(schedule_id)
        if not schedule:
            raise ValueError("Agendamento não encontrado")
        
        # Executar em background
        asyncio.create_task(
            self._execute_scheduled_workflow(schedule_id, schedule.workflow_id)
        )
        
        return schedule.workflow_id
    
    def list_schedules(self) -> List[ScheduleData]:
        """Lista todos os agendamentos ativos"""
        return scheduler_storage.list_schedules()
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduleData]:
        """Obtém detalhes de um agendamento"""
        return scheduler_storage.get_schedule(schedule_id)
    
    def get_schedule_by_workflow(self, workflow_id: str) -> Optional[ScheduleData]:
        """Obtém agendamento de um workflow"""
        return scheduler_storage.get_schedule_by_workflow(workflow_id)
    
    async def on_workflow_deleted(self, workflow_id: str):
        """Chamado quando um workflow é deletado - remove agendamentos associados"""
        schedule = scheduler_storage.get_schedule_by_workflow(workflow_id)
        if schedule:
            await self.remove_schedule(schedule.id)
            logger.info(f"🗑️ Agendamento removido após exclusão do workflow: {workflow_id}")


# Instância singleton
scheduler_service = SchedulerService()
