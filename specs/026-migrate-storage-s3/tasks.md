# Tasks: Migrar Armazenamento Local para S3

**Input**: Design documents from `specs/026-migrate-storage-s3/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Não solicitados explicitamente na especificação. Testes existentes devem ser ajustados para compatibilidade.

**Organization**: Tasks grouped by user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: Arquivos em `backend/` — `app.py`, `pipeline.py`, `s3_client.py`, `config.py`, `extract.py`, `pdf_generator.py`
- **Frontend**: Arquivos em `frontend/` — `index.html`, `js/loading.js`

---

## Phase 1: Setup & Foundational (Shared Infrastructure)

**Purpose**: Ajustes de configuração e funções compartilhadas que todas as user stories dependem.

**⚠️ CRITICAL**: Nenhuma user story pode começar sem esta fase concluída.

- [x] T001 Remover campos `docs_dir` e `md_dir` da dataclass `Config` em `backend/config.py` (tornar opcionais ou remover, já que armazenamento local não será mais usado para persistência)

- [x] T002 [P] Modificar `get_s3_combined_context()` em `backend/s3_client.py` para baixar documentos exclusivamente do S3 (`docs/`), removendo a lógica de fallback para `data/docs/` local

- [x] T003 [P] Modificar `save_markdown()` em `backend/extract.py` para salvar o markdown extraído no S3 (`markdown_docs/{filename}_extraido.md`) em vez de `data/markdown_docs/` local

- [x] T004 [P] Modificar `generate_pdf()` em `backend/pdf_generator.py` para receber os dados das etapas e do JSON final como parâmetros (em memória), em vez de ler arquivos de `data/etapas/` e `data/resultado_final.json` do disco. O retorno deve ser o PDF em bytes (não salvar em disco).

**Checkpoint**: Foundation ready — funções auxiliares preparadas para S3.

---

## Phase 2: User Story 1 - Upload de Documentos Direto para o S3 (Priority: P1) 🎯 MVP

**Goal**: Upload de documentos salva arquivo diretamente no S3 `docs/{filename}`, sem criar cópia local em `data/docs/`.

**Independent Test**: Fazer upload de um PDF via `POST /api/upload` e verificar: (a) arquivo existe em `s3://radiante-final/docs/{filename}`, (b) arquivo NÃO existe em `data/docs/{filename}`.

- [x] T005 [US1] Modificar `_handle_upload()` em `backend/app.py` para salvar o arquivo apenas no S3 (`upload_file()`), removendo a escrita local em `data/docs/` com `docs_dir.mkdir()` e `local_path.write_bytes()`

- [x] T006 [US1] Adicionar tratamento de erro no upload (`_handle_upload` em `backend/app.py`): se `upload_file()` lançar exceção (S3 indisponível), retornar HTTP 503 com mensagem "Serviço de armazenamento (S3) indisponível. Tente novamente." — sem salvar cópia local como fallback

**Checkpoint**: US1 funcional — upload opera 100% via S3.

---

## Phase 3: User Story 2 - Pipeline de Análise com Leitura/Escrita no S3 (Priority: P1)

**Goal**: Pipeline (modo 1x e 10x) lê documentos do S3 e salva etapas, JSON final, PDF e auditoria exclusivamente no S3, sem criar arquivos locais.

**Independent Test**: Executar análise 1x e verificar: (a) arquivos `results/etapa1_completo.md`, `results/etapa2_completo.md`, `results/etapa3_completo.md`, `results/etapa4_completo.md`, `results/resultado_final.json`, `results/relatorio_consolidado.pdf` existem no S3; (b) diretório `data/` local vazio.

- [x] T007 [US2] Em `run_single_pipeline()` em `backend/pipeline.py`: remover as 4 chamadas a `_save_etapa_md()` que salvam etapas localmente. Manter apenas o upload S3 já existente via `save_stage_files()`.

