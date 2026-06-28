# Contract: Metrics Module (backend/metrics.py)

## Public Interface

```python
from dataclasses import dataclass

@dataclass
class PipelineMetrics:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_tokens: int = 0
    cost_input: float = 0.0
    cost_output: float = 0.0
    cost_cache: float = 0.0
    cost_total: float = 0.0

def calculate_costs(
    prompt_tokens: int,
    completion_tokens: int,
    cache_tokens: int,
    model_type: str = "sonnet"
) -> PipelineMetrics:
    """Calcula custos com base nos precos do modelo."""
    ...

def merge_metrics(metrics_list: list[PipelineMetrics]) -> PipelineMetrics:
    """Soma metricas de multiplas etapas."""
    ...
```

## Dependencies

- config.Config (para precos)

## Thread Safety

- Funcoes sao stateless e thread-safe
