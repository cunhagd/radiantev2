# Feature Specification: Limpeza Completa do Sistema (Clear-All)

**Feature Branch**: `009-limpeza-completa`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "Limpeza completa do sistema ao clicar no botao lixeira. Ao clicar no botao lixeira (clear-all), o sistema deve limpar TODOS os dados da rodagem atual em TODOS os locais de armazenamento. Locais a serem limpos: 1. Diretorio local data/, 2. Bucket S3 radiante-final, 3. Memoria do servidor (ANALYSIS_JOBS), 4. Progress, 5. Historico de execucao, 6. Frontend. Apos a limpeza o sistema deve ficar como novo, pronto para uma nova rodagem."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Limpeza completa pós-análise (Priority: P1)

O usuário concluiu uma análise jurídica e visualizou os resultados na tela. Ao clicar no botão lixeira (clear-all), o sistema apaga todos os vestígios da rodagem atual — arquivos locais, dados no S3, memória do servidor, progresso, histórico e dados renderizados no frontend. O sistema retorna ao estado inicial, com os botões de upload e análise habilitados para uma nova rodagem.

**Why this priority**: Esta é a funcionalidade central — sem ela, a limpeza não ocorre em nenhum cenário. Representa o fluxo principal que o usuário espera.

**Independent Test**: Pode ser testada isoladamente: executar uma análise, verificar que dados existem em todos os 6 locais, clicar no botão lixeira, e confirmar que todos os locais foram limpos e o sistema está pronto para nova rodagem.

**Acceptance Scenarios**:

1. **Given** que o usuário completou uma análise e há dados nos 6 locais de armazenamento, **When** o usuário clica no botão lixeira e confirma a ação, **Then** o diretório local `data/` é limpo (docs/, markdown_docs/, PDFs, JSONs, relatórios .md).

2. **Given** que o usuário completou uma análise e há dados no bucket S3, **When** o usuário clica no botão lixeira e confirma a ação, **Then** os prefixos `docs/`, `markdown_docs/`, `results/` e `runs/` do bucket `radiante-final` são limpos.

3. **Given** que o usuário completou uma análise e há dados na memória do servidor, **When** o usuário clica no botão lixeira e confirma a ação, **Then** o dicionário `ANALYSIS_JOBS` é resetado ao estado inicial (`status: "idle"`, `message: ""`, `last_result: None`).

4. **Given** que o usuário completou uma análise e há dados de progresso, **When** o usuário clica no botão lixeira e confirma a ação, **Then** o `Progress` é resetado via `Progress.reset()` para o estado padrão.

5. **Given** que o usuário completou uma análise e há histórico de execução, **When** o usuário clica no botão lixeira e confirma a ação, **Then** o `_execution_history` é esvaziado.

6. **Given** que o usuário completou uma análise e há dados renderizados no frontend, **When** o usuário clica no botão lixeira e confirma a ação, **Then** a função `clearAllFrontendData()` é chamada e a tela é limpa.

7. **Given** que a limpeza foi concluída, **When** o usuário visualiza a interface, **Then** os botões de upload e análise estão habilitados para nova rodagem.

---

### User Story 2 - Limpeza com análise em andamento (Priority: P2)

O usuário iniciou uma análise (status: processing) e deseja cancelá-la e limpar tudo antes da conclusão.

**Why this priority**: Cenário importante para evitar dados inconsistentes, mas menos frequente que a limpeza pós-análise. Pode ser implementado em versão futura.

**Independent Test**: Pode ser testada isoladamente: iniciar uma análise, clicar no botão lixeira durante o processamento, confirmar que a análise é interrompida e todos os dados são limpos.

**Acceptance Scenarios**:

1. **Given** que uma análise está em andamento (`status: "processing"`), **When** o usuário clica no botão lixeira e confirma, **Then** o sistema interrompe a análise em execução.

2. **Given** que a análise foi interrompida, **When** a limpeza é executada, **Then** todos os 6 locais de armazenamento são limpos conforme User Story 1.

---

### User Story 3 - Limpeza sem dados existentes (Priority: P3)

O usuário clica no botão lixeira quando o sistema já está limpo (sem rodagens anteriores).

**Why this priority**: Cenário de borda para garantir robustez — não deve causar erros ou comportamento inesperado.

**Independent Test**: Pode ser testada isoladamente: abrir o sistema pela primeira vez (sem nenhuma análise), clicar no botão lixeira, e verificar que permanece no estado inicial sem erros.

**Acceptance Scenarios**:

1. **Given** que o sistema está em estado inicial (sem dados em nenhum local), **When** o usuário clica no botão lixeira e confirma, **Then** o sistema permanece em estado inicial sem exibir mensagens de erro.

2. **Given** que o sistema está em estado inicial, **When** o usuário clica no botão lixeira e confirma, **Then** a interface não apresenta mudanças visuais (já estava limpa) e os botões de upload e análise continuam habilitados.

