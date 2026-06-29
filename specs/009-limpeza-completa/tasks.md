# Tasks — Limpeza Completa do Sistema

**Input**: specs/009-limpeza-completa/spec.md, specs/009-limpeza-completa/plan.md

## 1. [US1] Limpeza do diretorio data/ local em _handle_clear
**Arquivo**: `backend/app.py`
- Adicionar logica para remover todos os arquivos de `data/docs/`, `data/markdown_docs/`, e da raiz `data/` (PDFs, JSONs, .md)
- Manter estrutura de diretorios (criar novamente se necessario)
- **P**: Pode ser feito em paralelo com S3

## 2. [US2] Limpeza S3 (ja implementado, verificar)
**Arquivo**: `backend/app.py`
- `delete_files(config, prefix)` para `docs/`, `markdown_docs/`, `results/`, `runs/` — ja existe, apenas verificar

## 3. [US3] Reset de estado em memoria
**Arquivo**: `backend/app.py`
- Resetar `ANALYSIS_JOBS` para `{"status": "idle", "message": "", "error_details": "", "last_result": None}`
- Chamar `Progress.reset(total_runs=1)` para reiniciar progresso
- **P**: Pode ser feito em paralelo com limpeza local

## 4. [US3] Limpeza do historico de execucao
**Arquivo**: `backend/pipeline.py`
- Adicionar funcao `clear_execution_history()` que reseta `_execution_history = []`
- Importar e chamar em `_handle_clear`

## 5. [US4] Reset da interface frontend
**Arquivo**: `frontend/js/ui.js`
- Em `clearAllFrontendData()`, garantir que `btnOnce.disabled = false` e `btnTen.disabled = false` apos limpeza
