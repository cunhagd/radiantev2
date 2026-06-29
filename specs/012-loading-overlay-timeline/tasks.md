# Tasks: Loading Overlay com Timeline Interativa

**Input**: Design documents from `/specs/012-loading-overlay-timeline/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks are included to validate the existing implementation.

> **Nota**: O modulo `frontend/js/loading.js` ja esta implementado e funcional.
> As tasks abaixo sao de **verificacao e auditoria** para garantir que a
> implementacao existente cobre todos os requisitos da spec. Nao ha codigo
> novo a ser escrito para US1-US4 — apenas testes (Phase 7).

**Organization**: Tasks are grouped by user story to enable independent verification of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Radiante v2 (Web app)**: `frontend/js/loading.js` para o modulo de loading;
  `frontend/js/api.js` para chamadas HTTP; `frontend/js/state.js` para estado global;
  `frontend/index.html` para estrutura HTML da timeline; `frontend/css/animations.css` e
  `frontend/css/components.css` para estilos.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: N/A — o modulo loading.js ja existe implementado em `frontend/js/loading.js`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: N/A — nao ha dependencias bloqueantes; o modulo ja esta integrado ao sistema.

---

## Phase 3: User Story 1 - Analise unica (1x) mostra progresso das 4 etapas (Priority: P1) 🎯 MVP

**Goal**: Verificar que a timeline para modo 1x exibe 4 etapas com status em tempo real e overlay fecha apos conclusao.

**Independent Test**: Iniciar analise 1x, observar overlay, aguardar conclusao e confirmar que relatorio aparece.

- [x] T001 [US1] Verificar que `buildTimelineHTML(1)` em `frontend/js/loading.js` gera 4 steps com 1 sub-step na etapa 3
- [x] T002 [US1] Verificar que `runAnalysis('once')` em `frontend/js/loading.js` define titulo como "Analise unica em andamento"
- [x] T003 [US1] Verificar que `updateTimeline()` em `frontend/js/loading.js` atualiza corretamente os 4 estados (pending/active/done/error) para cada etapa
- [x] T004 [US1] Verificar que `forceAllDone()` em `frontend/js/loading.js` marca todas as etapas como done
- [x] T005 [US1] Verificar que `cleanupLoading()` em `frontend/js/loading.js` esconde overlay, para polling e reabilita botoes

**Checkpoint**: Timeline para modo 1x funcional e testada.

---

## Phase 4: User Story 2 - Analise 10x mostra progresso detalhado (Priority: P1)

**Goal**: Verificar que a timeline para modo 10x exibe 10 sub-etapas na etapa 3 com status individuais e contador.

**Independent Test**: Iniciar analise 10x, observar 10 sub-etapas, confirmar contador de progresso.

- [x] T006 [P] [US2] Verificar que `buildTimelineHTML(10)` em `frontend/js/loading.js` gera 4 steps com 10 sub-steps na etapa 3
- [x] T007 [US2] Verificar que `runAnalysis('ten')` em `frontend/js/loading.js` define titulo como "Analise 10x em andamento"
- [x] T008 [US2] Verificar que `updateTimeline()` em `frontend/js/loading.js` atualiza badge da etapa 3 com contador (ex: "3/10 (2 em andamento)")
- [x] T009 [US2] Verificar que quando todas as 10 rodadas estao done, badge exibe "10/10 concluidas"

**Checkpoint**: Timeline para modo 10x funcional e testada.

---

## Phase 5: User Story 3 - Timer e feedback visual (Priority: P2)

**Goal**: Verificar que o timer na overlay funciona e e atualizado a cada segundo.

**Independent Test**: Iniciar analise, observar timer contando em MM:SS.

- [x] T010 [US3] Verificar que `STATE.timerId` e criado com `setInterval` de 1s em `frontend/js/loading.js` linha 239
- [x] T011 [US3] Verificar que o timer exibe formato MM:SS no elemento `#loading-timer`
- [x] T012 [US3] Verificar que `cleanupLoading()` limpa `STATE.timerId` com `clearInterval`

