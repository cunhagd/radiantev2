# Data Model: Metricas de Uso

## PipelineMetrics (dataclass Python — backend/metrics.py)

Representa as metricas de uma execucao unica (4 etapas) ou consolidada (10x).

```python
@dataclass
class PipelineMetrics:
    prompt_tokens: int       # Total de tokens de entrada
    completion_tokens: int    # Total de tokens de saida
    cache_tokens: int         # Total de tokens de cache
    cost_input: float         # Custo dos tokens de entrada (USD)
    cost_output: float        # Custo dos tokens de saida (USD)
    cost_cache: float         # Custo dos tokens de cache (USD)
    cost_total: float         # Custo total (input + output + cache) (USD)
```

## JSON Payload — Resultado da Analise (retornado ao frontend)

Estrutura completa do JSON retornado por `/api/last-result` e `/api/run`:

```json
{
  "numero_processo": "string",
  "autor": "string",
  "adv_reclamante": "string",
  "localidade": "string",
  "juizo": "string",
  "reclamada": "string",
  "inicio_processo": "string",
  "valor_causa": "string",
  "cifras": [...],
  "valor_total_estimado": "string",
  "pdf_filename": "string",

  "metrics": {
    "prompt_tokens": 12345,
    "completion_tokens": 6789,
    "cache_tokens": 500,
    "cost_input": 0.015431,
    "cost_output": 0.016973,
    "cost_cache": 0.000100,
    "cost_total": 0.032504,
    "runs": [
      {
        "run": 1,
        "prompt_tokens": 2000,
        "completion_tokens": 1000,
        "cache_tokens": 100,
        "cost_total": 0.0035
      }
    ]
  }
}
```

**Nota**: O campo `runs` dentro de `metrics` so existe no modo 10x e contem as metricas
individuais de cada uma das 10 rodadas da etapa 3.

## Precos (via .env — backend/config.py)

| Variavel | Descricao | Exemplo |
|----------|-----------|---------|
| GROK_PRICE_INPUT | Preco por 1M tokens de entrada (USD) | 0.00000125 |
| GROK_PRICE_OUTPUT | Preco por 1M tokens de saida (USD) | 0.00000250 |
| GROK_PRICE_CACHE_READ | Preco por 1M tokens de cache (USD) | 0.00000020 |

Formula: `custo = (tokens / 1_000_000) * preco`
