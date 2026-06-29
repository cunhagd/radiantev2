# Contract: Bedrock Fallback

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
