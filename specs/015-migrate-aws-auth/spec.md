# Feature Specification: Migracao de Autenticacao AWS

**Feature Branch**: `015-migrate-aws-auth`

**Created**: 2026-06-29

**Status**: Draft

**Input**: As chaves da conta AWS 406223549358 expiraram. O DevOps criou um usuario IAM `radiante-poc` com novas credenciais (Access Key + Secret Key) e tambem um Bearer Token para o Bedrock Mantle. O sistema precisa ser ajustado para usar `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` do `.env` como metodo de autenticacao padrao (S3 e Textract), e `AWS_BEARER_TOKEN_BEDROCK` exclusivamente para chamadas ao Bedrock Mantle (IA/Grok). Toda a dependencia do profile SSO deve ser removida do codigo e da documentacao.

## User Scenarios & Testing

### User Story 1 - Autenticar servicos AWS com Access Keys (Priority: P1)

O usuario desenvolvedor/configurador do sistema precisa configurar as credenciais AWS no arquivo `.env`. Ao iniciar o sistema, ele deve conseguir acessar S3 e Textract usando `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` definidas no `.env`, sem depender de `aws sso login` ou profile SSO. As chamadas ao Bedrock Mantle (IA) devem usar o `AWS_BEARER_TOKEN_BEDROCK`.

**Why this priority**: Sem essa migracao, o sistema para de funcionar quando a sessao SSO expira, o que e inaceitavel para um ambiente de producao. As novas credenciais IAM sao permanentes.

**Independent Test**: Com as variaveis AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY e AWS_BEARER_TOKEN_BEDROCK definidas no .env e SEM profile SSO configurado, o sistema deve inicializar e autenticar em S3, Textract e Bedrock Mantle com sucesso.

**Acceptance Scenarios**:

1. **Given** que o arquivo `.env` contem `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` e `AWS_BEARER_TOKEN_BEDROCK` validos, **When** o sistema inicia, **Then** ele autentica no S3 sem erros.
2. **Given** que o sistema esta rodando com as novas credenciais, **When** uma analise e iniciada, **Then** o Textract funciona corretamente para OCR.
3. **Given** que o sistema esta rodando com as novas credenciais, **When** uma etapa de IA e executada, **Then** o Bedrock Mantle (Grok) funciona usando o Bearer Token.
4. **Given** que nao ha profile SSO `radiante` configurado, **When** o sistema inicia, **Then** ele nao tenta usar SSO e funciona apenas com as variaveis do `.env`.

---

### Edge Cases

- **Bearer Token expirado**: Se o `AWS_BEARER_TOKEN_BEDROCK` expirar, o sistema deve reportar erro claro e nao tentar fallback para Access Keys no Bedrock.
- **Access Keys invalidas**: Se as Access Keys forem invalidas, o sistema deve reportar erro claro ao tentar S3 ou Textract, sem travar.
- **Ambiente hibrido (EC2)**: Na EC2 com IAM Role, as variaveis de ambiente AWS_ACCESS_KEY_ID/SECRET tem prioridade sobre a IMDS. O .env de producao deve ser configurado sem essas chaves para que a EC2 use a IAM Role.

## Requirements

### Functional Requirements

- **FR-001**: O sistema DEVE ler `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` do arquivo `.env` e usa-los como credenciais padrao para todos os clientes AWS (S3, Textract).
- **FR-002**: O sistema DEVE usar `AWS_BEARER_TOKEN_BEDROCK` do `.env` exclusivamente para autenticacao no Bedrock Mantle (chamadas ao modelo Grok 4.3).
- **FR-003**: O sistema NAO DEVE depender de profile SSO (`AWS_PROFILE=radiante`) para autenticacao. O profile SSO deve ser removido do codigo e da documentacao.
- **FR-004**: O sistema DEVE garantir que a EC2 em producao (com IAM Role) continue funcionando — as variaveis AWS_ACCESS_KEY_ID/SECRET so devem ser usadas se explicitamente definidas no .env.
- **FR-005**: O sistema DEVE reportar erros claros de autenticacao quando as credenciais estiverem invalidas ou faltando, diferenciando entre Access Keys e Bearer Token.

### Key Entities

- **Credenciais AWS**: `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` — par de chaves IAM do usuario `radiante-poc` na conta 406223549358.
- **Bearer Token Bedrock**: `AWS_BEARER_TOKEN_BEDROCK` — API Key do Bedrock Mantle para autenticacao nas chamadas de IA.
- **Profile SSO**: Configuracao `[profile radiante]` no arquivo `~/.aws/config` — sera removida como dependencia do sistema.
- **IAM Role EC2**: Role assumida pela instancia EC2 em producao — fornece credenciais via IMDS, sem necessidade de chaves fixas.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Com apenas `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` e `AWS_BEARER_TOKEN_BEDROCK` no `.env` (sem SSO), o sistema autentica em S3 e Textract com sucesso.
- **SC-002**: O cliente Bedrock Mantle e criado usando o Bearer Token, nao as Access Keys.
- **SC-003**: Nenhuma referencia a `AWS_PROFILE`, `--profile radiante` ou `sso_` permanece no codigo ou documentacao do projeto.

## Assumptions

- O usuario `radiante-poc` tem as permissoes necessarias: S3 (leitura/escrita no bucket `radiante-final`), Textract (`DetectDocumentText`), Bedrock (`InvokeModel` para `xai.grok-4.3`).
- As Access Keys sao rotacionaveis — se mudarem, basta atualizar o `.env`, nao o codigo.
- Em producao (EC2), o `.env` nao contera chaves fixas — a IAM Role fornece as credenciais automaticamente.
