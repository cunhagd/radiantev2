# Tasks: Remocao do Bloco "Ver Relatorio de Auditoria"

**Input**: Design documents from `/specs/014-remove-audit-block/`

**Prerequisites**: plan.md, spec.md

**Tests**: Test tasks are included — feature requer ajustes em testes existentes para refletir a remocao.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend HTML**: `frontend/index.html`
- **Frontend JS**: `frontend/js/api.js`, `frontend/js/ui.js`, `frontend/js/state.js`, `frontend/js/loading.js`
- **Frontend CSS**: `frontend/css/components.css`
- **Backend**: `backend/app.py`
- **Test fixtures**: `frontend/tests/setup.js`
- **Test files**: `frontend/tests/api.test.js`, `frontend/tests/loading.test.js`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: N/A — feature de remocao, sem necessidade de setup.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: N/A — sem prerrequisitos bloqueantes.

---

## Phase 3: User Story 1 - Remover bloco de auditoria da interface (Priority: P1) 🎯 MVP

**Goal**: Remover o bloco "Ver Relatorio de Auditoria" do frontend (HTML, JS, CSS) e a rota `/api/audit-log` do backend.

**Independent Test**: Apos analise 1x ou 10x, verificar que `.audit-section` nao existe no DOM e que `/api/audit-log` retorna 404.

### Implementation for User Story 1

- [ ] T001 [US1] Remover bloco `.audit-section` (HTML) de `frontend/index.html` — remover as linhas 102-108 (`.audit-section`, `.audit-toggle`, `.audit-body`)
- [ ] T002 [P] [US1] Remover `DOM.auditContent` de `frontend/js/state.js` — remover a linha 41 (`DOM.auditContent = document.getElementById('audit-content')`)
- [ ] T003 [P] [US1] Remover `API.loadAuditLog` de `frontend/js/api.js` — remover funcao `API.loadAuditLog` (linhas 60-72) e sua chamada em `index.html` linha 284 (`API.loadAuditLog()`)
- [ ] T004 [P] [US1] Remover `toggleAuditLog` e referencias audit de `frontend/js/ui.js` — remover funcao `toggleAuditLog` (linhas 136-139), remover linha 89 (`DOM.auditContent.innerText = 'Carregando...'`), remover linha 146 (`UI.toggleAuditLog = toggleAuditLog`)
- [ ] T005 [P] [US1] Remover chamada `API.loadAuditLog` de `frontend/js/loading.js` — remover linha 297 (`await API.loadAuditLog()`) no polling de conclusao
- [ ] T006 [P] [US1] Remover estilos `.audit-section`, `.audit-toggle`, `.audit-body` de `frontend/css/components.css` — remover linhas 315-363
- [ ] T007 [P] [US1] Remover event listener `audit-toggle` de `frontend/index.html` — remover bloco do event listener (linhas 270-273)
- [ ] T008 [P] [US1] Remover rota `/api/audit-log` de `backend/app.py` — remover bloco `elif path == "/api/audit-log":` (linhas 88-99) do metodo `do_GET`

### Test adjustments

- [ ] T009 [US1] Remover bloco `.audit-section` do HTML de teste em `frontend/tests/setup.js` — remover linhas 73-76
- [ ] T010 [US1] Remover testes de `API.loadAuditLog` de `frontend/tests/api.test.js` — remover os 2 testes que usam `/api/audit-log` (linhas 39-54)
- [ ] T011 [US1] Remover mock de `API.loadAuditLog` de `frontend/tests/loading.test.js` — remover linhas 394 e 413 (`API.loadAuditLog = vi.fn().mockResolvedValue(undefined)`)

**Checkpoint**: Bloco de auditoria removido, rota `/api/audit-log` retorna 404, testes atualizados passam.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Verificacoes finais.

- [ ] T012 Rodar `npx vitest run` em `frontend/` e confirmar que todos os testes existentes passam apos as alteracoes
- [ ] T013 Executar `python dev.py --server` e validar os 3 cenarios do `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: Pode comecar imediatamente — todas as tarefas sao independentes entre si
- **Polish (Phase 4)**: Apos US1 completo

### Parallel Opportunities

- T001-T008: Todas paralelas [P] (arquivos diferentes)
- T009-T011: Sequencial apos as implementacoes (testes dependem do codigo atualizado)
- T012: Apos T009-T011
- T013: Apos T012

### Parallel Example: Implementation

```bash
# Todas as implementacoes podem rodar em paralelo:
Task: "T001 - Remover HTML do audit-section"
Task: "T002 - Remover DOM.auditContent do state.js"
Task: "T003 - Remover API.loadAuditLog do api.js"
Task: "T004 - Remover toggleAuditLog do ui.js"
Task: "T005 - Remover chamada audit do loading.js"
Task: "T006 - Remover estilos audit do components.css"
Task: "T007 - Remover event listener audit do index.html"
Task: "T008 - Remover rota /api/audit-log do app.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Completar Phase 3: US1 (T001-T011)
2. **STOP e VALIDATE**: Verificar que o bloco de auditoria nao aparece
3. Seguir para Phase 4: Polish

### Incremental Delivery

1. T001-T008: Remocao do codigo (paralelo)
2. T009-T011: Ajuste dos testes (sequencial)
3. T012: Rodar testes
4. T013: Validacao manual
