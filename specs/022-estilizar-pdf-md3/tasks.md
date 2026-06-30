# Tasks: Estilizar PDF com Material Design 3 (022)

**Input**: Design documents from `specs/022-estilizar-pdf-md3/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/generate_pdf.md, quickstart.md

**Tests**: Não solicitados — validação visual do PDF gerado.

**Organization**: Feature com duas user stories (P1, P2) — ambas modificam o mesmo arquivo `backend/pdf_generator.py`.

## Format: `[ID] [P] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Verificar dependências e garantir que o backup da feature anterior existe.

- [ ] T001 Verificar que `reportlab` está instalado (`pip list | Select-String -Pattern "reportlab"`)
- [ ] T002 Criar backup do `backend/pdf_generator.py` atual para `backend/pdf_generator.py.bak`

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No work can begin until this phase is complete.

- [ ] T003 Ler o research.md (`specs/022-estilizar-pdf-md3/research.md`) e o contrato (`specs/022-estilizar-pdf-md3/contracts/generate_pdf.md`) para entender todas as decisões de design MD3

---

## Phase 3: User Story 1 — PDF com Estilo Profissional MD3 (Priority: P1) 🎯 MVP

**Goal**: Aplicar o tema Material Design 3 ao PDF — paleta de cores MD3, títulos coloridos por nível (primary/secondary/tertiary), cabeçalho/rodapé com cores MD3, tabelas com cabeçalho primary, blocos de código com fundo surface variant, accent bars + dividers entre etapas, listas com bullet Unicode.

**Independent Test**: Executar `python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas', 'data/teste_md3.pdf'); print(f'OK: {p}')"` e verificar visualmente que todos os elementos estão estilizados com MD3.

**Atenção**: Todas as tarefas T004-T010 modificam o mesmo arquivo (`backend/pdf_generator.py`), portanto DEVEM ser executadas sequencialmente na ordem abaixo.

### Implementation for User Story 1

- [ ] T004 [US1] Adicionar paleta de cores MD3 (12 constantes `C_*`) e substituir as cores anteriores em `backend/pdf_generator.py` — `C_PRIMARY #6750A4`, `C_SECONDARY #625B71`, `C_TERTIARY #7D5260`, `C_SURFACE #FFFBFE`, `C_SURFACE_VARIANT #E7E0EC`, `C_OUTLINE #79747E`, `C_ERROR #B3261E`, `C_BACKGROUND #FFFBFE`, `C_ON_PRIMARY #FFFFFF`, `C_ON_SURFACE #1C1B1F`, `C_ON_SURFACE_VARIANT #49454F` (FR-001)
- [ ] T005 [US1] Atualizar estilos de Paragraph com as cores MD3 em `backend/pdf_generator.py` — `TITLE_STYLE` com `C_PRIMARY`, `H2_STYLE` com `C_SECONDARY`, `H3_STYLE` com `C_TERTIARY`, `BODY_STYLE` com `C_ON_SURFACE`, `CODE_STYLE` com `C_ON_SURFACE`, `LIST_STYLE` com `C_ON_SURFACE` (FR-009, FR-010)
- [ ] T006 [US1] Implementar accent bar (Table 4pt x 18pt cor `C_PRIMARY`) e HRFlowable divider (0.5pt `C_OUTLINE`) entre blocos de etapa em `backend/pdf_generator.py` — inserir divider antes de cada etapa (exceto a primeira) e accent bar no início de cada etapa; NÃO usar Table wrapper para conteúdo (FR-002, FR-003, pesquisa R2/R4)
- [ ] T007 [US1] Atualizar `_make_table()` em `backend/pdf_generator.py` com estilo MD3 — cabeçalho com `BACKGROUND` `C_PRIMARY` + `TEXTCOLOR` `C_ON_PRIMARY`, linhas do corpo alternando `C_SURFACE`/`C_SURFACE_VARIANT`, grid `INNERGRID` 0.5pt `C_OUTLINE` (FR-006)
- [ ] T008 [US1] Implementar bloco de código com fundo e borda em `backend/pdf_generator.py` — códigos ≤ 20 linhas: Table wrapper com `BACKGROUND` `C_SURFACE_VARIANT` + `BOX` 0.5pt `C_OUTLINE`; códigos > 20 linhas: Paragraph Courier simples sem wrapper (FR-007, pesquisa R6)
- [ ] T009 [US1] Atualizar `afterPage()` em `backend/pdf_generator.py` com cores MD3 — cabeçalho "Radiante — Análise Jurídica" em `C_PRIMARY`, linha separadora em `C_OUTLINE`, rodapé "Página X de Y" em `C_ON_SURFACE_VARIANT` (FR-004, FR-005)
- [ ] T010 [US1] Atualizar listas markdown em `backend/pdf_generator.py` — substituir `* ` e `- ` por bullet Unicode `\u2022` (•) com `leftIndent=15` (FR-008, pesquisa R10)

