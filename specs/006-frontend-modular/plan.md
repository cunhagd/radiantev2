# Implementation Plan: Modularizacao do Frontend

**Branch**: `006-frontend-modular` | **Date**: 2026-06-28

## Summary
Dividir o frontend monolítico em 6 modulos JS e 5 arquivos CSS, mantendo
o HTML como orquestrador leve. Adicionar testes com Vitest + Happy-DOM.

## Technical Context
**Language**: JavaScript (Vanilla ES6+), CSS3, HTML5
**Test**: Vitest + Happy-DOM
**Dependencies**: vitest, happy-dom (devDependencies)

## Constitution Check
1. GATE-FRAMEWORK: PASS (sem frameworks web, sem bundlers)
2. GATE-DEPENDENCIAS: PASS (apenas devDependencies para teste)
3. GATE-FRONTEND: EMENDED (Principio V atualizado para permitir arquivos modulares desde que SEM bundlers/frameworks)

## Execution Order
1. Remover CSS inline do index.html -> 5 arquivos CSS
2. Criar 6 modulos JS a partir do script inline
3. Refatorar index.html como orquestrador
4. Configurar Vitest + Happy-DOM
5. Criar testes para cada modulo
6. Validar servidor servindo arquivos estaticos
