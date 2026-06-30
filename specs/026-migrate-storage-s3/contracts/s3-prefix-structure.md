# Contract: Estrutura de Prefixos S3

**Date**: 2026-06-30

## Bucket

```
radiante-final (us-east-1)
```

## Prefixos e Operações Permitidas

### `docs/` — Documentos enviados pelo usuário

```
s3://radiante-final/docs/{filename}
```

- **Upload**: `s3:PutObject` (POST /api/upload)
- **Leitura (contexto do pipeline)**: `s3:GetObject` (get_s3_combined_context)
- **Listagem**: `s3:ListBucket` (para construir contexto)
- **Limpeza**: `s3:DeleteObject` com prefixo `docs/`

> ⚠️ Filename é preservado do upload original. Não há subdiretórios dentro de `docs/`.

### `markdown_docs/` — Texto extraído em markdown

```
s3://radiante-final/markdown_docs/{filename}_extraido.md
```

- **Escrita**: `s3:PutObject` (save_markdown em extract.py)
- **Limpeza**: `s3:DeleteObject` com prefixo `markdown_docs/`

> ⚠️ Nome do arquivo = `{nome_original_sem_extensao}_extraido.md`.

### `results/` — Artefatos do pipeline

```
s3://radiante-final/results/
├── etapa1_completo.md
├── etapa2_completo.md
├── etapa3_completo.md               # Modo once (unificado)
├── etapa3_repeticao_{1..10}.md      # Modo 10x (individuais)
├── etapa4_completo.md
├── resultado_final.json             # Modo once
├── consolidado_10x.json             # Modo 10x
├── relatorio_consolidado.pdf        # Modo once
├── relatorio_consolidado_10x.pdf    # Modo 10x
└── auditoria_10x.md                 # Modo 10x
```

- **Escrita**: `s3:PutObject` (pipeline.py — save_stage_files e uploads diretos)
- **Leitura (last-result)**: `s3:GetObject` — tenta `consolidado_10x.json` primeiro, depois `resultado_final.json`
- **Leitura (servir PDF)**: `s3:GetObject` — endpoint `/data/{filename}` busca em `results/{filename}`
- **Leitura (PDF generator)**: `s3:GetObject` — etapas e JSON final (alternativa: receber por parâmetro)
- **Limpeza**: `s3:DeleteObject` com prefixo `results/`

> ⚠️ O endpoint `/api/last-result` busca na ordem: memória cache → `results/consolidado_10x.json` → `results/resultado_final.json`.

### `runs/` — Prefixo reservado

```
s3://radiante-final/runs/
```

- **Limpeza**: `s3:DeleteObject` com prefixo `runs/` (atualmente vazio)

## Convenções de Nomenclatura

- Todos os prefixos **terminam com `/`** (padrão S3 para "diretório")
- Filenames **preservam maiúsculas/minúsculas** do upload original
- Markdown extraído usa sufixo `_extraido.md`
- Repetições da etapa 3 (modo 10x) usam `etapa3_repeticao_{i}.md` com `i` de 1 a 10
- PDFs seguem o padrão `relatorio_consolidado[_10x].pdf`

## Política de Cache e Consistência

- **Nenhum cache S3** (CloudFront) configurado — operações diretas via SDK boto3
- Consistência **read-after-write** para PutObject de novas chaves (padrão S3)
- Consistência **eventual** para operações de listagem após DeleteObjects
