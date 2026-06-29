# Feature Specification: Controle de Estado dos Botoes

**Feature Branch**: `010-controle-botoes`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "Sistema analisa se tem dados de rodagem anterior ou atual renderizado na tela. Se tiver: bloquear totalmente todos os botoes e deixar disponivel apenas o botao de lixeira. Se nao tiver: liberar o botao de upload, mantendo os botoes de 1x e 10x bloqueados. Os botoes de 1x e 10x so serao liberados depois que o upload for confirmado com sucesso."

## User Scenarios & Testing

### User Story 1 - Sistema sem dados (estado inicial) (Priority: P1)
O usuario abre o sistema pela primeira vez. Nao ha dados de rodagem anterior. O sistema deve liberar apenas o botao de upload. Os botoes de analise 1x e 10x devem permanecer bloqueados.

**Acceptance Scenarios**:
1. **Given** que o sistema esta em estado inicial (sem dados), **When** a pagina carrega, **Then** o botao de upload esta habilitado.
2. **Given** que o sistema esta em estado inicial, **When** a pagina carrega, **Then** os botoes de analise 1x e 10x estao desabilitados.
3. **Given** que o sistema esta em estado inicial, **When** a pagina carrega, **Then** o botao lixeira esta desabilitado (nao ha nada para limpar).

### User Story 2 - Sistema com dados de rodagem anterior (Priority: P1)
O usuario ja executou uma analise e ha dados na tela. O sistema deve bloquear todos os botoes exceto o de lixeira, forcando o usuario a limpar antes de comecar nova rodagem.

**Acceptance Scenarios**:
1. **Given** que ha dados de rodagem anterior renderizados na tela, **When** a pagina carrega ou os dados sao exibidos, **Then** o botao de upload esta desabilitado.
2. **Given** que ha dados de rodagem anterior, **When** a pagina carrega, **Then** os botoes de analise 1x e 10x estao desabilitados.
3. **Given** que ha dados de rodagem anterior, **When** a pagina carrega, **Then** o botao lixeira esta habilitado.
4. **Given** que ha dados de rodagem anterior e o usuario clica na lixeira e limpa os dados, **When** a limpeza e concluida, **Then** o sistema volta ao estado inicial (US1): apenas upload liberado.

### User Story 3 - Apos upload bem-sucedido (Priority: P1)
O usuario fez upload de documentos com sucesso. O sistema deve liberar os botoes de analise 1x e 10x.

**Acceptance Scenarios**:
1. **Given** que o usuario fez upload de 1 ou mais documentos com sucesso, **When** o sistema confirma o upload, **Then** os botoes de analise 1x e 10x sao habilitados.
2. **Given** que o usuario fez upload com sucesso, **When** o sistema confirma, **Then** o botao de upload permanece habilitado.
3. **Given** que o usuario fez upload com sucesso, **When** o sistema confirma, **Then** o botao lixeira permanece desabilitado (ainda nao ha dados para limpar ate a analise ser executada).

### User Story 4 - Apos analise ser executada (Priority: P1)
A analise foi concluida e os dados estao na tela. O sistema deve bloquear upload e analise, liberar lixeira.

**Acceptance Scenarios**:
1. **Given** que a analise foi concluida e os dados estao renderizados, **When** o renderAll e chamado, **Then** o botao de upload e desabilitado.
2. **Given** que a analise foi concluida, **When** os dados sao renderizados, **Then** os botoes 1x e 10x sao desabilitados.
3. **Given** que a analise foi concluida, **When** os dados sao renderizados, **Then** o botao lixeira e habilitado.

### Edge Cases
- O que acontece se a pagina for recarregada com dados da rodagem anterior? O sistema deve chamar `/api/last-result` na inicializacao (ja existe) e, se houver dados, bloquear os botoes conforme US2.
- O que acontece se o upload falhar? Os botoes de analise nao devem ser liberados. O botao de upload deve permanecer habilitado para tentar novamente.
- O que acontece se o usuario limpar os dados e depois recarregar a pagina? O estado inicial (US1) deve ser restaurado.

## Requirements

### Functional Requirements
- **FR-001**: O sistema DEVE detectar automaticamente se ha dados de rodagem anterior renderizados na tela a cada carregamento de pagina e a cada alteracao de estado.
- **FR-002**: Quando houver dados renderizados, o sistema DEVE desabilitar os botoes de upload e analise (1x e 10x), habilitando apenas o botao lixeira.
- **FR-003**: Quando nao houver dados renderizados, o sistema DEVE habilitar apenas o botao de upload, mantendo 1x e 10x desabilitados.
- **FR-004**: Apos upload bem-sucedido de 1 ou mais documentos, o sistema DEVE habilitar os botoes de analise 1x e 10x.
- **FR-005**: Apos a conclusao da limpeza (lixeira), o sistema DEVE restaurar o estado conforme FR-003 (apenas upload liberado).
- **FR-006**: A funcao `clearAllFrontendData()` DEVE ser responsavel por re-aplicar o estado FR-003 apos limpeza.

## Success Criteria
- **SC-001**: Usuario consegue identificar visualmente quais acoes estao disponiveis em cada estado.
- **SC-002**: Nenhuma analise pode ser iniciada sem que documentos tenham sido enviados.
- **SC-003**: Nenhum upload ou analise pode ser iniciado enquanto houver dados de rodagem anterior sem limpeza.
