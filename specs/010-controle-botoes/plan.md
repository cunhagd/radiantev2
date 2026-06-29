# Implementation Plan: Controle de Estado dos Botoes

**Branch**: `feature/010-controle-botoes` | **Date**: 2026-06-28 | **Spec**: `specs/010-controle-botoes/spec.md`

## Summary
Controlar quais botoes estao disponiveis com base na presenca de dados. Implementar uma funcao `updateButtonsState()` no frontend que gerencia o estado dos botoes com base em uma flag `hasData`. Nenhuma alteracao no backend necessaria.

## Technical Context

**Language/Version**: JavaScript Vanilla (frontend)

**Primary Dependencies**: Nenhuma — apenas manipulacao de DOM.

**Storage**: N/A — estado gerenciado no frontend via flag `hasData`.

**Testing**: Vitest (frontend, ja existente)

**Target Platform**: Browser (Chrome, Firefox, Edge)

**Performance Goals**: Atualizacao de estado em < 10ms.

**Constraints**:
- Nao pode depender de backend — o estado deve ser determinado localmente no frontend
- Botoes sao referenciados via `DOM.btnOnce`, `DOM.btnTen`, `DOM.btnUpload`, `DOM.btnClear`

## Constitution Check

*GATE: Passed. Backend nao foi alterado. Frontend segue regras de modularizacao.*

## Arquivos a Modificar

### frontend/js/ui.js
- Criar funcao `updateButtonsState(hasData)` que gerencia estado dos 4 botoes:
  - `hasData = true`: apenas `btnClear` habilitado
  - `hasData = false`: apenas `btnUpload` habilitado
- Chamar `updateButtonsState(true)` em `clearAllFrontendData()` apos limpeza (hasData = false)
- Chamar `updateButtonsState(false)` apos upload bem-sucedido em `handleFileUpload`

### frontend/js/state.js
- Adicionar `DOM.btnClear` se nao existir (ja existe? verificar)
- Adicionar funcao auxiliar `setButtonsEnabled(btn, enabled)`

### frontend/index.html
- Nenhuma alteracao — botoes ja existem no HTML

### frontend/tests/ui.test.js
- Adicionar testes para `updateButtonsState()`
