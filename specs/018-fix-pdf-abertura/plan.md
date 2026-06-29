# Implementation Plan: Corrigir Abertura do PDF Consolidado

**Branch**: `018-fix-pdf-abertura` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/018-fix-pdf-abertura/spec.md`

## Summary

Corrigir o parser de markdown em `backend/pdf_generator.py` para que o PDF do relatório consolidado (1x e 10x) seja gerado com pelo menos 1 página e estrutura PDF válida, mesmo quando o texto retornado pela IA contiver formatação inesperada, conteúdo extenso ou caracteres especiais.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: reportlab (já instalado)

**Storage**: Sistema de arquivos local (`data/`) + S3 (`radiante-final`)

**Testing**: pytest (backend)

**Target Platform**: Linux (EC2) e Windows (desenvolvimento local)

**Project Type**: Web service (backend HTTP nativo + frontend estatico)

**Performance Goals**: N/A — feature de correcao de parser, sem impacto em performance

**Constraints**:
- ReportLab já instalado — sem novas dependencias
- Conteudo textual gerado em `pipeline.py` permanece inalterado
- PDF deve ser valido (PDF-1.3+, >=1 pagina, trailer integro)
- Deve tratar conteudo vindo da IA com formatacao imprevisivel

**Scale/Scope**: Apenas o arquivo `backend/pdf_generator.py` (parser de markdown)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: Sem alteracoes no backend HTTP. ✅ OK
2. **GATE-CREDENCIAIS**: Sem alteracoes. ✅ OK
3. **GATE-PIPELINE**: Sem alteracoes no pipeline de 4 etapas. ✅ OK
4. **GATE-CEGUEIRA**: Sem alteracoes. ✅ OK
5. **GATE-CPC25**: Sem alteracoes. ✅ OK
6. **GATE-S3-BUCKET**: Sem alteracoes. ✅ OK
7. **GATE-EXTRACAO**: Sem alteracoes. ✅ OK
8. **GATE-FRONTEND**: Sem alteracoes. ✅ OK
9. **GATE-DEPENDENCIAS**: ReportLab ja esta listado como dependencia aprovada. ✅ OK
10. **GATE-DEPLOY**: Sem alteracoes no CI/CD. ✅ OK

**Resultado**: Nenhuma violacao. Feature de correcao de parser do PDF.

## Project Structure

### Documentation (this feature)

```text
specs/018-fix-pdf-abertura/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app.py                # Sem alteracoes
├── pipeline.py           # Sem alteracoes (apenas chama generate_pdf)
├── pdf_generator.py      # UNICO arquivo modificado — correcao do parser
└── metrics.py            # Sem alteracoes
```

**Structure Decision**: Mantem a estrutura existente. Apenas `backend/pdf_generator.py` e modificado.

## Complexity Tracking

Nenhuma violacao — sem necessidade de justificativa de complexidade.
