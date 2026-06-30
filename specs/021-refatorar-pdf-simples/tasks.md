# Tasks: Refatorar PDF para estilo simples (021)

**Input**: Design documents from `specs/021-refatorar-pdf-simples/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/generate_pdf.md, quickstart.md

**Tests**: Não solicitados — validação visual do PDF gerado.

**Organization**: Feature com uma única user story (P1) — refatoração completa do `backend/pdf_generator.py`.

## Format: `[ID] [P] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Verificar dependências e fazer backup do arquivo atual.

- [X] T001 Verificar se `reportlab` está instalado (`pip list | Select-String -Pattern "reportlab"`)
- [X] T002 Criar backup do `backend/pdf_generator.py` atual para `backend/pdf_generator.py.bak`

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No work can begin until this phase is complete.

- [X] T003 Ler o research.md (`specs/021-refatorar-pdf-simples/research.md`) e o contrato (`specs/021-refatorar-pdf-simples/contracts/generate_pdf.md`) para entender todas as decisões de refatoração

---

## Phase 3: User Story 1 — Gerar PDF consolidado com estilo simples (Priority: P1) 🎯 MVP

**Goal**: Reescrever `backend/pdf_generator.py` com estilo simples, removendo toda a estilização Material Design 3.

**Independent Test**: Executar `python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas', 'data/teste_simples.pdf'); print(f'OK: {p}')"` e verificar que o PDF abre corretamente.

### Implementation for User Story 1

- [X] T004 [US1] Reescrever `backend/pdf_generator.py` com os 5 estilos de Paragraph simplificados (TITLE_STYLE 16pt, H2_STYLE 14pt, H3_STYLE 12pt, BODY_STYLE 11pt, CODE_STYLE Courier 9pt) — remover paleta de cores MD3, CALLOUT_STYLE e constantes de cor
- [X] T005 [US1] Implementar parser markdown linear em `backend/pdf_generator.py` — remover estado `in_etapa`, `etapa_body`, `flush_etapa()`, `RE_ETAPA`, `_make_etapa_block()`, `_make_callout()`; cada linha vira elemento diretamente na lista `elements`
- [X] T006 [US1] Tratar listas markdown em `backend/pdf_generator.py` — linhas iniciadas com `* ` ou `- ` devem ser renderizadas como `BODY_STYLE` com `leftIndent=15` (recuo de 15pt), preservando a identação visual (FR-008)
- [X] T007 [US1] Simplificar `_make_table()` em `backend/pdf_generator.py` — remover detecção de total/callout, remover cores, manter apenas grid simples 0.5pt (#cccccc) e header em negrito
- [X] T008 [US1] Manter `_make_page_callback()` em `backend/pdf_generator.py` — cabeçalho "Radiante — Análise Jurídica" (Helvetica-Bold 9pt) + rodapé "Página X de Y" (Helvetica 8pt)
- [X] T009 [US1] Manter two-pass build com `_validate_pdf()` e tratamento de erro com limpeza de arquivos parciais em `backend/pdf_generator.py`
- [X] T010 [US1] Ajustar margens para 2cm (~56.7pt) em todos os lados no `SimpleDocTemplate` em `backend/pdf_generator.py`

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e verificação de conformidade.

- [X] T011 Executar `python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas', 'data/teste_simples.pdf'); print(f'OK: {p}')"` para validar geração do PDF
- [X] T012 Verificar que o PDF gerado abre corretamente com `Start-Process "C:\radiantev2\data\teste_simples.pdf"`
- [X] T013 Verificar que o código final tem no máximo 200 linhas (`(Get-Content backend/pdf_generator.py).Count`)
- [X] T014 Remover `backend/pdf_generator.py.bak` após validação bem-sucedida

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pode iniciar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — necessário entender o contrato
- **User Story 1 (Phase 3)**: Depende de Foundational concluída
- **Polish (Phase 4)**: Depende de User Story 1 completa

### User Story Dependencies

- **User Story 1 (P1)**: Única user story — sem dependências externas

### Within User Story 1

Todas as tarefas T004-T010 modificam o mesmo arquivo (`backend/pdf_generator.py`), portanto DEVEM ser executadas sequencialmente. T004 deve ser a primeira (definir estilos), seguida por T005-T010.

### Parallel Opportunities

Nenhuma — todas as tarefas modificam o mesmo arquivo.

---

## Parallel Example: User Story 1

```bash
# Todas as tarefas são sequenciais (mesmo arquivo):
Task: "T004: Definir 5 estilos simplificados em backend/pdf_generator.py"
Task: "T005: Parser linear em backend/pdf_generator.py"
Task: "T006: Listas com recuo em backend/pdf_generator.py"
Task: "T007: Tabelas simplificadas em backend/pdf_generator.py"
# ...
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (backup)
2. Complete Phase 2: Foundational (entender design)
3. Complete Phase 3: User Story 1 (reescrever pdf_generator.py inteiro)
4. **STOP and VALIDATE**: Testar geração do PDF
5. Completar Phase 4: Polish

Após a Fase 3, o MVP está completo. Toda a refatoração é no arquivo `backend/pdf_generator.py`.
