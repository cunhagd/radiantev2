# Data Model: Migracao de Autenticacao AWS

Nao ha novas entidades de dominio. As unicas "entidades" sao as variaveis de configuracao:

## Config

| Variavel | Origem | Uso | Obrigatoria |
|----------|--------|-----|-------------|
| `AWS_ACCESS_KEY_ID` | `.env` | Autenticacao S3 e Textract (boto3) | Sim (exceto EC2 com IAM Role) |
| `AWS_SECRET_ACCESS_KEY` | `.env` | Autenticacao S3 e Textract (boto3) | Sim (exceto EC2 com IAM Role) |
| `AWS_BEARER_TOKEN_BEDROCK` | `.env` | Autenticacao Bedrock Mantle (OpenAI SDK) | Sim |
| `REGION` | `.env` | Regiao AWS padrao | Sim (default: us-east-1) |

## Comportamento

- **EC2 (IAM Role)**: Se `AWS_ACCESS_KEY_ID` nao estiver no `.env`, o boto3 usara a cadeia padrao de credenciais (IMDS)
- **Bearer Token**: Usado exclusivamente no `api_key` do OpenAI SDK para Bedrock Mantle. Nunca usado no boto3.
- **Remocao do `os.environ`**: Apos ler do `.env` via `python-dotenv`, as variaveis DEVEM ser removidas do `os.environ` para evitar captura automatica pelo boto3.
