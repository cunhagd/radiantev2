# Implementation Plan: Migracao de Autenticacao AWS

**Branch**: `015-migrate-aws-auth` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/015-migrate-aws-auth/spec.md`

## Summary

Substituir a autenticacao por profile SSO por `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` do `.env` para S3 e Textract, mantendo `AWS_BEARER_TOKEN_BEDROCK` exclusivamente para Bedrock Mantle (Grok). Remover toda dependencia de profile SSO do codigo e documentacao.

## Technical Context

**Language/Version**: Python 3.14

**Primary Dependencies**: boto3, python-dotenv, openai, requests-aws4auth

**Storage**: Sistema de arquivos local (`data/`) + S3 (`radiante-final`)

**Testing**: pytest (backend), vitest + happy-dom (frontend)

**Target Platform**: Linux (EC2) e Windows (desenvolvimento local)

**Project Type**: Web service (backend HTTP nativo + frontend estatico)

**Performance Goals**: N/A — feature de configuracao, sem impacto em performance

**Constraints**: 
- Nao quebrar autenticacao via IAM Role da EC2 em producao
- Bearer Token deve ser usado exclusivamente para Bedrock Mantle
- Access Keys devem ser passadas explicitamente nos clientes boto3 (Principio II da Constitution)

**Scale/Scope**: Arquivos de configuracao (`config.py`, `s3_client.py`, `bedrock_client.py`, `extract.py`) e `.env`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: Sem alteracoes no backend HTTP — mantem `SimpleHTTPRequestHandler`. ✅ OK
2. **GATE-CREDENCIAIS**: **VIOLACAO ATUAL** — as credenciais sao lidas do `.env` mas NAO sao passadas explicitamente nos clientes boto3 (confiam no profile SSO). **Feature criada para corrigir isso.** ⚠️
3. **GATE-PIPELINE**: Sem alteracoes no pipeline juridico. ✅ OK
4. **GATE-CEGUEIRA**: Sem alteracoes. ✅ OK
5. **GATE-CPC25**: Sem alteracoes. ✅ OK
6. **GATE-S3-BUCKET**: Bucket `radiante-final` mantido. ✅ OK
7. **GATE-EXTRACAO**: Sem alteracoes. ✅ OK
8. **GATE-FRONTEND**: Sem alteracoes. ✅ OK
9. **GATE-DEPENDENCIAS**: `requests-aws4auth` e `httpx` ja existem para SigV4. Sem novas dependencias. ✅ OK
10. **GATE-DEPLOY**: Sem alteracoes no CI/CD. ✅ OK

**Resultado**: 1 violacao ativa (GATE-CREDENCIAIS) que sera corrigida por esta feature.

## Project Structure

### Documentation (this feature)

```text
specs/015-migrate-aws-auth/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
backend/
├── config.py             # Adicionar load de AWS_ACCESS_KEY_ID/SECRET, remover aws_profile
├── s3_client.py          # Passar credenciais explicitamente no cliente boto3
├── bedrock_client.py     # Remover logica de SigV4 com profile SSO
├── extract.py            # Passar credenciais no cliente Textract
├── app.py                # Nenhuma alteracao no roteamento
├── tests/
│   ├── test_config.py    # Atualizar tests
│   └── test_integration.py  # Atualizar tests

.env                      # Novo formato documentado
infra/scripts/
├── .env.production       # Atualizar template
└── setup-aws-infra.sh    # Remover referencias a SSO

docs/                     # Documentacao diversa (GROK_DOC.md, etc.)
```

**Structure Decision**: Mantem a estrutura existente do projeto. Apenas arquivos de configuracao e clientes AWS serao modificados.

## Complexity Tracking

| Violacao | Por que e Necessario | Alternativa Rejeitada |
|----------|---------------------|------------------------|
| GATE-CREDENCIAIS (Principio II) | As credenciais AWS precisam ser passadas explicitamente nos clientes boto3 e removidas do `os.environ`, em vez de depender de profile SSO que expira | Manter SSO e usar `AWS_PROFILE` continuaria exigindo `aws sso login` periodico, o que e inviavel para um servidor em producao |
