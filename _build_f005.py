#!/usr/bin/env python3
"""Gera artefatos da Feature 005: Testes Automatizados."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

BASE = "specs/005-testes-automatizados"
os.makedirs(f"{BASE}/contracts", exist_ok=True)
os.makedirs(f"{BASE}/checklists", exist_ok=True)

spec = """# Feature Specification: Testes Automatizados

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
"""

plan = """# Implementation Plan: Testes Automatizados

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
"""

tasks = """---
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
"""

for fname, content in [("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks)]:
    with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written {len(content)} chars to {BASE}/{fname}")

print("F005 artifacts created!")
