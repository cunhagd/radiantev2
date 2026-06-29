# Tasks: Bloco de Metricas de Uso

**Input**: Design documents from `specs/016-metrics-usage-block/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test tasks sao opcionais — feature nao requer novos testes (mudancas sao incrementais em codigo existente).

**Organization**: Tasks grouped by single user story, executed sequentially.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app.py`, `backend/pipeline.py`, `backend/metrics.py`
- **Frontend**: `frontend/index.html`, `frontend/js/metrics.js`, `frontend/css/components.css`
- **Test fixtures**: `frontend/tests/setup.js`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: N/A — feature de exibicao de metricas sobre codigo ja existente.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: N/A — sem prerrequisitos bloqueantes.

---

## Phase 3: User Story 1 - Visualizar metricas detalhadas de uso da IA (Priority: P1) 🎯 MVP

**Goal**: Incluir as metricas de tokens/custos no JSON de resultado do backend e renderiza-las no frontend no card "Metricas de Uso", posicionado abaixo do bloco de "Provisao de Cifras".

**Independent Test**: Ao completar uma analise 1x, o bloco "Metricas de Uso" aparece com tokens e custos preenchidos. No modo 10x, exibe adicionalmente tabela com metricas individuais das rodadas.

### Implementation for User Story 1

- [X] T001 [P] [US1] Incluir objeto `metrics` no JSON de resultado em `backend/app.py` na linha 163 (`_run_analysis`): apos `parsed_data["pdf_filename"]`, adicionar `parsed_data["metrics"] = result.get("metrics")` com serializacao dos campos do PipelineMetrics
- [X] T002 [P] [US1] Incluir `runs` individuais no retorno de `run_ten_times()` em `backend/pipeline.py`: modificar o dict de retorno (linha 673-678) para incluir `run_metrics_list` com as metricas individuais de cada rodada valida da etapa 3
- [X] T003 [P] [US1] Reposicionar o card `#observability-card` em `frontend/index.html`: mover o bloco HTML do card de metricas (linhas 104-153) para DENTRO da div `.container`, imediatamente apos o fechamento do card de cifras (`</div>` da linha 102)
- [X] T004 [P] [US1] Atualizar `Metrics.renderMetrics()` em `frontend/js/metrics.js` para ler `metrics` do JSON principal (via `window.renderAll`) em vez de depender de chamada separada a `/api/metrics` — ajustar logica para receber `data.metrics` diretamente
- [X] T005 [US1] Garantir que `Metrics.renderMetrics()` em `frontend/js/metrics.js` renderize a tabela de rodadas a partir de `data.metrics.runs` (ja implementado parcialmente, verificar compatibilidade com estrutura do data-model.md)
- [X] T006 [US1] Remover ou adaptar a rota `/api/metrics` em `backend/app.py` (linha 90-92) — as metricas agora sao servidas no JSON principal; manter a rota como fallback ou redirecionar para o JSON principal

**Checkpoint**: Bloco de metricas funcional para modos 1x e 10x, com dados vindo do JSON principal.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Ajustes finos de estilo e validacao.

- [X] T007 Rodar `pytest backend/tests/ -v` e confirmar que todos os testes existentes passam apos as alteracoes
- [ ] T008 Executar `python dev.py --server` e validar os 4 cenarios do `quickstart.md` (modo 1x, modo 10x, JSON principal, clear)

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: Tasks T001-T002 (backend) podem rodar em paralelo. T003-T005 (frontend) dependem de T001-T002 concluidos.
- **Polish (Phase 4)**: Apos US1 completo.

### Within User Story 1

- T001 e T002: Paralelos (arquivos diferentes — `app.py` vs `pipeline.py`)
- T003 e T004: Paralelos (arquivos diferentes — `index.html` vs `metrics.js`)
- T005: Depende de T004 (mesmo arquivo `metrics.js`)
- T006: Pode rodar em paralelo com frontend

### Parallel Opportunities

- T001 + T002 (backend, arquivos diferentes)
- T003 + T004 (frontend, arquivos diferentes)
- T007 + T008 (validacao, independentes)

### Parallel Example: Implementation

```bash
# Backend (T001 + T002 em paralelo):
Task: "Incluir metrics no JSON de resultado em app.py"
Task: "Incluir runs individuais no retorno de run_ten_times() em pipeline.py"

# Frontend (T003 + T004 em paralelo):
Task: "Reposicionar card observability no index.html"
Task: "Atualizar renderMetrics para ler do JSON principal"

# Apos backend e frontend prontos:
Task: "Ajustar tabela de rodadas e rota /api/metrics"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 3: US1 (T001-T006) — Backend + Frontend integrados
2. **STOP e VALIDATE**: Testes passam, servidor exibe metricas corretamente
3. Seguir para Phase 4: Polish

### Incremental Delivery

1. T001-T002: Backend — incluir metrics + runs no JSON de resultado
2. T003-T005: Frontend — reposicionar card + renderizar do JSON principal
3. T006: Remover dependencia de /api/metrics
4. T007: Rodar testes
5. T008: Validacao manual
