# Data Model: Migrar Armazenamento Local para S3

**Date**: 2026-06-30

## Entity: Bucket S3 `radiante-final`

Única fonte de verdade para armazenamento persistente de dados.

### Prefixos

| Prefixo | Conteúdo | Operações | TTL / Limpeza |
|---------|----------|--------|---------------|
| `docs/{filename}` | Documentos enviados pelo usuário (PDF, JSON, DOCX, TXT) | `PutObject` (upload), `GetObject` (leitura contexto), `ListObjects` (listar), `DeleteObjects` (limpeza) | Até limpeza manual |
| `markdown_docs/{filename}_extraido.md` | Texto extraído dos documentos em formato markdown | `PutObject` (save_markdown), `DeleteObjects` (limpeza) | Até limpeza manual |
| `results/etapa1_completo.md` | Saída da Etapa 1 (Metadados) | `PutObject` (pipeline), `GetObject` (PDF generator), `DeleteObjects` (limpeza) | Até limpeza manual |
| `results/etapa2_completo.md` | Saída da Etapa 2 (Cifras CLT) | `PutObject`, `GetObject`, `DeleteObjects` | Até limpeza manual |
| `results/etapa3_completo.md` | Saída da Etapa 3 (Probabilidade e Risco CPC 25) — modo once, unificado | `PutObject`, `GetObject`, `DeleteObjects` | Até limpeza manual |
| `results/etapa3_repeticao_{i}.md` | Saída individual de cada repetição da Etapa 3 (modo 10x, i=1..10) | `PutObject` (pipeline 10x), `DeleteObjects` | Até limpeza manual |
| `results/etapa4_completo.md` | Saída da Etapa 4 (Consolidação Final) | `PutObject`, `GetObject`, `DeleteObjects` | Até limpeza manual |
| `results/resultado_final.json` | JSON consolidado final (modo once) | `PutObject` (pipeline), `GetObject` (last-result), `DeleteObjects` | Até limpeza manual |
| `results/consolidado_10x.json` | JSON consolidado final (modo 10x) | `PutObject` (pipeline 10x), `GetObject` (last-result), `DeleteObjects` | Até limpeza manual |
| `results/relatorio_consolidado.pdf` | PDF consolidado (modo once) | `PutObject` (pipeline), `GetObject` (/data/ endpoint), `DeleteObjects` | Até limpeza manual |
| `results/relatorio_consolidado_10x.pdf` | PDF consolidado (modo 10x) | `PutObject` (pipeline 10x), `GetObject` (/data/ endpoint), `DeleteObjects` | Até limpeza manual |
| `results/auditoria_10x.md` | Relatório de auditoria (modo 10x) | `PutObject` (pipeline 10x), `DeleteObjects` | Até limpeza manual |
| `runs/` | Prefixo reservado (não usado atualmente) | `DeleteObjects` (limpeza) | Até limpeza manual |

### Permissões S3 Necessárias

| Ação | Objeto | Uso |
|------|--------|-----|
| `s3:PutObject` | `radiante-final/*` | Upload docs, salvar etapas/JSON/PDF/auditoria |
| `s3:GetObject` | `radiante-final/docs/*`, `radiante-final/results/*` | Leitura de contexto, last-result, servir PDF |
| `s3:ListBucket` | `radiante-final` | Listar docs para contexto, listar objetos para limpeza |
| `s3:DeleteObject` | `radiante-final/docs/*`, `radiante-final/markdown_docs/*`, `radiante-final/results/*`, `radiante-final/runs/*` | Limpeza de dados |

## Entity: Cache em Memória (`ANALYSIS_JOBS["last_result"]`)

Cache volátil em RAM do último resultado de análise.

| Campo | Tipo | Origem |
|-------|------|--------|
| `last_result` | `dict \| None` | Populado ao final do pipeline (modo once ou 10x) |
| `status` | `str` | `"idle"`, `"processing"`, `"completed"`, `"error"` |

**Comportamento**: Ao reiniciar o servidor, o cache é perdido. O endpoint `/api/last-result` então busca do S3.

## Entity: Diretório `data/` (Local — Não Persistente)

Após a migração, o diretório `data/` local **não é mais** uma fonte de verdade.

| Subdiretório | Uso Atual | Novo Comportamento |
|-------------|-----------|-------------------|
| `data/docs/` | Upload de documentos | **Removido** — upload vai direto para S3 |
| `data/markdown_docs/` | Texto extraído | **Removido** — save_markdown salva no S3 |
| `data/etapas/` | Etapas do pipeline | **Removido** — pipeline salva no S3 |
| `data/resultado_final.json` | JSON modo once | **Removido** — apenas no S3 |
| `data/consolidado_10x.json` | JSON modo 10x | **Removido** — apenas no S3 |
| `data/auditoria_10x.md` | Auditoria modo 10x | **Removido** — apenas no S3 |
| `data/relatorio_consolidado*.pdf` | PDFs consolidados | **Removido** — apenas no S3 |

O diretório pode permanecer vazio no repositório para evitar breaking changes em imports que referenciem `ROOT_DIR / "data"`, mas nenhuma operação de negócio dependerá dele.

## Mapa de Transição: Operação → Fonte

| Operação | Antes (Local) | Depois (S3) |
|----------|---------------|-------------|
| Upload | `data/docs/` + S3 `docs/` | S3 `docs/` apenas |
| Leitura de contexto | `data/docs/` → fallback S3 | S3 `docs/` apenas |
| Salvar etapas | `data/etapas/` + S3 `results/` | S3 `results/` apenas |
| Salvar JSON | `data/` + S3 `results/` | S3 `results/` apenas |
| Salvar PDF | `data/` + S3 `results/` | S3 `results/` apenas |
| Salvar markdown extraído | `data/markdown_docs/` | S3 `markdown_docs/` apenas |
| Servir PDF (/data/) | Disco local (`data/`) | S3 `results/` (baixar para memória) |
| Limpeza | Local + S3 (4 prefixos) | S3 (4 prefixos) apenas |
| Cache last-result | Memória → local → S3 | Memória → S3 |
