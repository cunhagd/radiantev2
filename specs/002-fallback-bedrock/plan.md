# Implementation Plan: Sistema de Fallback Bedrock

**Branch**: `002-fallback-bedrock` | **Date**: 2026-06-28 | **Spec**: specs/002-fallback-bedrock/spec.md

## Summary

Refinar o sistema de fallback regional do bedrock_client.py, adicionando
metricas de failover, endpoint de status, logs estruturados e testes de
rotacao entre as 6 combinacoes.

## Technical Context

**Language/Version**: Python 3.11+
**Dependencies**: boto3, botocore
**Storage**: N/A (estado em memoria)
**Target**: Linux EC2 + Windows

## Constitution Check

1. GATE-FRAMEWORK: PASS - sem frameworks web
2. GATE-CREDENCIAIS: PASS - usa config centralizada
3. GATE-PIPELINE: PASS - pipeline inalterado
4. GATE-DEPENDENCIAS: PASS - nenhuma nova dependencia

## Project Structure

```
backend/
+-- bedrock_client.py     # Refinado com fallback + metricas
+-- app.py                # Novo endpoint /api/fallback-status
specs/002-fallback-bedrock/
+-- spec.md / plan.md / research.md / contracts/
+-- tasks.md
```

## Execution Order

1. Refatorar bedrock_client.py (fallback metrics, logging)
2. Adicionar endpoint /api/fallback-status no app.py
3. Criar test_fallback.py (teste de rotacao)
