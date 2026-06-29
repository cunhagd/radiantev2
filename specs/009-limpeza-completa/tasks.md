# Tasks — Limpeza Completa do Sistema

**Input**: specs/009-limpeza-completa/spec.md, specs/009-limpeza-completa/plan.md

## 1. [US1] [P] Limpeza do diretorio data/ local em _handle_clear [X]
**Arquivo**: `backend/app.py`
- Adicionar logica para remover todos os arquivos de `data/docs/`, `data/markdown_docs/`, e da raiz `data/` (PDFs, JSONs, .md)
- Manter estrutura de diretorios (criar novamente se necessario)

## 2. [US2] [P] Limpeza S3 (ja implementado, verificar) [X]
**Arquivo**: `backend/app.py`
- `delete_files(config, prefix)` para `docs/`, `markdown_docs/`, `results/`, `runs/` — ja existe, apenas verificar

## 3. [US3] [P] Reset de estado em memoria [X]
**Arquivo**: `backend/app.py`
- Resetar `ANALYSIS_JOBS` para `{"status": "idle", "message": "", "error_details": "", "last_result": None}`
- Chamar `Progress.reset(total_runs=1)` para reiniciar progresso

## 4. [US3] Limpeza do historico de execucao [X]
**Arquivo**: `backend/pipeline.py`
- Adicionar funcao `clear_execution_history()` que reseta `_execution_history = []`
- Importar e chamar em `_handle_clear`

## 5. [US4] Reset da interface frontend [X]
**Arquivo**: `frontend/js/ui.js`
- Em `clearAllFrontendData()`, garantir que `btnOnce.disabled = false` e `btnTen.disabled = false` apos limpeza

## 6. [US1] Verificacao de analise em andamento (FR-012) [X]
**Arquivo**: `backend/app.py`
- Em `_handle_clear()`, verificar `ANALYSIS_JOBS["status"]` antes de limpar
- Se `"processing"`, retornar HTTP 409 (Conflict)

## 7. [US1] Tratamento de erros parciais (FR-011) [X]
**Arquivo**: `backend/app.py`
- Envolver cada etapa da limpeza em try/except
- Coletar erros em lista e retornar status "partial" se houver falhas
