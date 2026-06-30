# Contract: Mudanças na API HTTP

**Date**: 2026-06-30

## Endpoints Modificados

### `POST /api/upload`

**Antes**:
1. Salva arquivo em `data/docs/{filename}` (local)
2. Tenta upload para S3 `docs/{filename}` (fallback silencioso se falhar)

**Depois**:
1. Salva arquivo diretamente no S3 `docs/{filename}`
2. Se S3 falhar → retorna erro HTTP 503 com mensagem "Serviço de armazenamento indisponível"
3. **NÃO** salva cópia local

**Resposta de sucesso** (inalterada):
```json
{"status": "ok", "filename": "documento.pdf"}
```

**Nova resposta de erro** (S3 indisponível):
```json
{"status": "error", "message": "Serviço de armazenamento (S3) indisponível. Tente novamente."}
```

---

### `GET /api/last-result`

**Antes**:
1. Cache em memória (`ANALYSIS_JOBS["last_result"]`)
2. Fallback: `data/consolidado_10x.json` (local)
3. Fallback: `data/resultado_final.json` (local)
4. Fallback: `results/consolidado_10x.json` (S3)
5. Fallback: `results/resultado_final.json` (S3)

**Depois**:
1. Cache em memória (`ANALYSIS_JOBS["last_result"]`)
2. Fallback: `results/consolidado_10x.json` (S3)
3. Fallback: `results/resultado_final.json` (S3)

**Comportamento**: Mesmas respostas JSON. Apenas a ordem de busca muda (remove passos 2 e 3).

---

### `GET /data/{filename}`

**Antes**: Lê arquivo de `{ROOT_DIR}/data/{filename}` do disco local.

**Depois**: Busca o arquivo no S3 em `results/{filename}` e transmite ao cliente.

**Mudança de lookup**: O endpoint agora procura no prefixo `results/` do S3. Para PDFs, a chave é `results/relatorio_consolidado.pdf` ou `results/relatorio_consolidado_10x.pdf`.

**Resposta**: Inalterada — Content-Type adequado ao arquivo, Content-Length, streaming.

**Em caso de 404 no S3**: Retorna HTTP 404 com mensagem "Arquivo não encontrado".

---

### `POST /api/clear-all`

**Antes**:
1. Limpa `data/` local (recria estrutura de diretórios)
2. Limpa S3 `docs/`
3. Limpa S3 `markdown_docs/`
4. Limpa S3 `results/`
5. Limpa S3 `runs/`
6. Reseta estado em memória
7. Reseta progresso

**Depois**:
1. Limpa S3 `docs/`
2. Limpa S3 `markdown_docs/`
3. Limpa S3 `results/`
4. Limpa S3 `runs/`
5. Reseta estado em memória
6. Reseta progresso

**Eventos SSE**: Os eventos `step` enviados para o frontend mudam de:

```
step: {"step": "local", "status": "processing", "file": "data/"}        ← REMOVIDO
step: {"step": "local", "status": "done"}                                ← REMOVIDO
step: {"step": "s3_docs", "status": "processing", "file": "docs/"}
step: {"step": "s3_docs", "status": "done", "deleted_count": N}
step: {"step": "s3_markdown", "status": "processing", "file": "markdown_docs/"}
step: {"step": "s3_markdown", "status": "done", "deleted_count": N}
step: {"step": "s3_results", "status": "processing", "file": "results/"}
step: {"step": "s3_results", "status": "done", "deleted_count": N}
step: {"step": "s3_runs", "status": "processing", "file": "runs/"}
step: {"step": "s3_runs", "status": "done", "deleted_count": N}
step: {"step": "reset", "status": "processing"}
step: {"step": "reset", "status": "done"}
complete: {"status": "ok", "message": "Sistema limpo com sucesso", "s3_deleted": N}
```

## Endpoints Não Modificados

- `GET /api/status` — inalterado (apenas estado em memória)
- `GET /api/progress` — inalterado (progresso em memória)
- `GET /api/fallback-status` — inalterado
- `GET /api/metrics` — inalterado
- `GET /api/metrics/history` — inalterado
- `POST /api/run-once` — inalterado (apenas o pipeline salva no S3 em vez de local)
- `POST /api/run-ten` — inalterado (apenas o pipeline salva no S3 em vez de local)
