---
description: "Task list for modo cli interativo"
---
# Tasks: Modo CLI Interativo

## Phase 1: Setup
- [ ] T001 Criar specs/004-modo-cli/

## Phase 2: Foundational
- [ ] T002 Refatorar main() do app.py com argumentos CLI completos
  - --mode cli: modo terminal
  - --docs PATH: diretorio com documentos
  - --step N: executar etapa especifica (1-4)
  - --once / --ten: modo de execucao
  - --output PATH: salvar resultados localmente

## Phase 3: US1 — Pipeline via CLI (P1)
- [ ] T003 [US1] Implementar execucao completa no modo CLI
  - Carregar documentos de data/docs/
  - Executar pipeline completo
  - Salvar resultados em data/results/

## Phase 4: US2 — Modo Interativo (P2)
- [ ] T004 [US2] Implementar --step para execucao por etapa
  - Etapa 1: so metadados
  - Etapa 2: cifras (requer Etapa 1)
  - Modo interativo com confirmacao entre etapas

## Phase 5: Validacao
- [ ] T005 Testar python backend/app.py --mode cli --once
- [ ] T006 Testar python backend/app.py --mode cli --step 1
