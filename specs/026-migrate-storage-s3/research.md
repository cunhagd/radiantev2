# Research: Migrar Armazenamento Local para S3

**Date**: 2026-06-30

## Summary

Análise completa do código-fonte para mapear todas as operações de leitura/escrita no diretório `data/` local e no bucket S3 `radiante-final`. O objetivo é eliminar completamente o uso do armazenamento local para dados persistentes.

---

## 1. Mapeamento de Operações no Diretório `data/` Local

### 1.1 Upload de Documentos

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| Salvar upload | `backend/app.py` | 197-200 | `docs_dir.mkdir()` + `local_path.write_bytes()` — salva em `data/docs/` |
| Upload no S3 | `backend/app.py` | 203 | `upload_file(config, data, f"docs/{fn}")` — **já existe** como cópia |

**Decisão**: Remover a escrita local (`data/docs/`) e manter apenas o upload S3. O S3 já recebe o arquivo.

### 1.2 Leitura de Contexto para Pipeline

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| Ler docs locais | `backend/s3_client.py` | 150-162 | `get_s3_combined_context()` lê de `data/docs/` primeiro |
| Fallback S3 | `backend/s3_client.py` | 165-168 | Se `data/docs/` vazio, busca de `docs/` no S3 |

**Decisão**: Inverter a prioridade — S3 primeiro (e único). Remover a leitura de `data/docs/`.

### 1.3 Salvamento de Etapas do Pipeline

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| Salvar etapa 1-4 (modo once) | `backend/pipeline.py` | 198, 218, 239, 272 | `_save_etapa_md()` → `data/etapas/etapaN.md` |
| Salvar no S3 | `backend/pipeline.py` | 322-323 | `upload_file()` → `results/etapaN_completo.md` |
| Salvar etapas (modo 10x) | `backend/pipeline.py` | 528, 553, 614-615, 656 | `_save_etapa_md()` → `data/etapas/` |
| Upload 10x S3 | `backend/pipeline.py` | 677-680 | `upload_file()` → `results/etapa3_repeticao_{i}.md` |

**Decisão**: Remover chamadas a `_save_etapa_md()`. Manter apenas os uploads S3. A função `_save_etapa_md()` pode ser removida.

### 1.4 Salvamento de Resultados Finais

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| JSON final local (modo once) | `backend/pipeline.py` | 332-334 | `local_json_path.write_text()` → `data/resultado_final.json` |
| JSON final S3 | `backend/pipeline.py` | 335-338 | `upload_file()` → `results/resultado_final.json` |
| JSON 10x local | `backend/pipeline.py` | 710-712 | `json_local_path.write_text()` → `data/consolidado_10x.json` |
| JSON 10x S3 | `backend/pipeline.py` | 713 | `upload_file()` → `results/consolidado_10x.json` |
| Auditoria local | `backend/pipeline.py` | 695-697 | `audit_local_path.write_text()` → `data/auditoria_10x.md` |
| Auditoria S3 | `backend/pipeline.py` | 699 | `upload_file()` → `results/auditoria_10x.md` |
| PDF local | `backend/pipeline.py` | 453, 716-717 | `generate_pdf()` → `data/relatorio_consolidado[_10x].pdf` |
| PDF S3 | `backend/pipeline.py` | 458-461, 719-723 | `upload_file()` → `results/relatorio_consolidado[_10x].pdf` |

**Decisão**: Remover todas as escritas locais. Manter apenas as escritas S3.

### 1.5 Leitura de Resultados (Endpoint /api/last-result)

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| Cache memória | `backend/app.py` | 48-51 | `ANALYSIS_JOBS["last_result"]` |
| Fallback local | `backend/app.py` | 55-72 | `data/consolidado_10x.json` → `data/resultado_final.json` |
| Fallback S3 | `backend/app.py` | 75-87 | `results/consolidado_10x.json` → `results/resultado_final.json` |

**Decisão**: Remover o fallback local (passo 2). Manter: memória cache → S3.

### 1.6 Servir Arquivos via HTTP (Endpoint /data/)

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| Servir de `data/` | `backend/app.py` | 96-102 | `ROOT_DIR / path.lstrip("/")` → lê do disco |

**Decisão**: Substituir por download do S3 para memória, transmitindo ao cliente. Exemplo no frontend: `API.BASE + '/data/' + pdfName`.

