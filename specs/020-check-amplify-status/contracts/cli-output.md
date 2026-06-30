# Contract: CLI `check_amplify.py`

## Interface

**Comando**: `python scripts/check_amplify.py`

**Tipo**: Script CLI standalone

**Dependências externas**: Nenhuma — usa `boto3` + `python-dotenv` já instalados

---

## Comportamento

### Fluxo Principal

```
1. Carregar credenciais do .env (via Config)
2. Criar cliente boto3 amplify
3. Chamar amplify.list_apps()
4. Se lista vazia:
     Exibir "Amplify: INATIVO (nenhum aplicativo encontrado na regiao {regiao})"
     Exit code 0
5. Para cada app:
     Exibir nome, ID, data de criacao
     Chamar amplify.list_branches(appId=app.app_id)
     Para cada branch:
       Exibir nome, stage, status, URL, ultima atualizacao
6. Exit code 0
```

### Fluxo de Erro

| Cenário | Saída | Exit Code |
|---------|-------|-----------|
| Credenciais AWS não encontradas no `.env` | `"Erro: credenciais AWS nao encontradas no .env"` | 1 |
| `AccessDeniedException` | `"Erro: sem permissao para acessar Amplify"` | 1 |
| `UnrecognizedClientException` | `"Erro: credenciais AWS invalidas ou expiradas"` | 1 |
| `EndpointConnectionError` / `ConnectTimeoutError` | `"Erro: nao foi possivel conectar a AWS"` | 1 |
| Exceção genérica | `"Erro inesperado: {mensagem}"` | 1 |

---

## Formato de Saída

```
=== AWS Amplify Status ===
Regiao: us-east-1
Status: ATIVO (2 aplicativos encontrados)

--- App: meu-app-producao ---
ID: d123456
Criado: 2024-01-15 10:30:00

  Ambientes:
  - main [PRODUCTION]  ATIVO       URL: https://main.d123456.amplifyapp.com
  - dev   [DEVELOPMENT] BUILDING   URL: https://dev.d123456.amplifyapp.com

--- App: meu-app-staging ---
ID: d789012
Criado: 2024-03-20 14:00:00

  Ambientes:
  - staging [PRODUCTION] ATIVO     URL: https://staging.d789012.amplifyapp.com
```

### Caso inativo

```
=== AWS Amplify Status ===
Regiao: us-east-1
Status: INATIVO
Motivo: Nenhum aplicativo Amplify encontrado na regiao us-east-1.
```

### Caso erro de permissão

```
=== AWS Amplify Status ===
Erro: sem permissao para acessar o Amplify.
Verifique se as credenciais AWS tem a politica 'AmplifyFullAccess' ou similar.
```
