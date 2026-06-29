# Tasks: Reformatação do PDF Consolidado

**Input**: Design documents from `specs/017-reformat-pdf/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test tasks sao opcionais — feature nao requer novos testes (mudancas sao puramente visuais no PDF, sem alteracao de logica).

**Organization**: Tasks grouped by single user story, executed sequentially.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/pdf_generator.py` — unico arquivo modificado
- **Documentacao**: `specs/017-reformat-pdf/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: N/A — reportlab ja instalado, codigo existente.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: N/A — sem prerrequisitos bloqueantes.

---

## Phase 3: User Story 1 - Visualizar relatorio PDF com design profissional (Priority: P1) 🎯 MVP

**Goal**: Reformatar o PDF do relatorio consolidado (1x e 10x) com design profissional seguindo Material Design 3, mantendo exatamente o mesmo conteudo textual.

**Independent Test**: Ao gerar um PDF (qualquer modo), o documento exibe cabecalho "Radiante — Analise Juridica", rodape com numeracao, blocos coloridos para cada etapa, tabelas estilizadas e callout de destaque para o valor total.

### Implementation for User Story 1

- [X] T001 [P] [US1] Implementar cabecalho "Radiante — Analise Juridica" e rodape com "Pagina X de Y" em `backend/pdf_generator.py` usando `onFirstPage`/`onLaterPages` do `SimpleDocTemplate`
- [X] T002 [P] [US1] Implementar blocos visuais para cada etapa (Metadados, Cifras, Risco, Consolidacao) com fundo alternado (#f8f9fa / #e8eaed), titulo em azul #4285f4 e espacamento adequado em `backend/pdf_generator.py`
- [X] T003 [P] [US1] Implementar callout de destaque para o valor total estimado (KPI) com fundo #e6f4ea e borda verde #34a853 em `backend/pdf_generator.py`
- [X] T004 [US1] Implementar estilizacao de tabelas com grade sutil (#dadce0), cabecalho com fundo azul claro (#e8f0fe) e padding adequado em `backend/pdf_generator.py`
- [X] T005 [US1] Aplicar paleta Material Design 3 em todo o documento e garantir que blocos de codigo usem fonte Courier com fundo cinza (#f1f5f9) em `backend/pdf_generator.py`

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Ajustes finos e validacao.

- [X] T006 Rodar `pytest backend/tests/ -v` e confirmar que todos os testes existentes passam apos as alteracoes
- [X] T007 Executar `python dev.py --server` e validar os 3 cenarios do `quickstart.md` (PDF 1x, PDF 10x, consistencia visual)

---


## Phase 5: Convergence

**Purpose**: Fechar gaps identificados na analise de convergencia.

- [X] T008 Corrigir rodape para exibir "Pagina X de Y" (total de paginas) em `backend/pdf_generator.py` usando two-pass build do SimpleDocTemplate (FR-003, AC4) (partial)
- [X] T009 Alterar cor do titulo das etapas para azul primario #4285f4 em `backend/pdf_generator.py` para atender T002 e FR-004 (partial)

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: T001-T005 podem rodar em paralelo (todos alteram o mesmo arquivo `pdf_generator.py`, mas sao secoes independentes do mesmo arquivo — recomenda-se implementacao sequencial para evitar conflitos)
- **Polish (Phase 4)**: Apos US1 completo.

### Within User Story 1

- T001-T005: Recomendado sequencial (mesmo arquivo `pdf_generator.py`, mas logicas independentes)
- T006-T007: Independentes, apos implementacao

### Parallel Opportunities

- T001 + T002 + T003 (secoes diferentes do mesmo arquivo, mas recomenda-se sequencial)
- T006 + T007 (validacao, independentes)

### Parallel Example: Implementation

```bash
# Todos os tasks tocam o mesmo arquivo — recomenda-se implementacao sequencial:
Task: "Implementar cabecalho e rodape no pdf_generator.py"
Task: "Implementar blocos de etapa no pdf_generator.py"
Task: "Implementar callout de total no pdf_generator.py"
Task: "Implementar estilizacao de tabelas no pdf_generator.py"
Task: "Aplicar paleta MD3 e estilo de codigo no pdf_generator.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 3: US1 (T001-T005) — PDF reformatado
2. **STOP e VALIDATE**: Testes passam, PDF gerado com design profissional
3. Seguir para Phase 4: Polish

### Incremental Delivery

1. T001-T005: Implementacao sequencial em `pdf_generator.py`
2. T006: Rodar testes
3. T007: Validacao manual com servidor
