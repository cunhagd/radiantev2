# Implementation Plan: Modo CLI Interativo

**Branch**: `004-modo-cli` | **Date**: 2026-06-28

## Summary
Adicionar modo CLI completo com argparse, execucao passo a passo,
suporte a documentos locais e salvamento local.

## Technical Context
**Language**: Python 3.11+
**Dependencies**: Nenhuma nova
**Storage**: Local (data/docs/, data/results/) ou S3

## Constitution Check
1. GATE-FRAMEWORK: PASS
2. GATE-DEPENDENCIAS: PASS
3. GATE-PIPELINE: PASS

## Execution Order
1. Refatorar main() em app.py com modo CLI completo
2. Adicionar --docs, --step, --once/--ten, --output
3. Adicionar modo interativo passo a passo
