---
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
