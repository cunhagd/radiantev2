# Implementation Plan: Check Amplify Status

**Branch**: `020-check-amplify-status` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/020-check-amplify-status/spec.md`

## User Stories

### User Story 1 — Diagnóstico do status do Amplify via CLI (Priority: P1) 🎯 MVP

O desenvolvedor/operador pode executar um comando via terminal que verifica se o AWS Amplify está ativo na conta configurada, listando os aplicativos Amplify existentes, seus ambientes e o status de cada um.

**Independent Test**: Ao executar `python scripts/check_amplify.py`, o sistema retorna uma saída formatada no terminal com o status do Amplify (ativo/inativo), lista de aplicativos e ambientes, ou uma mensagem clara de erro/exceção.

## Summary

Criar um script/ferramenta CLI em Python (User Story 1) que verifica o status do AWS Amplify na conta AWS configurada, listando aplicativos Amplify, ambientes (branches), status de deploy e URLs. Utiliza o SDK boto3 e as credenciais AWS do `.env`.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: `boto3` (já instalado)

**Storage**: N/A — ferramenta de diagnóstico, sem armazenamento persistente

**Testing**: N/A — script de diagnóstico único, sem testes automatizados previstos

**Target Platform**: Linux (EC2), Windows (desenvolvimento local) e macOS — qualquer ambiente onde o projeto rode

**Project Type**: Script CLI (ferramenta auxiliar de diagnóstico)

**Performance Goals**: N/A — execução única para diagnóstico, sem requisito de performance

**Constraints**:
- Usar `boto3` já instalado — sem novas dependências
- Credenciais AWS do `.env` (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION)
- Deve funcionar independente do servidor HTTP do backend
- Saída em texto simples para terminal (stdout)
- Tratar erros de permissão, timeout, região incorreta

**Scale/Scope**: 
- `scripts/check_amplify.py` — novo script CLI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: Script CLI independente — não afeta o backend HTTP. ✅ OK
2. **GATE-CREDENCIAIS**: Reutiliza o mesmo mecanismo de leitura do `.env` via `python-dotenv`. As credenciais serão passadas explicitamente ao cliente boto3, seguindo o Princípio II. ✅ OK
3. **GATE-PIPELINE**: Sem alterações no pipeline de 4 etapas. ✅ OK
4. **GATE-CEGUEIRA**: Sem alterações. ✅ OK
5. **GATE-CPC25**: Sem alterações. ✅ OK
6. **GATE-S3-BUCKET**: Sem alterações na estrutura do bucket. ✅ OK
7. **GATE-EXTRACAO**: Sem alterações. ✅ OK
8. **GATE-FRONTEND**: Sem alterações no frontend. ✅ OK
9. **GATE-DEPENDENCIAS**: `boto3` já está listado como dependência aprovada. Nenhuma nova dependência. ✅ OK
10. **GATE-DEPLOY**: Sem alterações no CI/CD. ✅ OK

**Resultado**: Nenhuma violação. Ferramenta CLI auxiliar de diagnóstico.

## Project Structure

### Documentation (this feature)

```text
specs/020-check-amplify-status/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
scripts/
└── check_amplify.py      # NOVO — script CLI para diagnosticar Amplify
```

**Structure Decision**: Criar diretório `scripts/` na raiz do projeto para ferramentas auxiliares de diagnóstico e operação, mantendo-as separadas do backend e frontend.

## Complexity Tracking

Nenhuma violação — sem necessidade de justificativa de complexidade.
