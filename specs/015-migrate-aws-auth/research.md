# Research: Migracao de Autenticacao AWS

## Decisions

### 1. Metodo de autenticacao para S3 e Textract

- **Decision**: Usar `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` do `.env` passadas explicitamente nos clientes boto3
- **Rationale**: Credenciais IAM de usuario sao permanentes (nao expiram como SSO). Passar explicitamente evita conflito com IMDS da EC2 e segue o Principio II da Constitution.
- **Alternatives considered**:
  - Profile SSO `radiante`: Rejeitado porque expira a cada 8h e exige `aws sso login`
  - Variaveis de ambiente `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` no `os.environ`: Rejeitado porque conflita com IMDS da EC2 (Principio II exige remover do `os.environ`)

### 2. Metodo de autenticacao para Bedrock Mantle (Grok)

- **Decision**: Usar `AWS_BEARER_TOKEN_BEDROCK` do `.env` como API Key do OpenAI SDK
- **Rationale**: O SDK OpenAI aceita `api_key` diretamente. Bearer Token e o metodo recomendado pela AWS para Bedrock Mantle, sem necessidade de SigV4.
- **Alternatives considered**:
  - AWS SigV4 com Access Keys: Rejeitado porque o token Bearer e mais simples e especifico do Mantle
  - AWS SigV4 com SSO: Rejeitado pelo mesmo motivo — SSO expira

### 3. Remocao do profile SSO

- **Decision**: Remover toda dependencia de `AWS_PROFILE=radiante` do codigo e documentacao
- **Rationale**: Elimina ponto de falha (sessao expirada) e simplifica configuracao
- **Alternatives considered**:
  - Manter SSO como fallback: Rejeitado por complexidade desnecessaria

### 4. Compatibilidade com EC2 (IAM Role)

- **Decision**: Se `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` nao estiverem no `.env`, o boto3 usara a cadeia padrao (IMDS da EC2)
- **Rationale**: EC2 com IAM Role nao precisa de chaves fixas. O `.env` de producao nao deve conter essas variaveis.
- **Alternatives considered**: N/A — e o comportamento padrao do boto3

### 5. Format do `.env`

- **Decision**: Documentar tres variaveis obrigatorias: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_BEARER_TOKEN_BEDROCK`
- **Rationale**: Clareza na configuracao. Cada servico com seu metodo de autenticacao.
- **Alternatives considered**: N/A
