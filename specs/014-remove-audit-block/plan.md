# Implementation Plan: Remocao do Bloco "Ver Relatorio de Auditoria"

**Branch**: `014-remove-audit-block` | **Date**: 2026-06-29 | **Spec**: `specs/014-remove-audit-block/spec.md`

**Input**: Feature specification from `specs/014-remove-audit-block/spec.md`

## Summary

Remover o bloco "Ver Relatorio de Auditoria" da interface do frontend, eliminando o toggle de auditoria, o endpoint `/api/audit-log` e toda logica associada. O unico meio de acesso ao relatorio passa a ser o botao "Baixar Relatorio PDF" ja existente.

## Technical Context

**Language/Version**: Python 3.14, JavaScript Vanilla (ES5/6)

**Primary Dependencies**: Nenhuma nova — apenas manipulacao DOM nativa

**Storage**: N/A — remocao de funcionalidade, sem novo armazenamento

**Testing**: Vitest + Happy-DOM (frontend)

**Target Platform**: Browser (Chrome, Firefox, Edge)

**Performance Goals**: N/A — remocao de codigo tende a melhorar performance

**Constraints**:
- Nao adicionar novas dependencias (Constitution Stack)
- Frontend sem bundlers/frameworks (Constitution V)
- Remover tambem o endpoint `/api/audit-log` do backend para nao manter codigo morto

## Constitution Check

*GATE: Passed. A remocao nao viola nenhum principio: mexe apenas no frontend (HTML/CSS/JS) e endpoint de backend, nao adiciona dependencias, nao altera pipeline, nao mexe em credenciais nem S3.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK** (Principio I): ✅ Nao mexe no servidor HTTP.
2. **GATE-CREDENCIAIS** (Principio II): ✅ Nao mexe em credenciais AWS.
3. **GATE-PIPELINE** (Principio III): ✅ Nao altera o pipeline de 4 etapas.
4. **GATE-CEGUEIRA** (Principio III — Regras 1, 14): ✅ Nao mexe em regras de negocio.
5. **GATE-CPC25** (Principio III): ✅ Nao mexe em classificacao de risco.
6. **GATE-S3-BUCKET** (Principio IV): ✅ Nao mexe em S3.
7. **GATE-EXTRACAO** (Principio IV): ✅ Nao mexe em extracao.
8. **GATE-FRONTEND** (Principio V): ✅ Frontend continua sem frameworks/bundlers.
9. **GATE-DEPENDENCIAS** (Stack): ✅ Nenhuma nova dependencia.
10. **GATE-DEPLOY** (Infraestrutura): ✅ Nao mexe em deploy.

## Project Structure

### Source Code (repository root)

```text
frontend/
├── index.html          # Remover bloco .audit-section (HTML) + event listener audit-toggle
├── js/api.js           # Remover funcao API.loadAuditLog
├── js/loading.js       # Remover chamada a API.loadAuditLog apos analise
├── js/ui.js            # Remover funcao toggleAuditLog, ref. auditContent em clearAll
├── js/state.js         # Remover DOM.auditContent
└── css/                # Remover estilos .audit-section, .audit-toggle, .audit-body

backend/
└── app.py              # Remover rota /api/audit-log do do_GET
```

**Structure Decision**: Single project — frontend e backend no mesmo repo, com a feature afetando ambos os lados.

### Documentation (this feature)

```text
specs/014-remove-audit-block/
├── plan.md              # This file
├── research.md          # (N/A — feature simples, sem unknowns)
├── data-model.md        # (N/A — sem alteracao de dados)
├── contracts/           # (N/A — sem novos contratos)
├── quickstart.md        # Cenario de validacao
└── tasks.md             # (/speckit-tasks output)
```

## Complexity Tracking

Nenhuma violacao da Constitution. Feature de baixissima complexidade (remocao de codigo).

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Nenhuma | — | — |
