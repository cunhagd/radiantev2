# Research: Sistema de Fallback Bedrock

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
