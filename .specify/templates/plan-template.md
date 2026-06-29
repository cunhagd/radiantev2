# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: O backend utiliza exclusivamente
   `http.server.SimpleHTTPRequestHandler`? NENHUM framework web externo
   (FastAPI, Flask, Django) foi introduzido? (Princípio I)
2. **GATE-CREDENCIAIS**: As credenciais AWS são lidas do `.env` via
   `python-dotenv`, passadas explicitamente nos clientes boto3 e removidas
   do `os.environ`? (Princípio II)
3. **GATE-PIPELINE**: O pipeline segue exatamente 4 etapas encadeadas
   (Metadados → Cifras → Risco → JSON)? Os estados do agente evoluem
   corretamente? (Princípio III)
4. **GATE-CEGUEIRA**: A Etapa 2 recalcula valores do zero sem copiar cifras
   da petição? A trava de ponto eletrônico (≤20%) está implementada?
   (Princípio III — Regras 1, 14)
5. **GATE-CPC25**: A Etapa 3 classifica risco como Provável >50%, Possível
   25-50%, Remota <25%? O Art. 477 é tratado como binário? (Princípio III)
6. **GATE-S3-BUCKET**: Bucket `radiante-final` com prefixos `docs/`,
   `markdown_docs/`, `results/` e `runs/run_{i}/`? (Princípio IV)
7. **GATE-EXTRACAO**: PDF usa PyMuPDF com fallback Textract se < 100
   chars/página? DOCX usa leitura XML nativa? (Princípio IV)
8. **GATE-FRONTEND**: Frontend é arquivo único `frontend/index.html` sem
   bundlers ou frameworks JS? Usa polling a cada 3s? (Princípio V)
9. **GATE-DEPENDENCIAS**: Nenhuma dependência além de `boto3`, `pymupdf`,
   `openai`, `python-dotenv`, `reportlab` sem justificativa? (Stack
   Tecnológico)
10. **GATE-DEPLOY**: CI/CD via GitHub Actions com rsync + SSH para EC2 na
    branch `main-poc`? (Infraestrutura AWS)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
