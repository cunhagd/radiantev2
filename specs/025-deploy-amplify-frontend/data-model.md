# Data Model — Deploy Frontend no Amplify

## Amplify App Configuration

```json
{
  "appId": "d2e6pwly2l3rt",
  "name": "radiante-final",
  "repository": "https://github.com/cunhagd/radiantev2",
  "platform": "WEB",
  "defaultDomain": "d2e6pwly2l3rt.amplifyapp.com",
  "productionBranch": "main",
  "repositoryCloneMethod": "TOKEN",
  "buildSpec": "version: 1\napplications:\n  - frontend:\n      phases:\n        build:\n          commands:\n            - echo \"window.API_BASE='$API_BASE';\" > js/env.js\n      artifacts:\n        baseDirectory: /\n        files:\n          - '**/*'\n      cache:\n        paths: []\n    appRoot: frontend\n",
  "customRules": [
    {
      "source": "/<*>",
      "target": "/index.html",
      "status": "404-200"
    }
  ],
  "cacheConfig": {
    "type": "AMPLIFY_MANAGED_NO_COOKIES"
  },
  "environmentVariables": [
    { "key": "AMPLIFY_DIFF_DEPLOY", "value": "false" },
    { "key": "AMPLIFY_MONOREPO_APP_ROOT", "value": "frontend" },
    { "key": "API_BASE", "value": "http://18.208.190.159:8000" }
  ],
  "enableBranchAutoBuild": true,
  "enableBasicAuth": false
}
```

## Entity Relationship

```
GitHub Repository                    AWS Amplify App
(cunhagd/radiantev2) ────conecta────> d2e6pwly2l3rt
       │                                     │
       │ push                                │ gera
       ▼                                     ▼
  Branch: main ────────build────────> Frontend Estático
       │                              d2e6pwly2l3rt.amplifyapp.com
       │                                     │
       │ envia                              │ chama
       ▼                                     ▼
  GitHub Webhook ───────────► Amplify Build ──► Backend EC2
                                      18.208.190.159:8000
```

## Key Configuration Entities

### Environment Variables (Amplify App)

| Chave | Valor | Origem | Descrição |
|-------|-------|--------|-----------|
| `API_BASE` | `http://18.208.190.159:8000` | Configurada no Amplify | URL base do backend para chamadas AJAX |
| `AMPLIFY_MONOREPO_APP_ROOT` | `frontend` | Manter existente | Diretório raiz do frontend no monorepo |
| `AMPLIFY_DIFF_DEPLOY` | `false` | Manter existente | Desabilita deploy diferencial |

### Build Spec Commands

| Fase | Comando | Efeito |
|------|---------|--------|
| `build` | `echo "window.API_BASE='$API_BASE';" > js/env.js` | Gera `frontend/js/env.js` com a URL do backend injetada |

### Branch Configuration

| Propriedade | Valor |
|-------------|-------|
| `branchName` | `main` |
| `stage` | `PRODUCTION` |
| `enableAutoBuild` | `true` |

## State Transitions

### Deploy Flow

```
Push (main) → Webhook → Build Queued → Build In Progress → Build Succeeded → Site Updated
                  │                                    │
                  └── Webhook Error                    └── Build Failed → Logs Available
```

### Site Serving

```
Request → Amplify CDN → Cache Hit? → Serve Static Files
               │                        │
               └── Cache Miss ──────────┘
                        │
                     S3 Bucket
```
