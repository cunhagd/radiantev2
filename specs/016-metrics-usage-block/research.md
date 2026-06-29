# Research: Bloco de Metricas de Uso

## Phase 0 — Unresolved Items

Nenhum item NEEDS CLARIFICATION permaneceu apos a especificacao. Todas as decisoes foram
tomadas com base no codigo existente e nas praticas ja estabelecidas do projeto.

## Technical Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Incluir metrics no JSON principal | FR-007 exige eliminacao de chamada extra. O JSON de resultado ja inclui `data` (parsed_json), basta adicionar `metrics` e `runs` no mesmo nivel. | Manter `/api/metrics` separado — rejeitado por exigir requisicao extra e aumentar latencia |
| Reaproveitar card #observability-card existente | O HTML e JS do card ja existem desde implementacoes anteriores. Apenas reposicionar no DOM e garantir que renderize a partir dos dados do JSON principal. | Criar novo card do zero — maior risco de quebra e duplicacao de codigo |
| Adicionar `runs` individuais no metrics do modo 10x | Para a tabela detalhada (FR-004), as metricas de cada etapa 3 devem ser agregadas e retornadas como array no JSON | Calcular no frontend a partir de dados brutos — maior complexidade no frontend e mais chamadas |
| PipelineMetrics permanece como dataclass Python | Ja implementado e testado. Os precos sao calculados com `calculate_costs()` que usa `config.grok_price_*`. | Nenhuma alternativa necessaria |

## Code Points of Interest

- **`backend/pipeline.py`**: `run_once()` retorna dict com `metrics`. `run_ten_times()` retorna dict com `metrics` (consolidado). Ambos precisam incluir `metrics` no `data` retornado ao `app.py`.
- **`backend/app.py`**: O handler `/api/run` ja insere `parsed_data` em `ANALYSIS_JOBS["last_result"]`. Precisamos garantir que `metrics` seja incluido nesse dict.
- **`frontend/js/metrics.js`**: `Metrics.renderMetrics()` ja renderiza a partir de `data.metrics`. Precisa ser atualizado para ler do JSON principal (`result.metrics` em vez de chamar `/api/metrics`).
- **`frontend/index.html`**: O `#observability-card` esta atualmente APOS o fechamento da div `.container` (linha 153), o que o posiciona fora do fluxo correto. Precisa ser movido para DENTRO da `.container`, abaixo do card de cifras.
