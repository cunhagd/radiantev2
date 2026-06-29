# Implementation Plan: Estruturar Etapas do Pipeline em Markdown

**Branch**: `019-estruturar-etapas-pipeline` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/019-estruturar-etapas-pipeline/spec.md`

## Summary

Refatorar o pipeline (`pipeline.py`) para salvar o resultado de cada etapa como um arquivo markdown estruturado em `data/etapas/` (`etapa1.md`, `etapa2.md`, `etapa3.md`, `etapa4.md` — e no modo 10x, `etapa3_rodada{N}.md`). O `generate_pdf()` em `pdf_generator.py` deve ser refatorado para consumir esses arquivos .md em vez do texto bruto concatenado, garantindo um PDF estruturado e consistente.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: `reportlab` (já instalado)

**Storage**: 
- Local: `data/etapas/` (diretório com arquivos .md por etapa)
- S3: `radiante-final` bucket (resultados já enviados via `save_stage_files`)

**Testing**: pytest (backend)

**Target Platform**: Linux (EC2) e Windows (desenvolvimento local)

**Project Type**: Web service (backend HTTP nativo + frontend estático)

**Performance Goals**: N/A — mudança puramente estrutural, sem impacto em latência de inferência

**Constraints**:
- ReportLab já instalado — sem novas dependências
- O pipeline (`pipeline.py`) continua executando as 4 etapas — apenas a forma de armazenamento muda (memória → arquivo .md)
- `generate_pdf()` em `pdf_generator.py` deve aceitar diretório `data/etapas/` como entrada
- Diretório `data/etapas/` deve ser limpo antes de cada nova análise
- O conteúdo salvo deve ser markdown limpo e organizado (tabelas, cabeçalhos, seções)

**Scale/Scope**: 
- `backend/pipeline.py` — adicionar funções de salvamento de etapa em .md
- `backend/pdf_generator.py` — refatorar `generate_pdf()` para ler arquivos .md de um diretório
- `data/etapas/` — novo diretório (adicionar ao `.gitignore`)
- `frontend/index.html` — verificar se o nome do PDF mudou (mantido inalterado)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: Sem alterações no backend HTTP. ✅ OK
2. **GATE-CREDENCIAIS**: Sem alterações no manuseio de credenciais. ✅ OK
3. **GATE-PIPELINE**: Pipeline continua com exatas 4 etapas encadeadas. O salvamento em .md é uma melhoria no armazenamento, não uma alteração na estrutura do pipeline. ✅ OK
4. **GATE-CEGUEIRA**: Sem alterações nas regras de cegueira da Etapa 2. ✅ OK
5. **GATE-CPC25**: Sem alterações na classificação de risco. ✅ OK
6. **GATE-S3-BUCKET**: Sem alterações na estrutura do bucket S3. ✅ OK
7. **GATE-EXTRACAO**: Sem alterações na lógica de extração de documentos. ✅ OK
8. **GATE-FRONTEND**: Sem alterações no frontend. ✅ OK
9. **GATE-DEPENDENCIAS**: Nenhuma nova dependência — `reportlab` já está aprovado. ✅ OK
10. **GATE-DEPLOY**: Sem alterações no CI/CD. ✅ OK

**Resultado**: Nenhuma violação. Feature de estruturação de armazenamento das etapas do pipeline.

## Project Structure

### Documentation (this feature)

```text
specs/019-estruturar-etapas-pipeline/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app.py                # Sem alterações
├── pipeline.py           # MODIFICADO — salvar cada etapa como .md em data/etapas/
├── pdf_generator.py      # MODIFICADO — ler arquivos .md de data/etapas/
└── metrics.py            # Sem alterações

data/
├── etapas/               # NOVO — diretório com arquivos .md de cada etapa
│   ├── etapa1.md
│   ├── etapa2.md
│   ├── etapa3.md
│   ├── etapa4.md
│   └── etapa3_rodada{N}.md  # (modo 10x)
└── ...                   # demais diretórios existentes

.gitignore                # MODIFICADO — adicionar data/etapas/
```

**Structure Decision**: Estrutura existente mantida. Adicionado diretório `data/etapas/` para centralizar os arquivos .md de cada etapa. Modificações apenas em `backend/pipeline.py` (salvar) e `backend/pdf_generator.py` (consumir).

## Complexity Tracking

Nenhuma violação — sem necessidade de justificativa de complexidade.