- [x] T008 [US2] Em `save_stage_files()` em `backend/pipeline.py`: remover a escrita local de `data/resultado_final.json`. Manter apenas o upload S3.

- [x] T009 [US2] Em `run_once()` em `backend/pipeline.py`: substituir a geração de PDF local (`generate_pdf()` que salva em `data/`) pela nova versão que retorna bytes, e fazer upload para S3 `results/relatorio_consolidado.pdf`.

- [x] T010 [P] [US2] Em `run_ten_times()` em `backend/pipeline.py`: remover as chamadas a `_save_etapa_md()` e remover escritas locais de `data/auditoria_10x.md` e `data/consolidado_10x.json`. Manter apenas uploads S3.

- [x] T011 [P] [US2] Em `run_ten_times()` em `backend/pipeline.py`: substituir a geração de PDF local pela nova versão que retorna bytes, fazendo upload para S3 `results/relatorio_consolidado_10x.pdf`.

- [x] T012 [US2] Em `backend/pipeline.py`: remover a função `clean_etapas_dir()` e suas chamadas.

- [x] T013 [US2] Em `backend/pipeline.py`: remover a função `clean_artefatos_anteriores()` (opera apenas local) — a deleção de artefatos do modo oposto agora é feita via `delete_files()` S3.

- [x] T014 [US2] Ajustar todas as chamadas de `generate_pdf()` no pipeline (modo once e 10x) para passar os dados das etapas e JSON final como parâmetros em memória, em vez de depender que `generate_pdf()` leia do disco.

**Checkpoint**: US2 funcional — pipeline opera 100% via S3.

---

## Phase 4: User Story 3 - Visualização de Resultados via S3 (Priority: P2)

**Goal**: Endpoints `/api/last-result` e `/data/{filename}` buscam dados exclusivamente do cache em memória ou do S3, sem fallback para arquivos locais.

**Independent Test**: Executar análise, reiniciar servidor (perde cache), acessar página: resultados carregam do S3. Download de PDF funciona via `/data/`.

- [x] T015 [US3] Em `backend/app.py` (`do_GET`, endpoint `/api/last-result`): remover o bloco de fallback local que tenta ler `data/consolidado_10x.json` e `data/resultado_final.json`. Manter apenas: cache memória -> S3 (`results/consolidado_10x.json` -> `results/resultado_final.json`).

- [x] T016 [US3] Em `backend/app.py` (`do_GET`, endpoint `/data/{filename}`): substituir a leitura de disco local por download do S3, transmitindo os bytes ao cliente com Content-Type adequado.

- [x] T017 [P] [US3] Adicionar validacao de integridade do PDF baixado do S3 no endpoint `/data/{filename}` em `backend/app.py`: verificar se os bytes baixados formam um PDF valido (ex: cabecalho `%PDF-` nos primeiros 5 bytes) antes de transmitir ao cliente. Se invalido, retornar HTTP 502 com mensagem "Arquivo PDF corrompido ou incompleto no servidor".

**Checkpoint**: US3 funcional — resultados servidos exclusivamente via S3.

---

## Phase 5: User Story 4 - Limpeza de Dados Exclusivamente no S3 (Priority: P2)

**Goal**: Clear-all remove apenas dados do S3, sem etapa de limpeza local. Timeline SSE mostra apenas etapas S3.

**Independent Test**: Executar clear-all com `stream=true` e verificar: (a) eventos SSE não incluem etapa "local", (b) após limpeza, bucket está vazio nos prefixos `docs/`, `markdown_docs/`, `results/`, `runs/`.

- [x] T018 [US4] Em `_handle_clear()` em `backend/app.py`: remover todo o bloco de limpeza local que itera `data/` com `shutil.rmtree()` e `unlink()`. Manter apenas as 4 etapas de limpeza S3 (`docs/`, `markdown_docs/`, `results/`, `runs/`) e o reset de estado em memoria.

