# Research: Check Amplify Status

## Visão Geral

Pesquisa sobre como implementar um script CLI para verificar o status do AWS Amplify na conta configurada.

---

## R1: Como criar o cliente boto3 para Amplify?

### Decisão
Criar o cliente `amplify` do boto3 usando as mesmas credenciais do `.env` que o resto do projeto utiliza (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION). Reutilizar o mecanismo de `Config` de `backend/config.py`.

### Racional
- O projeto já possui `Config` e `_load_env()` que carregam e isolam as credenciais AWS
- FR-005 exige explicitamente reutilizar as credenciais do `.env`
- Segue o Princípio II da Constituição (isolamento de credenciais)
- O cliente boto3 para Amplify é `boto3.client("amplify", ...)` com os mesmos parâmetros

### Alternativas Consideradas
- **AWSCLI via subprocess**: Mais frágil, depende de instalação externa, parsing de JSON complexo. Rejeitado.

---

## R2: Quais chamadas AWS Amplify são necessárias?

### Decisão
Usar duas chamadas da API Amplify:
1. `amplify.list_apps()` — lista todos os aplicativos Amplify na região
2. Para cada app, `amplify.list_branches(appId=app_id)` — lista ambientes/branches com status

### Racional
- `list_apps` retorna `apps[]` com `appId`, `name`, `description`, `createTime`
- `list_branches` retorna `branches[]` com `branchName`, `displayName`, `stage` (PRODUCTION, STAGING, DEVELOPMENT), `activeJobId`, `buildSpec`, `createTime`, `environmentVariables`
- O status do ambiente pode ser inferido por `activeJobId` (se vazio, sem build ativo; se preenchido, build em andamento)
- Para URL de deploy, cada branch tem `branchName` e podemos montar a URL no formato `https://{branch}.{appId}.amplifyapp.com`

### Alternativas Consideradas
- **`amplify.get_app()`**: Apenas para app específico, não para listagem geral. Rejeitado.
- **`amplify.list_jobs()`**: Para status de build detalhado, mas adiciona complexidade desnecessária para um diagnóstico rápido.

---

## R3: Formato de saída no terminal?

### Decisão
Texto simples formatado com seções e indentação. Exemplo:

```
=== AWS Amplify Status ===
Regiao: us-east-1
Status: ATIVO (2 aplicativos encontrados)

--- App: meu-app-producao ---
ID: d123456
Criado: 2024-01-15 10:30:00

  Ambientes:
  - main [PRODUCTION]  ATIVO  URL: https://main.d123456.amplifyapp.com
  - develop [DEVELOPMENT]  ATIVO  URL: https://develop.d123456.amplifyapp.com

--- App: meu-app-staging ---
ID: d789012
Criado: 2024-03-20 14:00:00

  Ambientes:
  - staging [PRODUCTION]  BUILDING  URL: https://staging.d789012.amplifyapp.com
```

### Racional
- Formato legível e auto-contido (SC-002)
- Fácil de parsear visualmente
- Cores/sem formatação especial — funciona em qualquer terminal

### Alternativas Consideradas
- **JSON output**: Útil para machine reading, mas o requisito é diagnóstico humano. Rejeitado.
- **Tabela formatada**: Mais complexo de implementar, ganho marginal. Rejeitado.

---

## R4: Tratamento de erros

### Decisão
Capturar exceções específicas do boto3 e exibir mensagens amigáveis:

| Erro | Mensagem |
|------|----------|
| `ClientError` com código `AccessDeniedException` | "Erro: sem permissão para acessar o Amplify. Verifique as permissões da AWS." |
| `ClientError` com código `UnrecognizedClientException` | "Erro: credenciais AWS inválidas ou expiradas." |
| `EndpointConnectionError` / `ConnectTimeoutError` | "Erro: não foi possível conectar à AWS. Verifique sua conexão de rede." |
| Qualquer outro | "Erro inesperado: {mensagem}. Verifique o console AWS para mais detalhes." |

### Racional
- FR-006 exige mensagens de erro claras
- Cada tipo de erro mapeado para uma mensagem que indica a causa e sugere próximo passo (SC-003)
- Tratamento genérico como fallback para erros imprevistos

### Alternativas Consideradas
- **Deixar o boto3 lançar a exceção crua**: Mensagem técnica e pouco amigável. Rejeitado.

---

## Resumo das Decisões

| # | Decisão | Arquivo | Impacto |
|---|---------|---------|---------|
| R1 | Cliente boto3 Amplify com credenciais do Config | `scripts/check_amplify.py` | ~10 linhas |
| R2 | `list_apps()` + `list_branches()` | `scripts/check_amplify.py` | ~15 linhas |
| R3 | Saída em texto simples formatado | `scripts/check_amplify.py` | ~30 linhas |
| R4 | Tratamento de erros com mensagens amigáveis | `scripts/check_amplify.py` | ~20 linhas |
