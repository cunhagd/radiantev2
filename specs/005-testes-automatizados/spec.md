# Feature Specification: Testes Automatizados

**Feature Branch**: `005-testes-automatizados`
**Created**: 2026-06-28
**Status**: Draft

**Input**: Criar suite completa de testes unitarios e de integracao para todos
os modulos do backend.

## User Stories

### US1 — Testes Unitarios por Modulo (P1)
Como desenvolvedor, quero testar cada modulo isoladamente para garantir
que interfaces publicas funcionam corretamente.

### US2 — Testes de Integracao (P2)
Como desenvolvedor, quero testar o pipeline completo com dados mockados
para validar o fluxo ponta a ponta.

### US3 — Testes do Servidor HTTP (P3)
Como desenvolvedor, quero testar endpoints HTTP com requests simuladas
para garantir que o servidor responde corretamente.

## Requirements
- FR-001: Testes para backend/config.py (carregamento, validacao, .env)
- FR-002: Testes para backend/metrics.py (calculo de custos, merge)
- FR-003: Testes para backend/extract.py (PDF, DOCX, JSON, TXT)
- FR-004: Testes para backend/pipeline.py (4 etapas, agregacao, historico)
- FR-005: Testes para backend/bedrock_client.py (fallback, metricas, status)
- FR-006: Testes para backend/app.py (endpoints HTTP)
- FR-007: Testes para backend/s3_client.py (upload, download, list)
- FR-008: Testes para backend/pdf_generator.py (geracao PDF)
- FR-009: Testes rodam com pytest, sem dependencia externa real
- FR-010: Coverage minima de 70%

## Success Criteria
- SC-001: python -m pytest backend/tests/ --cov=backend --cov-report=term-minimal
- SC-002: Todos os modulos tem pelo menos 3 testes unitarios
- SC-003: Testes mockam AWS (boto3, S3, Bedrock)