---

## Phase 4: User Story 2 — Página de Capa com Resumo (Priority: P2)

**Goal**: Adicionar página de capa profissional ao PDF com metadados do processo extraídos de `data/resultado_final.json`.

**Independent Test**: Executar `python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas', 'data/teste_capa.pdf'); print(f'OK: {p}')"` e verificar que a primeira página é uma capa com título "Radiante", subtítulo "Análise Jurídica" e dados do processo.

**Atenção**: T011 modifica o mesmo arquivo (`backend/pdf_generator.py`) que as tasks da US1 — deve executar DEPOIS da US1.

### Implementation for User Story 2

- [ ] T011 [US2] Implementar página de capa em `backend/pdf_generator.py` — ler `data/resultado_final.json` (se existir, graceful fallback se não existir); adicionar `COVER_TITLE_STYLE` (Helvetica-Bold 24pt, `C_PRIMARY`, `alignment=TA_CENTER`) e `COVER_SUBTITLE_STYLE` (Helvetica 14pt, `C_SECONDARY`, `alignment=TA_CENTER`); inserir elementos da capa no início da lista `elements`: Spacer(1, A4[1]/4), título "Radiante", subtítulo "Análise Jurídica", HRFlowable centralizado (width=60%), dados do processo (Processo, Autor, Reclamada, Valor Total Estimado, Data de Geração) (FR-011, pesquisa R7)

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e verificação de conformidade.

- [ ] T012 Executar `python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas', 'data/teste_md3.pdf'); print(f'OK: {p}')"` para validar geração do PDF com estilo MD3
- [ ] T013 Verificar que o PDF gerado abre corretamente com `Start-Process "C:\radiantev2\data\teste_md3.pdf"`
- [ ] T014 Executar `python backend/pipeline.py` para validar que o pipeline gera o PDF com estilo MD3
- [ ] T015 Remover `backend/pdf_generator.py.bak` após validação bem-sucedida

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pode iniciar imediatamente (já concluído)
- **Foundational (Phase 2)**: Depende de Setup — necessário entender o design
- **User Story 1 (Phase 3)**: Depende de Foundational concluída
- **User Story 2 (Phase 4)**: Depende de User Story 1 completa (mesmo arquivo)
- **Polish (Phase 5)**: Depende de User Story 2 completa

### User Story Dependencies

- **User Story 1 (P1)**: Única user story core — sem dependências externas
- **User Story 2 (P2)**: Depende de US1 — ambas modificam o mesmo arquivo

### Within User Story 1

Todas as tarefas T004-T010 modificam o mesmo arquivo (`backend/pdf_generator.py`), portanto DEVEM ser executadas sequencialmente. T004 deve ser a primeira (definir cores), seguida por T005 (estilos), T006 (accent bar/dividers), T007 (tabelas), T008 (código), T009 (header/footer), T010 (listas).

### Within User Story 2

T011 modifica o mesmo arquivo (`backend/pdf_generator.py`) — executa após US1.

### Parallel Opportunities

Nenhuma — todas as tarefas modificam o mesmo arquivo.

---

## Parallel Example: User Story 1

```bash
# Todas as tarefas são sequenciais (mesmo arquivo):
Task: "T004: Paleta MD3 em backend/pdf_generator.py"
Task: "T005: Estilos MD3 em backend/pdf_generator.py"
Task: "T006: Accent bar + dividers em backend/pdf_generator.py"
Task: "T007: Tabelas MD3 em backend/pdf_generator.py"
# ...
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (entender design)
3. Complete Phase 3: User Story 1 (aplicar MD3 ao PDF)
4. **STOP and VALIDATE**: Testar geração do PDF com MD3
5. Completar Phase 4: User Story 2 (capa)
6. Completar Phase 5: Polish

Após a Fase 3, o MVP está completo (US1 — estilo MD3 básico). A Fase 4 (capa) é um incremento opcional. Toda a implementação é no arquivo `backend/pdf_generator.py`.
