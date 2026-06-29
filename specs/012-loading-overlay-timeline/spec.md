# Feature Specification: Loading Overlay com Timeline Interativa

**Created**: 2026-06-28

**Status**: Draft

**Input**: Tela de loading que mostra o progresso em tempo real da analise juridica, com uma timeline interativa no estilo Material Design 3. Exibe as 4 etapas (Extracao de Cabecalho, Calculo de Cifras, Calculo de Probabilidade, Consolidacao do Provisionamento) e, na etapa 3, mostra sub-etapas para cada rodada (1x ou 10x). Ao finalizar, retorna automaticamente para a tela de relatorio.

## User Scenarios & Testing

### User Story 1 - Analise unica (1x) mostra progresso das 4 etapas (Priority: P1)
O usuario faz upload de documentos e clica em "Analisar 1x". Uma overlay de loading e exibida com uma timeline mostrando o progresso de cada etapa. Ao finalizar, a overlay fecha automaticamente e o relatorio e exibido.

**Acceptance Scenarios**:
1. **Given** que o usuario clicou em "1x", **When** a analise inicia, **Then** uma overlay e exibida com titulo "Analise unica em andamento".
2. **Given** que a overlay esta visivel, **Then** a timeline mostra 4 etapas na vertical: Extracao de Cabecalho, Calculo de Cifras, Calculo de Probabilidade, Consolidacao do Provisionamento.
3. **Given** que a etapa 3 esta sendo processada no modo 1x, **Then** apenas 1 sub-etapa e exibida ("Analise de probabilidade").
4. **Given** que cada etapa muda de status, **Then** o badge e o icone visual atualizam em tempo real (Aguardando -> Processando -> Concluido / Falhou).
5. **Given** que a analise foi concluida com sucesso, **Then** a overlay fecha apos 600ms e o relatorio e renderizado na tela.

### User Story 2 - Analise 10x mostra progresso detalhado (Priority: P1)
O usuario clica em "Analisar 10x". A overlay exibe a timeline com a etapa 3 mostrando 10 sub-etapas para cada rodada de probabilidade.

**Acceptance Scenarios**:
1. **Given** que o usuario clicou em "10x", **When** a analise inicia, **Then** o titulo exibe "Analise 10x em andamento".
2. **Given** que a etapa 3 esta ativa, **Then** 10 sub-etapas sao exibidas, cada uma com seu status individual.
3. **Given** que algumas rodadas foram concluidas, **Then** o badge da etapa 3 mostra o contador parcial (ex: "3/10 (2 em andamento)").
4. **Given** que todas as 10 rodadas foram concluidas, **Then** o badge exibe "10/10 concluidas".
5. **Given** que a analise 10x concluiu, **Then** aplica-se o mesmo comportamento do US1/ACS: overlay fecha e resultados sao renderizados.

### User Story 3 - Timer e feedback visual (Priority: P2)
O usuario ve um cronometro na overlay mostrando o tempo decorrido da analise.

**Acceptance Scenarios**:
1. **Given** que a overlay foi aberta, **Then** um timer no formato MM:SS comeca a contar.
2. **Given** que o usuario ve o timer, **Then** os minutos e segundos sao atualizados a cada segundo.

### User Story 4 - Tratamento de erros e conflitos (Priority: P2)
Se ocorrer um erro durante a analise ou se ja houver uma analise em andamento, o usuario e notificado.

**Acceptance Scenarios**:
1. **Given** que a analise falhou no backend, **Then** a overlay exibe alerta com a mensagem de erro e fecha.
2. **Given** que o usuario tenta iniciar analise enquanto outra ja esta rodando, **Then** um alerta informa "Ja existe uma analise em andamento".
3. **Given** que houve erro de conexao, **Then** um alerta "Erro de conexao ao servidor" e exibido.

### Edge Cases
- Se o progresso do backend retornar dados incompletos (etapas faltando ou status inesperados), a timeline deve tratar graciosamente, sem quebrar a exibicao.
- Se o backend nao tiver a rota `/api/progress`, o sistema deve continuar funcionando (apenas sem a timeline em tempo real).

## Requirements

### Functional Requirements
- **FR-001**: O sistema DEVE exibir uma overlay de loading com timeline vertical ao iniciar qualquer analise (1x ou 10x).
- **FR-002**: A timeline DEVE ter 4 etapas fixas: Extracao de Cabecalho, Calculo de Cifras, Calculo de Probabilidade, Consolidacao do Provisionamento.
- **FR-003**: A etapa 3 DEVE exibir sub-etapas: 1 para modo 1x, 10 para modo 10x.
- **FR-004**: Cada etapa/sub-etapa DEVE ter 4 estados visuais: pending (Aguardando), active (Processando), done (Concluido), error (Falhou).
  > **Mapeamento de estados**: A interface exibe termos em portugues para o usuario, mas o codigo e a API usam termos em ingles:
  > | UX (Portugues) | API/Codigo (Ingles) |
  > |----------------|---------------------|
  > | Aguardando | `pending` |
  > | Processando | `processing` / `active` |
  > | Concluido | `completed` / `done` |
  > | Falhou | `error` |
- **FR-005**: O sistema DEVE fazer polling do progresso a cada 1.2s nos endpoints `/api/status` e `/api/progress`.
- **FR-006**: Ao detectar status "completed" no backend, a overlay DEVE forcar todos os steps como "done" e fechar apos 600ms.
- **FR-007**: Ao detectar status "error", a overlay DEVE exibir alerta com a mensagem de erro e fechar.
- **FR-008**: O sistema DEVE exibir um timer (MM:SS) na overlay, atualizado a cada segundo.
- **FR-009**: Ao fechar a overlay, os botoes 1x e 10x DEVEM ser reabilitados.
- **FR-010**: O polling DEVE parar quando a analise for concluida ou falhar.

## Success Criteria
- **SC-001**: Usuario consegue ver o progresso de cada etapa em tempo real durante a analise.
- **SC-002**: Usuario consegue identificar visualmente qual etapa esta sendo processada, qual ja concluiu e qual falhou.
- **SC-003**: A overlay fecha automaticamente apos a conclusao e o relatorio e renderizado sem necessidade de recarregar a pagina.
- **SC-004**: Usuario recebe feedback claro em caso de erro (alerta com mensagem do backend).
