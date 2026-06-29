#!/usr/bin/env python3
"""Gera artefatos da Feature 002: Sistema de Fallback Bedrock."""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

BASE = "specs/002-fallback-bedrock"

# ===========================================================================
# SPEC
# ===========================================================================
spec = """# Feature Specification: Sistema de Fallback Bedrock

**Feature Branch**: `002-fallback-bedrock`

**Created**: 2026-06-28

**Status**: Draft

**Input**: Implementar e refinar o sistema de fallback regional do Amazon Bedrock
com 6 combinacoes de modelo/regiao, retry inteligente, metricas de failover e
testes de rotacao.

## User Scenarios & Testing

### User Story 1 — Fallback Automatico Transparente (Priority: P1)

Como operador do sistema, quero que o fallback entre modelos/regioes ocorra
automaticamente sem intervencao manual, para que a analise nunca seja
interrompida por throttling ou falhas regionais.

**Why this priority**: O sistema atual depende de um unico modelo/regiao.
Se houver throttling, toda a analise falha.

**Acceptance Scenarios**:
1. Given o cluster primario (Opus 4.6 us-west-2) esta em throttling,
   When o pipeline inicia, Then o fallback rotaciona para Opus 4.6 us-east-1.
2. Given todas as 3 regioes Opus falham, When o pipeline tenta,
   Then o fallback rotaciona para Sonnet 4.6 us-west-2.
3. Given todas as 6 combinacoes falham, When o pipeline tenta,
   Then uma excecao clara e lancada indicando exaustao de fallback.

### User Story 2 — Metricas e Monitoramento de Fallback (Priority: P2)

Como desenvolvedor, quero metricas detalhadas de cada tentativa de fallback
(modelo, regiao, tempo, erro) para diagnosticar problemas de disponibilidade.

**Why this priority**: Sem metricas, nao e possivel saber qual combinacao
esta falhando e por que.

**Acceptance Scenarios**:
1. Given uma execucao com fallback, When o pipeline termina,
   Then o relatorio inclui quantas tentativas foram feitas por combinacao.
2. Given uma falha de throttling, When ocorre o fallback,
   Then o erro e registrado com timestamp e combinacao tentada.

### User Story 3 — Custo Variavel por Modelo (Priority: P3)

Como gestor de custos, quero que o sistema escolha automaticamente o modelo
mais barato disponivel quando ambos estiverem disponiveis.

**Why this priority**: Opus 4.6 custa 5x mais que Sonnet 4.6. Usar Sonnet
quando possivel reduz custos sem perder qualidade.

**Acceptance Scenarios**:
1. Given Sonnet 4.6 e Opus 4.6 estao ambos disponiveis,
   When nao ha requisito de modelo especifico,
   Then o sistema prefere Sonnet 4.6 (mais barato).
2. Given o modelo primario esta especificado na config,
   When o modelo esta disponivel, Then usa o configurado.

## Requirements

- FR-001: Sistema DEVE implementar 6 combinacoes de fallback (Opus 4.6 + Sonnet 4.6 em us-west-2, us-east-1, eu-central-1).
- FR-002: Cada tentativa DEVE ter retry com backoff exponencial (2s, 4s, 8s) antes de rotacionar.
- FR-003: O sistema DEVE registrar metricas de cada tentativa (modelo, regiao, status, tempo, erro).
- FR-004: Um endpoint GET /api/fallback-status DEVE expor o estado atual do fallback.
- FR-005: A config DEVE permitir especificar modelo primario e estrategia de fallback.
- FR-006: O cache de prompt DEVE ser mantido mesmo durante fallback entre regioes.

## Success Criteria

- SC-001: Fallback completo entre 6 combinacoes testado com sucesso.
- SC-002: Tempo total de failover < 30 segundos (incluindo retries).
- SC-003: Metricas de fallback disponiveis via API.
- SC-004: Zero intervencao manual necessaria durante fallback.

## Assumptions

- As 3 regioes (us-west-2, us-east-1, eu-central-1) tem modelos Claude disponiveis.
- O bucket S3 radiante-final e acessivel de todas as regioes.
- O custo do cache de prompt e mantido mesmo em fallback entre regioes.
"""

