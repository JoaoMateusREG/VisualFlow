import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Clock, Play, Pause, Trash2, RotateCcw, X, ChevronDown, ChevronUp, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { 
  schedulerService, 
  Schedule, 
  ScheduleConfig,
  ScheduleDetails
} from '../services/schedulerService';

interface SchedulerPanelProps {
  isOpen: boolean;
  onClose: () => void;
  workflows: Array<{ id: string; name: string }>;
  onWorkflowExecuted?: () => void;
}

const DAYS_OF_WEEK = [
  { value: 'monday', label: 'Segunda' },
  { value: 'tuesday', label: 'Terça' },
  { value: 'wednesday', label: 'Quarta' },
  { value: 'thursday', label: 'Quinta' },
  { value: 'friday', label: 'Sexta' },
  { value: 'saturday', label: 'Sábado' },
  { value: 'sunday', label: 'Domingo' },
];

/**
 * Formata data ISO para formato local brasileiro
 */
const formatDateTime = (dateStr: string | null): string => {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
};

/**
 * Gera descrição legível do agendamento baseado na configuração
 */
const getScheduleDescription = (config: ScheduleConfig): string => {
  switch (config.schedule_type) {
    case 'daily':
      return `Todos os dias às ${config.time}`;
    case 'weekly':
      const days = config.days_of_week?.map(d => 
        DAYS_OF_WEEK.find(dw => dw.value === d)?.label || d
      ).join(', ') || 'Segunda';
      return `${days} às ${config.time}`;
    case 'monthly':
      const monthDays = config.days_of_month?.join(', ') || '1';
      return `Dia(s) ${monthDays} às ${config.time}`;
    case 'interval':
      return `A cada ${config.interval_minutes} minutos`;
    case 'cron':
      return config.cron_expression || '0 9 * * *';
    default:
      return 'Agendamento personalizado';
  }
};

/**
 * Painel de Gerenciamento de Agendamentos
 * Permite visualizar, pausar, retomar e remover agendamentos de workflows
 */