---

### Edge Cases

- O que acontece quando a limpeza do S3 falha parcialmente (ex: um prefixo não é deletado)? O sistema deve reportar a falha mas continuar limpando os demais locais, garantindo limpeza máxima possível.
- O que acontece quando o diretório local `data/` está bloqueado por outro processo? O sistema deve capturar a exceção, registrar o erro e prosseguir com a limpeza dos demais locais.
- O que acontece quando ocorre um erro de rede durante a limpeza do S3? O sistema deve retentar uma vez e, se persistir, reportar o erro sem interromper a limpeza dos outros locais.
- Como o sistema se comporta se o usuário clicar no botão lixeira múltiplas vezes rapidamente? O botão deve ser desabilitado durante a operação de limpeza para evitar requisições concorrentes.
- O que acontece se o bucket S3 `radiante-final` não existir ou não estiver acessível? A limpeza do S3 deve falhar graciosamente sem travar o resto da operação.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE expor um endpoint `/api/clear-all` que aceite requisições POST e execute a limpeza completa em todos os 6 locais de armazenamento.
- **FR-002**: O sistema DEVE limpar o diretório local `data/` removendo todos os arquivos e subdiretórios em `docs/`, `markdown_docs/`, PDFs, JSONs e relatórios `.md` na raiz.
- **FR-003**: O sistema DEVE limpar o bucket S3 `radiante-final` removendo todos os objetos sob os prefixos `docs/`, `markdown_docs/`, `results/` e `runs/`.
- **FR-004**: O sistema DEVE resetar a memória do servidor reinicializando o dicionário `ANALYSIS_JOBS` para seu estado padrão (`status: "idle"`, `message: ""`, `error_details: ""`, `last_result: None`).
- **FR-005**: O sistema DEVE executar `Progress.reset()` para reinicializar o estado de progresso para o padrão.
- **FR-006**: O sistema DEVE limpar o `_execution_history` no módulo `pipeline`, esvaziando a lista de histórico de execuções.
- **FR-007**: O frontend DEVE chamar `clearAllFrontendData()` após receber confirmação de sucesso do backend, limpando todos os dados renderizados na tela.
- **FR-008**: O sistema DEVE manter os botões de upload e análise habilitados após a conclusão da limpeza.
- **FR-009**: O sistema DEVE desabilitar o botão de confirmação do modal de limpeza durante a execução da operação para evitar cliques concorrentes.
- **FR-010**: O sistema DEVE exibir mensagem de status na barra superior da interface indicando o início e a conclusão da limpeza.
- **FR-011**: O sistema DEVE capturar e reportar erros parciais sem interromper a limpeza dos demais locais.
- **FR-012**: O endpoint `/api/clear-all` DEVE verificar se há uma análise em andamento; em caso positivo, DEVE rejeitar a requisição com status 409 (Conflict) a menos que a funcionalidade de cancelamento esteja implementada (P2).

### Key Entities *(include if feature involves data)*

- **Estado do Sistema (System State)**: Representa o estado agregado do sistema nos 6 locais de armazenamento. A limpeza deve restaurar este estado ao "estado inicial" (como se nenhuma rodagem tivesse ocorrido).
- **Locais de Armazenamento (Storage Locations)**: 6 destinos independentes que armazenam dados da rodagem. Cada um tem seu próprio mecanismo de limpeza (filesystem, S3 API, reset de variável em memória, reset de classe, reset de lista, manipulação de DOM).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuários conseguem executar uma limpeza completa em menos de 5 segundos para uma rodagem típica (até 10 documentos).
- **SC-002**: Após a limpeza, 100% dos dados da rodagem anterior são removidos de todos os 6 locais de armazenamento verificáveis.
- **SC-003**: Usuários conseguem iniciar uma nova rodagem imediatamente após a limpeza, sem necessidade de recarregar a página.
- **SC-004**: Em caso de falha parcial (ex: S3 indisponível), pelo menos os locais acessíveis são limpos com sucesso e o erro é reportado ao usuário.

## Assumptions

- O bucket S3 `radiante-final` existe e as credenciais AWS configuradas têm permissão de leitura/escrita/delete nos prefixos `docs/`, `markdown_docs/`, `results/` e `runs/`.
- O diretório local `data/` é utilizado exclusivamente pelo sistema Radiante e pode ser limpo sem afetar outros processos.
- O botão lixeira (clear-all) já existe na interface do usuário e está integrado ao backend via chamada POST para `/api/clear-all`.
- A função `clearAllFrontendData()` já existe no frontend e está funcional.
- O `Progress.reset()` aceita ser chamado sem argumentos para resetar ao estado padrão (total_runs=1).
- A limpeza não precisa preservar logs de auditoria ou histórico entre rodagens — a limpeza é completa e irreversível.
- O usuário confirma a ação em um modal antes da execução (comportamento já existente no botão lixeira).
