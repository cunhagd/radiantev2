#!/usr/bin/env python3
"""Gera artefatos da Feature 004: Modo CLI Interativo."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

BASE = "specs/004-modo-cli"
os.makedirs(f"{BASE}/contracts", exist_ok=True)
os.makedirs(f"{BASE}/checklists", exist_ok=True)

spec = """# Feature Specification: Modo CLI Interativo

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
"""

plan = """# Implementation Plan: Modo CLI Interativo

**Branch**: `004-modo-cli` | **Date**: 2026-06-28

## Summary
Adicionar modo CLI completo com argparse, execucao passo a passo,
suporte a documentos locais e salvamento local.

## Technical Context
**Language**: Python 3.11+
**Dependencies**: Nenhuma nova
**Storage**: Local (data/docs/, data/results/) ou S3

## Constitution Check
1. GATE-FRAMEWORK: PASS
2. GATE-DEPENDENCIAS: PASS
3. GATE-PIPELINE: PASS

## Execution Order
1. Refatorar main() em app.py com modo CLI completo
2. Adicionar --docs, --step, --once/--ten, --output
3. Adicionar modo interativo passo a passo
"""

tasks = """---
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
"""

for fname, content in [("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks)]:
    with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written {len(content)} chars to {BASE}/{fname}")

print("F004 artifacts created!")
