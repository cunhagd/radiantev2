# Contract: Config Module (backend/config.py)

## Public Interface

```python
class Config:
    @property
    def aws_access_key_id(self) -> str: ...
    @property
    def aws_secret_access_key(self) -> str: ...
    @property
    def aws_region(self) -> str: ...
    @property
    def bedrock_model_id(self) -> str: ...
    @property
    def bearer_token(self) -> str: ...
    @property
    def bucket_name(self) -> str: ...
    @property
    def docs_dir(self) -> str: ...
    @property
    def md_dir(self) -> str: ...
    @property
    def grok_prices(self) -> dict: ...

def load_config() -> Config:
    """Carrega config do .env, valida campos obrigatorios,
    remove variaveis AWS do os.environ. Aborta com erro se
    configuracao invalida."""
    ...
```

## Usage

```python
from backend.config import load_config
config = load_config()
print(config.aws_region)  # us-east-1
```

## Dependencies

- python-dotenv
- os (stdlib)

## Errors

- SystemExit: se campo obrigatorio faltando
