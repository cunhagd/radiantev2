# Quickstart: Check Amplify Status (020)

## Pré-requisitos

- Projeto Radiante v2 clonado e configurado
- `.env` com `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `REGION`
- Python 3.14+
- `boto3` e `python-dotenv` instalados (já presentes no `requirements.txt` principal)

## Validação 1 — Script CLI funciona sem servidor backend

```powershell
cd C:\radiantev2
python scripts/check_amplify.py
```

**Resultado esperado**: Saída formatada no terminal com status do Amplify (ativo ou inativo) sem precisar iniciar o servidor HTTP.

---

## Validação 2 — Amplify ativo com aplicativos

Se a conta tiver aplicativos Amplify configurados:

```
=== AWS Amplify Status ===
Regiao: us-east-1
Status: ATIVO (1 aplicativo encontrado)

--- App: radiante-app ---
ID: d123456
Criado: 2024-06-01 12:00:00

  Ambientes:
  - main [PRODUCTION]  ATIVO   URL: https://main.d123456.amplifyapp.com
  - dev   [DEVELOPMENT] ATIVO  URL: https://dev.d123456.amplifyapp.com
```

---

## Validação 3 — Amplify inativo / sem aplicativos

Se a conta não tiver aplicativos Amplify:

```
=== AWS Amplify Status ===
Regiao: us-east-1
Status: INATIVO
Motivo: Nenhum aplicativo Amplify encontrado na regiao us-east-1.
```

---

## Validação 4 — Erro de credenciais

**Cenário**: `.env` com credenciais inválidas.

```
=== AWS Amplify Status ===
Erro: credenciais AWS invalidas ou expiradas.
```

---

## Validação 5 — Erro de permissão

**Cenário**: credenciais sem permissão para Amplify.

```
=== AWS Amplify Status ===
Erro: sem permissao para acessar o Amplify.
Verifique se as credenciais AWS tem a politica 'AmplifyFullAccess' ou similar.
```

---

## Detalhes da Implementação

| Item | Referência |
|------|------------|
| Contrato de saída CLI | [contracts/cli-output.md](contracts/cli-output.md) |
| Data Model | [data-model.md](data-model.md) |
| Pesquisa técnica | [research.md](research.md) |
