# Implementation Plan: Refatorar PDF para estilo simples

**Branch**: `021-refatorar-pdf-simples` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/021-refatorar-pdf-simples/spec.md`

## User Stories

### User Story 1 — Gerar PDF consolidado com estilo simples (Priority: P1) 🎯 MVP

O operador do pipeline executa a análise jurídica e obtém um PDF funcional com todo o conteúdo das 4 etapas, formatado de forma simples e limpa, sem estilização complexa.

**Independent Test**: Executar o pipeline (1x) e verificar que `data/relatorio_consolidado.pdf` abre corretamente com todo o conteúdo.

## Summary

Refatorar `backend/pdf_generator.py` para remover toda a estilização complexa (Material Design 3 — cores, callouts, fundos coloridos, bordas) e substituir por um estilo simples, funcional e robusto. O PDF deve apenas consolidar os arquivos markdown de `data/etapas/` em um documento limpo com fonte Helvetica, títulos em negrito, tabelas com linhas simples e blocos de código monoespaçados. O código deve ser reduzido de ~416 linhas para no máximo 200 linhas.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: `reportlab` (já instalado)

**Storage**: N/A — PDF gerado em `data/relatorio_consolidado.pdf`

**Testing**: Validação visual — abrir PDF gerado e verificar conteúdo

**Target Platform**: Multiplataforma (Windows/Linux/macOS) — o PDF deve abrir em qualquer leitor

**Project Type**: Refatoração de módulo interno (`backend/pdf_generator.py`)

**Performance Goals**: Geração em < 5s para até 50 páginas

**Constraints**:
- ReportLab é a única biblioteca permitida para PDF
- Nenhuma nova dependência externa
- Código final com no máximo 200 linhas
- PDF deve funcionar sem estilos complexos (sem _make_callout, sem _make_etapa_block com fundos)
- Manter two-pass build (Página X de Y) e validação pós-build (%PDF-, %%EOF)
- Manter a assinatura `generate_pdf(etapas_dir, output_path) -> str`
- Remover paleta de cores, callouts, fundos de etapa, estilos MD3
- Simplificar a lógica de parsing: cada linha markdown vira um Paragraph ou Table

**Scale/Scope**: 
- `backend/pdf_generator.py` — refatoração completa (substituir conteúdo)
- `backend/pipeline.py` — sem alterações (já chama `generate_pdf(ETAPAS_DIR, pdf_path)`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: Sem alterações no backend HTTP — apenas refatoração interna do gerador de PDF. ✅ OK
2. **GATE-CREDENCIAIS**: Sem alterações. ✅ OK
3. **GATE-PIPELINE**: Sem alterações no pipeline de 4 etapas. ✅ OK
4. **GATE-CEGUEIRA**: Sem alterações. ✅ OK
5. **GATE-CPC25**: Sem alterações. ✅ OK
6. **GATE-S3-BUCKET**: Sem alterações. ✅ OK
7. **GATE-EXTRACAO**: Sem alterações. ✅ OK
8. **GATE-FRONTEND**: Sem alterações. ✅ OK
9. **GATE-DEPENDENCIAS**: `reportlab` já está listado como dependência aprovada. Nenhuma nova dependência. ✅ OK
10. **GATE-DEPLOY**: Sem alterações no CI/CD. ✅ OK

**Resultado**: Nenhuma violação.

## Project Structure

### Documentation (this feature)

```text
specs/021-refatorar-pdf-simples/
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
└── pdf_generator.py      # REFATORADO — remover estilos MD3, simplificar parsing
```

**Structure Decision**: Apenas o arquivo `backend/pdf_generator.py` será modificado. O pipeline (`backend/pipeline.py`) já chama `generate_pdf(ETAPAS_DIR, pdf_path)` corretamente — não precisa de alterações.

## Complexity Tracking

Nenhuma violação — sem necessidade de justificativa de complexidade.
