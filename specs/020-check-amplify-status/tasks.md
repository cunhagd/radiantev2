# Tasks: Check Amplify Status (020)

**Input**: Design documents from `specs/020-check-amplify-status/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-output.md, quickstart.md

**Tests**: Não solicitados — script de diagnóstico único, sem testes automatizados.

**Organization**: Feature com uma única user story (P1) — script CLI de diagnóstico.

## Format: `[ID] [P] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Criar diretório `scripts/` e verificar estrutura base.

- [X] T001 Criar diretório `scripts/` na raiz do projeto
- [X] T002 Verificar se `boto3` e `python-dotenv` estão instalados via `requirements.txt` (`pip list | Select-String -Pattern "boto3|python-dotenv"`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No work can begin until this phase is complete.

- [X] T003 Estudar o mecanismo de carregamento de configuração em `backend/config.py` para reutilizar `Config` e `load_config()` no script CLI

---

## Phase 3: User Story 1 — Diagnóstico do status do Amplify via CLI (Priority: P1) 🎯 MVP

**Goal**: Criar script `scripts/check_amplify.py` que verifica o status do AWS Amplify na conta configurada, listando aplicativos, ambientes e status de cada um.

**Independent Test**: Executar `python scripts/check_amplify.py` e verificar saída formatada no terminal.

### Implementation for User Story 1

- [X] T004 [P] [US1] Implementar carregamento de configuração em `scripts/check_amplify.py` usando `from backend.config import load_config` — obter região e credenciais AWS
- [X] T005 [P] [US1] Implementar função `format_datetime(dt)` para formatar datas AWS (ISO 8601) no padrão brasileiro em `scripts/check_amplify.py`
- [X] T006 [US1] Implementar função `get_amplify_status()` em `scripts/check_amplify.py` — criar cliente boto3 `amplify` com credenciais explícitas, chamar `list_apps()` e retornar lista de aplicativos (app_id, name, description, create_time)
- [X] T007 [US1] Implementar função `get_branch_status(amplify_client, app_id)` em `scripts/check_amplify.py` — chamar `list_branches(appId=app_id)` e retornar lista de branches (branch_name, stage, status inferido de activeJobId, deploy_url montado, last_update)
- [X] T008 [US1] Implementar função `print_status(apps)` em `scripts/check_amplify.py` — formatar e exibir a saída no terminal conforme contrato em `contracts/cli-output.md`
- [X] T009 [US1] Implementar `main()` e `if __name__ == "__main__"` em `scripts/check_amplify.py` — orquestrar fluxo principal: carregar config → criar cliente → listar apps → para cada app listar branches → exibir saída
- [X] T010 [US1] Implementar tratamento de erros em `scripts/check_amplify.py` — capturar `ClientError` (AccessDeniedException, UnrecognizedClientException), `EndpointConnectionError`, `ConnectTimeoutError` e exceções genéricas com mensagens amigáveis e exit code 1

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e ajustes.

- [X] T011 Executar `python scripts/check_amplify.py` para validar funcionamento com credenciais reais — verificar saída conforme `contracts/cli-output.md`
- [X] T012 Verificar se a saída corresponde ao formato do contrato (`contracts/cli-output.md`) em todos os cenários (ativo, inativo, erro) — referência: `contracts/cli-output.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pode iniciar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — necessário para entender mecanismo de Config
- **User Story 1 (Phase 3)**: Depende de Foundational concluída
- **Polish (Phase 4)**: Depende de User Story 1 completa

### User Story Dependencies

- **User Story 1 (P1)**: Única user story — sem dependências externas

### Within User Story 1

Tarefas T004 e T005 são independentes e podem rodar em paralelo. T006 e T007 são independentes entre si, mas dependem de T004. T008 depende de T006 e T007. T009 depende de T004-T008. T010 é independente de T005-T009 (pode ser implementado separadamente).

### Parallel Opportunities

- T004 e T005: paralelo (arquivos diferentes, sem dependências)
- T006 e T007: paralelo (funções diferentes no mesmo arquivo, sem dependência entre si)
- T010: pode ser implementado em paralelo com T005-T009 (tratamento de erros é independente)

---

## Parallel Example: User Story 1

```bash
# T004 e T005 em paralelo:
Task: "Implementar carregamento de config em scripts/check_amplify.py"
Task: "Implementar format_datetime() em scripts/check_amplify.py"

# T006 e T007 em paralelo:
Task: "Implementar get_amplify_status() em scripts/check_amplify.py"
Task: "Implementar get_branch_status() em scripts/check_amplify.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (todo o script CLI)
4. **STOP and VALIDATE**: Executar `python scripts/check_amplify.py` e verificar saída
5. Completar Phase 4: Polish

O script é único e auto-contido — após a Fase 3, o MVP está completo.
