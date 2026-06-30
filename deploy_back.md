# Deploy do Backend — Radiante v2 (Single EC2)

## Visão Geral da Arquitetura

```
Usuario (navegador)
  │  https://radiante.emaster.info
  ▼
EC2 t3a.micro — porta 443 (HTTPS)
  ┌──────────────────────────────────────┐
  │  Nginx (container)                   │
  │  ├── / (arquivos estaticos)          │
  │  ├── /api/*  → proxy → backend:8000 │
  │  ├── /data/* → proxy → backend:8000 │
  │  └── SSL: Let's Encrypt (Certbot)    │
  ├──────────────────────────────────────┤
  │  Backend Python (container)          │
  │  ├── API HTTP na porta 8000          │
  │  ├── AWS Bedrock (Grok 4.3)          │
  │  ├── S3 (documentos, resultados)     │
  │  └── Textract (OCR)                  │
  └──────────────────────────────────────┘
```

## Pré-requisitos

| Item | Descricao |
|------|-----------|
| **Instancia EC2** | `i-0df8ba5134b0e0b28` (t3a.micro, Amazon Linux 2023) |
| **IAM Role** | Anexada a EC2 com permissoes para S3 (`radiante-final`), Bedrock, Textract |
| **Token Bedrock** | `AWS_BEARER_TOKEN_BEDROCK` no arquivo `.env` |
| **Dominio** | `radiante.emaster.info` (gerenciado no Route53 da conta AWS) |
| **Elastic IP** | IP publico fixo associado a EC2 |

## Fluxo de Configuracao

### 1. Elastic IP e DNS

Antes de configurar o HTTPS, a EC2 precisa de um IP publico fixo e o dominio deve apontar para ele.

**No console AWS:**

1. Acesse **EC2 > Elastic IPs > Allocar endereco IP**
2. Associe o Elastic IP a instancia `i-0df8ba5134b0e0b28`
3. Acesse **Route53 > Hosted zones > radiante.emaster.info**
4. Crie um registro **A**:
   ```
   radiante.emaster.info  A  →  [Elastic IP]
   ```
5. Remova registros antigos (CNAME do ALB, se existir)

### 2. Conectar via Session Manager

```bash
aws ssm start-session --target i-0df8ba5134b0e0b28 --region us-east-1
```

### 3. Setup do Ambiente

```bash
cd /tmp
wget -q https://raw.githubusercontent.com/cunhagd/radiantev2/main/dpbc.py
sudo python3 dpbc.py --setup
```

O script vai pedir para criar o arquivo `.env`. Siga as instrucoes e rode `--setup` novamente.

### 4. Arquivo .env

Criar em `/opt/radiante/.env`:

```bash
sudo bash -c 'cat > /opt/radiante/.env << "EOF"
REGION=us-east-1
BEDROCK_MODEL_ID=xai.grok-4.3
AWS_BEARER_TOKEN_BEDROCK=<seu-token-bedrock>
AWS_ACCESS_KEY_ID=<sua-access-key>
AWS_SECRET_ACCESS_KEY=<sua-secret-key>
BUCKET_NAME=radiante-final
GROK_PRICE_INPUT=1.25
GROK_PRICE_OUTPUT=2.50
GROK_PRICE_CACHE_READ=0.20
GROK_REASONING_EFFORT=xhigh
EOF'
```

Apos criar, execute `--setup` novamente:

```bash
sudo python3 dpbc.py --setup
```

### 5. HTTPS com Let's Encrypt (Certbot)

> **Importante:** O DNS `radiante.emaster.info` ja deve estar apontando para o Elastic IP da EC2 antes de executar este passo.

```bash
sudo python3 dpbc.py --ssl
```

O que o comando faz:

1. Instala Certbot na EC2
2. Para o container Nginx temporariamente
3. Obtem certificado SSL para `radiante.emaster.info` (modo standalone)
4. Copia os certificados para o volume Docker
5. Sobe os containers com HTTPS ativo
6. Agenda renovacao automatica (cron, 03:00 diario via webroot)

### 6. Verificacao

```bash
# Health check completo (via Nginx)
curl -I http://localhost/api/status

# Via HTTPS
curl -k https://localhost/api/status

# Via dominio publico
curl -I https://radiante.emaster.info/api/status

# Status geral
sudo python3 dpbc.py --status
```

Resultado esperado:

```json
{"status": "idle", "message": "", "error_details": "", "last_result": null}
```

## Manutencao

### Atualizar backend

```bash
cd /opt/radiante
sudo python3 dpbc.py --update
```

O comando faz `git pull`, rebuild do backend e restart sem derrubar o Nginx.

### Ver status

```bash
sudo python3 dpbc.py --status
```

Exibe: containers rodando, health check, HTTPS, systemd, disco, uptime.

### Logs em tempo real

```bash
sudo python3 dpbc.py --logs
```

### Renovacao do certificado SSL

A renovacao e automatica (cron diario as 03:00). Para renovar manualmente:

```bash
sudo certbot renew --webroot -w /opt/radiante/certs-webroot
docker exec radiante-frontend nginx -s reload
```

### Parar tudo

```bash
cd /opt/radiante
docker compose down
```

### Atualizar dpbc.py na EC2

```bash
cd /tmp
wget -q -O dpbc.py https://raw.githubusercontent.com/cunhagd/radiantev2/main/dpbc.py
sudo cp dpbc.py /opt/radiante/dpbc.py
```

## Solucao de Problemas

### Nginx nao sobe com HTTPS

Verifique se os certificados existem:

```bash
ls -la /opt/radiante/certs/letsencrypt/live/radiante.emaster.info/
```

Se estiver vazio, execute:

```bash
sudo python3 dpbc.py --ssl
```

### Health check falha

```bash
# Testar backend direto
curl http://localhost:8000/api/status

# Testar via Nginx
curl http://localhost/api/status

# Ver logs do backend
cd /opt/radiante && docker compose logs backend --tail=30
```

### CORS

Se houver erros de CORS no navegador, verifique se o backend esta respondendo com os headers corretos:

```bash
curl -I -X OPTIONS -H "Origin: https://radiante.emaster.info" -H "Access-Control-Request-Method: POST" http://localhost:8000/api/status
```

Deve retornar `Access-Control-Allow-Origin: *`.

### Erro de conexao com S3

Verifique se a IAM Role da EC2 tem as permissoes necessarias:

```bash
aws sts get-caller-identity
aws s3 ls s3://radiante-final/
```

## Comandos Rapidos

| Comando | Descricao |
|---------|-----------|
| `sudo python3 dpbc.py --setup` | Configurar ambiente do zero |
| `sudo python3 dpbc.py --ssl` | Configurar HTTPS (Certbot) |
| `sudo python3 dpbc.py --update` | Atualizar backend |
| `sudo python3 dpbc.py --status` | Ver status dos servicos |
| `sudo python3 dpbc.py --logs` | Ver logs em tempo real |
| `docker compose logs -f` | Logs dos containers |
| `docker compose down` | Parar tudo |
| `sudo systemctl stop radiante-backend` | Parar servico systemd |
| `sudo systemctl start radiante-backend` | Iniciar servico systemd |
