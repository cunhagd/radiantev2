# Contract: S3 Client Module (backend/s3_client.py)

## Public Interface

```python
def upload_file(file_bytes: bytes, s3_key: str) -> bool:
    """Upload de arquivo para S3."""
    ...

def download_file(s3_key: str) -> bytes | None:
    """Download de arquivo do S3. Retorna None se nao existir."""
    ...

def list_files(prefix: str) -> list[str]:
    """Lista arquivos em um prefixo S3."""
    ...

def delete_files(prefix: str) -> int:
    """Deleta todos os arquivos em um prefixo. Retorna qtd deletada."""
    ...

def get_s3_combined_context() -> str:
    """Baixa docs do S3, extrai texto, gera markdowns, concatena contexto."""
    ...
```

## Dependencies

- boto3
- config.Config

## Errors

- Fallback para modo local (data/docs/) em caso de falha S3
