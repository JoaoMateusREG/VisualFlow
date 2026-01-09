# Documentação da API VisualFlow v2.0

Esta API fornece acesso completo às funcionalidades de automação, gerenciamento de workflows, agendamento de tarefas e acesso aos dados gerados.

Base URL: `http://localhost:8000`

## 📚 Sumário
- [Execução de Fluxos](#execução-de-fluxos)
- [Gerenciamento de Workflows](#gerenciamento-de-workflows)
- [Sistema de Agendamento](#sistema-de-agendamento)
- [Acesso a Dados (Planilhas)](#acesso-a-dados-planilhas)
- [Sistema](#sistema)

---

## Execução de Fluxos

### `POST /api/execute-flow`
Inicia a execução de um workflow em segundo plano.

**Request Body:**
```json
{
  "metadata": { "name": "Nome do Fluxo", ... },
  "executionOrder": [ ... ] // Array de nós do fluxo
}
```

**Response:**
```json
{
  "execution_id": "uuid-v4",
  "status": "started",
  "message": "Execução iniciada com sucesso"
}
```

### `GET /api/execution/{execution_id}`
Retorna o status detalhado e logs de uma execução específica.

### `GET /api/executions`
Lista todas as execuções recentes (memória).

### `DELETE /api/execution/{execution_id}`
Cancela uma execução que esteja em andamento.

### `POST /api/validate-flow`
Valida a estrutura de um workflow sem executá-lo, verificando conexões e configurações obrigatórias.

---

## Gerenciamento de Workflows

### `GET /api/workflows`
Lista todos os workflows salvos.
- `include_templates` (query param, bool): Inclui templates na listagem (default: true).

### `POST /api/workflows`
Salva um novo workflow. Se o workflow contiver um bloco `Schedule`, o agendamento é criado automaticamente.

**Request Body:**
```json
{
  "flow_data": { ... },
  "name": "Meu Workflow",
  "description": "Automação de vendas",
  "tags": ["vendas", "produção"],
  "is_template": false
}
```

### `GET /api/workflows/{workflow_id}`
Retorna os dados completos de um workflow salvo.

### `PUT /api/workflows/{workflow_id}`
Atualiza um workflow existente. Atualiza automaticamente o agendamento associado se houver blocos de schedule.

### `DELETE /api/workflows/{workflow_id}`
Remove um workflow e seus agendamentos associados.

### `POST /api/workflows/{workflow_id}/duplicate`
Cria uma cópia do workflow.
- `name` (query param, string): Nome opcional para a cópia.

### `GET /api/workflows/search`
Busca workflows.
- `q` (query param): Texto para busca em nome/descrição.
- `tags` (query param): Tags separadas por vírgula.

---

## Sistema de Agendamento

### `GET /api/schedules`
Lista todos os agendamentos configurados no sistema.

### `POST /api/schedules`
Cria manualmente um agendamento (geralmente gerenciado automaticamente pelo bloco de workflow).

### `GET /api/schedules/{schedule_id}`
Retorna detalhes de um agendamento, incluindo histórico de execuções.

### `PUT /api/schedules/{schedule_id}`
Atualiza configurações de um agendamento.

### `DELETE /api/schedules/{schedule_id}`
Remove um agendamento.

### `POST /api/schedules/{schedule_id}/pause`
Pausa um agendamento (não será executado até ser retomado).

### `POST /api/schedules/{schedule_id}/resume`
Retoma um agendamento pausado.

### `POST /api/schedules/{schedule_id}/run-now`
Força a execução imediata de um workflow agendado, independente do cronograma.

### `GET /api/workflows/{workflow_id}/schedule`
Atalho para encontrar o agendamento associado a um workflow específico.

---

## Acesso a Dados (Planilhas)

### `GET /api/data/list-files`
Lista todos os arquivos de planilhas gerados, incluindo subpastas (recursivo). Ideal para integração com Power BI / Excel.

**Query Params:**
- `path` (opcional): Filtrar por subpasta específica.
- `recursive` (opcional, default: true): Se false, lista apenas nível atual.

**Response Example:**
```json
[
  {
    "name": "vendas.xlsx",
    "folder": "loja_01",
    "relative_path": "loja_01/vendas.xlsx",
    "url": "http://localhost:8000/api/data/sheets/loja_01/vendas.xlsx",
    "size": 15400,
    "updated_at": "2024-01-09T15:00:00"
  }
]
```

### `GET /api/data/sheets/{caminho_arquivo}`
Endpoint de download direto para arquivos de planilhas.
Permite acessar arquivos em subpastas, ex: `/api/data/sheets/relatorios/arquivo.xlsx`.

---

## Sistema

### `GET /visualflow-icon.svg`
Retorna o ícone da aplicação.

### `GET /`
Serve a aplicação frontend (React) quando construída.
