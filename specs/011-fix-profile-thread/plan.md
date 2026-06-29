# Implementation Plan: Correcao de Perfil AWS em Threads

**Branch**: `fix/011-fix-profile-thread` | **Date**: 2026-06-28 | **Spec**: `specs/011-fix-profile-thread/spec.md`

## Summary

Corrigir dois problemas:
1. Profile AWS `radiante` nao e propagado para threads (erro `The config profile () could not be found`)
2. Servidor antigo sem rota `/api/progress` — garantir que o servidor usa a versao mais recente

## Technical Context

**Causa raiz**: Quando o servidor inicia, `load_config()` captura `os.getenv("AWS_PROFILE", "")` no momento da inicializacao. Porem, `_run_analysis` roda em uma `threading.Thread()` que nao herda as variaveis de ambiente da sessao do shell. Alem disso, o `config` e carregado no modulo global e pode ser None se o servidor foi iniciado antes de aplicar o fix do PR #19.

**Solucao**: 
1. Em `_run_analysis`, forcar o `os.environ["AWS_PROFILE"]` a partir do config antes de chamar o pipeline
2. A funcao `_build_client` em `bedrock_client.py` ja recebe `config.aws_profile` — mas se o valor for vazio, o boto3.Session() nao encontra profile. Garantir fallback para `AWS_DEFAULT_PROFILE`.
3. Adicionar log de debug do profile ativo antes de cada chamada ao LLM

## Arquivos a Modificar

### backend/app.py
- `_run_analysis`: antes de iniciar o pipeline, forcar `os.environ["AWS_PROFILE"]` com o valor do config
- Verificar se o `config` global nao foi sobrescrito por `load_config()` dentro da thread

### backend/config.py
- Em `load_config()`, fazer fallback para `AWS_DEFAULT_PROFILE` se `AWS_PROFILE` estiver vazio
- Se ambos vazios, tentar o profile padrao do boto3

### backend/bedrock_client.py
- Em `_build_client`, se `config.aws_profile` estiver vazio, tentar `os.environ.get("AWS_DEFAULT_PROFILE", "")`
- Adicionar log do profile usado
