# Implementation Plan: Renderizar Markdown Inline no PDF

**Branch**: `023-renderizar-markdown-inline` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/023-renderizar-markdown-inline/spec.md`

## Summary

Adicionar um parser de markdown inline puro (regex Python) no `backend/pdf_generator.py` que converte marcadores `**negrito**`, `*itálico*`, `` `código inline` ``, e `> blockquote` para XML compatível com ReportLab (`<b>`, `<i>`, `<font face="Courier">`). A formatação aninhada é preservada. Blocos de código e tabelas não são afetados.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `reportlab` (já instalado), `re` (stdlib Python)

**Storage**: N/A — apenas transformação de texto em memória

**Testing**: Validação visual do PDF gerado + inspeção do output XML do `_parse_inline()`

**Target Platform**: Linux server (EC2 Ubuntu) / Windows (desenvolvimento)

**Project Type**: Web service backend (utilitário de geração de PDF)

**Performance Goals**: PDF gerado em < 10s para até 50 páginas

**Constraints**: 
- ReportLab não suporta border-radius
- ReportLab 5.0.0 pode mutar flowables — usar `deepcopy` no two-pass build (já implementado)
- Blocos de código >20 linhas devem usar Paragraph simples, não Table (evitar "Flowable too large")
- A função `_parse_inline` deve ser pura (sem estado, sem efeitos colaterais)

**Scale/Scope**: 1 PDF por execução do pipeline, ~4-8 páginas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

| Gate | Status | Justification |
|------|--------|---------------|
| **GATE-FRAMEWORK** (Princípio I) | ✅ PASS | Nenhuma alteração no backend HTTP. Apenas `pdf_generator.py` é modificado. |
| **GATE-CREDENCIAIS** (Princípio II) | ✅ PASS | Nenhuma alteração em credenciais AWS. |
| **GATE-PIPELINE** (Princípio III) | ✅ PASS | Pipeline de 4 etapas inalterado. |
| **GATE-CEGUEIRA** (Princípio III) | ✅ PASS | Pipeline inalterado. |
| **GATE-CPC25** (Princípio III) | ✅ PASS | Pipeline inalterado. |
| **GATE-S3-BUCKET** (Princípio IV) | ✅ PASS | Nenhuma alteração no S3. |
| **GATE-EXTRACAO** (Princípio IV) | ✅ PASS | Nenhuma alteração na extração. |
| **GATE-FRONTEND** (Princípio V) | ✅ PASS | Nenhuma alteração no frontend. |
| **GATE-DEPENDENCIAS** (Stack) | ✅ PASS | Nenhuma nova dependência. Apenas `re` (stdlib). |
| **GATE-DEPLOY** (Infraestrutura) | ✅ PASS | Nenhuma alteração no deploy. |

**Resultado**: ✅ Todos os 10 gates passam. Nenhuma violação da Constituição.

## Project Structure

### Documentation (this feature)

```text
specs/023-renderizar-markdown-inline/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 - pesquisa técnica
├── data-model.md        # Phase 1 - modelo de dados
├── quickstart.md        # Phase 1 - guia de validação
├── contracts/
│   └── parse_inline.md  # Contrato da função _parse_inline
├── checklists/
│   └── requirements.md  # Checklist de qualidade da spec
└── tasks.md             # (gerado pelo /speckit-tasks)
```

### Source Code

```text
backend/
└── pdf_generator.py     # ÚNICO arquivo modificado
```

**Structure Decision**: Modificação localizada em um único arquivo (`backend/pdf_generator.py`). Adicionar função `_parse_inline()` e ajustar o parser de linhas para aplicar formatação inline em parágrafos, listas e blockquotes.

## Complexity Tracking

> Nenhuma violação da Constitution. Seção não aplicável.
