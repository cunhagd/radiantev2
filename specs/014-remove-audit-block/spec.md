# Feature Specification: Remocao do Bloco "Ver Relatorio de Auditoria"

**Feature Branch**: `014-remove-audit-block`

**Created**: 2026-06-29

**Status**: Draft

**Input**: Excluir o bloco "Ver Relatorio de Auditoria" — o usuario acessa o relatorio apenas via download do PDF no botao que ja existe.

## User Scenarios & Testing

### User Story 1 - Remover bloco de auditoria da interface (Priority: P1)

O usuario acessa a tela de resultados apos uma analise e nao ve mais o bloco "Ver Relatorio de Auditoria". O unico meio de obter o relatorio e clicando no botao "Baixar Relatorio PDF", que ja existe na interface.

**Why this priority**: O bloco de auditoria e redundante e polui a interface. O PDF consolidado ja contem todas as informacoes necessarias. Remover este bloco simplifica o UX.

**Independent Test**: Apos uma analise 1x ou 10x, verificar que o elemento "Ver Relatorio de Auditoria" nao esta presente no DOM.

**Acceptance Scenarios**:

1. **Given** que uma analise 1x foi concluida, **When** o usuario visualiza a tela de resultados, **Then** o bloco "Ver Relatorio de Auditoria" nao e exibido.
2. **Given** que uma analise 10x foi concluida, **When** o usuario visualiza a tela de resultados, **Then** o bloco "Ver Relatorio de Auditoria" nao e exibido.
3. **Given** que o bloco de auditoria foi removido, **When** o usuario deseja obter o relatorio, **Then** o unico meio disponivel e o botao "Baixar Relatorio PDF".

---

### Edge Cases

- **Sem resultados**: Se nao ha dados de analise na tela, nenhum bloco adicional deve ser exibido (ja e o comportamento atual).
- **Auditoria 10x vs 1x**: Ambos os modos (1x e 10x) devem ter o bloco de auditoria removido — nao importa o modo, o bloco nao deve aparecer.

## Requirements

### Functional Requirements

- **FR-001**: O sistema NAO DEVE exibir o bloco "Ver Relatorio de Auditoria" na tela de resultados apos qualquer analise (1x ou 10x).
- **FR-002**: O botao "Baixar Relatorio PDF" DEVE continuar funcionando como unico meio de acesso ao relatorio.

### Key Entities

- **Bloco de auditoria**: Elemento HTML exibido apos a analise que permite visualizar o relatorio de auditoria (arquivos `auditoria_10x.md`).
- **Botao "Baixar Relatorio PDF"**: Botao existente na interface que faz download do PDF consolidado.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Apos qualquer analise (1x ou 10x), o elemento "Ver Relatorio de Auditoria" nao esta presente no DOM.
- **SC-002**: O botao "Baixar Relatorio PDF" continua funcional apos a remocao do bloco de auditoria.

## Assumptions

- O bloco de auditoria e um elemento HTML no frontend (`frontend/index.html` ou `frontend/js/`) que pode ser removido sem impacto em outras funcionalidades.
- O backend precisa de alteracao minima — remover a rota `/api/audit-log` em `backend/app.py` para evitar codigo morto.
- O botao "Baixar Relatorio PDF" ja existe e esta funcionando corretamente (conforme feature 013).
