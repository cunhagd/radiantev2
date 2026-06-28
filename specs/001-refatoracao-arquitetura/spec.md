# Feature Specification: Refatoracao da Arquitetura - Modularizacao do Backend

**Feature Branch**: `001-refatoracao-arquitetura`

**Created**: 2026-06-28

**Status**: Draft

**Input**: Refatorar o backend monolitico (1973 linhas em backend/app.py) em modulos independentes e coesos, mantendo total compatibilidade com a API existente e preservando todas as regras de negocio.

## User Scenarios & Testing

### User Story 1 - Migracao Sem Interrupcao (Priority: P1)

Como desenvolvedor, quero que a refatoracao do backend seja totalmente transparente para o usuario final, sem alteracoes nos endpoints da API ou no formato das respostas.

**Why this priority**: Esta e a restricao mais critica.

**Acceptance Scenarios**:
1. Given sistema modular, When GET /api/status, Then resposta tem o mesmo formato de antes.
2. Given sistema modular, When POST /api/run-once, Then retorna HTTP 202.
3. Given analise completa, When GET /api/last-result, Then JSON tem mesma estrutura.

### User Story 2 - Separacao Clara de Responsabilidades (Priority: P1)

Como desenvolvedor, quero modulos independentes com interfaces bem definidas.

**Why this priority**: Monolito de 1973 linhas mistura servidor, pipeline, extracao, S3 e PDF.

**Acceptance Scenarios**:
1. Given modulos refatorados, When importo apenas extracao, Then extraio PDF sem servidor.
2. Given modulos refatorados, When importo apenas pipeline, Then executo 4 etapas sem HTTP.
3. Given modulos refatorados, When altero PDF, Then servidor e pipeline nao mudam.

### User Story 3 - Configuracao Centralizada (Priority: P2)

Como desenvolvedor, quero configuracao centralizada com validacao na inicializacao.

**Why this priority**: Credenciais AWS lidas e limpas do os.environ no escopo global.

**Acceptance Scenarios**:
1. Given .env valido, When sistema inicializa, Then valida todas as configuracoes.
2. Given config carregada, When processo termina, Then os.environ esta limpo.
3. Given config invalida, When inicializa, Then erro claro e aborta.

### User Story 4 - Observabilidade e Metricas (Priority: P3)

Como desenvolvedor, quero metricas de operacao em formato consistente.

**Why this priority**: Sistema atual usa print() para metricas.

**Acceptance Scenarios**:
1. Given pipeline completo, When termina, Then metricas por etapa disponiveis.
2. Given erro no pipeline, When ocorre, Then erro registrado com timestamp.

## Requirements

- FR-001: Sistema DEVE manter 100% de compatibilidade retroativa com API existente.
- FR-002: Backend DEVE ser dividido em modulos: servidor, pipeline, extracao, S3, Bedrock, PDF, prompts, config, metricas.
- FR-003: Cada modulo DEVE ter interface publica clara sem dependencias circulares.
- FR-004: Configuracao DEVE ser centralizada, validada e limpar os.environ.
- FR-005: Cliente Bedrock DEVE implementar fallback regional (6 combinacoes).
- FR-006: Pipeline DEVE executar exatamente 4 etapas encadeadas.
- FR-007: Sistema DEVE registrar metricas de tokens, custo, tempo e erros.
- FR-008: Servidor HTTP DEVE usar http.server.SimpleHTTPRequestHandler sem frameworks.

## Success Criteria

- SC-001: Todos os endpoints existentes continuam funcionando sem alteracoes.
- SC-002: app.py reduzido de 1973 para maximo 200 linhas.
- SC-003: Cada modulo pode ser importado e testado em isolamento.
- SC-004: Configuracao invalida impede inicializacao com erro claro.
- SC-005: Fallback Bedrock ativado automaticamente em ThrottlingException.

## Assumptions

- Python 3.11+ em Windows e Linux (EC2 Ubuntu).
- Credenciais AWS via .env na raiz (nao IAM Role).
- Branch de deploy: main-poc com GitHub Actions.
- Frontend index.html nao sera modificado nesta feature.
- Bucket S3 radiante-final existe e esta acessivel.
- Modelo principal: us.anthropic.claude-sonnet-4-6.
- Sem banco de dados - estado em S3 e memoria.
