# Tasks: Correcao de Consistencia de PDFs e JSONs

**Input**: Design documents from `/specs/013-fix-pdf-consistency/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/

**Tests**: Test tasks are NOT included — feature e de correcao de bugs, validada manualmente via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app.py` (servidor HTTP), `backend/pipeline.py` (logica de pipeline)
- **Frontend**: `frontend/index.html` (link de download PDF), `frontend/js/api.js` (chamadas HTTP)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: N/A — feature de correcao, sem necessidade de setup de projeto.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: N/A — as correcoes sao independentes entre si.

---

## Phase 3: User Story 1 - Navegacao "/data/" retorna 200 se o arquivo existe (Priority: P1) 🎯 MVP

**Goal**: Corrigir a rota `/data/` em `backend/app.py` para usar `_clean_path()` e servir PDFs/JSONs corretamente.

**Independent Test**: Acessar `http://localhost:8000/data/relatorio_consolidado.pdf` diretamente apos analise 1x e receber 200.

- [x] T001 [US1] Corrigir rota `/data/` em `backend/app.py` — substituir `self.path.lstrip("/")` por `path.lstrip("/")` em todas as condicoes de rota estatica que constroem caminhos de arquivo usando `self.path`, para evitar que query strings contaminem o caminho
- [x] T002 [US1] Corrigir rota `/css/` e `/js/` em `backend/app.py` — mesma correcao do T001: usar `path.lstrip("/")` em vez de `self.path.lstrip("/")`. Observacao: esta correcao e preventiva (o mesmo bug em potencial, embora CSS/JS raramente recebam query strings)

**Checkpoint**: Rota `/data/` funcional, PDFs servidos com 200.

---

## Phase 4: User Story 2 - Limpeza de artefatos antigos ao alternar modos (Priority: P1)

**Goal**: Garantir que ao gerar novos PDFs/JSONs, os artefatos do modo oposto sejam removidos primeiro.

**Independent Test**: Executar analise 1x, executar analise 10x, verificar que `relatorio_consolidado.pdf` e `resultado_final.json` foram removidos.

- [x] T003 [US2] Adicionar funcao `clean_artefatos_anteriores(mode)` em `backend/pipeline.py` que remove PDFs e JSONs do modo oposto antes de gerar novos
- [x] T004 [US2] Chamar `clean_artefatos_anteriores('once')` em `run_once()` em `backend/pipeline.py` antes de gerar o PDF e JSON
- [x] T005 [US2] Chamar `clean_artefatos_anteriores('ten')` em `run_ten_times()` em `backend/pipeline.py` antes de gerar o PDF e JSON
- [x] T006 [US2] Garantir que a limpeza no S3 remova artefatos do modo oposto antes do upload em `backend/pipeline.py`. OBS: o `upload_file()` do `s3_client.py` ja sobrescreve objetos com a mesma chave S3 — portanto, fazer upload dos novos arquivos para as mesmas chaves S3 que os artefatos antigos equivale a "limpeza" (sobrescrita, nao requer delete previo).

**Checkpoint**: Limpeza cruzada funcional — apenas 1 PDF e 1 JSON de resultado na pasta `data/`.

---

## Phase 5: User Story 3 - Backend informa pdf_filename na API (Priority: P1)

**Goal**: Adicionar campo `pdf_filename` ao objeto salvo como `last_result` e ao JSON em disco, para que o frontend nao dependa de heuristica.

**Independent Test**: Chamar `GET /api/last-result` apos analise 1x e verificar que `pdf_filename` contem `relatorio_consolidado.pdf`.

- [x] T007 [P] [US3] Adicionar `pdf_filename` ao `last_result` salvo em memoria em `backend/app.py` no metodo `_run_analysis()` — usar `"relatorio_consolidado.pdf"` para modo once e `"relatorio_consolidado_10x.pdf"` para modo ten
- [x] T008 [P] [US3] Adicionar `pdf_filename` ao JSON salvo em disco em `backend/pipeline.py` — em `run_once()` e `run_ten_times()`, incluir o campo no objeto antes de serializar

**Checkpoint**: API retorna `pdf_filename` corretamente.

---

## Phase 6: User Story 4 - Frontend usa pdf_filename da API (Priority: P2)

**Goal**: Substituir a heuristica `isTenMode` no frontend pelo uso direto do campo `pdf_filename` retornado pela API.

**Independent Test**: Apos analise 1x, verificar que o href do botao de download aponta para `/data/relatorio_consolidado.pdf`.

- [x] T009 [US4] Substituir logica `isTenMode` em `frontend/index.html` para usar `data.pdf_filename` do `last-result` na construcao do link de download do PDF

**Checkpoint**: Frontend usa campo oficial da API.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificacoes finais e documentacao.

- [x] T010 Executar `python dev.py --server` e validar todos os 4 cenarios do `quickstart.md`
- [x] T011 Rodar `npx vitest run` em `frontend/` e confirmar que todos os testes existentes passam apos as alteracoes

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: Pode comecar imediatamente — correcao isolada em `app.py`
- **US2 (Phase 4)**: Pode comecar em paralelo com US1 — altera `pipeline.py`
- **US3 (Phase 5)**: Pode comecar em paralelo com US1/US2 — altera `app.py` e `pipeline.py`
- **US4 (Phase 6)**: Depende de US3 estar concluido (precisa de `pdf_filename` na API)
- **Polish (Phase 7)**: Apos todos os phases anteriores

### Parallel Opportunities

- T001-T002 (US1): Sequencial (mesmo arquivo)
- T003-T006 (US2): Sequencial (mesmo arquivo `pipeline.py`)
- T007-T008 (US3): Paralelo [P] (arquivos diferentes: `app.py` e `pipeline.py`)
- T009 (US4): Apos US3
- T010-T011 (Polish): Sequencial (validacao manual + testes)

### Parallel Example: Phase 5

```bash
# T007 e T008 podem rodar em paralelo:
Task: "T007 - Adicionar pdf_filename em app.py _run_analysis"
Task: "T008 - Adicionar pdf_filename em pipeline.py run_once/run_ten_times"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Completar Phase 3: US1 (T001-T002)
2. **STOP e VALIDATE**: Servir PDF via `/data/relatorio_consolidado.pdf`
3. Seguir para US2 e demais

### Incremental Delivery

1. US1 → PDF servido corretamente (404 resolvido)
2. US2 → Limpeza de artefatos ao alternar modos
3. US3 → API informa pdf_filename
4. US4 → Frontend sem heuristica
5. Validacao final

---

## Phase 8: Convergence

**Purpose**: Correcoes pos-implementacao identificadas pelo `/speckit-converge`.

- [x] T012 [US2] Reordenar `run_once()` em `backend/pipeline.py`: `clean_artefatos_anteriores("once")` DEVE ser chamado **antes** de `save_stage_files()`, nao depois (FR-002, FR-007 — `partial`)
- [x] T013 [US2] Reordenar `run_ten_times()` em `backend/pipeline.py`: `clean_artefatos_anteriores("ten")` DEVE ser chamado **antes** de escrever o JSON consolidado e gerar o PDF, nao depois (FR-002, FR-007 — `partial`)
- [x] T014 [US2] Adicionar limpeza S3 do modo oposto em `run_once()` e `run_ten_times()` em `backend/pipeline.py`: apos limpeza local, deletar artefatos do modo oposto no S3 (`results/relatorio_consolidado[_10x].pdf`, `results/resultado_final.json`, `results/consolidado_10x.json`) via `delete_files()` ou `upload_file()` com sobrescrita — antes de fazer upload dos novos (FR-006 — `partial`)
