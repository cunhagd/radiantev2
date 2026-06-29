# Feature Specification: Correcao de Perfil AWS em Threads

**Created**: 2026-06-28

**Status**: Draft

**Input**: Erro `The config profile () could not be found` ao executar analise. O profile AWS (`radiante`) nao e propagado para as threads que executam o pipeline de analise. Alem disso, o endpoint `/api/progress` retorna 404 porque o servidor rodava uma versao desatualizada.

## User Scenarios & Testing

### User Story 1 - Analise funciona com SSO em background threads (Priority: P1)
O usuario faz upload de documentos e clica em "Analisar 1x". O servidor inicia uma thread em background para executar o pipeline. As chamadas ao Bedrock Mantle (Grok 4.3) devem autenticar via SSO corretamente.

**Acceptance Scenarios**:
1. **Given** que o servidor foi iniciado com `AWS_PROFILE=radiante`, **When** uma analise e iniciada (thread background), **Then** o boto3 consegue obter as credenciais SSO.
2. **Given** que as credenciais SSO estao validas, **When** `run_llm_stage_streaming` e chamado, **Then** o Grok 4.3 retorna resposta (200).
3. **Given** que a analise foi concluida com sucesso, **When** o frontend consulta `/api/last-result`, **Then** os dados sao retornados corretamente.

### User Story 2 - Progresso visivel durante analise (Priority: P2)
O usuario inicia uma analise e pode ver o progresso em tempo real via `/api/progress`.

**Acceptance Scenarios**:
1. **Given** que uma analise esta em andamento, **When** o frontend consulta `/api/progress`, **Then** retorna 200 com o estado atual de cada etapa.
2. **Given** que a analise terminou, **When** o frontend consulta `/api/progress`, **Then** retorna status "completed".

### Edge Cases
- O que acontece se o servidor for iniciado sem `AWS_PROFILE`? O config deve usar `AWS_DEFAULT_PROFILE` ou o profile padrao do boto3.
- O que acontece se o profile configurado nao existe? O erro deve ser informativo, indicando qual profile esta sendo procurado.

## Requirements

### Functional Requirements
- **FR-001**: O sistema DEVE propagar o profile AWS (`AWS_PROFILE`) para todas as threads filhas que fazem chamadas ao boto3.
- **FR-002**: O sistema DEVE usar o profile da variavel de ambiente no momento da inicializacao, mesmo em threads.
- **FR-003**: O endpoint `/api/progress` DEVE retornar HTTP 200 com o estado atual do progresso da analise.

## Success Criteria
- **SC-001**: Analises 1x e 10x completam sem erro de configuracao de profile.
- **SC-002**: Usuario ve progresso em tempo real durante a analise.
