# Implementation Plan: Limpeza Completa do Sistema

**Branch**: `feature/009-limpeza-completa-sistema` | **Date**: 2026-06-28 | **Spec**: `specs/009-limpeza-completa/spec.md`

**Input**: Feature specification from `/specs/009-limpeza-completa/spec.md`

## Summary

Funcionalidade de limpeza completa do sistema ao clicar no botao lixeira (clear-all).
Remove todos os dados da rodagem atual em 6 locais de armazenamento: diretorio local `data/`,
bucket S3 `radiante-final`, memoria do servidor (`ANALYSIS_JOBS`), progresso (`Progress`),
historico de execucao (`_execution_history`) e frontend. A implementacao ja foi realizada
no PR #14 e esta na branch `main`.

## Technical Context

**Language/Version**: Python 3.14 (backend), JavaScript Vanilla (frontend)

**Primary Dependencies**: Nenhuma dependencia nova necessaria. `shutil` (stdlib) para
remocao recursiva de diretorios locais. `boto3` (ja existente) para limpeza S3.

**Storage**:
- Local: `data/` (docs/, markdown_docs/, PDFs, JSONs, .md)
- Nuvem: Bucket S3 `radiante-final` (prefixos docs/, markdown_docs/, results/, runs/)
- Memoria: `ANALYSIS_JOBS` (dict), `Progress._data` (dict), `_execution_history` (list)

**Testing**: pytest (backend, ja existente), Vitest (frontend, ja existente)

**Target Platform**: Linux server (EC2) + Windows/Linux/macOS (desenvolvimento local)

**Project Type**: Web application (backend HTTP + frontend estatico)

**Performance Goals**: Limpeza completa em < 5 segundos para rodagem tipica (ate 10 documentos)

**Constraints**: 
- Nao pode depender de S3 (credenciais SSO podem expirar) — fallback local implementado
- Deve manter a estrutura de diretorios `data/` apos limpeza (docs/, markdown_docs/)
- Deve funcionar mesmo se S3 estiver indisponivel

**Scale/Scope**: Unico usuario, ambiente local/desenvolvimento

## Constitution Check

*GATE: Passed. Nenhuma violacao aos principios da Constituicao.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK** ✅ Backend continua usando `http.server.SimpleHTTPRequestHandler`.
   Nenhum framework web externo foi introduzido. (Principio I)
2. **GATE-CREDENCIAIS** ✅ Nenhuma alteracao no tratamento de credenciais AWS.
   (Principio II)
3. **GATE-PIPELINE** ✅ Nenhuma alteracao no pipeline de 4 etapas. (Principio III)
4. **GATE-CEGUEIRA** ✅ Nenhuma alteracao nas regras de negocio da Etapa 2.
   (Principio III)
5. **GATE-CPC25** ✅ Nenhuma alteracao nas regras de classificacao CPC 25.
   (Principio III)
6. **GATE-S3-BUCKET** ✅ Bucket `radiante-final` mantido com prefixos `docs/`,
   `markdown_docs/`, `results/` e `runs/`. (Principio IV)
7. **GATE-EXTRACAO** ✅ Nenhuma alteracao na extracao de documentos. (Principio IV)
8. **GATE-FRONTEND** ✅ Frontend continua sem bundlers ou frameworks JS.
   (Principio V)
9. **GATE-DEPENDENCIAS** ✅ Nenhuma dependencia nova adicionada. `shutil` e `os` sao
   stdlib do Python. (Stack Tecnologico)
10. **GATE-DEPLOY** ✅ Nenhuma alteracao no CI/CD. (Infraestrutura AWS)

## Project Structure

### Documentation (this feature)

```text
specs/009-limpeza-completa/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md  # Requirement checklist
└── tasks.md             # Phase 2 output (speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app.py              # _handle_clear() expandido (6 locais de limpeza)
├── pipeline.py         # clear_execution_history() adicionado
└── progress.py         # Sem alteracoes (Progress.reset() ja existe)

frontend/
└── js/
    └── ui.js           # clearAllFrontendData() ajustado (reabilita botoes)

specs/
└── 009-limpeza-completa/
    ├── spec.md
    ├── plan.md
    └── (artifacts gerados neste comando)
```

**Structure Decision**: Single project (backend + frontend no mesmo repositorio).
Os arquivos modificados seguem a estrutura modular ja existente.

## Complexity Tracking

Nenhuma violacao a Constituicao encontrada — secao nao aplicavel.
