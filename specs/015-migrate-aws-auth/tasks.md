# Tasks: Migracao de Autenticacao AWS

**Input**: Design documents from `specs/015-migrate-aws-auth/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Test tasks sao incluidos — feature requer ajustes em testes existentes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Backend config**: `backend/config.py`
- **S3 Client**: `backend/s3_client.py`
- **Bedrock Client**: `backend/bedrock_client.py`
- **Extract (Textract)**: `backend/extract.py`
- **Tests**: `backend/tests/test_config.py`, `backend/tests/conftest.py`
- **Infra**: `infra/scripts/.env.production`, `infra/scripts/setup-aws-infra.sh`
- **Root**: `.env`, `docs/GROK_DOC.md` (se existir)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: N/A — feature de configuracao, sem necessidade de setup de projeto.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: N/A — sem prerrequisitos bloqueantes.

---

## Phase 3: User Story 1 - Usar Access Keys do .env para S3 e Textract (Priority: P1) 🎯 MVP

**Goal**: Substituir a autenticacao por profile SSO por `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` do `.env` para S3 e Textract, passando as credenciais explicitamente nos clientes boto3 e removendo do `os.environ`.

**Independent Test**: Com `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` no `.env` e sem profile SSO ativo, o sistema deve inicializar e autenticar no S3 e Textract com sucesso.

### Implementation for User Story 1

- [X] T001 [P] [US1] Adicionar campos `aws_access_key_id` e `aws_secret_access_key` no dataclass `Config` em `backend/config.py` (linha 31-41)
- [X] T002 [P] [US1] Adicionar leitura de `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` no `_load_env()` em `backend/config.py` (linhas 54-64) e carrega-los no `load_config()` (linhas 139-148)
- [X] T003 [P] [US1] Atualizar `_build_s3_params()` em `backend/s3_client.py` (linhas 21-27) para passar `aws_access_key_id`, `aws_secret_access_key` e `region_name` explicitamente no retorno do dict
- [X] T004 [P] [US1] Atualizar `_ocr_pdf()` em `backend/extract.py` (linhas 69-74) para receber config e passar `aws_access_key_id`, `aws_secret_access_key` e `region_name` explicitamente no `boto3.client("textract", ...)`
- [X] T005 [US1] Remover o campo `aws_profile` do dataclass `Config` em `backend/config.py` (linha 33) e sua atribuicao em `load_config()` (linha 141)
- [X] T006 [US1] Substituir `_check_aws_credentials()` em `backend/config.py` (linhas 102-124) para validar apenas a presenca de `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` lidos do `.env`, sem depender de profile SSO ou ~/.aws/config. Atualizar `_validate()` (linhas 69-94) para refletir nova logica.
- [X] T007 [US1] Apos carregar as credenciais do `.env` em `load_config()`, remover `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` do `os.environ` (conforme Principio II da Constitution)
- [X] T008 [US1] Atualizar o docstring do modulo `backend/config.py` (linhas 3-7) removendo mencao a SSO
- [X] T009 [US1] Atualizar `get_s3_combined_context()` em `backend/s3_client.py` para passar `config` nas chamadas a `list_files()` e `download_file()` ja existentes — verificar se a assinatura ja aceita config

### Test adjustments

- [X] T010 [US1] Atualizar `test_config.py` — adicionar teste para `aws_access_key_id`/`aws_secret_access_key` no Config, remover teste `test_load_config_with_sso_succeeds` (linhas 32-41), adicionar teste que verifica remocao do `os.environ`
- [X] T011 [US1] Atualizar `conftest.py` — adicionar `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` no mock_env (linhas 25-33)

**Checkpoint**: S3 e Textract autenticam com Access Keys do .env sem SSO.

---

## Phase 4: User Story 2 - Bearer Token exclusivo para Bedrock Mantle (Priority: P1)

**Goal**: Garantir que o Bedrock Mantle use exclusivamente o Bearer Token, removendo o codigo de SigV4 com profile SSO do `bedrock_client.py`.

**Independent Test**: Com `AWS_BEARER_TOKEN_BEDROCK` no `.env`, as chamadas ao Grok funcionam. Sem o token, o erro e claro sobre Bearer Token faltante.

### Implementation for User Story 2

- [X] T012 [P] [US2] Em `_build_client()` em `backend/bedrock_client.py` (linhas 107-186), remover todo o bloco de autenticacao SigV4 com profile SSO (bloco de `import httpx` em diante — linhas 129-186), mantendo APENAS a logica do Bearer Token (linhas 122-127)
- [X] T013 [P] [US2] Atualizar `_build_client()` para validar que `config.bearer_token` nao esta vazio e lancar erro claro caso contrario (antes de criar o cliente OpenAI)
- [X] T014 [US2] Remover importacoes de `httpx`, `requests_aws4auth` e `boto3` que nao sao mais necessarias em `backend/bedrock_client.py`

**Checkpoint**: Bedrock Mantle usa apenas Bearer Token, sem dependencia de SigV4 ou SSO.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Limpeza de referencias SSO na documentacao e configuracao.

- [X] T015 Atualizar `.env` — remover comentarios sobre SSO (linhas 11-13), deixar apenas as variaveis atuais com comentarios claros sobre Access Keys + Bearer Token
- [X] T016 Atualizar `infra/scripts/.env.production` — remover variavel `BEDROCK_MODEL_ID` desatualizada (Claude), manter apenas Grok, adicionar comentarios sobre IAM Role
- [X] T017 Atualizar `infra/scripts/setup-aws-infra.sh` — remover comentarios ou secoes que mencionam profile SSO como prerequisito
- [X] T018 [P] Atualizar `docs/GROK_DOC.md` (se existir) ou criar nota removendo referencias a SSO — verificar se arquivo existe
- [X] T019 Rodar `pytest backend/tests/ -v` e confirmar que todos os testes existentes passam apos as alteracoes
- [X] T020 Executar `python dev.py --server` e validar os 2 cenarios do `quickstart.md` (Cenario 1: S3 funciona sem SSO, Cenario 5: erro claro com credenciais invalidas)

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: Tasks T001-T009 podem rodar parcialmente em paralelo. T005 e T006 dependem de T001/T002 (modelo de Config atualizado).
- **US2 (Phase 4)**: Pode rodar em paralelo com US1 (arquivos diferentes — `bedrock_client.py` vs `config.py`/`s3_client.py`/`extract.py`).
- **Polish (Phase 5)**: Apos US1 e US2 completos.

### Sequential Dependencies Within US1

- T005 (remover aws_profile) depende de T001 (novo modelo Config)
- T006 (nova validacao) depende de T001/T002 (modelo + load atualizados)
- T007 (remover do os.environ) depende de T002
- T008 e T009 podem rodar em paralelo com o restante

### Parallel Opportunities

- T001, T002, T003, T004: Paralelos (arquivos diferentes)
- T012, T013, T014: Paralelos (mesmo arquivo, mas edicoes em locais diferentes)
- T015, T016, T017, T018: Paralelos (arquivos diferentes)

### Parallel Example: Implementation

```bash
# Todas as alteracoes em config.py (T001, T002, T005, T006, T007, T008):
Task: "Adicionar campos e load de Access Keys + remover aws_profile + nova validacao + remover os.environ"

