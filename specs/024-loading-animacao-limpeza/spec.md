# Feature Specification: Loading Animação para Limpeza

**Feature Branch**: `024-loading-animacao-limpeza`

**Created**: 2026-06-29

**Status**: Draft

**Input**: User description: "Agora precisamos ajustar a tela de loading do botão lixeira para seguir o mesmo padrão visual da tela de loading das rodagens 1x e 10x. Ao clicar em limpar tudo deve aparecer um efeito de animaçao carregando a limpeza e mostrando na tela as etapas de limpeza com o status e os nomes dos arquivos listados limpos, exatamente como ocorrem com as etapas na tela de loading da rodagem 10x na etapa 3, onde temos a lsita de etapas e o status de cada."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Loading Visual com Timeline de Limpeza (Priority: P1)

O operador do sistema clica em "Limpar tudo" no modal de confirmação e, em vez de apenas ver um texto de status, visualiza uma tela de loading no mesmo padrão visual das análises 1x/10x, exibindo em tempo real as etapas de limpeza com status (Aguardando, Processando, Concluído) e os nomes dos arquivos/diretórios que estão sendo limpos.

**Why this priority**: O feedback visual de limpeza é importante para que o usuário saiba que a operação está em andamento, especialmente em buckets S3 com muitos arquivos onde a operação pode levar alguns segundos.

**Independent Test**: Clicar em "Limpar tudo" e verificar visualmente que o overlay de loading aparece com as etapas de limpeza sendo concluídas uma a uma.

**Acceptance Scenarios**:

1. **Given** que o usuário confirmou "Limpar tudo" no modal, **When** o processo de limpeza inicia, **Then** o modal de confirmação é fechado e o overlay de loading (mesmo visual das análises) aparece com o título "Limpando dados..." e cronômetro.
2. **Given** que o loading de limpeza está visível, **When** a limpeza começa, **Then** o overlay exibe uma timeline com etapas: "Limpando dados locais", "Limpando S3 (docs)", "Limpando S3 (markdown_docs)", "Limpando S3 (results)", "Limpando S3 (runs)", "Resetando estado do sistema", cada uma com status atualizado em tempo real (Aguardando → Processando → Concluído).
3. **Given** que uma etapa mostra os arquivos sendo limpos, **When** ela está em processamento, **Then** o badge da etapa exibe o nome do arquivo/diretório atual sendo limpo (ex.: "docs/" , "etapa1.md").
4. **Given** que a limpeza terminou com sucesso, **When** o último status de conclusão chega, **Then** o overlay fecha automaticamente e a tela é limpa (metadados zerados, cifras vazias).
5. **Given** que a limpeza encontrou erros parciais, **When** o processo termina, **Then** o overlay exibe a etapa com erro destacada em vermelho e fecha após alguns segundos.

---

### Edge Cases

- Se a limpeza for muito rápida (< 1s), a transição das etapas deve ser suave (mínimo de 300ms por etapa para dar tempo do usuário perceber)
- Se houver erro de conexão durante a limpeza, o overlay deve exibir mensagem de erro e fechar
- A limpeza não pode ser acionada se já estiver em andamento (botão desabilitado + verificação no backend, já existente)
- O histórico de execução deve ser limpo como última etapa

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O frontend DEVE exibir um overlay de loading (mesmo padrão visual de `loading-overlay` das análises) quando a limpeza é confirmada, reutilizando o mesmo HTML/CSS existente (loading card, header com ícone/título/cronômetro, timeline com steps).
- **FR-002**: O overlay DEVE exibir uma timeline com etapas de limpeza, cada uma com: nome descritivo, badge de status (Aguardando/Processando/Concluído/Erro), e dot visual colorido, seguindo o mesmo padrão de classe CSS `m3-step` / `m3-substep` da timeline de análise.
- **FR-003**: O backend DEVE modificar o endpoint `/api/clear-all` para suportar dois modos:
  - Se chamado com `Stream: text/event-stream` (ou parâmetro `stream=true`), DEVE retornar eventos SSE (Server-Sent Events) com o progresso de cada etapa de limpeza em tempo real.
  - Se chamado sem streaming, DEVE manter o comportamento atual (resposta JSON única ao final).
