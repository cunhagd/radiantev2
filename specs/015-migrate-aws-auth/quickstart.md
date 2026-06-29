# Quickstart — Migracao de Autenticacao AWS

## Pre-requisitos

- Servidor rodando: `python dev.py` (sem `$env:AWS_PROFILE='radiante'`)
- `.env` configurado com:
  - `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`
  - `AWS_BEARER_TOKEN_BEDROCK`
  - `REGION=us-east-1`
- Profile SSO `radiante` **NAO** deve estar configurado ou ativo

## Cenarios de Validacao

### Cenario 1: S3 funciona sem SSO

1. Remova ou desative o profile SSO: `$env:AWS_PROFILE=''`
2. Inicie o servidor: `python dev.py`
3. Acesse `http://localhost:8000/api/status`
4. **Esperado**: Resposta 200 com `{"status": "ok"}` — servidor inicializou sem erros de autenticacao

### Cenario 2: Upload e analise funcionam

1. Faca upload de 1 documento via interface
2. Clique em "Analisar 1x"
3. Aguarde a conclusao
4. **Esperado**: Analise conclui com sucesso, PDF gerado em `data/relatorio_consolidado.pdf`

### Cenario 3: Bearer Token e usado para Bedrock

1. Verifique nos logs do servidor que nao ha mensagens de erro relacionadas a SigV4 ou AWS4Auth
2. **Esperado**: As chamadas ao Grok usam o Bearer Token, nao SigV4

### Cenario 4: EC2 continua funcionando

1. Em um ambiente com IAM Role (EC2), nao configure `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` no `.env`
2. Inicie o servidor
3. **Esperado**: O servidor autentica via IMDS (IAM Role) e funciona normalmente

### Cenario 5: Erro claro com credenciais invalidas

1. Coloque uma Access Key invalida no `.env`
2. Inicie o servidor
3. Faca upload de um documento
4. **Esperado**: Mensagem de erro clara sobre falha de autenticacao S3, sem crash
