# Feature Specification: Deploy Frontend no Amplify

**Feature Branch**: `025-deploy-amplify-frontend`

**Created**: 2026-06-30

**Status**: Draft

**Input**: User description: "Agora precisamos preparar o frontend para deploy no amplify da conta já conectado (cujo você irá conferir via cli ID da aplicação: d2e6pwly2l3rt). Subiremos tudo na mesma conta declarada em .env com AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY id da conta 406223549358. Trocar o repositório no Amplify para radiantev2."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configurar Amplify para o repositório radiantev2 (Priority: P1)

Como desenvolvedor do Radiante v2, quero que o Amplify aponte para o repositório `github.com/cunhagd/radiantev2` na branch `main` para que o frontend seja servido automaticamente a partir do código-fonte atual.

**Why this priority**: Sem essa configuração, o Amplify continua servindo o código antigo do repositório `radiante-final`, que não reflete as últimas alterações.

**Independent Test**: Após a configuração, um push na branch `main` do repositório `radiantev2` dispara automaticamente um build no Amplify e o resultado fica acessível em `d2e6pwly2l3rt.amplifyapp.com`.

**Acceptance Scenarios**:

1. **Given** que o Amplify está configurado com o repositório `radiantev2`, **When** faço um push na branch `main`, **Then** o Amplify inicia automaticamente um build com o código mais recente
2. **Given** que o build foi concluído com sucesso, **When** acesso `d2e6pwly2l3rt.amplifyapp.com`, **Then** vejo a interface do Radiante v2 com as últimas alterações do frontend

---

### User Story 2 - Atualizar API_BASE para o backend no EC2 (Priority: P1)

Como usuário do Radiante v2, quero que o frontend no Amplify se comunique corretamente com o backend rodando no EC2 (`18.208.190.159:8000`) para que uploads, análises e resultados funcionem em produção.

**Why this priority**: Sem o API_BASE correto, o frontend tentará se conectar a um endpoint antigo (API Gateway) e todas as operações falharão.

**Independent Test**: Após a atualização, o frontend hospedado no Amplify consegue fazer upload de documentos e listar resultados do backend no EC2.

**Acceptance Scenarios**:

1. **Given** que o frontend está servido pelo Amplify, **When** o JavaScript tenta se conectar ao backend, **Then** a URL base aponta para `http://18.208.190.159:8000`
2. **Given** que o backend EC2 está ativo, **When** o frontend faz uma requisição para `/api/status`, **Then** a resposta é bem-sucedida (HTTP 200)

---

### User Story 3 - Build automático via GitHub (Priority: P2)

Como desenvolvedor, quero que o Amplify faça deploy automático a cada push na branch `main` do repositório `radiantev2` para que as alterações no frontend entrem em produção sem intervenção manual.

**Why this priority**: Automação reduz risco de erro humano e acelera o ciclo de deploy.

**Independent Test**: Um commit na branch `main` com alteração no `frontend/` dispara build e o site atualizado fica disponível em menos de 5 minutos.

**Acceptance Scenarios**:

1. **Given** que o Amplify está conectado ao repositório `radiantev2`, **When** faço um commit e push na branch `main`, **Then** o Amplify detecta a mudança e inicia um novo build
2. **Given** que o build está em andamento, **When** verifico o status no console Amplify, **Then** vejo o progresso (pendente → em execução → bem-sucedido)
3. **Given** que um build falhou, **When** verifico os logs, **Then** consigo identificar o erro no console do Amplify

---

### Edge Cases

- O Amplify pode exigir reconexão do repositório GitHub, o que requer autorização OAuth do usuário dono do repositório
- A chave `AMPLIFY_MONOREPO_APP_ROOT` já está configurada como `frontend` — se o repositório mudar, é necessário verificar se o path continua correto
- O build spec atual copia todos os arquivos (`**/*`) — pode copiar `node_modules` se não houver exclusão adequada
- Durante a troca de repositório, pode haver um período sem frontend servido (downtime de alguns minutos)
- Se o webhook do GitHub não for recriado após a troca de repositório, builds automáticos não dispararão
- A API_BASE no `api.js` está hardcoded com fallback para API Gateway — precisa ser alterada para apontar para o EC2
- A branch `main` contém código diferente da branch `main-poc` que estava sendo usada — pode haver incompatibilidades

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O Amplify DEVE ser reconectado ao repositório GitHub `github.com/cunhagd/radiantev2` na branch `main`
- **FR-002**: O build spec do Amplify DEVE copiar todo o conteúdo da pasta `frontend/` como aplicação web estática
- **FR-003**: As variáveis de ambiente do Amplify DEVEM incluir `API_BASE` com o valor `http://18.208.190.159:8000`
- **FR-004**: A variável `AMPLIFY_MONOREPO_APP_ROOT` DEVE permanecer como `frontend`
- **FR-005**: O build automático (auto-build) DEVE estar habilitado para a branch `main`
- **FR-006**: O arquivo `frontend/js/api.js` DEVE ser atualizado para usar a variável de ambiente `API_BASE` quando disponível, com fallback para localhost em desenvolvimento
- **FR-007**: O domínio padrão `d2e6pwly2l3rt.amplifyapp.com` DEVE ser mantido
- **FR-008**: A regra de redirecionamento `(/<*>) → /index.html` com status `404-200` DEVE ser mantida para suporte a SPA
- **FR-009**: O frontend DEVE ser acessível publicamente via HTTPS no domínio do Amplify
- **FR-010**: O cache configurado como `AMPLIFY_MANAGED_NO_COOKIES` DEVE ser mantido

### Key Entities

- **Amplify App**: Recurso AWS Amplify que hospeda o frontend estático, com ID `d2e6pwly2l3rt` e nome `radiante-final`
- **Repositório GitHub**: `github.com/cunhagd/radiantev2` — fonte do código do frontend
- **Build Spec**: Configuração YAML que define como o Amplify faz o build e deploy
- **Variáveis de Ambiente**: Configurações injetadas no build, incluindo `API_BASE` e `AMPLIFY_MONOREPO_APP_ROOT`
- **EC2 Backend**: Instância `i-0df8ba5134b0e0b28` rodando o backend Python no IP `18.208.190.159:8000`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O frontend do Radiante v2 está acessível via HTTPS em `d2e6pwly2l3rt.amplifyapp.com` em menos de 10 minutos após o deploy
- **SC-002**: O frontend consegue se comunicar com o backend EC2 e exibir dados de análise corretamente
- **SC-003**: Um push na branch `main` dispara automaticamente um build que conclui em menos de 5 minutos
- **SC-004**: 100% das funcionalidades do frontend (upload, análise, visualização de cifras, download de PDF) funcionam no ambiente Amplify
- **SC-005**: Nenhum erro de CORS, roteamento ou conexão aparece no console do navegador ao acessar o site

## Assumptions

- O usuário `radiante-poc` (credenciais no `.env`) tem permissões suficientes para gerenciar o Amplify App
- O repositório `radiantev2` está acessível publicamente ou o usuário tem acesso para conectar ao Amplify
- A conexão Amplify-GitHub requer autorização OAuth — o usuário deve estar logado no GitHub com acesso ao repositório
- O backend EC2 continuará rodando no IP `18.208.190.159:8000` (ou será atualizado conforme necessário)
- A branch `main` contém o código frontend mais recente e estável para produção
- O Amplify já está configurado com as permissões adequadas de serviço (IAM service role)