const SchedulerPanel: React.FC<SchedulerPanelProps> = ({
  isOpen,
  onClose,
  onWorkflowExecuted,
}) => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSchedule, setExpandedSchedule] = useState<string | null>(null);
  const [scheduleDetails, setScheduleDetails] = useState<ScheduleDetails | null>(null);

  /**
   * Carrega a lista de agendamentos do backend
   */
  const loadSchedules = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await schedulerService.listSchedules();
      setSchedules(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar agendamentos');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      loadSchedules();
    }
  }, [isOpen, loadSchedules]);

  /**
   * Carrega detalhes de histórico de um agendamento específico
   */
  const loadScheduleDetails = async (scheduleId: string) => {
    try {
      const details = await schedulerService.getSchedule(scheduleId);
      setScheduleDetails(details);
    } catch (err) {
      console.error('Erro ao carregar detalhes:', err);
    }
  };

  const handleExpand = (scheduleId: string) => {
    if (expandedSchedule === scheduleId) {
      setExpandedSchedule(null);
      setScheduleDetails(null);
    } else {
      setExpandedSchedule(scheduleId);
      loadScheduleDetails(scheduleId);
    }
  };

  /**
   * Pausa ou retoma um agendamento
   */
  const handlePauseResume = async (schedule: Schedule) => {
    try {
      if (schedule.is_paused) {
        await schedulerService.resumeSchedule(schedule.id);
      } else {
        await schedulerService.pauseSchedule(schedule.id);
      }
      loadSchedules();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao alterar estado');
    }
  };

  /**
   * Força execução imediata de um agendamento
   */
  const handleRunNow = async (scheduleId: string) => {
    try {
      await schedulerService.runNow(scheduleId);
      alert('Execução iniciada! Verifique o painel de execuções.');
      onWorkflowExecuted?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao executar');
    }
  };

  /**
   * Remove agendamento
   */
  const handleDelete = async (scheduleId: string) => {
    if (!window.confirm('Tem certeza que deseja remover este agendamento? O bloco de agendamento no workflow permanecerá, mas o agendamento será desativado até você salvar o workflow novamente.')) {
      return;
    }
    
    try {
      await schedulerService.deleteSchedule(scheduleId);
      loadSchedules();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao remover');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col border border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-violet-600/20 rounded-lg">
              <Calendar className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Agendamentos</h2>
              <p className="text-sm text-gray-400">Workflows com execução programada</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {error && (
            <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center gap-2 text-red-300">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          {/* Info Banner */}
          <div className="mb-4 p-3 bg-violet-600/20 border border-violet-500/30 rounded-lg">
            <p className="text-sm text-violet-200">
              💡 <strong>Dica:</strong> Para criar um agendamento, adicione o bloco{' '}
              <strong>Agendamento</strong> ao seu workflow e salve no Gerenciador de Workflows.
            </p>
          </div>

          {/* Schedules List */}
          {loading ? (
            <div className="flex items-center justify-center py-8 text-gray-400">
              <Loader2 className="w-6 h-6 animate-spin mr-2" />
              Carregando...
            </div>
          ) : schedules.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="font-medium text-white mb-1">Nenhum agendamento ativo</p>
              <p className="text-sm mb-3">Para agendar um workflow:</p>
              <ol className="text-sm text-left max-w-xs mx-auto space-y-1">
                <li>1. Arraste o bloco <strong className="text-violet-400">Agendamento</strong> para seu workflow</li>
                <li>2. Configure o horário desejado no bloco</li>
                <li>3. Salve o workflow no <strong className="text-purple-400">Gerenciador de Workflows</strong></li>
              </ol>
              <p className="text-xs mt-3 text-gray-500">O agendamento será criado automaticamente!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {schedules.map((schedule) => (
                <div
                  key={schedule.id}
                  className="bg-gray-700/50 rounded-lg border border-gray-600 overflow-hidden"
                >
                  {/* Schedule Header */}
                  <div
                    className="p-4 cursor-pointer hover:bg-gray-700/70 transition-colors"
                    onClick={() => handleExpand(schedule.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          schedule.is_paused ? 'bg-yellow-400' : 'bg-green-400'
                        }`} />
                        <div>
                          <h4 className="text-white font-medium">{schedule.workflow_name}</h4>
                          <p className="text-sm text-gray-400">
                            {getScheduleDescription(schedule.config)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-1 rounded ${
                          schedule.is_paused
                            ? 'bg-yellow-500/20 text-yellow-300'
                            : 'bg-green-500/20 text-green-300'
                        }`}>
                          {schedule.is_paused ? 'Pausado' : 'Ativo'}
                        </span>
                        {expandedSchedule === schedule.id ? (
                          <ChevronUp className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        )}
                      </div>
                    </div>
                    
                    <div className="mt-2 flex items-center gap-4 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        Próxima: {formatDateTime(schedule.next_run)}
                      </span>
                      {schedule.last_run && (
                        <span>Última: {formatDateTime(schedule.last_run)}</span>
                      )}
                      <span>Execuções: {schedule.execution_count}</span>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {expandedSchedule === schedule.id && (
                    <div className="border-t border-gray-600 p-4 bg-gray-800/50">
                      {/* Actions */}
                      <div className="flex flex-wrap gap-2 mb-4">
                        <button
                          onClick={() => handlePauseResume(schedule)}
                          className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-1 transition-colors ${
                            schedule.is_paused
                              ? 'bg-green-600 hover:bg-green-700 text-white'
                              : 'bg-yellow-600 hover:bg-yellow-700 text-white'
                          }`}
                        >
                          {schedule.is_paused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                          {schedule.is_paused ? 'Retomar' : 'Pausar'}
                        </button>
                        <button
                          onClick={() => handleRunNow(schedule.id)}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm flex items-center gap-1 transition-colors"
                        >
                          <RotateCcw className="w-3 h-3" />
                          Executar Agora
                        </button>
                        <button
                          onClick={() => handleDelete(schedule.id)}
                          className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm flex items-center gap-1 transition-colors"
                        >
                          <Trash2 className="w-3 h-3" />
                          Remover
                        </button>
                      </div>

                      {/* Execution History */}
                      {scheduleDetails?.execution_history && scheduleDetails.execution_history.length > 0 && (
                        <div>
                          <h5 className="text-sm font-medium text-gray-300 mb-2">Histórico de Execuções</h5>
                          <div className="space-y-1 max-h-40 overflow-y-auto">
                            {scheduleDetails.execution_history.map((exec, idx) => (
                              <div
                                key={idx}
                                className="flex items-center justify-between text-xs p-2 bg-gray-700/50 rounded"
                              >
                                <div className="flex items-center gap-2">
                                  {exec.status === 'success' ? (
                                    <CheckCircle2 className="w-3 h-3 text-green-400" />
                                  ) : (
                                    <AlertCircle className="w-3 h-3 text-red-400" />
                                  )}
                                  <span className="text-gray-300">
                                    {formatDateTime(exec.executed_at)}
                                  </span>
                                </div>
                                <span className={exec.status === 'success' ? 'text-green-400' : 'text-red-400'}>
                                  {exec.status === 'success' ? 'Sucesso' : 'Erro'}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SchedulerPanel;