# ===========================================================================
# PLAN
# ===========================================================================
plan = """# Implementation Plan: Sistema de Fallback Bedrock

**Branch**: `002-fallback-bedrock` | **Date**: 2026-06-28 | **Spec**: specs/002-fallback-bedrock/spec.md

## Summary

Refinar o sistema de fallback regional do bedrock_client.py, adicionando
metricas de failover, endpoint de status, logs estruturados e testes de
rotacao entre as 6 combinacoes.

## Technical Context

**Language/Version**: Python 3.11+
**Dependencies**: boto3, botocore
**Storage**: N/A (estado em memoria)
**Target**: Linux EC2 + Windows

## Constitution Check

1. GATE-FRAMEWORK: PASS - sem frameworks web
2. GATE-CREDENCIAIS: PASS - usa config centralizada
3. GATE-PIPELINE: PASS - pipeline inalterado
4. GATE-DEPENDENCIAS: PASS - nenhuma nova dependencia

## Project Structure

```
backend/
+-- bedrock_client.py     # Refinado com fallback + metricas
+-- app.py                # Novo endpoint /api/fallback-status
specs/002-fallback-bedrock/
+-- spec.md / plan.md / research.md / contracts/
+-- tasks.md
```

## Execution Order

1. Refatorar bedrock_client.py (fallback metrics, logging)
2. Adicionar endpoint /api/fallback-status no app.py
3. Criar test_fallback.py (teste de rotacao)
"""

# ===========================================================================
# RESEARCH
# ===========================================================================
research = """# Research: Sistema de Fallback Bedrock

## Analise do Codigo Atual

O bedrock_client.py ja implementa:
- 6 combinacoes na FALLBACK_STRATEGY
- Retry com backoff (2s, 4s, 8s)
- Cache de prompt via cachePoint

Melhorias necessarias:
1. Metricas de fallback (quantas tentativas, qual combinacao venceu)
2. Endpoint de status para debug
3. Logging estruturado de cada tentativa
4. Preferencia por Sonnet (mais barato) quando disponivel

## Estrategia de Custo

Opus 4.6: $15/MTok input, $75/MTok output (5x mais caro que Sonnet)
Sonnet 4.6: $3/MTok input, $15/MTok output

Regra: Sonnet e o padrao. Fallback para Opus apenas se Sonnet
indisponivel em todas as 3 regioes.
"""

# ===========================================================================
# CONTRACTS
# ===========================================================================
contracts = {
    "bedrock_fallback.md": """# Contract: Bedrock Fallback

## Public Interface

```python
class FallbackAttempt:
    model_name: str
    model_id: str
    region: str
    status: str  # success, throttled, error
    error: str | None
    duration_ms: int
    timestamp: str

class FallbackMetrics:
    total_attempts: int
    successful_attempt: FallbackAttempt | None
    all_attempts: list[FallbackAttempt]
    total_duration_ms: int
    cache_tokens_used: int

def get_fallback_status() -> dict:
    '''Retorna estado atual do fallback (ultimas tentativas).'''

def run_llm_stage_streaming(...) -> tuple[str, PipelineMetrics]:
    '''Executa LLM com fallback automatico e metricas.'''
```
""",
}

# ===========================================================================
# TASKS
# ===========================================================================
tasks = """---
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
"""

artifacts = {
    "spec.md": spec,
    "plan.md": plan,
    "research.md": research,
    "tasks.md": tasks,
}

for fname, content in artifacts.items():
    path = os.path.join(BASE, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written {len(content)} chars to {path}")

for fname, content in contracts.items():
    path = os.path.join(BASE, "contracts", fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written {len(content)} chars to {path}")

print("\nFeature 002 artifacts created successfully!")
