---
description: "Task list for sistema de fallback bedrock"
---

# Tasks: Sistema de Fallback Bedrock

## Phase 1: Setup
- [ ] T001 Criar specs/002-fallback-bedrock/contracts/ (ja criado)

## Phase 2: Foundational
- [ ] T002 Refatorar backend/bedrock_client.py com FallbackMetrics e FallbackAttempt
  - Adicionar dataclass FallbackAttempt e FallbackMetrics
  - Registrar cada tentativa com timestamp, duracao e erro
  - Preferir Sonnet como primario para reducao de custos
  - Exportar funcao get_fallback_status()

## Phase 3: US1 — Fallback Automatico (P1)
- [ ] T003 [US1] Atualizar run_llm_stage_streaming para usar FallbackMetrics
  - Coletar metricas de cada tentativa
  - Propagar metricas para o PipelineMetrics
- [ ] T004 [US1] Testar rotacao entre 6 combinacoes com ThrottlingException simulada

## Phase 4: US2 — Metricas (P2)
- [ ] T005 [US2] Adicionar endpoint GET /api/fallback-status no app.py
  - Retornar ultimas tentativas, status atual, combinacoes disponiveis
- [ ] T006 [US2] Criar backend/tests/test_fallback.py com simulacao de falhas

## Phase 5: US3 — Custo (P3)
- [ ] T007 [US3] Implementar logica de custo: preferir Sonnet como primario
  - Config permitir override para Opus quando necessario
  - Logar economia de custo quando fallback usa modelo mais barato

## Phase 6: Validacao
- [ ] T008 Testar fallback completo: 6 combinacoes + retries
- [ ] T009 Validar metricas via GET /api/fallback-status
- [ ] T010 Verificar cache de prompt mantido durante fallback
