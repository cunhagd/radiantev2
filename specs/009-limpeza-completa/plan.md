# Plan — Limpeza Completa do Sistema

## Arquivos a Modificar

### backend/app.py
- `_handle_clear()`: expandir para limpar:
  1. Diretorio `data/` local (recursivo, mantendo estrutura de diretorios)
  2. Bucket S3 (ja faz)
  3. Resetar `ANALYSIS_JOBS` para estado inicial (incluindo `last_result = None`)
  4. Chamar `Progress.reset()` para reiniciar progresso
  5. Chamar funcao para limpar `_execution_history` da pipeline

### backend/pipeline.py
- Adicionar funcao `clear_execution_history()` que reseta `_execution_history`

### backend/progress.py
- `Progress.reset()` ja existe e faz o reset corretamente — apenas garantir que seja chamado

### backend/s3_client.py
- Nenhuma alteracao necessaria — `delete_files` ja funciona

### frontend/js/ui.js
- `clearAllFrontendData()`: apos limpar, garantir que botoes de upload e analise fiquem habilitados

## Dados Tecnicos

### Diretorios locais a limpar em `data/`:
- `data/docs/` — documentos enviados
- `data/markdown_docs/` — documentos extraidos
- `data/` — PDFs, JSONs e arquivos de auditoria (.pdf, .json, .md)

### Chaves S3 a limpar:
- `docs/`
- `markdown_docs/`
- `results/`
- `runs/`
