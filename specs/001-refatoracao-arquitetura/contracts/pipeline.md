# Contract: Pipeline Module (backend/pipeline.py)

## Public Interface

```python
def run_single_pipeline(
    combined_context: str,
    run_idx: int | None = None,
    stream_to_console: bool = True
) -> dict | None:
    """Executa as 4 etapas do pipeline: Metadados -> Cifras -> Risco -> JSON."""
    ...

def run_once(combined_context: str) -> dict:
    """Executa pipeline unico, salva resultados no S3, gera PDF."""
    ...

def run_ten_times(combined_context: str) -> dict:
    """Executa 10 pipelines paralelos com ThreadPoolExecutor(max_workers=5),
    agrega resultados com media."""
    ...

def aggregate_results(results: list[dict]) -> dict:
    """Agrega resultados de multiplas rodadas (media, padronizacao)."""
    ...

def save_stage_files(s3_prefix: str, combined_context: str, data: dict):
    """Salva arquivos de cada etapa no S3 com prompt + contexto + resposta."""
    ...
```

## Dependencies

- bedrock_client (run_llm_stage_streaming)
- extract (get_document_text)
- prompts (constantes de prompt)
- s3_client (save_stage_files)
- pdf_generator (generate_pdf)
- metrics (PipelineMetrics)
- concurrent.futures (ThreadPoolExecutor)
