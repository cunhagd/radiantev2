# Tasks: Deploy Frontend no Amplify

**Input**: Design documents from `specs/025-deploy-amplify-frontend/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No explicit test tasks — validação manual via navegador e console Amplify conforme quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/js/api.js`, `frontend/index.html`
- **Infra (config)**: AWS Amplify console / AWS CLI commands
- **Documentação**: `specs/025-deploy-amplify-frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar credenciais e ambiente para as operações de deploy

**Note**: Esta feature é operacional — não requer criação de projeto ou dependências. O foco é configurar o Amplify e ajustar o código frontend.

- [x] T001 Obter GitHub Personal Access Token do usuário `cunhagd` com escopos `repo` e `admin:repo_hook`
- [x] T002 [P] Verificar se o usuário AWS `radiante-poc` tem permissão `amplify:*` via CLI (`aws amplify list-apps`)
- [x] T003 [P] Verificar se o Amplify GitHub App está instalado na conta/organização do GitHub

**Checkpoint**: Setup completo — credenciais e permissões verificadas

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Alterações no código-fonte que DEVEM ser commitadas antes de configurar o Amplify

**⚠️ CRITICAL**: O código precisa estar atualizado no repositório `radiantev2` (branch `main`) ANTES de trocar o repositório no Amplify

- [x] T004 Atualizar `frontend/js/api.js` para usar `window.API_BASE` como fonte primária da URL do backend, com fallback para `localhost` em desenvolvimento e API Gateway antigo em produção
- [x] T005 [P] Adicionar `<script src="js/env.js"></script>` antes dos demais scripts em `frontend/index.html`
- [x] T006 Commitar as alterações e fazer push para `origin main`: `git add frontend/js/api.js frontend/index.html && git commit -m "feat: preparar frontend para deploy no Amplify" && git push origin main`

**Checkpoint**: Código frontend atualizado e disponível no GitHub `cunhagd/radiantev2` branch `main`

---

## Phase 3: User Story 2 — Atualizar API_BASE para o backend EC2 (Priority: P1) 🎯 MVP

**Goal**: Garantir que o frontend no Amplify se comunique corretamente com o backend rodando no EC2 (`18.208.190.159:8000`)

**Independent Test**: Após o deploy, abrir o console do navegador em `d2e6pwly2l3rt.amplifyapp.com` e verificar que `API.BASE` retorna `http://18.208.190.159:8000` e requisições a `/api/status` retornam HTTP 200

### Implementation for User Story 2

- [x] T007 [P] [US2] Verificar/atualizar a variável de ambiente `API_BASE` no Amplify via CLI
- [x] T008 [US2] Atualizar o build spec do Amplify com o comando de injeção do `API_BASE`

**Checkpoint**: Variáveis de ambiente e build spec configurados para injetar `API_BASE` no frontend

---

## Phase 4: User Story 1 — Configurar Amplify para o repositório radiantev2 (Priority: P1)

**Goal**: Trocar o repositório do Amplify de `radiante-final` para `radiantev2` na branch `main`

**Independent Test**: Após a troca, um push na branch `main` do `radiantev2` dispara build e o site fica acessível em `d2e6pwly2l3rt.amplifyapp.com`

### Implementation for User Story 1

- [x] T009 [US1] Trocar o repositório no Amplify via CLI
- [x] T010 [P] [US1] Verificar se as regras de redirecionamento foram mantidas
- [x] T011 [P] [US1] Verificar se a configuração de cache foi mantida
- [x] T012 [US1] Verificar se o webhook foi recriado e está ativo

**Checkpoint**: Amplify conectado ao repositório `radiantev2` com todas as configurações preservadas

---

## Phase 5: User Story 3 — Build automático via GitHub (Priority: P2)

**Goal**: Ativar auto-build na branch `main` para deploys automáticos a cada push

**Independent Test**: Um commit na branch `main` com alteração no `frontend/` dispara build que conclui em menos de 5 minutos

### Implementation for User Story 3

- [x] T013 [US3] Conectar/criar a branch `main` no Amplify como PRODUCTION com auto-build ativado
- [x] T014 [US3] Verificar o status do primeiro build