**Checkpoint**: Timer funcional e testado.

---

## Phase 6: User Story 4 - Tratamento de erros e conflitos (Priority: P2)

**Goal**: Verificar que erros e conflitos sao tratados com feedback claro ao usuario.

**Independent Test**: Simular erro no backend, verificar alerta.

- [x] T013 [US4] Verificar que quando `statusData.status === 'error'`, `loading.js` exibe alerta com `error_details` e chama `cleanupLoading()`
- [x] T014 [US4] Verificar que quando servidor retorna 409, alerta "Ja existe uma analise em andamento" e chama `cleanupLoading()`
- [x] T015 [US4] Verificar que erro de conexao (catch) exibe alerta "Erro de conexao ao servidor" e chama `cleanupLoading()`
- [x] T015b [US4] Verificar que quando `/api/progress` retorna dados incompletos (etapas faltando), `updateTimeline()` em `frontend/js/loading.js` nao quebra e trata graciosamente
- [x] T015c [US4] Verificar que quando `/api/progress` retorna 404, `runAnalysis()` em `frontend/js/loading.js` continua funcionando sem a timeline em tempo real

**Checkpoint**: Tratamento de erros funcional e testado.

---

## Phase 7: Testes Unitarios

**Goal**: Criar testes automatizados para o modulo loading.js.

- [x] T016 [P] Criar test para `buildTimelineHTML()` em `frontend/tests/loading.test.js` — verificar numero de steps e sub-steps
- [x] T017 [P] Criar test para `setStep()` em `frontend/tests/loading.test.js` — verificar classes CSS
- [x] T018 [P] Criar test para `setSubStep()` em `frontend/tests/loading.test.js` — verificar classes e badges
- [x] T019 [P] Criar test para `updateTimeline()` em `frontend/tests/loading.test.js` — verificar mapeamento de status
- [x] T020 [P] Criar test para `forceAllDone()` em `frontend/tests/loading.test.js` — verificar forca todos para done
- [x] T021 [P] Criar test para `cleanupLoading()` em `frontend/tests/loading.test.js` — verificar cleanup de timers e reabilitacao de botoes

**Checkpoint**: Testes unitarios passando.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verificacoes finais e documentacao.

- [x] T022 Rodar `npx vitest run` em `frontend/` e confirmar que todos os testes existentes + novos passam
- [x] T023 Rodar `python dev.py --server` e verificar que a timeline funciona em http://localhost:8000
- [x] T024 Executar `quickstart.md` — validar todos os 4 cenarios manualmente

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: Pode comecar imediatamente — modulo ja existe
- **US2 (Phase 4)**: Pode comecar em paralelo com US1
- **US3 (Phase 5)**: Pode comecar em paralelo com US1/US2
- **US4 (Phase 6)**: Pode comecar em paralelo com US1/US2/US3
- **Testes (Phase 7)**: Depende da conclusao de US1-US4 para garantir cobertura completa
- **Polish (Phase 8)**: Apos todos os testes

### Parallel Opportunities

- T001-T005 (US1): Podem rodar em sequencia
- T006-T009 (US2): Podem rodar em paralelo com US1
- T010-T012 (US3): Podem rodar em paralelo com US1/US2
- T013-T015 (US4): Podem rodar em paralelo com US1/US2/US3
- T016-T021 (Testes): Todos marcados [P] — podem rodar em paralelo

### Parallel Example: Tests

```bash
# Launch all test tasks together:
Task: "T016 - buildTimelineHTML test in frontend/tests/loading.test.js"
Task: "T017 - setStep test in frontend/tests/loading.test.js"
Task: "T018 - setSubStep test in frontend/tests/loading.test.js"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Completar Phase 3: US1 (T001-T005)
2. **STOP e VALIDATE**: Testar timeline para modo 1x
3. Seguir para US2 e demais

### Incremental Delivery

1. US1 → timeline 1x funcional
2. US2 → timeline 10x funcional
3. US3 → timer funcional
4. US4 → tratamento de erros
5. Testes automatizados
