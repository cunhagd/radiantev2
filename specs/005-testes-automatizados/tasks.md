---
description: "Task list for testes automatizados"
---
# Tasks: Testes Automatizados

## Phase 1: Setup
- [ ] T001 Instalar pytest, pytest-cov, pytest-mock
- [ ] T002 Criar conftest.py com fixtures compartilhadas (mock config, mock boto3)

## Phase 2: Testes Unitarios
- [ ] T003 [US1] Criar test_config.py — carregamento, validacao, campos obrigatorios
- [ ] T004 [US1] Criar test_metrics.py — calculo custos, merge, formatacao
- [ ] T005 [US1] Criar test_extract.py — PDF, DOCX, JSON, TXT, OCR fallback
- [ ] T006 [US1] Criar test_bedrock_client.py — fallback, FallbackMetrics, status
- [ ] T007 [US1] Criar test_pipeline.py — pipeline 4 etapas, agregacao, historico
- [ ] T008 [US1] Criar test_s3_client.py — upload, download, list, delete
- [ ] T009 [US1] Criar test_pdf_generator.py — geracao PDF com dados mock

## Phase 3: Testes de Integracao
- [ ] T010 [US2] Criar test_integration.py — pipeline completo com dados mockados

## Phase 4: Testes do Servidor HTTP
- [ ] T011 [US3] Criar test_app.py — endpoints GET/POST com http.server mock

## Phase 5: Validacao
- [ ] T012 Executar pytest e verificar coverage minima de 70%