### 1.7 Limpeza de Dados

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| Limpeza local | `backend/app.py` | 244-256 | `shutil.rmtree()`, `unlink()`, `mkdir()` |
| Limpeza S3 docs | `backend/app.py` | 261-269 | `delete_files(config, "docs/")` |
| Limpeza S3 markdown | `backend/app.py` | 271-279 | `delete_files(config, "markdown_docs/")` |
| Limpeza S3 results | `backend/app.py` | 281-289 | `delete_files(config, "results/")` |
| Limpeza S3 runs | `backend/app.py` | 291-299 | `delete_files(config, "runs/")` |
| Timeline frontend | `frontend/js/loading.js` | ~62-69, ~507-517 | Mapa `clearStepMap` com etapa "local" |

**Decisão**: Remover a etapa de limpeza local. Manter apenas as 4 etapas S3. Atualizar `loading.js`.

### 1.8 Geração de PDF

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| Ler etapas do disco | `backend/pdf_generator.py` | 191 | `etapas_path.glob("*.md")` — lê `data/etapas/*.md` |
| Ler JSON do disco | `backend/pdf_generator.py` | 200 | `json_path.read_text()` — lê `data/resultado_final.json` |
| Ler conteúdo MD | `backend/pdf_generator.py` | 240 | `fpath.read_text()` — lê cada etapa |

**Decisão**: Modificar `generate_pdf()` para receber os dados das etapas e JSON por parâmetro (em memória), passados pelo pipeline. O pipeline já tem esses dados disponíveis antes de salvar.

### 1.9 Extração de Texto (save_markdown)

| Operação | Arquivo | Linhas | Ação |
|---|---|---|---|
| Salvar markdown local | `backend/extract.py` | 176-186 | `md_path.write_text()` → `data/markdown_docs/` |

**Decisão**: Modificar `save_markdown()` para salvar no S3 (`markdown_docs/`). Atualmente o S3 tem prefixo `markdown_docs/` mas não é populado — esta é uma oportunidade de fazê-lo.

---

## 2. Configuração

### 2.1 Config (`backend/config.py`)

| Campo | Valor atual | Decisão |
|---|---|---|
| `docs_dir` | `ROOT_DIR / "data" / "docs"` | Remover ou manter como opcional (não usado para persistência) |
| `md_dir` | `ROOT_DIR / "data" / "markdown_docs"` | Remover ou tornar opcional |

### 2.2 Limpeza de Artefatos (pipeline.py)

| Função | Ação | Decisão |
|---|---|---|
| `clean_artefatos_anteriores()` | Deleta PDFs/JSONs em `data/` | Migrar para S3 |
| `clean_etapas_dir()` | Deleta `*.md` em `data/etapas/` | Remover (etapas não serão mais locais) |

---

## 3. Modo CLI

O modo CLI (`--mode cli`) em `backend/app.py` (linhas 418-512) também lê de `data/docs/` e salva em `data/results/`. **Decisão**: Migrar para S3, consistente com o modo web.

---

## 4. Frontend

### 4.1 Timeline de Limpeza

Em `frontend/js/loading.js`, o mapa `clearStepMap` (linhas ~507-517) mapeia:

```javascript
"local": 1,
"s3_docs": 2,
"s3_markdown": 3,
"s3_results": 4,
"s3_runs": 5,
```

**Decisão**: Remover a entrada `"local": 1` e reindexar.

### 4.2 Link de Download do PDF

Em `frontend/index.html` (linha ~227):

```javascript
var pdfLink = API.BASE + '/data/' + pdfName;
```

**Decisão**: O endpoint `/data/` continuará existindo, mas buscará do S3. O frontend não precisa mudar o link.

---

## 5. Impacto em Testes

| Teste | Impacto | Ação |
|---|---|---|
| `backend/tests/test_config.py` | Verifica `docs_dir` aponta para `data/docs/` | Ajustar expectativa |
| Testes que dependem de `data/` local | Precisam mockar S3 ou usar `moto` | Adicionar fixture com `moto` |

**Decisão**: Usar `moto` (biblioteca de mock AWS) nos testes para simular S3. `moto` já é compatível com `boto3` e não requer permissões reais.

---

## 6. Dependências

Nenhuma nova dependência de runtime. Para testes, será necessário adicionar `moto` (já amplamente usado para mock de serviços AWS em testes Python).

**Estimativa de esforço**: ~50-80 linhas alteradas no backend, ~5-10 linhas no frontend.
