# Tasks: Corrigir Abertura do PDF Consolidado

**Input**: Design documents from `specs/018-fix-pdf-abertura/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test tasks sao opcionais — feature de correcao de parser sem novos testes unitarios. Validacao estrutural sera feita via quickstart.

**Organization**: Tasks grouped by single user story, executed sequencialmente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/pdf_generator.py` — unico arquivo modificado
- **Documentacao**: `specs/018-fix-pdf-abertura/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: N/A — reportlab ja instalado, codigo existente.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: N/A — sem prerrequisitos bloqueantes.

---

## Phase 3: User Story 1 - Baixar e abrir PDF do relatorio consolidado (Priority: P1) 🎯 MVP

**Goal**: Garantir que o PDF gerado tenha >= 1 pagina e estrutura valida, mesmo com conteudo extenso ou formatacao inesperada vinda da IA.

**Independent Test**: Ao gerar um PDF (qualquer modo), o arquivo possui pelo menos 1 pagina no dicionario `/Count >= 1` e pode ser aberto em Chrome/Edge/Adobe Reader.

### Implementation for User Story 1

- [X] T001 [US1] Adicionar validacao pos-build em `backend/pdf_generator.py`: apos `doc.build()`, verificar se o PDF gerado possui estrutura valida (cabecalho `%PDF-`, trailer `%%EOF`, pelo menos 1 pagina). Se invalido, levantar excecao com mensagem clara.

- [X] T002 [US1] Adicionar tratamento de erro (try/except) no `doc.build()` em `backend/pdf_generator.py`: capturar excecoes do ReportLab, remover o PDF parcial do disco e relancar o erro para o chamador.

- [X] T003 [US1] Adicionar fallback de conteudo vazio em `backend/pdf_generator.py`: se a lista `elements` estiver vazia apos o parser, adicionar um Paragraph padrao "Nenhum conteudo disponivel" para garantir que o PDF tenha pelo menos 1 pagina.

- [X] T004 [US1] Garantir robustez do parser em `backend/pdf_generator.py`: toda linha que nao corresponder aos padroes conhecidos (#, ##, ###, ```, |, vazio) deve ser tratada como texto comum com BODY_STYLE (fallback ja existente — verificar e adicionar teste unitario se necessario). **Atencao especial a caracteres UTF-8 (acentos, cedilha, aspas curvas)** que devem ser renderizados sem corrompimento no Paragraph.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validacao final.

- [X] T005 Rodar `pytest backend/tests/ -v` e confirmar que todos os testes existentes passam apos as alteracoes
- [X] T006 Executar os 4 cenarios do `quickstart.md` (PDF valido, PDF extenso, pipeline completo, validacao estrutural automatizada). **Nota**: SC-004 (abertura em Chrome/Edge/Adobe Reader) requer validacao manual — abrir o PDF gerado em cada leitor e confirmar que abre sem erros.

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: T001-T004 sequenciais (mesmo arquivo `pdf_generator.py`)
- **Polish (Phase 4)**: Apos US1 completo.

### Within User Story 1

- T001-T004: Sequencial (mesmo arquivo)
- T005-T006: Apos implementacao

### Parallel Opportunities

- N/A — todas as tasks tocam o mesmo arquivo

### Parallel Example: Implementation

```bash
Task: "Validacao pos-build em pdf_generator.py"
Task: "Try/except no doc.build() em pdf_generator.py"
Task: "Fallback de conteudo vazio em pdf_generator.py"
Task: "Robustez do parser em pdf_generator.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 3: US1 (T001-T004) — PDF valido robusto
2. **STOP e VALIDATE**: Testes passam, PDF gerado com estrutura valida
3. Seguir para Phase 4: Polish

### Incremental Delivery

1. T001: Validacao pos-build
2. T002: Try/except no build
3. T003: Fallback de conteudo vazio
4. T004: Robustez do parser
5. T005: Rodar testes
6. T006: Validacao manual com quickstart
