# Implementation Plan: Testes Automatizados

**Branch**: `005-testes-automatizados` | **Date**: 2026-06-28

## Summary
Criar suite de testes com pytest, utilizando mocks para AWS e dados
de exemplo para cada modulo.

## Technical Context
**Language**: Python 3.11+
**Dependencies**: pytest, pytest-cov, pytest-mock
**Mocks**: unittest.mock (boto3, S3, Bedrock, Textract)

## Constitution Check
1. GATE-DEPENDENCIAS: PASS (pytest/pytest-cov adicionados)

## Execution Order
1. Instalar pytest e dependencias de teste
2. Criar test_config.py, test_metrics.py
3. Criar test_extract.py, test_bedrock_client.py
4. Criar test_pipeline.py, test_app.py
5. Criar test_s3_client.py, test_pdf_generator.py
6. Executar suite completa e verificar coverage
