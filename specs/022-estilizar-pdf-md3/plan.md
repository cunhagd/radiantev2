# Implementation Plan: Estilizar PDF com Material Design 3

**Branch**: `022-estilizar-pdf-md3` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/022-estilizar-pdf-md3/spec.md`

## User Stories

### User Story 1 — PDF com Estilo Profissional MD3 (Priority: P1) 🎯 MVP

O operador do pipeline jurídico gera o relatório consolidado em PDF e obtém um documento visualmente profissional, com identidade visual consistente (cores, tipografia, espaçamentos) seguindo o sistema Material Design 3.

**Independent Test**: Gerar o PDF via pipeline e verificar visualmente que os elementos de design MD3 estão presentes em todas as páginas.

### User Story 2 — Página de Capa com Resumo (Priority: P2)

O operador do pipeline recebe um PDF com uma página de capa profissional contendo dados do processo extraídos de `data/resultado_final.json`.

**Independent Test**: Gerar o PDF e verificar que a primeira página é uma capa com as informações do processo.

## Summary

Adicionar estilização Material Design 3 ao `backend/pdf_generator.py` — paleta de cores MD3 completa, blocos de etapa com fundo alternado, tabelas com cabeçalho estilizado, blocos de código com borda e fundo, títulos coloridos por nível (primary/secondary/tertiary), cabeçalho/rodapé com cores MD3, e página de capa com metadados do processo.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: `reportlab` (já instalado)

**Storage**: N/A — PDF gerado em `data/relatorio_consolidado.pdf`; metadados da capa lidos de `data/resultado_final.json`

**Testing**: Validação visual — abrir PDF gerado e verificar cores MD3, blocos alternados, tabelas estilizadas

**Target Platform**: Multiplataforma (Windows/Linux/macOS) — o PDF deve abrir em qualquer leitor

**Project Type**: Refatoração de estilo em módulo interno (`backend/pdf_generator.py`)

**Performance Goals**: Geração em < 10s para até 50 páginas

**Constraints**:
- ReportLab é a única biblioteca permitida para PDF
- Nenhuma nova dependência externa
- ReportLab não suporta border-radius nativo — usar soluções equivalentes (Tables com cantos ou Preformatted)
- Manter two-pass build (Página X de Y) com `afterPage()` e `deepcopy()` (bug RL5.0.0)
- Manter a assinatura `generate_pdf(etapas_dir, output_path) -> str`
- Pipeline (`backend/pipeline.py`) não precisa ser modificado
- A capa (US2) pode consumir `data/resultado_final.json` se existir; caso não exista, gerar PDF sem capa

**Scale/Scope**: 
- `backend/pdf_generator.py` — adicionar estilos MD3, capa, blocos alternados
- `data/resultado_final.json` — fonte de dados para capa (leitura, não modificação)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: Sem alterações no backend HTTP — apenas estilização do gerador de PDF. ✅ OK
2. **GATE-CREDENCIAIS**: Sem alterações. ✅ OK
3. **GATE-PIPELINE**: Sem alterações no pipeline de 4 etapas. ✅ OK
4. **GATE-CEGUEIRA**: Sem alterações. ✅ OK
5. **GATE-CPC25**: Sem alterações. ✅ OK
6. **GATE-S3-BUCKET**: Sem alterações. ✅ OK
7. **GATE-EXTRACAO**: Sem alterações. ✅ OK
8. **GATE-FRONTEND**: Sem alterações no frontend. ✅ OK
9. **GATE-DEPENDENCIAS**: `reportlab` já está listado como dependência aprovada. Nenhuma nova dependência. ✅ OK
10. **GATE-DEPLOY**: Sem alterações no CI/CD. ✅ OK

**Resultado**: Nenhuma violação.

## Project Structure

### Documentation (this feature)

```text
specs/022-estilizar-pdf-md3/
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
└── pdf_generator.py      # ESTILIZADO — adicionar paleta MD3, blocos, capa, tabelas
```

**Structure Decision**: Apenas o arquivo `backend/pdf_generator.py` será modificado. O pipeline (`backend/pipeline.py`) permanece inalterado.

## Complexity Tracking

Nenhuma violação — sem necessidade de justificativa de complexidade.
