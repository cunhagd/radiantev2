# Feature Specification: Modo CLI Interativo

**Feature Branch**: `004-modo-cli`
**Created**: 2026-06-28
**Status**: Draft

**Input**: Implementar modo de linha de comando interativo para executar
o pipeline completo diretamente no terminal, sem servidor web.

## User Stories

### US1 — Pipeline via CLI (P1)
Como operador, quero executar o pipeline completo (upload + extracao +
4 etapas) via terminal com um unico comando.

### US2 — Modo Interativo Passo a Passo (P2)
Como desenvolvedor, quero executar cada etapa individualmente via CLI
para debug e validacao de resultados intermediarios.

## Requirements
- FR-001: python backend/app.py --mode cli executa pipeline completo no terminal
- FR-002: --docs PATH permite especificar diretorio com documentos locais
- FR-003: --mode cli --step 1 executa apenas Etapa 1
- FR-004: --mode cli --step 4 executa apenas Etapa 4 (consolidacao)
- FR-005: --once executa 1x, --ten executa 10x no modo CLI
- FR-006: --output PATH salva resultados em diretorio local (nao S3)

## Success Criteria
- SC-001: Modo CLI funcional sem servidor web
- SC-002: Pipeline completo executavel com unico comando
- SC-003: Cada etapa executavel individualmente