- **FR-004**: O backend DEVE enviar eventos SSE com a estrutura: `{"step": "local", "status": "processing", "file": "data/docs/"}`, `{"step": "local", "status": "done", "file": null}`, etc., para cada etapa de limpeza.
- **FR-005**: O frontend DEVE usar EventSource (ou fetch com leitura de stream) para consumir os eventos SSE e atualizar a timeline em tempo real.
- **FR-006**: As etapas de limpeza no frontend DEVEM ser:
  1. "Limpando dados locais" — remove arquivos e diretórios em `data/`
  2. "Limpando S3 (docs)" — deleta `docs/` do bucket
  3. "Limpando S3 (markdown_docs)" — deleta `markdown_docs/` do bucket
  4. "Limpando S3 (results)" — deleta `results/` do bucket
  5. "Limpando S3 (runs)" — deleta `runs/` do bucket
  6. "Resetando estado do sistema" — limpa memória, progresso e histórico
- **FR-007**: Cada etapa DEVE exibir no badge o nome do arquivo ou diretório sendo processado naquele momento (ex.: "docs/", "etapa1.md") enquanto estiver em processamento.
- **FR-008**: Ao final da limpeza (sucesso ou erro), o overlay DEVE fechar automaticamente e o frontend DEVE limpar os dados da tela (metadados zerados, cifras vazias, estado "initial").
- **FR-009**: Em caso de erro parcial, as etapas com erro DEVEM ser destacadas em vermelho e o overlay DEVE fechar após 3 segundos com mensagem de erro visível.

### Key Entities *(include if feature involves data)*

- **Overlay de Loading**: Camada visual semi-transparente com card centralizado, reutilizando o mesmo HTML/CSS do overlay de análise existente.
- **Timeline de Limpeza**: Lista de etapas visuais com dots, linhas conectoras, labels e badges de status, seguindo o padrão `m3-step` / `m3-step-line` / `m3-step-dot`.
- **Evento SSE (Server-Sent Event)**: Mensagem JSON enviada pelo backend durante a limpeza com campos `step` (identificador), `status` (pending/processing/done/error) e `file` (opcional, nome do arquivo atual).
- **Etapa de Limpeza**: Unidade atômica do processo de limpeza (local, S3 prefix, reset).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O overlay de loading aparece em menos de 200ms após confirmação da limpeza.
- **SC-002**: Todas as 6 etapas de limpeza são exibidas sequencialmente com transições visuais suaves.
- **SC-003**: O overlay fecha automaticamente em até 2 segundos após conclusão da última etapa.
- **SC-004**: O estado da aplicação retorna ao estado inicial (apenas botão Upload habilitado) após a limpeza.
- **SC-005**: Se a limpeza falhar parcialmente, as etapas com erro são exibidas com destaque vermelho.

## Assumptions

- O backend Python (`app.py`) continuará usando `http.server.SimpleHTTPRequestHandler` — sem frameworks web.
- Para SSE com o handler nativo, a resposta será configurada com `Content-Type: text/event-stream` e chamadas `self.wfile.write()` e `self.wfile.flush()`.
- O SSE enviará eventos diretamente via `self.wfile.write()` e `self.wfile.flush()` sem utilizar a classe `Progress` (conforme definido no `research.md`).
- O frontend JS poderá criar uma instância separada de timeline para limpeza ou reutilizar a existente com novos steps.
- Apenas os arquivos `backend/app.py`, `frontend/js/loading.js`, `frontend/js/ui.js`, `frontend/index.html` e possivelmente `frontend/css/components.css` serão modificados.
