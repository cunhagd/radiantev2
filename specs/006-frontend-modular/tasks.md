---
description: "Task list for frontend modularizacao"
---
# Tasks: Modularizacao do Frontend

## Phase 1: Setup
- [ ] T001 Criar diretorios frontend/css/, frontend/js/, frontend/tests/

## Phase 2: CSS Modules
- [ ] T002 Criar frontend/css/tokens.css (design tokens)
- [ ] T003 Criar frontend/css/layout.css (grid, container, header, cards)
- [ ] T004 Criar frontend/css/components.css (botoes, badges, cifras, metricas, modal)
- [ ] T005 Criar frontend/css/animations.css (keyframes)
- [ ] T006 Criar frontend/css/responsive.css (media queries)

## Phase 3: JS Modules
- [ ] T007 Criar frontend/js/state.js (STATE global, DOM refs)
- [ ] T008 Criar frontend/js/api.js (API_BASE, fetchJSON, fetchText)
- [ ] T009 Criar frontend/js/ui.js (upload, clear modal, audit toggle)
- [ ] T010 Criar frontend/js/cifras.js (renderMetadata, renderCifras)
- [ ] T011 Criar frontend/js/metrics.js (renderMetrics)
- [ ] T012 Criar frontend/js/loading.js (runAnalysis, cleanupLoading, polling)

## Phase 4: HTML Orquestrador
- [ ] T013 Refatorar index.html (remover style/script inline, importar modulos)

## Phase 5: Testes
- [ ] T014 Configurar vitest + happy-dom (package.json + vitest.config.js)
- [ ] T015 Criar frontend/tests/state.test.js
- [ ] T016 Criar frontend/tests/api.test.js
- [ ] T017 Criar frontend/tests/cifras.test.js
- [ ] T018 Criar frontend/tests/metrics.test.js
- [ ] T019 Criar frontend/tests/loading.test.js

## Phase 6: Validacao
- [ ] T020 Testar npm test
- [ ] T021 Testar servidor servindo arquivos estaticos
- [ ] T022 Verificar funcionalidades completas
