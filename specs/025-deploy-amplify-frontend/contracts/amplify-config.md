# Contrato: AWS Amplify App Configuration

## App Settings

| Parâmetro | Valor Obrigatório |
|-----------|-------------------|
| App ID | `d2e6pwly2l3rt` |
| Nome | `radiante-final` |
| Repositório | `https://github.com/cunhagd/radiantev2` |
| Token de Acesso | GitHub PAT com escopos `repo` + `admin:repo_hook` |
| Plataforma | `WEB` |
| Domínio | `d2e6pwly2l3rt.amplifyapp.com` |
| Compute Type | `STANDARD_8GB` |

## Build Spec

```yaml
version: 1
applications:
  - frontend:
      phases:
        build:
          commands:
            - echo "window.API_BASE='$API_BASE';" > js/env.js
      artifacts:
        baseDirectory: /
        files:
          - '**/*'
      cache:
        paths: []
    appRoot: frontend
```

## Variáveis de Ambiente

| Chave | Valor | Obrigatório |
|-------|-------|-------------|
| `AMPLIFY_MONOREPO_APP_ROOT` | `frontend` | Sim |
| `AMPLIFY_DIFF_DEPLOY` | `false` | Sim |
| `API_BASE` | `http://18.208.190.159:8000` | Sim |

## Regras de Redirecionamento

```json
[
  {
    "source": "/<*>",
    "target": "/index.html",
    "status": "404-200"
  }
]
```

## Cache

```json
{
  "type": "AMPLIFY_MANAGED_NO_COOKIES"
}
```

## Branch Production

| Parâmetro | Valor |
|-----------|-------|
| Nome | `main` |
| Stage | `PRODUCTION` |
| Auto Build | Ativado |
