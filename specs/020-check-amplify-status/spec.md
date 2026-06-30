# Feature Specification: Check Amplify Status

**Feature Branch**: `020-check-amplify-status`

**Created**: 2026-06-29

**Status**: Draft

**Input**: Analisar via CLI se o Amplify está ativo na conta AWS configurada e quais recursos estão rodando.

## User Scenarios & Testing

### User Story 1 - Diagnóstico do status do Amplify via CLI (Priority: P1)

O desenvolvedor/operador pode executar um comando via terminal que verifica se o AWS Amplify está ativo na conta configurada, listando os aplicativos Amplify existentes, seus ambientes e o status de cada um.

**Why this priority**: Sem essa verificação, não há visibilidade sobre o estado do Amplify na conta, dificultando diagnósticos de deploy, monitoramento de recursos ativos e identificação de problemas de infraestrutura.

**Independent Test**: Ao executar o comando de diagnóstico, o sistema retorna uma saída formatada no terminal com o status do Amplify (ativo/inativo), lista de aplicativos e ambientes, ou uma mensagem clara de erro/exceção.

**Acceptance Scenarios**:

1. **Given** que a conta AWS configurada possui Amplify ativo, **When** o comando de diagnóstico é executado, **Then** a saída exibe "Amplify: ATIVO" com a lista de aplicativos, ambientes e status de deploy de cada um.
2. **Given** que a conta AWS não possui Amplify configurado ou não há aplicativos, **When** o comando é executado, **Then** a saída exibe "Amplify: INATIVO" ou "Nenhum aplicativo Amplify encontrado."
3. **Given** que ocorre um erro de permissão ou falha na chamada AWS, **When** o comando é executado, **Then** a saída exibe uma mensagem de erro clara indicando o problema (ex: "Erro: sem permissão para listar Amplify apps").
4. **Given** que Amplify está ativo com múltiplos ambientes (produção, staging, dev), **When** o comando é executado, **Then** cada ambiente é listado com seu status (BRANCH, ACTIVE, BUILDING, etc.) e URL do deploy.

---

### Edge Cases

- **Conta sem Amplify habilitado**: A CLI deve retornar mensagem clara ("Amplify não está habilitado nesta conta/região").
- **Erro de credenciais**: Se as credenciais AWS não tiverem permissão para `amplify:ListApps`, exibir erro específico.
- **Timeout ou throttling**: Se a API do Amplify demorar ou sofrer rate limiting, exibir mensagem de timeout com sugestão de retry.
- **Região incorreta**: Se o Amplify estiver ativo em outra região que não a configurada, exibir mensagem orientativa.
- **Saída vazia**: Se a lista de apps for vazia, informar que Amplify está ativo mas sem aplicativos.

## Requirements

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um comando/script CLI que verifica o status do AWS Amplify na conta configurada.
- **FR-002**: O comando DEVE listar todos os aplicativos Amplify encontrados na região configurada.
- **FR-003**: Para cada aplicativo Amplify, o comando DEVE listar os ambientes (branches) com seu status atual (ACTIVE, BUILDING, FAILED, etc.).
- **FR-004**: Para cada ambiente, o comando DEVE exibir a URL do deploy e a data da última atualização.
- **FR-005**: O comando DEVE utilizar as credenciais AWS já configuradas no `.env` (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).
- **FR-006**: Em caso de erro (permissão, timeout, região inválida), o comando DEVE exibir uma mensagem de erro clara e amigável.
- **FR-007**: O comando DEVE ser executável via terminal sem depender do servidor HTTP do backend.

### Key Entities

- **Aplicativo Amplify**: Projeto Amplify contendo um ou mais ambientes (branches) com configurações de build e deploy.
- **Ambiente (Branch)**: Branch de um aplicativo Amplify, com status (ACTIVE, BUILDING, FAILED, etc.), URL de deploy e última atualização.
- **Credenciais AWS**: Access Key e Secret Key do arquivo `.env` usadas para autenticar as chamadas à API do Amplify.

## Success Criteria

### Measurable Outcomes

- **SC-001**: O comando de diagnóstico completa a execução em menos de 10 segundos (dependendo da latência da API AWS).
- **SC-002**: A saída do comando é auto-contida e legível, não exigindo consulta a documentação externa para interpretação.
- **SC-003**: Em cenários de erro, a mensagem indica claramente a causa e o próximo passo sugerido.
- **SC-004**: O comando pode ser executado sem necessidade do servidor backend rodando.

## Assumptions

- As credenciais AWS já estão configuradas no `.env` e têm permissão para `amplify:ListApps` e `amplify:ListBranches`.
- O SDK boto3 já está instalado como dependência do projeto.
- O Amplify pode ou não estar ativo na conta — o comando deve funcionar em ambos os casos.
- A saída será no terminal (stdout) em formato texto simples, sem necessidade de interface gráfica.
