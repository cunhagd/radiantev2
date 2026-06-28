# Implementation Plan: Refatoracao da Arquitetura - Modularizacao do Backend

**Branch**: `001-refatoracao-arquitetura` | **Date**: 2026-06-28 | **Spec**: specs/001-refatoracao-arquitetura/spec.md

## Summary

Refatorar o backend monolitico (1973 linhas em backend/app.py) em modulos
independentes e coesos, mantendo 100% de compatibilidade retroativa com a
API existente. Cada responsabilidade (servidor, pipeline, extracao, S3,
Bedrock, PDF, metricas) sera isolada em seu proprio modulo com interfaces
bem definidas, eliminando dependencias ocultas e facilitando manutencao.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: boto3, pymupdf, openai, python-dotenv, reportlab

**Storage**: Amazon S3 (bucket radiante-final) + dicionarios em memoria

**Target Platform**: Linux (EC2 Ubuntu) e Windows (desenvolvimento local)

**Project Type**: web-service (backend HTTP + servidor de arquivos estaticos)

**Constraints**: Framework-free, credenciais explicitas, pipeline 4 etapas

## Constitution Check

1. GATE-FRAMEWORK: PASS - backend continua usando http.server puro
2. GATE-CREDENCIAIS: PASS - config centralizada com limpeza de os.environ
3. GATE-PIPELINE: PASS - pipeline de 4 etapas mantido com estados
4. GATE-CEGUEIRA: PASS - regras de negocio intactas em prompts.py
5. GATE-CPC25: PASS - classificacao CPC 25 mantida
6. GATE-S3-BUCKET: PASS - bucket e prefixos inalterados
7. GATE-EXTRACAO: PASS - extracao movida para modulo proprio
8. GATE-FRONTEND: PASS - frontend nao modificado nesta feature
9. GATE-DEPENDENCIAS: PASS - nenhuma nova dependencia adicionada
10. GATE-DEPLOY: PASS - CI/CD inalterado na branch main-poc

**Resultado**: Todos os 10 gates aprovados. Nenhuma violacao.

## Project Structure

### Source Code

```
backend/
+-- __init__.py
+-- app.py              # Orquestrador HTTP (< 200 linhas)
+-- config.py           # Configuracao centralizada (.env + validacao)
+-- pipeline.py         # Pipeline de 4 etapas encadeadas
+-- prompts.py          # Prompts juridicos (mantido do original)
+-- extract.py          # Extracao de documentos (PDF, DOCX, JSON, TXT)
+-- s3_client.py        # Cliente S3 (upload, download, listagem)
+-- bedrock_client.py   # Cliente Bedrock com fallback regional
+-- pdf_generator.py    # Geracao de PDF (ReportLab)
+-- metrics.py          # Observabilidade e metricas
frontend/
+-- index.html          # Interface web unica (inalterado)
```

## Complexity Tracking

Nenhuma violacao da Constitution Check. Secao vazia.

## Execution Order

1. config.py - Sem dependencias de outros modulos
2. metrics.py - Depende apenas de config
3. s3_client.py - Depende de config
4. extract.py - Depende de config, s3_client
5. pdf_generator.py - Depende de config
6. bedrock_client.py - Depende de config (com fallback regional)
7. pipeline.py - Depende de bedrock_client, extract, prompts, config
8. app.py - Depende de todos os modulos (orquestrador leve)