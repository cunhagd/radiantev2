# Research — Deploy Frontend no Amplify

## 1. Troca de Repositório no Amplify via CLI

### Comando AWS CLI

```
aws amplify update-app \
  --app-id d2e6pwly2l3rt \
  --repository https://github.com/cunhagd/radiantev2 \
  --access-token <GITHUB_PAT>
```

### Pré-requisitos

- **GitHub Personal Access Token (PAT)** com escopos:
  - `repo` (acesso total ao repositório)
  - `admin:repo_hook` (para criar/manter webhooks)
- O token deve ser criado pelo dono do repositório (`cunhagd`)
- O Amplify GitHub App **deve estar instalado** na organização/conta GitHub

### Comportamento Esperado

| Comportamento | Detalhes |
|---------------|----------|
| Webhook automático | O Amplify recria o webhook no novo repositório para builds automáticos |
| Build spec | Mantido do app anterior (precisa verificar) |
| Variáveis de ambiente | Mantidas do app anterior |
| Regras de redirecionamento | Mantidas do app anterior |
| Branch production | **Precisa ser atualizada** de `main-poc` para `main` |
| Downtime | Pode haver alguns minutos sem frontend servido durante a troca |

### Alternativa: Criar novo app

Caso o `update-app` não funcione (ex: erro de validação), a alternativa é:
- `aws amplify get-app --app-id d2e6pwly2l3rt` para capturar configurações
- `aws amplify create-app` com as mesmas configurações + novo repositório
- Isso requer recriar variáveis de ambiente, redirect rules e config

### Atualizar Branch Production

Após trocar o repositório, atualizar a branch de production:

```
aws amplify update-branch \
  --app-id d2e6pwly2l3rt \
  --branch-name main \
  --stage PRODUCTION
```

E também desabilitar auto-build na branch antiga se necessário.

---

## 2. Injeção de API_BASE no Frontend Estático

### Problema

O frontend estático (HTML/CSS/JS puro, sem bundler) não tem `process.env` ou mecanismo de build para substituir variáveis. O `api.js` atualmente hardcoda a URL do backend:

```js
const API_BASE = window.location.hostname === 'localhost'
  ? "http://localhost:8000"
  : "https://jtuuxek832.execute-api.us-east-1.amazonaws.com";
```

### Solução 1: Script de ambiente gerado no build (RECOMENDADO)

**Como funciona**: No build spec do Amplify, adicionar um comando que gera um arquivo JS com a variável de ambiente injetada:

```
# amplify.yml
frontend:
  phases:
    build:
      commands:
        - echo "window.API_BASE='$API_BASE';" > js/env.js
  artifacts:
    baseDirectory: /
    files:
      - '**/*'
```

**No `api.js`**: Adicionar verificação no início:

```js
const API_BASE = window.API_BASE || (
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://localhost:8000"
    : "https://jtuuxek832.execute-api.us-east-1.amazonaws.com"
);
```

**Vantagens**:
- Sempre atualizado no build
- Sem alteração no HTML
- Funciona para qualquer ambiente (local, produção)
- Fallback seguro se a env var não existir

### Solução 2: Substituição via sed no build spec

Alternativa usando substituição direta no `api.js` durante o build:

```
- sed -i "s|API_BASE_PLACEHOLDER|$API_BASE|g" js/api.js
```

**Desvantagem**: Modifica o source file, pode causar problemas de cache.

### Decisão

**Solução 1 é a recomendada** por ser mais limpa, sem modificar o código fonte e com fallback claro.

---

## 3. Configurações Atuais do Amplify App

Coletadas via `aws amplify get-app --app-id d2e6pwly2l3rt`:

| Configuração | Valor Atual |
|---|---|
| **App Name** | `radiante-final` |
| **Repositório** | `https://github.com/cunhagd/radiante-final` |
| **Repository Clone Method** | `TOKEN` (GitHub App) |
| **Platform** | `WEB` |
| **Default Domain** | `d2e6pwly2l3rt.amplifyapp.com` |
| **Production Branch** | `main-poc` |
| **Auto Build** | false (desabilitado no app level) |
| **Enable Basic Auth** | false |
| **Custom Rules** | `/{source<*>} → /index.html (404-200)` |
| **Cache Config** | `AMPLIFY_MANAGED_NO_COOKIES` |
| **Build Compute Type** | `STANDARD_8GB` |

### Variáveis de Ambiente Atuais

| Chave | Valor |
|---|---|
| `AMPLIFY_DIFF_DEPLOY` | `false` |
| `AMPLIFY_MONOREPO_APP_ROOT` | `frontend` |
| `API_BASE` | `http://18.208.190.159:8000` |

A variável `API_BASE` já está configurada no Amplify! Apenas precisamos usá-la no frontend.

### Build Spec Atual

```yaml
version: 1
applications:
  - frontend:
      phases:
        build:
          commands: []
      artifacts:
        baseDirectory: /
        files:
          - '**/*'
      cache:
        paths: []
    appRoot: frontend
```

**Observação**: O build spec atual não tem comandos de build. Precisamos adicionar o comando para gerar o `js/env.js`.

---

## 4. Permissões do Usuário AWS

O usuário `radiante-poc` tem permissões para Amplify (testado com sucesso via CLI). Porém:

- **Não tem** `ec2:DescribeInstances` (verificar EC2)
- **Não tem** `ssm:DescribeInstanceInformation` (verificar SSM)
- Permissões de Amplify (`amplify:*`) funcionam corretamente

**Ação**: Para esta feature, apenas Amplify é necessário — as permissões existentes são suficientes. Se precisar gerenciar a branch `main` no Amplify, pode ser necessário verificar permissões para `amplify:UpdateBranch`.

---

## 5. Estrutura de Branches no Amplify

| Branch Atual | Stage | Auto Build |
|---|---|---|
| `main-poc` | PRODUCTION | ✅ |

**Alteração necessária**:
1. Conectar a branch `main` do novo repositório
2. Opcional: definir `main` como PRODUCTION
3. Manter `main-poc` ou remover se não for mais necessário
