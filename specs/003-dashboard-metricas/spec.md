# Feature Specification: Dashboard de Metricas e Cache de Tokens

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