**Checkpoint**: Branch `main` configurada com auto-build — deploys automáticos funcionando

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e verificação de que tudo está funcionando

- [x] T015 Acessar `https://d2e6pwly2l3rt.amplifyapp.com` e verificar que o frontend carrega sem erros no console
- [x] T016 Verificar que `API.BASE` aponta para `http://18.208.190.159:8000` no console do navegador
- [x] T017 [P] Fazer um push de teste na branch `main` e confirmar que o build automático dispara
- [ ] T018 Remover a branch `main-poc` do Amplify se não for mais necessária (requer permissões adicionais — pode ser feito manualmente no console AWS se desejar)
- [ ] T019 Executar validação completa conforme `specs/025-deploy-amplify-frontend/quickstart.md`
- [ ] T020 Atualizar documentação e contexto do agente apontando para o deploy concluído

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — pode começar imediatamente (obter GitHub PAT)
- **Foundational (Phase 2)**: Depende de T001 (GitHub PAT) para commit/push — BLOCKS phases 3-6
- **US2 (Phase 3)**: Depende de Phase 2 (código commitado) — pode executar depois que o push for feito
- **US1 (Phase 4)**: Depende de Phase 2 (código no repositório) + T001 (GitHub PAT)
- **US3 (Phase 5)**: Depende de US1 (Phase 4) — precisa do repositório trocado primeiro
- **Polish (Phase 6)**: Depende de todas as fases anteriores

### User Story Dependencies

- **User Story 2 (P1)**: Pode começar após Foundational (Phase 2) — código frontend commitado
- **User Story 1 (P1)**: Pode começar após Foundational (Phase 2) — código frontend no repositório
- **User Story 3 (P2)**: Depende de US1 — precisa do repositório trocado

### Parallel Opportunities

- T002 e T003 (verificação de permissões) podem rodar em paralelo
- T004 e T005 (alterações no código) podem rodar em paralelo (arquivos diferentes)
- T007 e T010, T011 podem rodar em paralelo (operações Amplify independentes)
- US2 e US1 podem ser executadas em sequência imediata se o GitHub PAT já estiver disponível

---

## Parallel Example: User Story 2

```bash
# Verificar variáveis de ambiente e build spec podem ser feitos juntos:
Task: "Verificar/atualizar API_BASE no Amplify via CLI"
Task: "Atualizar build spec no Amplify via CLI"
```

## Parallel Example: User Story 1

```bash
# Verificações de configuração mantida podem ser paralelas:
Task: "Verificar regras de redirecionamento mantidas"
Task: "Verificar configuração de cache mantida"
```

---

## Implementation Strategy

### MVP First (User Story 2 + User Story 1)

1. Complete Phase 1: Obter GitHub PAT
2. Complete Phase 2: Atualizar código frontend e commitar
3. Complete Phase 3 (US2): Configurar env vars e build spec no Amplify
4. Complete Phase 4 (US1): Trocar repositório no Amplify
5. **STOP and VALIDATE**: Acessar `d2e6pwly2l3rt.amplifyapp.com` e testar funcionalidades
6. Deploy/demo se estiver pronto

### Incremental Delivery

1. Code update + Amplify config → Frontend servindo do novo repositório (MVP!)
2. Adicionar auto-build (US3) → Deploys automáticos
3. Validação final → Aplicação em produção

### Observação Importante

Esta feature é **operacional/infraestrutura** — a maior parte das tarefas envolve comandos AWS CLI e configuração no Amplify, não código novo. As únicas alterações de código são:
- `frontend/js/api.js` — adicionar suporte a `window.API_BASE`
- `frontend/index.html` — adicionar script `js/env.js`

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- É necessário um GitHub Personal Access Token com escopos `repo` e `admin:repo_hook` (criado pelo dono do repositório `cunhagd`)
- O comando `aws amplify update-app --repository` requer o `--access-token` (ou `--oauth-token`)
- O build spec atual não tem comandos de build — precisamos adicionar o comando de geração do `js/env.js`
- Stop at any checkpoint to validate story independently
