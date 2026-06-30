# Tasks: Loading Animação para Limpeza

**Input**: Design documents from `/specs/024-loading-animacao-limpeza/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included — validação manual conforme quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Radiante v2 (Web app)**: `backend/app.py` + `frontend/js/loading.js` + `frontend/js/ui.js` + `frontend/index.html`
- Paths reflect the existing multi-file modular structure.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Backup dos arquivos que serão modificados

- [X] T001 Backup de `backend/app.py` para `specs/024-loading-animacao-limpeza/backups/app.py.bak`
- [X] T002 Backup de `frontend/js/loading.js` para `specs/024-loading-animacao-limpeza/backups/loading.js.bak`
- [X] T003 Backup de `frontend/js/ui.js` para `specs/024-loading-animacao-limpeza/backups/ui.js.bak`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Funções auxiliares que serão usadas pela User Story 1

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Adicionar função auxiliar `_send_sse()` no backend `backend/app.py` para enviar eventos SSE (formato `event: {type}\ndata: {json}\n\n`) via `self.wfile.write()` e `self.wfile.flush()`
- [X] T005 [P] Adicionar função `buildClearTimelineHTML()` em `frontend/js/loading.js` que gera o HTML da timeline de 6 etapas de limpeza (reutilizando classes `m3-step`, `m3-step-dot`, `m3-step-line`, `m3-step-badge`)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 — Loading Visual com Timeline de Limpeza (Priority: P1) 🎯 MVP

**Goal**: Substituir o feedback textual de limpeza por um overlay com timeline interativa estilo análise 1x/10x

**Independent Test**: Clicar em "Limpar tudo" — o overlay de loading deve aparecer com 6 etapas que progridem sequencialmente e o overlay fecha automaticamente ao final.

### Implementation for User Story 1

- [X] T006 [US1] Modificar `_handle_clear()` em `backend/app.py` para detectar `?stream=true` e usar SSE: enviar `event: step` para cada etapa (`local`, `s3_docs`, `s3_markdown`, `s3_results`, `s3_runs`, `reset`) com status `processing` e `done`, seguido de `event: complete`
- [X] T007 [US1] Adicionar função `runClear()` em `frontend/js/loading.js` que:
  1. Mostra overlay de loading (reutilizando `DOM.loadingOverlay`)
  2. Define título "Limpando dados..." e inicia cronômetro
  3. Renderiza timeline via `buildClearTimelineHTML()`
  4. Faz POST para `/api/clear-all?stream=true`
  5. Lê o stream SSE via `response.body.getReader()` e TextDecoder
  6. Para cada `event: step`, chama `setStep()` para atualizar status e badge com nome do arquivo
  7. Ao receber `event: complete`, força timeline como concluída e fecha overlay
- [X] T008 [US1] Adicionar função auxiliar `consumeClearSSE(response)` em `frontend/js/loading.js` para parsear o stream SSE manualmente (buffer de texto, split por `\n`, detecção de `event:` e `data:`)
- [X] T009 [US1] Modificar `confirmClearAll()` em `frontend/js/ui.js` para:
  1. Chamar `Loading.runClear()` em vez do antigo fetch inline
  2. Manter `closeClearModal()` antes de iniciar o loading
  3. A função `clearAllFrontendData()` deve ser chamada ao final do `runClear()` (via callback)
- [X] T010 [US1] Em `frontend/js/loading.js`, garantir que `Loading.runClear` seja exposta no objeto `window.Loading` e possa ser chamada de `ui.js`
- [X] T011 [US1] Verificar se CSS `.m3-step.is-error` já existe em `frontend/css/layout.css` (confirmado que sim) e garantir destaque vermelho no step de erro
- [X] T012 [US1] Garantir que `DOM.loadingOverlay` e `DOM.btnClear` estão disponíveis via `state.js` ou referência direta em `loading.js`
- [X] T013 [US1] Garantir que ao final da limpeza (sucesso), o overlay fecha automaticamente (delay de 500ms) e `clearAllFrontendData()` é chamado para resetar a tela
- [X] T014 [US1] Adicionar delay mínimo de 300ms por etapa em `runClear()` no `frontend/js/loading.js` para garantir transições visuais perceptíveis mesmo em limpeza rápida
- [X] T015 [US1] Adicionar tratamento de erro de conexão em `runClear()` no `frontend/js/loading.js` — se o fetch falhar ou o stream abortar, exibir mensagem de erro e fechar o overlay

**Checkpoint**: At this point, User Story 1 should be fully functional. O overlay de loading aparece com as 6 etapas, cada uma progride com status, e o overlay fecha automaticamente ao final.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validação e limpeza

- [X] T016 Executar validação manual conforme `quickstart.md` (Cenários 1 a 5)
- [X] T017 Remover backups se a validação passar

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **Polish (Final Phase)**: Depends on US1 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Única user story - can start after Foundational (Phase 2)

### Within each user story

- Core implementation before integration

### Parallel Opportunities

- T001, T002, T003 (backups) — podem rodar em paralelo
- T004 e T005 (foundational) — podem rodar em paralelo (arquivos diferentes: backend vs frontend)
- T006 a T015 — sequenciais dentro do US1, mas T008 pode ser feito junto com T007

---

## Parallel Example: Foundational Phase

```bash
# Launch backend SSE helper and frontend timeline builder together:
Task: "Adicionar _send_sse() em backend/app.py"
Task: "Adicionar buildClearTimelineHTML() em frontend/js/loading.js"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (backups)
2. Complete Phase 2: Foundational (SSE helper + timeline builder)
3. Complete Phase 3: User Story 1 (implementação completa)
4. **STOP and VALIDATE**: Testar limpeza visualmente
5. Polish: Remover backups

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test → **MVP concluído!**
3. Polish → Cleanup

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each task has exact file path
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Avoid: vague tasks, same file conflicts
