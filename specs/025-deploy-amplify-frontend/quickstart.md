# Quickstart — Deploy Frontend no Amplify

## Pré-requisitos

- AWS CLI configurada com credenciais do usuário `radiante-poc` (acesso ao Amplify)
- GitHub Personal Access Token com escopos `repo` + `admin:repo_hook`
- Acesso de owner ao repositório `github.com/cunhagd/radiantev2`
- Amplify GitHub App instalado na conta/organização

## Passo a Passo

### 1. Atualizar `frontend/js/api.js`

Adicionar suporte para `window.API_BASE` como fallback principal:

```js
(function () {
  const API_BASE = window.API_BASE || (
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? "http://localhost:8000"
      : "https://jtuuxek832.execute-api.us-east-1.amazonaws.com"
  );

  API.BASE = API_BASE;
  // ... resto do código existente
})();
```

### 2. Adicionar `js/env.js` no HTML

Inserir antes dos outros scripts no `frontend/index.html`:

```html
<!-- Env vars injetadas pelo Amplify -->
<script src="js/env.js"></script>
```

### 3. Commitar e fazer push

```bash
git add frontend/js/api.js frontend/index.html
git commit -m "feat: preparar frontend para deploy no Amplify"
git push origin main
```

### 4. Trocar repositório no Amplify

```bash
aws amplify update-app \
  --app-id d2e6pwly2l3rt \
  --repository https://github.com/cunhagd/radiantev2 \
  --access-token <SEU_GITHUB_PAT>
```

### 5. Atualizar build spec

```bash
aws amplify update-app \
  --app-id d2e6pwly2l3rt \
  --build-spec "version: 1
applications:
  - frontend:
      phases:
        build:
          commands:
            - echo \"window.API_BASE='\$API_BASE';\" > js/env.js
      artifacts:
        baseDirectory: /
        files:
          - '**/*'
      cache:
        paths: []
    appRoot: frontend"
```

### 6. Verificar variáveis de ambiente

```bash
# API_BASE já existe, mas vamos garantir
aws amplify update-app \
  --app-id d2e6pwly2l3rt \
  --environment-variables '{"AMPLIFY_MONOREPO_APP_ROOT":"frontend","AMPLIFY_DIFF_DEPLOY":"false","API_BASE":"http://18.208.190.159:8000"}'
```

### 7. Conectar branch main e ativar auto-build

```bash
# Criar/atualizar branch main
aws amplify create-branch \
  --app-id d2e6pwly2l3rt \
  --branch-name main \
  --stage PRODUCTION \
  --enable-auto-build
```

### 8. Verificar deploy

```bash
# Listar branches
aws amplify list-branches --app-id d2e6pwly2l3rt

# Verificar jobs
aws amplify list-jobs --app-id d2e6pwly2l3rt --branch-name main
```

## Validação

### Teste 1: Acessar o site

```
URL: https://d2e6pwly2l3rt.amplifyapp.com
Esperado: Página do Radiante v2 carrega sem erros no console
```

### Teste 2: Comunicação com backend

```
Abrir DevTools → Console
Esperado: Nenhum erro de rede (CORS, 404, conexão)
Checar: API.BASE deve apontar para http://18.208.190.159:8000
```

### Teste 3: Build automático

```
Fazer push na branch main → Verificar Amplify Console
Esperado: Build dispara automaticamente e conclui em < 5 min
```

## Rollback

Se algo der errado:

```bash
# Reverter para repositório anterior
aws amplify update-app \
  --app-id d2e6pwly2l3rt \
  --repository https://github.com/cunhagd/radiante-final \
  --access-token <TOKEN>
```

Ou, como alternativa mais segura, criar um novo app apontando para o repositório antigo e ajustar o DNS.
