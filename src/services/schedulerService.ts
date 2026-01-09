/**
 * Serviço para gerenciar agendamentos de workflows
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

export interface ScheduleConfig {
  schedule_type: 'daily' | 'weekly' | 'monthly' | 'interval' | 'cron';
  time: string;
  timezone: string;
  days_of_week?: string[];
  days_of_month?: number[];
  interval_minutes?: number;
  cron_expression?: string;
  start_date?: string;
  end_date?: string;
  max_executions?: number;
}

export interface Schedule {
  id: string;
  workflow_id: string;
  workflow_name: string;
  config: ScheduleConfig;
  is_active: boolean;
  is_paused: boolean;
  next_run: string | null;
  last_run: string | null;
  execution_count: number;
  created_at: string;
  updated_at: string;
}

export interface ScheduleExecution {
  executed_at: string;
  status: 'success' | 'error';
  error_message?: string;
  execution_id?: string;
}

export interface ScheduleDetails extends Schedule {
  execution_history: ScheduleExecution[];
}

export interface WorkflowSchedule {
  has_schedule: boolean;
  schedule?: {
    id: string;
    config: ScheduleConfig;
    is_paused: boolean;
    next_run: string | null;
    last_run: string | null;
    execution_count: number;
  };
}

/**
 * Lista todos os agendamentos
 */
export async function listSchedules(): Promise<Schedule[]> {
  const response = await fetch(`${API_BASE}/api/schedules`);
  if (!response.ok) {
    throw new Error('Erro ao listar agendamentos');
  }
  return response.json();
}

/**
 * Cria um novo agendamento
 */
export async function createSchedule(
  workflowId: string,
  config: ScheduleConfig
): Promise<{ id: string; message: string; next_run: string | null }> {
  const response = await fetch(`${API_BASE}/api/schedules`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      workflow_id: workflowId,
      ...config,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erro ao criar agendamento');
  }
  
  return response.json();
}

/**
 * Obtém detalhes de um agendamento
 */
export async function getSchedule(scheduleId: string): Promise<ScheduleDetails> {
  const response = await fetch(`${API_BASE}/api/schedules/${scheduleId}`);
  if (!response.ok) {
    throw new Error('Agendamento não encontrado');
  }
  return response.json();
}

/**
 * Atualiza um agendamento
 */
export async function updateSchedule(
  scheduleId: string,
  config: Partial<ScheduleConfig>
): Promise<{ message: string; next_run: string | null }> {
  const response = await fetch(`${API_BASE}/api/schedules/${scheduleId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erro ao atualizar agendamento');
  }
  
  return response.json();
}

/**
 * Remove um agendamento
 */
export async function deleteSchedule(scheduleId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/schedules/${scheduleId}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error('Erro ao remover agendamento');
  }
}

/**
 * Pausa um agendamento
 */
export async function pauseSchedule(scheduleId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/schedules/${scheduleId}/pause`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Erro ao pausar agendamento');
  }
}

/**
 * Retoma um agendamento
 */
export async function resumeSchedule(scheduleId: string): Promise<{ next_run: string | null }> {
  const response = await fetch(`${API_BASE}/api/schedules/${scheduleId}/resume`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Erro ao retomar agendamento');
  }
  
  return response.json();
}

/**
 * Executa imediatamente
 */
export async function runNow(scheduleId: string): Promise<{ workflow_id: string }> {
  const response = await fetch(`${API_BASE}/api/schedules/${scheduleId}/run-now`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error('Erro ao executar workflow');
  }
  
  return response.json();
}

/**
 * Obtém agendamento de um workflow específico
 */
export async function getWorkflowSchedule(workflowId: string): Promise<WorkflowSchedule> {
  const response = await fetch(`${API_BASE}/api/workflows/${workflowId}/schedule`);
  if (!response.ok) {
    throw new Error('Erro ao obter agendamento do workflow');
  }
  return response.json();
}

export const schedulerService = {
  listSchedules,
  createSchedule,
  getSchedule,
  updateSchedule,
  deleteSchedule,
  pauseSchedule,
  resumeSchedule,
  runNow,
  getWorkflowSchedule,
};

export default schedulerService;
