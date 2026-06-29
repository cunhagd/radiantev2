# Tasks — Correcao de Perfil AWS em Threads

**Input**: specs/011-fix-profile-thread/spec.md, specs/011-fix-profile-thread/plan.md

## 1. [FR-001] Forcar AWS_PROFILE em _run_analysis antes de iniciar pipeline
**Arquivo**: `backend/app.py`
- Dentro de `_run_analysis`, antes de chamar `get_s3_combined_context` ou `run_once`/`run_ten_times`:
  ```python
  if config.aws_profile:
      os.environ["AWS_PROFILE"] = config.aws_profile
  ```

## 2. [FR-002] Fallback para AWS_DEFAULT_PROFILE em config.py
**Arquivo**: `backend/config.py`
- Em `load_config()`, se `AWS_PROFILE` estiver vazio, tentar `AWS_DEFAULT_PROFILE`
- Se ambos vazios, manter vazio (boto3 usara profile default)
- Remover a secao de credenciais estaticas do .env que polui o ambiente

## 3. [FR-002] Log do profile em bedrock_client._build_client
**Arquivo**: `backend/bedrock_client.py`
- Em `_build_client`, antes de criar o Session, logar qual profile esta sendo usado
- Se `config.aws_profile` estiver vazio, tentar `os.environ.get("AWS_DEFAULT_PROFILE")` ou `"default"`

## 4. [FR-003] Verificar que o servidor esta na versao correta
**Arquivo**: N/A — acao manual
- Parar servidor antigo
- Iniciar com: `$env:AWS_PROFILE='radiante'; python -m backend.app`
- Verificar que `/api/progress` retorna 200
