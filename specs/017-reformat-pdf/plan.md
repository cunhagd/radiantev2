# Implementation Plan: Reformatação do PDF Consolidado

**Branch**: `017-reformat-pdf` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/017-reformat-pdf/spec.md`

## Summary

Reformatar o PDF do relatório consolidado (modos 1x e 10x) com design profissional seguindo a identidade visual Material Design 3. O conteúdo textual permanece IDÊNTICO — apenas a formatação visual (cabeçalho, rodapé, blocos de etapa, tabelas, callout de total) é alterada no módulo `backend/pdf_generator.py`.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: reportlab (já instalado)

**Storage**: Sistema de arquivos local (`data/`) + S3 (`radiante-final`)

**Testing**: pytest (backend)

**Target Platform**: Linux (EC2) e Windows (desenvolvimento local)

**Project Type**: Web service (backend HTTP nativo + frontend estatico)

**Performance Goals**: N/A — feature de formatação visual, sem impacto em performance

**Constraints**:
- Mesmo conteúdo textual — nenhuma informação alterada
- Design deve seguir Material Design 3 (paleta: #4285f4, tons de cinza)
- Fontes padrão do ReportLab (Helvetica, Courier)
- Sem novas dependências

**Scale/Scope**: Apenas o arquivo `backend/pdf_generator.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: Sem alterações no backend HTTP. ✅ OK
2. **GATE-CREDENCIAIS**: Sem alterações. ✅ OK
3. **GATE-PIPELINE**: Sem alterações no pipeline de 4 etapas. ✅ OK
4. **GATE-CEGUEIRA**: Sem alterações. ✅ OK
5. **GATE-CPC25**: Sem alterações. ✅ OK
6. **GATE-S3-BUCKET**: Sem alterações. ✅ OK
7. **GATE-EXTRACAO**: Sem alterações. ✅ OK
8. **GATE-FRONTEND**: Sem alterações. ✅ OK
9. **GATE-DEPENDENCIAS**: ReportLab já está listado como dependência aprovada. ✅ OK
10. **GATE-DEPLOY**: Sem alterações no CI/CD. ✅ OK

**Resultado**: Nenhuma violação. Feature puramente de formatação visual.

## Project Structure

### Documentation (this feature)

```text
specs/017-reformat-pdf/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app.py                # Sem alterações
├── pipeline.py           # Sem alterações (apenas chama generate_pdf)
├── pdf_generator.py      # ÚNICO arquivo modificado — reformatação completa
└── metrics.py            # Sem alterações
```

**Structure Decision**: Mantém a estrutura existente. Apenas `backend/pdf_generator.py` é modificado.

## Complexity Tracking

Nenhuma violação — sem necessidade de justificativa de complexidade.
