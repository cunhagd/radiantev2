# Feature Specification: Bloco de Metricas de Uso

**Feature Branch**: `016-metrics-usage-block`

**Created**: 2026-06-29

**Status**: Draft

**Input**: Precisamos criar o bloco de métricas de tokens/custos (input, cache, output) e custo total da rodagem (1x e 10x). O bloco deve seguir o mesmo padrão de identidade visual dos demais blocos e deve vir abaixo do bloco de Provisão de Cifras. Para os valores serem calculados corretamente, devemos utilizar as métricas de GROK_PRICE... declaradas no .env e capturar exatamente a quantidade de tokens de cada parâmetro (input, cache, output) durante cada etapa da análise para ao final termos a soma total do consolidado para exibirmos as métricas no bloco.

## User Scenarios & Testing

### User Story 1 - Visualizar métricas detalhadas de uso da IA (Priority: P1)

O usuário, após executar uma análise (modo 1x ou 10x), deseja visualizar um bloco com métricas detalhadas de uso dos modelos de IA: tokens de entrada, tokens em cache, tokens de saída, custo parcial de cada categoria e custo total em USD. As métricas devem ser calculadas automaticamente com base nos preços declarados no `.env` e nos tokens coletados em cada etapa do pipeline.

**Why this priority**: A visualização de custos é essencial para que o usuário tenha transparência sobre o consumo dos modelos de IA e possa monitorar o gasto por análise.

**Independent Test**: Ao finalizar uma análise 1x, o sistema exibe o bloco "Métricas de Uso" com tokens de entrada, cache, saída e custo total preenchidos. No modo 10x, o bloco exibe adicionalmente o detalhamento por rodada.

**Acceptance Scenarios**:

1. **Given** que o bloco de métricas existe abaixo do bloco de Provisão de Cifras, **When** uma análise é concluída, **Then** o bloco fica visível com os valores preenchidos.
2. **Given** que uma análise 1x foi concluída, **When** o bloco de métricas é renderizado, **Then** ele exibe tokens de entrada, cache, saída e custo total (input + output + cache).
3. **Given** que uma análise 10x foi concluída, **When** o bloco de métricas é renderizado, **Then** ele exibe os totais gerais e uma tabela com o detalhamento por rodada (entrada, cache, saída, custo).
4. **Given** que os preços no `.env` foram alterados (GROK_PRICE_INPUT, GROK_PRICE_OUTPUT, GROK_PRICE_CACHE_READ), **When** uma nova análise é executada, **Then** os custos refletem os novos preços sem necessidade de alteração de código.
5. **Given** que não há dados de análise, **When** a página carrega, **Then** o bloco de métricas permanece oculto.

---

### Edge Cases

- **Modo 1x**: O bloco exibe apenas os totais consolidados das 4 etapas, sem tabela de rodadas.
- **Modo 10x**: O bloco exibe os totais consolidados (etapas 1+2+4 + todas as 10 execuções da etapa 3) e uma tabela com as métricas individuais de cada uma das 10 rodadas da etapa 3.
- **Preços zerados**: Se GROK_PRICE_* estiverem zerados no `.env`, o custo total será $0.00, mas os tokens continuam sendo exibidos normalmente.
- **Dados corrompidos**: Se as métricas não estiverem disponíveis no JSON de resultado, o bloco permanece oculto.
- **Clear**: Ao limpar os dados, o bloco de métricas é ocultado.

## Requirements

### Functional Requirements

- **FR-001**: O sistema DEVE exibir um bloco "Métricas de Uso" abaixo do bloco "Provisão de Cifras", seguindo o mesmo padrão visual (cards, cores, tipografia).
- **FR-002**: O sistema DEVE exibir os tokens de entrada (prompt), tokens em cache, tokens de saída (completion) e custo total da análise em USD.
- **FR-003**: O sistema DEVE calcular os custos usando os preços declarados em `GROK_PRICE_INPUT`, `GROK_PRICE_OUTPUT` e `GROK_PRICE_CACHE_READ` do `.env`.
- **FR-004**: No modo 10x, o sistema DEVE exibir adicionalmente uma tabela detalhada com as métricas de cada rodada da etapa 3 (entrada, cache, saída, custo).
- **FR-005**: O bloco de métricas DEVE ficar oculto quando não há dados de análise disponíveis.
- **FR-006**: O sistema DEVE coletar e somar os tokens de todas as 4 etapas (mais todas as repetições da etapa 3 no modo 10x) para gerar o consolidado.
- **FR-007**: O JSON de resultado retornado ao frontend DEVE incluir as métricas consolidadas no mesmo payload, eliminando a necessidade de uma chamada separada a `/api/metrics`.

### Key Entities

- **PipelineMetrics**: Estrutura de dados que carrega `prompt_tokens`, `completion_tokens`, `cache_tokens`, `cost_input`, `cost_output`, `cost_cache`, `cost_total`.
- **Preços Grok**: `GROK_PRICE_INPUT`, `GROK_PRICE_OUTPUT`, `GROK_PRICE_CACHE_READ` — valores em USD por milhão de tokens, declarados no `.env`.
- **Bloco de Métricas**: Card visual no frontend, logo abaixo do bloco de Provisão de Cifras.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Ao completar uma análise 1x, o bloco "Métricas de Uso" aparece com tokens de entrada, cache, saída e custo total preenchidos, e sua posição é imediatamente abaixo do bloco de Provisão de Cifras.
- **SC-002**: Ao completar uma análise 10x, o bloco exibe os totais consolidados e uma tabela com métricas individuais das 10 rodadas.
- **SC-003**: Os custos calculados correspondem aos preços definidos no `.env` (ex: 100k tokens de input com GROK_PRICE_INPUT=1.25 → custo = 100000/1000000 * 1.25 = $0.125).
- **SC-004**: Nenhuma requisição extra é necessária para carregar as métricas — os dados vêm no mesmo JSON do resultado.
- **SC-005**: Ao limpar dados ou recarregar sem análise, o bloco permanece oculto.

## Assumptions

- O bloco de métricas já existe no HTML (`#observability-card`) e no JavaScript (`Metrics.renderMetrics()`), mas atualmente carrega dados de `/api/metrics` separadamente. A feature deve integrar as métricas no JSON principal do resultado.
- O cálculo `(tokens / 1_000_000) * preco` já está implementado em `backend/metrics.py` e é correto.
- As métricas já são coletadas em cada etapa do pipeline e agregadas via `merge_metrics()`.
- O design visual segue o padrão Material Design 3 já estabelecido nos demais cards.
