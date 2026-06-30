# Implementation Plan: Migrar Armazenamento Local para S3

**Branch**: `026-migrate-storage-s3` | **Date**: 2026-06-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/026-migrate-storage-s3/spec.md`

## Summary

Migrar 100% do armazenamento de dados do diretório local `data/` para o bucket S3 `radiante-final`. Upload de documentos, leitura de contexto, salvamento de etapas do pipeline, resultados JSON, PDFs consolidados e limpeza de dados passarão a operar exclusivamente via S3. O diretório `data/` deixará de ser usado para armazenamento persistente, eliminando dependência de disco local e viabilizando ambientes efêmeros (containers EC2).

## Technical Context

**Language/Version**: Python 3.14 (já estabelecido no projeto)

**Primary Dependencies**: `boto3` (SDK AWS S3) — já presente. Nenhuma nova dependência necessária.

**Storage**: Amazon S3 — bucket `radiante-final` (já existente e em uso como cópia de segurança). A migração faz o S3 passar de "cópia de segurança" para "única fonte de verdade".

**Testing**: `pytest` com `pytest-cov` (backend). Testes existentes precisarão de ajustes para não dependerem de arquivos locais (uso de `moto` para mock S3 ou fixtures de integração).

**Target Platform**: Linux (EC2) + Windows (dev local). S3 é acessível de qualquer plataforma via boto3.

**Project Type**: Web service (backend HTTP nativo) + CLI.

**Performance Goals**: Operações S3 têm latência adicional de ~50-200ms vs. disco local. Aceitável para o volume esperado (documentos de até ~10MB, dezenas por sessão).

**Constraints**: Manter compatibilidade com desenvolvimento local (`localhost:8000`). Sem fallback para disco local em caso de falha S3.

**Scale/Scope**: Bucket único `radiante-final`. 4 prefixos: `docs/`, `markdown_docs/`, `results/`, `runs/`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

| Gate | Status | Justificativa |
|------|--------|---------------|
| **GATE-FRAMEWORK** (Princípio I) | ✅ PASS | Nenhum framework web novo introduzido. `boto3` já é dependência existente. |
| **GATE-CREDENCIAIS** (Princípio II) | ✅ PASS | Credenciais AWS já são lidas do `.env` e passadas explicitamente ao boto3. Nenhuma mudança. |
| **GATE-PIPELINE** (Princípio III) | ✅ PASS | Pipeline de 4 etapas permanece idêntico. Apenas o destino do armazenamento muda (local → S3). |
| **GATE-CEGUEIRA** (Princípio III) | ✅ PASS | Nenhuma alteração na lógica de cálculo de cifras ou regras de negócio. |
| **GATE-CPC25** (Princípio III) | ✅ PASS | Nenhuma alteração na classificação de risco CPC 25. |
| **GATE-S3-BUCKET** (Princípio IV) | ✅ PASS | Bucket `radiante-final` com prefixos `docs/`, `markdown_docs/`, `results/` e `runs/` já é a estrutura definida. Esta feature reforça e unifica o uso. |
| **GATE-EXTRACAO** (Princípio IV) | ✅ PASS | Nenhuma alteração na lógica de extração de texto (PyMuPDF, Textract, DOCX XML). |
| **GATE-FRONTEND** (Princípio V) | ✅ PASS | Única alteração no frontend: remover etapa "local" da timeline de limpeza em `loading.js`. Sem frameworks ou bundlers. |
| **GATE-DEPENDENCIAS** (Stack Tecnológico) | ✅ PASS | Nenhuma nova dependência. `boto3` já é dependência existente e aprovada. |
| **GATE-DEPLOY** (Infraestrutura AWS) | ✅ PASS | CI/CD inalterado. A EC2 já tem IAM Role com permissões S3. |

**Resultado**: Todos os 10 gates aprovados. Nenhuma violação constitucional.

## Project Structure

### Documentation (this feature)

```text
specs/026-migrate-storage-s3/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── s3-prefix-structure.md
│   └── api-changes.md
└── tasks.md             # Phase 2 output (created by /speckit-tasks)
```

### Source Code (repository root)

```text
radiantev2/
├── backend/
│   ├── app.py              # [MODIFICADO] Upload → S3, clear-all sem local, /data/ via S3
│   ├── pipeline.py         # [MODIFICADO] Etapas, JSON, PDF → S3, remove clean_etapas_dir
│   ├── s3_client.py        # [MODIFICADO] get_s3_combined_context sem fallback local
│   ├── config.py           # [MODIFICADO] Remove/desativa docs_dir e md_dir
│   ├── pdf_generator.py    # [MODIFICADO] Recebe dados por parâmetro, não lê de data/
│   ├── extract.py          # [MODIFICADO] save_markdown → S3
│   └── tests/              # [MODIFICADO] Ajustar fixtures para não depender de data/
├── frontend/
│   ├── js/
│   │   └── loading.js      # [MODIFICADO] Remove etapa "local" da timeline
│   └── index.html          # [MODIFICADO] Link de download PDF via S3
└── data/                   # [INALTERADO] Pode permanecer vazio, não usado para operações
```

## Complexity Tracking

> Nenhuma violação constitucional identificada. Seção não aplicável.
