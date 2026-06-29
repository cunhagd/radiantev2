# Implementation Plan: Loading Overlay com Timeline Interativa

**Branch**: `feature/012-loading-overlay-timeline` | **Date**: 2026-06-28 | **Spec**: `specs/012-loading-overlay-timeline/spec.md`

## Summary

Criar o modulo `frontend/js/loading.js` com a logica completa da overlay de loading com timeline interativa no estilo Material Design 3. O modulo ja existe e foi implementado sem seguir o speckit — este plano formaliza sua documentacao e verifica conformidade com a constitution.

## Technical Context

**Language/Version**: JavaScript Vanilla (ES5/ES6 via frontend)

**Primary Dependencies**: Nenhuma — apenas manipulacao de DOM e Fetch API.

**Storage**: N/A — estado gerenciado em memoria (STATE global em state.js).

**Testing**: Vitest + Happy-DOM (ja configurado no frontend)

**Target Platform**: Browser (Chrome, Firefox, Edge)

**Performance Goals**: Polling a cada 1.2s; atualizacao da timeline em <50ms.

**Constraints**:
- Sem frameworks JS ou bundlers (Constitution V)
- Design Material Design 3 (Constitution V)
- Overlay deve ser via CSS puro (animations.css)

**NEEDS CLARIFICATION**: Nenhum — implementacao ja existe e funciona.

## Constitution Check

*GATE: Passed. O modulo loading.js segue todas as regras da Constitution: zero frameworks, zero bundlers, JavaScript Vanilla, design Material3, polling via Fetch API.*

## Phases

### Phase 0: Outline & Research

Nao ha necessidades de pesquisa — todas as decisoes ja estao implementadas e funcionando.

**Output**: research.md com confirmacao de que nao ha questoes em aberto.

### Phase 1: Design & Contracts

#### Data Model

O estado de progresso e definido pelo backend e consumido pelo frontend via `/api/progress`:

```typescript
interface ProgressData {
  etapa1: { status: "pending"|"processing"|"completed"|"error"; label: string };
  etapa2: { status: "pending"|"processing"|"completed"|"error"; label: string };
  etapa3: Array<{ status: "pending"|"processing"|"completed"|"error"; label: string }>;
  etapa4: { status: "pending"|"processing"|"completed"|"error"; label: string };
  total_runs: number; // 1 para 1x, 10 para 10x
}
```

#### Artefatos

1. **research.md** — confirmacao de decisoes
2. **data-model.md** — modelo de dados do progresso
3. **quickstart.md** — guia de validacao
4. **contracts/** — contrato da API `/api/progress`

## Complexity Tracking

- **Modulo loading.js**: ~330 linhas — complexidade MEDIA
- **CSS (animations.css + components.css)**: ~50 linhas de estilo de overlay — complexidade BAIXA
- **HTML (index.html)**: estruturas da timeline no DOM — complexidade BAIXA