# Todas as alteracoes no s3_client.py (T003):
Task: "Passar credenciais explicitamente no cliente S3"

# Todas as alteracoes no extract.py (T004):
Task: "Passar credenciais explicitamente no cliente Textract"

# Todas as alteracoes no bedrock_client.py (T012, T013, T014):
Task: "Remover SigV4, manter apenas Bearer Token"
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Completar Phase 3: US1 (T001-T011) — S3 e Textract com Access Keys
2. Completar Phase 4: US2 (T012-T014) — Bedrock com Bearer Token
3. **STOP e VALIDATE**: Testes passam, servidor funciona sem SSO
4. Seguir para Phase 5: Polish

### Incremental Delivery

1. T001-T009: Implementacao das alteracoes de autenticacao
2. T010-T011: Ajuste dos testes
3. T012-T014: Remocao do SigV4 do Bedrock
4. T015-T018: Limpeza de documentacao
5. T019: Rodar testes
6. T020: Validacao manual

---

## Phase 6: Convergence — Ajustes pos-implementacao

**Purpose**: Garantir compatibilidade com EC2 (IAM Role) e atualizar Constitution para refletir estado atual do projeto.

- [X] T021 [P] [FR-004] Tornar `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` opcionais na validacao em `backend/config.py`: se ausentes, permitir que boto3 use IAM Role (IMDS da EC2) sem credenciais explicitas, mantendo apenas `AWS_BEARER_TOKEN_BEDROCK` como obrigatorio (missing)
- [X] T022 [P] [SC-003] Atualizar secao "Infraestrutura AWS" e "Modelos de IA" em `.specify/memory/constitution.md` — remover referencias a Claude Sonnet 4.6 e rsync+SSH, refletir Grok 4.3, Bedrock Mantle e SSM SendCommand (partial)