- [x] T019 [US4] Em `frontend/js/loading.js`: remover a entrada `"local": 1` do mapa `clearStepMap` e reindexar as entradas S3 (`s3_docs: 1`, `s3_markdown: 2`, `s3_results: 3`, `s3_runs: 4`). Tambem remover quaisquer referencias a etapa "local" na timeline visual (steps de 6 para 5, loop `s <= 6` para `s <= 5`).

**Checkpoint**: US4 funcional — limpeza opera apenas no S3.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Ajustes finais para completar a migração.

- [x] T020 Migrar o modo CLI (`--mode cli`) em `backend/app.py` para operar 100% via S3: leitura de documentos via `get_s3_combined_context()`, salvamento de resultados via `upload_file` para `results/resultado.json`.

- [x] T021 [P] Ajustar `backend/tests/test_config.py` para nao esperar mais `docs_dir` e `md_dir` na dataclass `Config` (conforme T001).

- [x] T022 Executar o guia de validacao `quickstart.md` para confirmar que todos os cenarios funcionam: upload, pipeline 1x, pipeline 10x, visualizacao, limpeza, falha de S3.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Sem dependências — pode começar imediatamente
- **Phase 2 (US1)**: Depende de Phase 1
- **Phase 3 (US2)**: Depende de Phase 1 (T002, T004 para leitura de contexto e geração de PDF)
- **Phase 4 (US3)**: Depende de Phase 3 (precisa de resultados no S3 para servir)
- **Phase 5 (US4)**: Independente — pode executar em paralelo com Phase 2-4
- **Phase 6 (Polish)**: Depende de todas as fases anteriores

### User Story Dependencies

| User Story | Depende de | Pode paralelizar com |
|------------|-----------|---------------------|
| **US1 (P1)** | Phase 1 | — |
| **US2 (P1)** | Phase 1, US1 | — |
| **US3 (P2)** | Phase 1, US2 | — |
| **US4 (P2)** | Phase 1 | US1, US2, US3 |

### Parallel Opportunities

- T002, T003, T004 (Phase 1) podem rodar em paralelo (arquivos diferentes)
- T007 e T010 (Phase 3) podem rodar em paralelo (modo once vs modo 10x)
- T015, T016, T017 (Phase 4) podem rodar em paralelo (endpoints diferentes + validação de PDF)
- T018 e T019 (Phase 5) podem rodar em paralelo (backend vs frontend)
- US4 pode ser implementada em paralelo com US2/US3 (não há dependência de dados)

---

## Parallel Example: Phase 1 (Setup)

```bash
# Launch all Phase 1 tasks together:
Task: "T001 Remover docs_dir e md_dir do Config em backend/config.py"
Task: "T002 Modificar get_s3_combined_context em backend/s3_client.py"
Task: "T003 Modificar save_markdown em backend/extract.py"
Task: "T004 Modificar generate_pdf em backend/pdf_generator.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup & Foundational
2. Complete Phase 2: User Story 1 (Upload S3)
3. **STOP and VALIDATE**: Test upload independente
4. Deploy/demo se desejar

### Incremental Delivery

1. Phase 1 + US1 → Upload funciona 100% S3
2. Add US2 → Pipeline 100% S3
3. Add US3 → Resultados servidos do S3
4. Add US4 → Limpeza apenas S3
5. Phase 6 → CLI + testes + validação final

### Parallel Team Strategy

1. Dev A: Phase 1 (tasks compartilhadas) + US1 + US2
2. Dev B: US4 (pode começar após Phase 1, independente de US1-US3)
3. Dev C: US3 (começa após US2)

---

## Notes

- [P] tasks = different files, no dependencies
- [US1..US4] labels mapeiam para as user stories da spec
- Nenhuma nova dependência de runtime necessária (boto3 já presente)
- Para testes com mock S3, considerar adicionar `moto` como dependência de desenvolvimento
- Commit após cada fase para facilitar rollback
- Parar em qualquer checkpoint para validar independentemente
