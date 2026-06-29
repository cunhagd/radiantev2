# Feature Specification: Modularizacao do Frontend

**Feature Branch**: `006-frontend-modular`
**Created**: 2026-06-28
**Status**: Draft

**Input**: Dividir o frontend monolítico (1455 linhas) em arquivos JS e CSS
modulares, mantendo compatibilidade total com o backend e sem introduzir
frameworks ou bundlers.

## User Stories

### US1 — Modulos JS por Responsabilidade (P1)
Como desenvolvedor, quero que o JavaScript seja dividido em modulos com
responsabilidades bem definidas (api, state, ui, cifras, metrics, loading)
para facilitar testes unitarios e manutencao.

### US2 — CSS Modular por Categoria (P2)
Como desenvolvedor, quero que o CSS seja dividido em categorias (tokens,
layout, componentes, animacoes, responsivo) para facilitar alteracoes
sem colaterais.

### US3 — Testes Unitarios via DOM Simulado (P1)
Como desenvolvedor, quero testar cada modulo JS isoladamente usando
JSDOM/Happy-DOM sem servidor real, garantindo que:
- renderizacao de cifras funciona com dados validos e invalidos
- api.js faz chamadas corretas
- loading.js gerencia timers e polling

### US4 — HTML como Orquestrador (P1)
Como operador, quero que o HTML carregue os modulos na ordem correta e
funcione exatamente como antes.

## Requirements
- FR-001: 6 modulos JS: api.js, state.js, ui.js, cifras.js, metrics.js, loading.js
- FR-002: 5 arquivos CSS: tokens.css, layout.css, components.css, animations.css, responsive.css
- FR-003: index.html importa CSS via <link> e JS via <script src=...>
- FR-004: Nenhuma alteracao no backend app.py
- FR-005: Nenhuma dependencia de frameworks JS ou bundlers
- FR-006: Testes com Vitest + Happy-DOM
- FR-007: Cobertura minima de 80% nos modulos JS

## Success Criteria
- SC-001: npm test roda todos os testes sem erros
- SC-002: Servidor HTTP serve frontend modularizado sem erros 404
- SC-003: Funcionalidades existentes (upload, analise, metadados, cifras, metricas) funcionam identicamente
