# Tasks: Estruturar Etapas do Pipeline em Markdown

**Input**: Design documents from `/specs/019-estruturar-etapas-pipeline/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/generate_pdf.md

**Tests**: Não solicitados — feature sem testes automáticos.

**Organization**: Tasks grouped por fase. Feature única (US1) com dois sub-componentes paralelizáveis: pipeline.py e pdf_generator.py.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode executar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: US1 — única user story
- Incluir caminhos exatos dos arquivos nas descrições

---

## Phase 1: Setup

**Purpose**: Configuração inicial do diretório de etapas e gitignore

- [X] T001 Adicionar `data/etapas/` ao `.gitignore` para não versionar resultados de análise

**Checkpoint**: Setup completo — diretório `data/etapas/` ignorado pelo git

---

## Phase 2: User Story 1 — Pipeline salva cada etapa como .md e PDF consome os arquivos (Priority: P1) 🎯 MVP

**Goal**: O pipeline salva cada etapa (1-4) como arquivo .md estruturado em `data/etapas/` e o `generate_pdf()` é refatorado para ler esses arquivos e gerar o PDF consolidado.

**Teste Independente**: Ao executar `run_once()`, os arquivos `data/etapas/etapa1.md` a `etapa4.md` são criados. O `generate_pdf(etapas_dir="data/etapas", output_path="data/relatorio_consolidado.pdf")` gera PDF válido.

**Fulfilled Requirements**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009

---

### Sub-fase 2A: Pipeline — funções auxiliares (pipeline.py)

- [X] T002 [P] [US1] Criar função `_save_etapa_md(etapas_dir, stage_name, content, run_idx=None)` em `backend/pipeline.py` que escreve arquivo .md em `data/etapas/` com cabeçalho `# Etapa N — Nome` + conteúdo, aplicando fallback "Nenhum conteúdo disponível para esta etapa." se conteúdo vazio. O parâmetro `run_idx` é usado para nomear arquivos no modo 10x (`etapa3_rodada{N}.md`) (FR-003 a FR-006, FR-009). O título da etapa deve ser derivado internamente a partir do `stage_name`.
- [X] T003 [P] [US1] Criar função `clean_etapas_dir(etapas_dir)` em `backend/pipeline.py` que cria o diretório `data/etapas/` se não existir (FR-001) e remove todos os arquivos .md do diretório (FR-002)

---

### Sub-fase 2B: Pipeline — salvar etapas em run_single_pipeline (pipeline.py)

- [X] T004 [US1] Modificar `run_single_pipeline()` em `backend/pipeline.py` para chamar `_save_etapa_md()` após cada etapa concluída: etapa1_raw → `etapa1.md` (FR-003), etapa2_raw → `etapa2.md` (FR-004), etapa3_raw → `etapa3.md` (FR-005 modo 1x), etapa4_raw → `etapa4.md` (FR-006)

---

### Sub-fase 2C: Pipeline — limpeza e chamada em run_once e run_ten_times (pipeline.py)

- [X] T005 [US1] Modificar `run_once()` em `backend/pipeline.py` para chamar `clean_etapas_dir()` no início e substituir a geração do `report_text` concatenado pela chamada a `generate_pdf(etapas_dir, output_path)` (FR-007, FR-008). Incluir tratamento: se uma etapa falhar, salvar a mensagem de erro no arquivo .md correspondente (ex: `# Etapa 1 — Extração de Metadados\n\n**ERRO**: {mensagem}`) antes de interromper o pipeline (edge case: falha em etapa).
- [X] T006 [US1] Modificar `run_ten_times()` em `backend/pipeline.py` para chamar `clean_etapas_dir()` no início, salvar cada rodada da etapa 3 como `etapa3_rodada{N}.md` localmente (FR-005 modo 10x), e substituir a geração do `report_text` concatenado pela chamada a `generate_pdf(etapas_dir, output_path)` (FR-007, FR-008). Incluir tratamento: se uma etapa falhar, salvar a mensagem de erro no arquivo .md correspondente antes de interromper o pipeline (edge case: falha em etapa).

---

