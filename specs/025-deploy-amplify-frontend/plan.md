# Implementation Plan: Deploy Frontend no Amplify

**Branch**: `025-deploy-amplify-frontend` | **Date**: 2026-06-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/025-deploy-amplify-frontend/spec.md`

## Summary

Preparar o frontend do Radiante v2 para deploy no AWS Amplify. O Amplify App (`d2e6pwly2l3rt`) existe e está conectado ao repositório `github.com/cunhagd/radiante-final` na branch `main-poc`. É necessário:

1. Trocar o repositório no Amplify para `github.com/cunhagd/radiantev2` na branch `main`
2. Atualizar o `frontend/js/api.js` para usar a variável de ambiente `API_BASE` injetada pelo Amplify
3. Atualizar as variáveis de ambiente no Amplify (`API_BASE` apontando para `18.208.190.159:8000`)
4. Manter as configurações existentes (build spec, app root, redirect rules, cache)
5. Garantir que o frontend funcione corretamente no domínio `d2e6pwly2l3rt.amplifyapp.com`

**Abordagem técnica**: Operações via AWS CLI para gerenciar o Amplify + ajuste no `api.js` para ler variável de ambiente injetada no momento do build. Não há alterações no backend.

## Technical Context

**Language/Version**: JavaScript (Vanilla ES6), HTML5, CSS3 — sem alterações

**Primary Dependencies**: Nenhuma — frontend puro sem bundlers ou frameworks

**Storage**: AWS Amplify (hospedagem estática S3-based), conteúdo servido de `frontend/`

**Testing**: Teste manual via navegador após deploy + validação do console Amplify

**Target Platform**: AWS Amplify (WEB), navegadores modernos (Chrome, Firefox, Edge)

**Project Type**: Aplicação web estática servida via AWS Amplify

**Performance Goals**: Páginas carregam em < 3s via CDN do Amplify; builds completam em < 5 min

**Constraints**: Frontend sem bundlers — HTML/CSS/JS puro servido estaticamente; domínio existente `d2e6pwly2l3rt.amplifyapp.com`

**Scale/Scope**: Aplicação de uso interno/moderado, sem requisitos de escalabilidade crítica

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

| Gate | Status | Justification |
|------|--------|---------------|
| **GATE-FRAMEWORK** (Princípio I) | ✅ PASS | Nenhuma alteração no backend. O servidor continua usando `SimpleHTTPRequestHandler`. |
| **GATE-CREDENCIAIS** (Princípio II) | ✅ PASS | Credenciais AWS lidas do `.env` e usadas via AWS CLI para operações no Amplify. Nenhuma credencial é exposta no frontend ou versionada. |
| **GATE-PIPELINE** (Princípio III) | ✅ PASS | Nenhuma alteração no pipeline jurídico de 4 etapas. |
| **GATE-CEGUEIRA** (Princípio III) | ✅ PASS | Nenhuma alteração nas regras de negócio trabalhistas. |
| **GATE-CPC25** (Princípio III) | ✅ PASS | Nenhuma alteração nas classificações de risco. |
| **GATE-S3-BUCKET** (Princípio IV) | ✅ PASS | Nenhuma alteração no bucket S3 ou sua estrutura de prefixos. |
| **GATE-EXTRACAO** (Princípio IV) | ✅ PASS | Nenhuma alteração nos métodos de extração de documentos. |
| **GATE-FRONTEND** (Princípio V) | ✅ PASS | Frontend mantém-se sem bundlers ou frameworks JS. O deploy via Amplify serve os mesmos arquivos estáticos. A modularização (múltiplos CSS/JS) está em conformidade com a Emenda v1.1.0. |
| **GATE-DEPENDENCIAS** (Stack) | ✅ PASS | Nenhuma nova dependência adicionada ao backend ou frontend. |
| **GATE-DEPLOY** (Infraestrutura) | ✅ PASS (esclarecimento) | A Constituição menciona "CI/CD via GitHub Actions com rsync + SSH para EC2 na branch main-poc". Esta feature adiciona **Amplify** como mecanismo de deploy do frontend. O CI/CD EC2 existente permanece intacto. O Amplify opera em paralelo para servir o frontend estático. |

## Project Structure

### Documentation (this feature)

```text
specs/025-deploy-amplify-frontend/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (next command)
```

### Source Code (repository root)

```text
radiantev2/
├── frontend/
│   ├── index.html
│   ├── css/
│   │   ├── tokens.css
│   │   ├── layout.css
│   │   ├── components.css
│   │   ├── animations.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── state.js
│   │   ├── api.js        ← MODIFICADO: usar API_BASE de variável de ambiente
│   │   ├── cifras.js
│   │   ├── metrics.js
│   │   ├── ui.js
│   │   └── loading.js
│   └── package.json
├── .specify/
│   └── feature.json
└── specs/
    └── 025-deploy-amplify-frontend/
        └── ...
```

**Structure Decision**: Single project (Radlante v2 monorepo) com frontend estático em `frontend/`. O Amplify app root aponta para `frontend/`. A configuração `AMPLIFY_MONOREPO_APP_ROOT=frontend` já existe.

## Complexity Tracking

> Nenhuma violação da Constituição identificada — todos os gates passam sem justificativa adicional.
