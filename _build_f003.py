#!/usr/bin/env python3
"""Gera artefatos da Feature 003: Dashboard de Metricas e Cache de Tokens."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

BASE = "specs/003-dashboard-metricas"
os.makedirs(f"{BASE}/contracts", exist_ok=True)
os.makedirs(f"{BASE}/checklists", exist_ok=True)

spec = """# Feature Specification: Dashboard de Metricas e Cache de Tokens

**Feature Branch**: `003-dashboard-metricas`
**Created**: 2026-06-28
**Status**: Draft

**Input**: Implementar endpoint de metricas de uso (tokens, custos, cache hits)
e sistema de cache de prompt inteligente para reduzir custos em repeticoes.

## User Stories

### US1 — Endpoint de Metricas (P1)
Como operador, quero GET /api/metrics retornando custos, tokens e cache hits
da ultima execucao.

### US2 — Cache de Prompt Inteligente (P2)
Como sistema, quero reutilizar cache de prompt entre rodadas do modo 10x
para reduzir custos de entrada repetida.

### US3 — Historico de Execucoes (P3)
Como gestor, quero visualizar historico das ultimas N execucoes com metricas.

## Requirements
- FR-001: GET /api/metrics retorna PipelineMetrics da ultima execucao
- FR-002: GET /api/metrics/history retorna historico das ultimas 50 execucoes
- FR-003: Cache de prompt reutilizado entre rodadas do modo 10x
- FR-004: Metricas incluem custo total, tokens in/out/cache, tempo de execucao

## Success Criteria
- SC-001: Endpoint /api/metrics retorna dados em < 100ms
- SC-002: Historico mantem ate 50 execucoes
- SC-003: Cache de prompt reduz tokens de entrada em > 80% no modo 10x
"""

plan = """# Implementation Plan: Dashboard de Metricas e Cache

**Branch**: `003-dashboard-metricas` | **Date**: 2026-06-28

## Summary
Adicionar endpoint de metricas, historico de execucoes e cache de prompt
compartilhado entre rodadas 10x.

## Technical Context
**Language**: Python 3.11+
**Dependencies**: Nenhuma nova
**Storage**: Memoria (dict para historico, cache de prompt no Bedrock)

## Constitution Check
1. GATE-FRAMEWORK: PASS
2. GATE-DEPENDENCIAS: PASS
3. GATE-FRONTEND: PASS (frontend nao modificado)

## Execution Order
1. Adicionar historico de execucoes no pipeline.py
2. Criar endpoint /api/metrics e /api/metrics/history no app.py
3. Implementar cache compartilhado para modo 10x
4. Atualizar frontend para exibir metricas
"""

tasks = """---
description: "Task list for dashboard de metricas e cache"
---
# Tasks: Dashboard de Metricas e Cache de Tokens

## Phase 1: Setup
- [ ] T001 Criar specs/003-dashboard-metricas/

## Phase 2: Foundational
- [ ] T002 Adicionar ExecutionHistory em pipeline.py (historico em memoria)
  - Lista global com ate 50 entradas
  - Cada entrada: timestamp, modo (once/ten), PipelineMetrics, resumo JSON

## Phase 3: US1 — Endpoint de Metricas (P1)
- [ ] T003 [US1] Adicionar GET /api/metrics no app.py
  - Retorna PipelineMetrics da ultima execucao
- [ ] T004 [US1] Adicionar GET /api/metrics/history no app.py
  - Retorna historico paginado (ultimas 50)

## Phase 4: US2 — Cache de Prompt (P2)
- [ ] T005 [US2] Otimizar cache de prompt no bedrock_client.py
  - Compartilhar system prompt entre rodadas 10x
  - Usar cachePoint com prefixo comum para maximizar hits

## Phase 5: US3 — Historico (P3)
- [ ] T006 [US3] Integrar ExecutionHistory no run_once e run_ten_times
- [ ] T007 [US3] Testar historico com multiplas execucoes

## Phase 6: Validacao
- [ ] T008 Verificar endpoints /api/metrics e /api/metrics/history
- [ ] T009 Verificar reducao de tokens com cache compartilhado
"""

for fname, content in [("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks)]:
    with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written {len(content)} chars to {BASE}/{fname}")

print("F003 artifacts created!")