### Sub-fase 2D: PDF Generator — refatorar generate_pdf (pdf_generator.py)

- [X] T007 [P] [US1] Refatorar `generate_pdf()` em `backend/pdf_generator.py` para aceitar `etapas_dir: str | Path` e `output_path: str | Path`, lendo todos os arquivos .md do diretório em ordem alfabética, concatenando o conteúdo e processando com o parser markdown existente (FR-007, FR-008). Seguir o contrato em `contracts/generate_pdf.md`.

---

### Sub-fase 2E: Pipeline — remover geração de texto concatenado dos modos (pipeline.py)

- [X] T008 [US1] Remover a montagem do `report_text` concatenado em `run_once()` (linhas 384-390) e `run_ten_times()` (linhas 643-647) em `backend/pipeline.py`, já que o PDF agora é gerado a partir dos arquivos .md individuais

**Checkpoint**: Ao final da US1, o pipeline 1x gera 4 arquivos .md, o pipeline 10x gera 13 arquivos .md (4 etapas + 10 rodadas), e o PDF gerado a partir deles é válido.

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e ajustes

- [X] T009 Executar o quickstart.md (`specs/019-estruturar-etapas-pipeline/quickstart.md`) para validar todos os cenários: geração de arquivos .md (1x e 10x), geração de PDF a partir dos arquivos, limpeza entre análises

**Checkpoint**: Feature completa — todos os cenários do quickstart validados com sucesso.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — pode iniciar imediatamente
- **US1 - Sub-fase 2A (T002, T003)**: Sem dependências — ambas as funções [P] podem ser criadas em paralelo
- **US1 - Sub-fase 2B (T004)**: Depende de T002 (`_save_etapa_md` precisa existir)
- **US1 - Sub-fase 2C (T005, T006)**: Depende de T003 (`clean_etapas_dir` precisa existir) e T004 (etapas são salvas) e T007 (`generate_pdf` refatorado precisa existir)
- **US1 - Sub-fase 2D (T007)**: Sem dependências — [P] pode ser implementado em paralelo com Sub-fase 2A e 2B (arquivo diferente)
- **US1 - Sub-fase 2E (T008)**: Depende de T005 e T006 (só remover após confirmar que a nova chamada funciona)
- **Polish (Phase 3)**: Depende de todas as sub-fases da US1

### User Story Dependencies

- **US1 (P1)**: MVP — pode ser entregue de forma independente

### Parallel Opportunities

- T002 e T003 (funções auxiliares) — [P], arquivos diferentes na prática (mesmo arquivo mas funções independentes)
- T002/T003 (pipeline.py) e T007 (pdf_generator.py) — [P], arquivos completamente diferentes
- T005 e T006 (run_once e run_ten_times) — podem ser implementados em sequência ou paralelo

### Parallel Example: User Story 1

```bash
# Sub-fase 2A + 2D em paralelo (arquivos diferentes):
Task: "Criar _save_etapa_md e clean_etapas_dir em backend/pipeline.py"
Task: "Refatorar generate_pdf em backend/pdf_generator.py"
```

---

## Implementation Strategy

### MVP First (US1 Complete)

1. **Phase 1**: T001 — `.gitignore`
2. **Sub-fase 2A**: T002, T003 — funções auxiliares (podem ser em paralelo com 2D)
3. **Sub-fase 2D**: T007 — refatorar `generate_pdf()` (paralelo com 2A/2B)
4. **Sub-fase 2B**: T004 — salvar etapas em `run_single_pipeline()`
5. **Sub-fase 2C**: T005, T006 — limpeza e integração em `run_once()` e `run_ten_times()`
6. **Sub-fase 2E**: T008 — remover texto concatenado antigo
7. **Phase 3**: T009 — validação via quickstart

### Incremental Delivery

1. T001 + T002 + T003 + T007 → Estrutura pronta (funções existem, mas não são chamadas)
2. T004 → Etapas são salvas como .md durante execução (mas PDF pode ainda usar texto antigo)
3. T005 + T006 + T008 → Pipeline completo usando o novo fluxo
4. T009 → Validação final
