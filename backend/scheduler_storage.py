#!/usr/bin/env python3
"""
Sistema de persistência de agendamentos
Gerencia salvamento e carregamento de agendamentos em JSON
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid


class ScheduleConfig(BaseModel):
    """Configuração de agendamento"""
    schedule_type: str  # daily, weekly, monthly, interval, cron
    time: str = "09:00"  # HH:MM
    timezone: str = "America/Sao_Paulo"
    days_of_week: Optional[List[str]] = None  # ['monday', 'tuesday', ...]
    days_of_month: Optional[List[int]] = None  # [1, 15, 30]
    interval_minutes: Optional[int] = None
    cron_expression: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_executions: Optional[int] = None


class ScheduleExecution(BaseModel):
    """Registro de uma execução"""
    executed_at: datetime
    status: str  # success, error
    error_message: Optional[str] = None
    execution_id: Optional[str] = None


class ScheduleData(BaseModel):
    """Dados completos de um agendamento"""
    id: str
    workflow_id: str
    workflow_name: str
    config: ScheduleConfig
    is_active: bool = True
    is_paused: bool = False
    created_at: datetime
    updated_at: datetime
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    execution_count: int = 0
    execution_history: List[ScheduleExecution] = []


class SchedulerStorage:
    """Gerenciador de persistência de agendamentos"""
    
    def __init__(self):
        # Diretório de dados do usuário (volume Docker ou local)
        data_dir = os.environ.get("DATA_DIR", ".")
        self.storage_dir = Path(data_dir) / "schedules"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.schedules_file = self.storage_dir / "schedules.json"
        self._schedules: Dict[str, ScheduleData] = {}
        self._load_schedules()
    
    def _load_schedules(self) -> None:
        """Carrega agendamentos do arquivo"""
        if self.schedules_file.exists():
            try:
                with open(self.schedules_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for schedule_data in data.get('schedules', []):
                        try:
                            # Converter strings de data para datetime
                            if schedule_data.get('created_at'):
                                schedule_data['created_at'] = datetime.fromisoformat(schedule_data['created_at'])
                            if schedule_data.get('updated_at'):
                                schedule_data['updated_at'] = datetime.fromisoformat(schedule_data['updated_at'])
                            if schedule_data.get('next_run'):
                                schedule_data['next_run'] = datetime.fromisoformat(schedule_data['next_run'])
                            if schedule_data.get('last_run'):
                                schedule_data['last_run'] = datetime.fromisoformat(schedule_data['last_run'])
                            
                            # Converter histórico de execuções
                            if schedule_data.get('execution_history'):
                                for exec_record in schedule_data['execution_history']:
                                    if exec_record.get('executed_at'):
                                        exec_record['executed_at'] = datetime.fromisoformat(exec_record['executed_at'])
                            
                            schedule = ScheduleData(**schedule_data)
                            self._schedules[schedule.id] = schedule
                        except Exception as e:
                            print(f"⚠️ Erro ao carregar agendamento: {e}")
                print(f"✅ Carregados {len(self._schedules)} agendamentos")
            except Exception as e:
                print(f"⚠️ Erro ao carregar arquivo de agendamentos: {e}")
                self._schedules = {}
        else:
            print("📅 Nenhum agendamento salvo encontrado")
    
    def _save_schedules(self) -> None:
        """Salva agendamentos no arquivo"""
        try:
            schedules_list = []
            for schedule in self._schedules.values():
                schedule_dict = schedule.model_dump()
                # Converter datetime para string ISO
                schedule_dict['created_at'] = schedule_dict['created_at'].isoformat()
                schedule_dict['updated_at'] = schedule_dict['updated_at'].isoformat()
                if schedule_dict.get('next_run'):
                    schedule_dict['next_run'] = schedule_dict['next_run'].isoformat()
                if schedule_dict.get('last_run'):
                    schedule_dict['last_run'] = schedule_dict['last_run'].isoformat()
                
                # Converter histórico
                for exec_record in schedule_dict.get('execution_history', []):
                    if exec_record.get('executed_at'):
                        exec_record['executed_at'] = exec_record['executed_at'].isoformat()
                
                schedules_list.append(schedule_dict)
            
            with open(self.schedules_file, 'w', encoding='utf-8') as f:
                json.dump({'schedules': schedules_list}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar agendamentos: {e}")
    
    def save_schedule(
        self,
        workflow_id: str,
        workflow_name: str,
        config: ScheduleConfig,
        schedule_id: str = None
    ) -> ScheduleData:
        """Salva um novo agendamento"""
        now = datetime.now()
        
        if schedule_id and schedule_id in self._schedules:
            # Atualizar existente
            schedule = self._schedules[schedule_id]
            schedule.config = config
            schedule.updated_at = now
            schedule.workflow_name = workflow_name
        else:
            # Criar novo
            schedule_id = schedule_id or str(uuid.uuid4())[:8]
            schedule = ScheduleData(
                id=schedule_id,
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                config=config,
                created_at=now,
                updated_at=now
            )
            self._schedules[schedule_id] = schedule
        
        self._save_schedules()
        return schedule
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduleData]:
        """Obtém um agendamento pelo ID"""
        return self._schedules.get(schedule_id)
    
    def get_schedule_by_workflow(self, workflow_id: str) -> Optional[ScheduleData]:
        """Obtém agendamento de um workflow específico"""
        for schedule in self._schedules.values():
            if schedule.workflow_id == workflow_id:
                return schedule
        return None
    
    def list_schedules(self, include_inactive: bool = False) -> List[ScheduleData]:
        """Lista todos os agendamentos"""
        schedules = list(self._schedules.values())
        if not include_inactive:
            schedules = [s for s in schedules if s.is_active]
        return sorted(schedules, key=lambda s: s.created_at, reverse=True)
    
    def update_schedule(
        self,
        schedule_id: str,
        config: ScheduleConfig = None,
        is_paused: bool = None,
        next_run: datetime = None
    ) -> Optional[ScheduleData]:
        """Atualiza um agendamento existente"""
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return None
        
        if config is not None:
            schedule.config = config
        if is_paused is not None:
            schedule.is_paused = is_paused
        if next_run is not None:
            schedule.next_run = next_run
        
        schedule.updated_at = datetime.now()
        self._save_schedules()
        return schedule
    
    def record_execution(
        self,
        schedule_id: str,
        status: str,
        error_message: str = None,
        execution_id: str = None
    ) -> Optional[ScheduleData]:
        """Registra uma execução"""
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return None
        
        execution = ScheduleExecution(
            executed_at=datetime.now(),
            status=status,
            error_message=error_message,
            execution_id=execution_id
        )
        
        schedule.execution_history.insert(0, execution)
        # Manter apenas as últimas 20 execuções
        schedule.execution_history = schedule.execution_history[:20]
        schedule.last_run = execution.executed_at
        schedule.execution_count += 1
        schedule.updated_at = datetime.now()
        
        self._save_schedules()
        return schedule
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Remove um agendamento"""
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            self._save_schedules()
            return True
        return False
    
    def delete_schedules_for_workflow(self, workflow_id: str) -> int:
        """Remove todos os agendamentos de um workflow"""
        to_delete = [
            sid for sid, s in self._schedules.items() 
            if s.workflow_id == workflow_id
        ]
        for sid in to_delete:
            del self._schedules[sid]
        
        if to_delete:
            self._save_schedules()
        
        return len(to_delete)
    
    def deactivate_schedule(self, schedule_id: str) -> Optional[ScheduleData]:
        """Desativa um agendamento (soft delete)"""
        schedule = self._schedules.get(schedule_id)
        if schedule:
            schedule.is_active = False
            schedule.updated_at = datetime.now()
            self._save_schedules()
        return schedule


# Instância global
scheduler_storage = SchedulerStorage()
