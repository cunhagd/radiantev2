# Data Model: Check Amplify Status

## Entities

### Entity: Aplicativo Amplify (Amplify App)

Projeto Amplify contendo um ou mais ambientes.

| Campo | Tipo | Descrição | Fonte |
|-------|------|-----------|-------|
| `app_id` | `string` | ID único do aplicativo Amplify | `list_apps[].appId` |
| `name` | `string` | Nome do aplicativo | `list_apps[].name` |
| `description` | `string` | Descrição do aplicativo | `list_apps[].description` |
| `create_time` | `datetime` | Data de criação | `list_apps[].createTime` |
| `branches` | `list[Branch]` | Lista de ambientes/branches | `list_branches()` |

---

### Entity: Ambiente (Branch)

Branch de um aplicativo Amplify com status e URL de deploy.

| Campo | Tipo | Descrição | Fonte |
|-------|------|-----------|-------|
| `branch_name` | `string` | Nome da branch (ex: `main`, `develop`) | `list_branches[].branchName` |
| `stage` | `string` | Estágio: `PRODUCTION`, `STAGING`, `DEVELOPMENT` | `list_branches[].stage` |
| `status` | `string` | Status inferido: `ATIVO`, `BUILDING`, `FAILED`, `INATIVO` | Inferido de `activeJobId` |
| `deploy_url` | `string` | URL do deploy | Montado: `https://{branch}.{appId}.amplifyapp.com` |
| `last_update` | `datetime` | Data da última atualização | `list_branches[].createTime` |
| `has_active_job` | `bool` | Se há um build em andamento | `activeJobId` não vazio |

---

## Relationships

```mermaid
flowchart LR
    subgraph AWS[Conta AWS]
        AMP[Amplify Service] -->|list_apps| APP1[App: producao]
        AMP -->|list_apps| APP2[App: staging]
        APP1 -->|list_branches| B1[Branch: main]
        APP1 -->|list_branches| B2[Branch: develop]
        APP2 -->|list_branches| B3[Branch: main]
    end

    subgraph Script[scripts/check_amplify.py]
        CONFIG[Config (.env)] -->|credenciais| CLIENT[boto3 client amplify]
        CLIENT -->|list_apps + list_branches| OUTPUT[Saida formatada]
    end
```

---

## Estados

### Estado do Ambiente (Branch Status)

| Status | Descrição | Como detectar |
|--------|-----------|---------------|
| `ATIVO` | Branch com deploy concluído e sem build ativo | `activeJobId` vazio |
| `BUILDING` | Build em andamento | `activeJobId` não vazio |
| `FAILED` | Último build falhou | Requer chamada adicional `get_job()` — simplificado como ATIVO com observação |
| `INATIVO` | Branch sem deploy | Branch criada mas sem build concluído |
