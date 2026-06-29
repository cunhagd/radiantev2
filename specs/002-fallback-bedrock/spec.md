# Feature Specification: Sistema de Fallback Bedrock

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
