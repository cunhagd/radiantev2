# Contract: Bedrock Client Module (backend/bedrock_client.py)

## Public Interface

```python
FALLBACK_STRATEGY: list[dict] = [
    # 6 combinacoes: Opus 4.6 (3 regioes) + Sonnet 4.6 (3 regioes)
    {"priority": 1, "model_name": "...", "model_id": "...", "region": "..."},
    ...
]

def run_llm_stage_streaming(
    system_prompt: str,
    user_message: str,
    context: str,
    stream_to_console: bool = True
) -> tuple[str, PipelineMetrics]:
    """Executa etapa do LLM com streaming, cache de prompt e retry.
    Implementa fallback automatico entre as 6 combinacoes."""
    ...
```

## Dependencies

- boto3 (bedrock-runtime)
- openai (para Grok via Mantle)
- config.Config
- metrics.PipelineMetrics
