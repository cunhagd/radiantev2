# Quickstart — Bloco de Metricas de Uso

## Pre-requisitos

- Servidor rodando: `python dev.py --server` ou `python -m backend.app --mode web --port 8001`
- `.env` configurado com `GROK_PRICE_INPUT`, `GROK_PRICE_OUTPUT`, `GROK_PRICE_CACHE_READ`

## Cenarios de Validacao

### Cenario 1: Modo 1x exibe metricas corretamente

1. Faca upload de um documento juridico
2. Clique em "1x"
3. Aguarde a analise completar
4. **Esperado**: Bloco "Metricas de Uso" aparece abaixo de "Provisao de Cifras" com:
   - Tokens de entrada (prompt) > 0
   - Tokens em cache (cache) >= 0
   - Tokens de saida (completion) > 0
   - Custo total > $0.00
   - Nenhuma tabela de rodadas (apenas totais consolidados)

### Cenario 2: Modo 10x exibe metricas + tabela de rodadas

1. Faca upload de um documento juridico
2. Clique em "10x"
3. Aguarde a analise completar
4. **Esperado**: Bloco "Metricas de Uso" aparece com:
   - Tabela com 10 linhas (uma por rodada)
   - Cada linha: Rodada N, entrada, cache, saida, custo
   - Totais consolidados no cabecalho do card

### Cenario 3: Metricas no JSON principal (sem chamada extra)

1. Apos analise, inspecione a resposta do endpoint `/api/last-result`
2. **Esperado**: O JSON contem um objeto `metrics` no mesmo nivel que `cifras` e `numero_processo`

### Cenario 4: Clear oculta metricas

1. Apos analise, clique no botao de lixeira e confirme
2. **Esperado**: Bloco "Metricas de Uso" desaparece

## Contrato de Dados

Ver `data-model.md` para a estrutura completa do JSON de metricas.
