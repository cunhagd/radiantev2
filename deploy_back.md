# Guia de Deploy do Backend na EC2 — Radiante v2

> **Objetivo**: Provisionar o backend Python + Nginx na instância EC2 `i-0df8ba5134b0e0b28` usando o **Console AWS** (via navegador).

---

## Índice

1. [Visão Geral da Arquitetura](#1-visão-geral-da-arquitetura)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Passo 1: Conectar na EC2 via Session Manager](#3-passo-1-conectar-na-ec2-via-session-manager)
4. [Passo 2: Criar diretório e baixar arquivos do projeto](#4-passo-2-criar-diretório-e-baixar-arquivos-do-projeto)
5. [Passo 3: Configurar o arquivo .env](#5-passo-3-configurar-o-arquivo-env)
6. [Passo 4: Autenticar no ECR e fazer pull das imagens](#6-passo-4-autenticar-no-ecr-e-fazer-pull-das-imagens)
7. [Passo 5: Subir os containers com Docker Compose](#7-passo-5-subir-os-containers-com-docker-compose)
8. [Passo 6: Verificar se está funcionando](#8-passo-6-verificar-se-está-funcionando)
9. [Passo 7: Configurar restart automático (systemd)](#9-passo-7-configurar-restart-automático-systemd)
10. [Passo 8: Testar o frontend pelo Amplify](#10-passo-8-testar-o-frontend-pelo-amplify)
11. [Manutenção e Comandos Úteis](#11-manutenção-e-comandos-úteis)
12. [Solução de Problemas](#12-solução-de-problemas)

---

## 1. Visão Geral da Arquitetura

```
🌐 Usuário
    │
    ▼
┌─────────────────────────────────────┐
│  Amplify (Frontend Estático)        │
│  https://radiante.emaster.info/     │
│  HTML + CSS + JS                   │
└──────────┬──────────────────────────┘
           │ Chamadas API (AJAX / Fetch)
           ▼
┌─────────────────────────────────────┐
│  EC2 (t3a.micro — instância atual)  │
│                                     │
│  ┌──────────┐   ┌──────────────┐   │
│  │  Nginx   │──▶│  Backend     │   │
│  │  porta 80│   │  Python      │   │
│  │  (proxy) │   │  porta 8000  │   │
│  └──────────┘   └──────┬───────┘   │
│                         │           │
└─────────────────────────┼───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  AWS Bedrock (Grok)   │
              │  S3 (documentos)      │
              │  Textract            │
              └───────────────────────┘
```

**Como os containers se comunicam:**
- **Nginx** (porta 80) recebe as requisições e serve os arquivos estáticos ou redireciona para o backend
- **Backend Python** (porta 8000) processa as APIs, integra com Bedrock/Grok, S3 e Textract
- O `docker-compose.yml` orquestra os dois containers

---

## 2. Pré-requisitos

Antes de começar, verifique se você tem:

- ✅ Acesso ao **Console AWS** (https://console.aws.amazon.com)
- ✅ Conta AWS: `406223549358`
- ✅ Região: **us-east-1** (Norte da Virgínia)
- ✅ Instância EC2: `i-0df8ba5134b0e0b28` rodando
- ✅ **IAM Role** na EC2 com permissões para:
  - `AmazonSSMManagedInstanceCore` (para Session Manager funcionar)
  - `AmazonEC2ContainerRegistryReadOnly` (para baixar imagens do ECR)
  - Acesso ao S3 (`radiante-final`)
  - Acesso ao Bedrock
- ✅ Token do Bedrock Mantle (está no seu `.env` local como `AWS_BEARER_TOKEN_BEDROCK`)
- ✅ Sua instância já tem Docker e Docker Compose instalados

> ⚠️ A EC2 está em uma **subnet privada** — você NÃO consegue acessar via SSH diretamente.
> O acesso é feito exclusivamente via **AWS Systems Manager (SSM) Session Manager**.

---

## 3. Passo 1: Conectar na EC2 via Session Manager

O Session Manager permite abrir um terminal da EC2 diretamente pelo navegador, **sem precisar de SSH, sem abrir portas, sem bastion host**.

### 3.1 — Acessar o Console do Systems Manager

1. Abra o navegador em: https://console.aws.amazon.com/systems-manager/
2. Confirme que está na região **us-east-1** (canto superior direito)
3. No menu lateral esquerdo, clique em **Session Manager**

![Navegação Session Manager]*(imagem mental: menu esquerdo > Session Manager)*

### 3.2 — Iniciar uma sessão

1. Clique no botão **"Start session"** (laranja/azul)
2. Na lista de instâncias, localize: **`i-0df8ba5134b0e0b28`**
3. Clique no **radio button** ao lado dela
4. Clique em **"Start session"** no rodapé

> ✅ Você verá um terminal preto estilo Linux pronto para digitar comandos!

### 3.3 — Testar se a conexão está ok

Digite no terminal da sessão:

```bash
whoami
```

Deverá retornar algo como `ssm-user` ou `ec2-user`.

```bash
docker --version
docker compose version
```

Se ambos mostrarem versões, está tudo certo para prosseguir.

---

## 4. Passo 2: Criar diretório e baixar arquivos do projeto

Agora vamos criar a estrutura de diretórios e baixar os arquivos necessários.

### 4.1 — Criar o diretório da aplicação

```bash
sudo mkdir -p /opt/radiante
sudo chown ssm-user:ssm-user /opt/radiante
cd /opt/radiante
```

> `/opt/radiante` é o diretório padrão definido nos scripts de deploy.

### 4.2 — Download dos arquivos necessários

Você tem duas opções:

#### ✅ Opção A (recomendada): Baixar direto do GitHub

```bash
# Baixar docker-compose.yml
curl -o docker-compose.yml \
  https://raw.githubusercontent.com/cunhagd/radiantev2/main/docker-compose.yml

# Baixar nginx.conf
mkdir -p infra/nginx
curl -o infra/nginx/nginx.conf \
  https://raw.githubusercontent.com/cunhagd/radiantev2/main/infra/nginx/nginx.conf

# Baixar Dockerfile do nginx
curl -o infra/nginx/Dockerfile \
  https://raw.githubusercontent.com/cunhagd/radiantev2/main/infra/nginx/Dockerfile
```

#### Opção B: Fazer git clone completo (se preferir)

```bash
sudo yum install -y git  # se não tiver git
git clone https://github.com/cunhagd/radiantev2.git /opt/radiante-tmp
cp /opt/radiante-tmp/docker-compose.yml /opt/radiante/
cp -r /opt/radiante-tmp/infra /opt/radiante/
rm -rf /opt/radiante-tmp
```

### 4.3 — Verificar se os arquivos estão lá

```bash
ls -la /opt/radiante/
```

Deverá ver pelo menos: `docker-compose.yml` e a pasta `infra/`.

---

## 5. Passo 3: Configurar o arquivo .env

Este é o passo **mais importante** e **sensível**. O `.env` contém as credenciais que o backend precisa para funcionar.

> ⚠️ **NUNCA** coloque credenciais reais em arquivos versionados no GitHub.

### 5.1 — Criar o .env

```bash
cat > /opt/radiante/.env << 'ENVEOF'
# AWS - IAM Role da instancia EC2 fornece credenciais automaticamente
AWS_REGION=us-east-1

# Bearer Token do Bedrock Mantle (Grok 4.3)
AWS_BEARER_TOKEN_BEDROCK=ABSKTWFudGxlQXBpS2V5LThkNXU1bWVkLWF0LTQwNjIyMzU0OTM1ODp6OURMelVaMUJkRURWblk3eDdBaHl1c05pMU9oclY2bnpoNFZsNjBMNFVyRjJDQ0MzZGJHb2NSQlNuVT0=

# Modelo de IA
BEDROCK_MODEL_ID=xai.grok-4.3

# Bucket S3
BUCKET_NAME=radiante-final

# Precificacao Grok (preencher conforme fatura AWS)
GROK_PRICE_INPUT=1.25
GROK_PRICE_OUTPUT=2.50
GROK_PRICE_CACHE_READ=0.20
GROK_REASONING_EFFORT=xhigh
ENVEOF
```

> **Importante**: O token `AWS_BEARER_TOKEN_BEDROCK` acima é o mesmo que está no seu `.env` local. Ele é necessário para chamar o modelo Grok 4.3 via Bedrock Mantle.
>
> Na EC2, **não** precisa de `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` — a IAM Role da instância fornece essas credenciais automaticamente via IMDS.

### 5.2 — Proteger o arquivo

```bash
chmod 600 /opt/radiante/.env
```

Isso garante que apenas o dono do arquivo possa ler.

---

## 6. Passo 4: Autenticar no ECR e fazer pull das imagens

O ECR (Elastic Container Registry) é o "Docker Hub" da AWS. As imagens dos containers precisam ser baixadas de lá.

### 6.1 — Autenticar no ECR

```bash
# Descobrir o ID da conta automaticamente
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Fazer login no ECR
aws ecr get-login-password --region us-east-1 | \
  sudo docker login --username AWS --password-stdin \
  "$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"
```

> Se aparecer `Login Succeeded` — ótimo! A IAM Role tem permissão de leitura no ECR.

### 6.2 — Fazer pull das imagens

```bash
# Puxar a imagem mais recente do backend
sudo docker pull $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/radiante-backend:latest

# Puxar a imagem mais recente do nginx
sudo docker pull $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/radiante-nginx:latest
```

### 6.3 — Verificar se as imagens foram baixadas

```bash
sudo docker images
```

Deverá ver duas imagens: `radiante-backend` e `radiante-nginx`.

> ℹ️ **E se o ECR estiver vazio (nenhuma imagem)?**
>
> As imagens são criadas automaticamente pelo GitHub Actions (CI/CD) quando você faz push na branch `main`. Se estiver vazio, você precisa:
> 1. Configurar os Secrets no GitHub (explicado no Apêndice)
> 2. Fazer um push na `main` para disparar o pipeline
>
> **Alternativa**: Você pode fazer o build manualmente na própria EC2 (veja Seção 12 — Solução de Problemas).

---

## 7. Passo 5: Subir os containers com Docker Compose

Agora vamos iniciar os containers.

### 7.1 — Subir os serviços

```bash
cd /opt/radiante
sudo docker compose up -d --remove-orphans
```

**Explicação dos parâmetros:**
- `up` — Cria e inicia os containers
- `-d` — Modo "detached" (roda em segundo plano)
- `--remove-orphans` — Remove containers antigos que não estão mais no compose

### 7.2 — Verificar se os containers estão rodando

```bash
sudo docker compose ps
```

Deverá ver algo como:

```
NAME                IMAGE                                          STATUS         PORTS
radiante-backend    XXXX.dkr.ecr.us-east-1.amazonaws.com/radiante-backend:latest   Up 5 minutes   0.0.0.0:8000->8000/tcp
radiante-frontend   XXXX.dkr.ecr.us-east-1.amazonaws.com/radiante-nginx:latest     Up 5 minutes   0.0.0.0:80->80/tcp
```

Ambos devem estar com status **"Up"**.

### 7.3 — Ver logs (se algo der errado)

```bash
sudo docker compose logs --tail=50
```

Para ver logs de um serviço específico:

```bash
sudo docker compose logs backend --tail=50
sudo docker compose logs frontend --tail=50
```

---

## 8. Passo 6: Verificar se está funcionando

Vamos fazer os health checks manualmente para garantir que está tudo operacional.

### 8.1 — Testar o health check do Nginx

```bash
curl -s http://localhost:80/health
```

Deverá retornar: `healthy`

### 8.2 — Testar a API do backend (via Nginx)

```bash
curl -s http://localhost:80/api/status
```

Deverá retornar um JSON como:

```json
{"status":"idle","message":"","error_details":"","last_result":null}
```

### 8.3 — Testar o backend diretamente

```bash
curl -s http://localhost:8000/api/status
```

Também deve retornar o mesmo JSON acima.

### 8.4 — Verificar as variáveis de ambiente

```bash
sudo docker compose exec backend env | grep -E "AWS|BEDROCK|BUCKET|GROK"
```

Confirme que o `AWS_BEARER_TOKEN_BEDROCK` aparece com o valor correto.

---

## 9. Passo 7: Configurar restart automático (systemd)

Para garantir que o backend suba sozinho caso a EC2 reinicie (ex: manutenção da AWS, falha de hardware), vamos configurar um serviço systemd.

```bash
sudo tee /etc/systemd/system/radiante.service > /dev/null << 'SVC'
[Unit]
Description=Radiante v2
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/docker compose -f /opt/radiante/docker-compose.yml up -d --remove-orphans
ExecStop=/usr/bin/docker compose -f /opt/radiante/docker-compose.yml down
ExecReload=/usr/bin/docker compose -f /opt/radiante/docker-compose.yml pull && /usr/bin/docker compose -f /opt/radiante/docker-compose.yml up -d --remove-orphans
WorkingDirectory=/opt/radiante
User=root

[Install]
WantedBy=multi-user.target
SVC
```

```bash
# Recarregar o systemd
sudo systemctl daemon-reload

# Habilitar para iniciar com o sistema
sudo systemctl enable radiante.service

# Verificar status
sudo systemctl status radiante.service
```

> Isso garante que, se a EC2 reiniciar, o Docker Compose será executado automaticamente e seus containers voltarão a funcionar.

---

## 10. Passo 8: Testar o frontend pelo Amplify

Agora que o backend está rodando na EC2, vamos confirmar que o frontend no Amplify consegue se comunicar com ele.

### 10.1 — Verificar a URL da API no Amplify

1. Acesse o Console do Amplify: https://console.aws.amazon.com/amplify/
2. Clique no app **Radiante v2** (`d2e6pwly2l3rt`)
3. No menu esquerdo, vá em **Environment variables**
4. Confirme que existe: `API_BASE = http://18.208.190.159:8000`

> 💡 **Dica**: Se o IP público da EC2 mudar (após stop/start), você precisará atualizar essa variável e fazer um novo build no Amplify.

### 10.2 — Forçar um novo build (se necessário)

Se você acabou de atualizar a variável:

1. Vá em **Branch management** (menu esquerdo)
2. Na branch **main**, clique nos três pontos `⋮` > **Redeploy**
3. Aguarde o build (cerca de 2-3 minutos)

### 10.3 — Testar o fluxo completo

1. Acesse: https://radiante.emaster.info/
2. Faça upload de um documento PDF
3. Clique em **"Rodar 1x"** ou **"Rodar 10x"**
4. Acompanhe o progresso — as chamadas API devem chegar na EC2

---

## 11. Manutenção e Comandos Úteis

### 11.1 — Atualizar o backend (manual)

Se você fez alterações no código e quer atualizar manualmente (sem o CI/CD):

```bash
cd /opt/radiante

# Autenticar no ECR
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region us-east-1 | \
  sudo docker login --username AWS --password-stdin \
  "$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"

# Puxar imagens novas
sudo docker compose pull

# Recriar containers
sudo docker compose up -d --remove-orphans
```

### 11.2 — Ver logs em tempo real

```bash
cd /opt/radiante
sudo docker compose logs -f
```

- Pressione `Ctrl + C` para sair

### 11.3 — Parar e remover containers

```bash
cd /opt/radiante
sudo docker compose down
```

### 11.4 — Verificar uso de recursos

```bash
# Uso de disco
df -h /

# Uso de memoria dos containers
sudo docker stats --no-stream
```

### 11.5 — Limpar imagens antigas

```bash
# Remove imagens não usadas há mais de 24h
sudo docker image prune -a -f --filter "until=24h"
```

---

## 12. Solução de Problemas

### ❌ "docker: command not found"

O Docker não está instalado. Instale com:

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ssm-user
```

> Depois, desconecte e reconecte a sessão SSM.

### ❌ "docker compose: command not found"

```bash
sudo yum install -y docker-compose-plugin
```

### ❌ "Cannot connect to the Docker daemon"

```bash
# Verificar se o daemon está rodando
sudo systemctl status docker

# Iniciar se parado
sudo systemctl start docker
```

### ❌ ECR retorna "Repository not found" no pull

Os repositórios ECR ainda não existem. Crie no Console AWS:

1. Acesse: https://console.aws.amazon.com/ecr/
2. Clique em **"Create repository"**
3. Crie dois repositórios:
   - **`radiante-backend`** — visibilidade: private
   - **`radiante-nginx`** — visibilidade: private

Depois siga para a seção de **Build manual das imagens** abaixo.

### ❌ ECR existe mas está vazio (sem imagens)

#### Opção 1: Disparar CI/CD (recomendado)

Configurar os secrets do GitHub e fazer push na `main`:

1. Vá em: https://github.com/cunhagd/radiantev2/settings/secrets/actions
2. Adicione os seguintes **Repository Secrets**:

| Nome | Valor |
|------|-------|
| `AWS_ROLE_ARN` | `arn:aws:iam::406223549358:role/github-actions-radiante` |
| `AWS_REGION` | `us-east-1` |
| `ECR_REPOSITORY_BACKEND` | `radiante-backend` |
| `ECR_REPOSITORY_NGINX` | `radiante-nginx` |
| `EC2_INSTANCE_ID` | `i-0df8ba5134b0e0b28` |

3. Depois faça um push na `main` (ou use `git push`)

#### Opção 2: Build manual na própria EC2 (fallback rápido)

Se o CI/CD não estiver configurado, você pode fazer o build manualmente:

```bash
# 1. Instalar git (se não tiver)
sudo yum install -y git

# 2. Clonar o repositório
cd /tmp
git clone https://github.com/cunhagd/radiantev2.git
cd radiantev2

# 3. Fazer o build da imagem do backend
sudo docker build -t radiante-backend:local \
  -f backend/Dockerfile \
  --target runtime .

# 4. Fazer o build da imagem do nginx
sudo docker build -t radiante-nginx:local \
  -f infra/nginx/Dockerfile .

# 5. Ajustar o docker-compose.yml para usar imagens locais
cd /opt/radiante
# Edite o docker-compose.yml: remova a linha "build:" e adicione "image: radiante-backend:local"
# Exemplo de como fazer rápido:
sed -i 's|build:|#build:|' docker-compose.yml
sed -i 's|dockerfile: backend/Dockerfile|image: radiante-backend:local|' docker-compose.yml
sed -i 's|context: .|#context: .|' docker-compose.yml
sed -i 's|target: runtime|#target: runtime|' docker-compose.yml
# Para o nginx:
sed -i 's|dockerfile: infra/nginx/Dockerfile|image: radiante-nginx:local|' docker-compose.yml

# 6. Subir
sudo docker compose up -d
```

### ❌ Permission denied ao criar pastas ou arquivos

Use `sudo` para todos os comandos que envolvam `/opt/radiante/`.

### ❌ "Unable to locate credentials" no `aws` CLI

A IAM Role não está anexada à EC2, ou o SSM Agent não conseguiu obtê-la:

```bash
# Testar se a role está disponível
aws sts get-caller-identity

# Se falhar, é necessário anexar a IAM Role à EC2 pelo Console:
```

Para **anexar a IAM Role**:

1. Acesse: https://console.aws.amazon.com/ec2/
2. Clique em **Instances** > selecione `i-0df8ba5134b0e0b28`
3. Clique em **Actions** > **Security** > **Modify IAM role**
4. Escolha a role existente (ex: `radiante-prod-ec2-ssm-role`)
5. Clique em **Save**

> Após anexar, pode levar alguns segundos para ficar disponível.

### ❌ "curl: (7) Failed to connect" ao testar localhost

O container pode não estar rodando. Verifique:

```bash
sudo docker compose ps
sudo docker compose logs --tail=30
```

### ❌ O Amplify retorna erro 404 ao chamar a API

Possíveis causas:

1. **IP da EC2 mudou**: Instâncias t3a.micro podem mudar de IP ao parar/iniciar. Verifique e atualize `API_BASE` no Amplify.

   ```
   API_BASE = http://NOVO_IP:8000
   ```

2. **Security Group bloqueando**: A EC2 está em subnet privada, então o tráfego chega pelo **Application Load Balancer** (ALB) ou **NAT Gateway**. Confirme que:
   - O Security Group da EC2 permite tráfego na porta 8000 vindo do ALB/NAT
   - Alternativamente, o Nginx (porta 80) está exposto via ALB

3. **O backend não está saudável**: Reconecte via Session Manager e verifique os logs.

---

---

## 13. Resolvendo Mixed Content (HTTPS no Backend)

O erro `Mixed Content: ... was loaded over HTTPS, but requested an insecure resource 'http://...'` ocorre porque o **frontend está no HTTPS** (Amplify) e tenta chamar o **backend via HTTP**. O navegador bloqueia.

A solução definitiva é colocar o backend atrás de HTTPS. A melhor forma é criar um **Application Load Balancer (ALB)** com certificado SSL via AWS Certificate Manager.

### Opção A (Recomendada): Application Load Balancer com HTTPS

1. **Acesse o Console AWS → CloudFormation**
2. **Crie uma stack** com o template abaixo (salve como `alb-https.yaml`):

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: "Radiante v2 - ALB com HTTPS"

Parameters:
  InstanceId:
    Type: AWS::EC2::Instance::Id
    Default: i-0df8ba5134b0e0b28
  InstancePort:
    Type: Number
    Default: 80
  VpcId:
    Type: AWS::EC2::VPC::Id
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Radiante ALB SG
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: radiante-alb
      Scheme: internet-facing
      Type: application
      SecurityGroups: [!Ref ALBSecurityGroup]
      Subnets: !Ref SubnetIds

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: radiante-tg
      Port: !Ref InstancePort
      Protocol: HTTP
      TargetType: instance
      VpcId: !Ref VpcId
      HealthCheckPath: /api/status
      Matcher: { HttpCode: "200,202" }

  TargetAttachment:
    Type: AWS::ElasticLoadBalancingV2::TargetGroupAttachment
    Properties:
      TargetGroupArn: !Ref TargetGroup
      TargetId: !Ref InstanceId
      Port: !Ref InstancePort

  HTTPListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref LoadBalancer
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - Type: redirect
          RedirectConfig:
            Protocol: HTTPS
            Port: "443"
            Host: "#{host}"
            Path: "/#{path}"
            Query: "#{query}"
            StatusCode: HTTP_301

  HTTPSListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref LoadBalancer
      Port: 443
      Protocol: HTTPS
      SslPolicy: ELBSecurityPolicy-TLS13-1-2-2021-06
      Certificates:
        - CertificateArn: !Ref Certificate
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup

  Certificate:
    Type: AWS::CertificateManager::Certificate
    Properties:
      DomainName: radiante.emaster.info
      SubjectAlternativeNames:
        - "*.radiante.emaster.info"
      ValidationMethod: DNS

Outputs:
  ALBDnsName:
    Value: !GetAtt LoadBalancer.DNSName
```

3. **No formulário de criação**, preencha:
   - **Stack name**: `radiante-alb-https`
   - **InstanceId**: `i-0df8ba5134b0e0b28`
   - **InstancePort**: `80`
   - **VpcId**: Selecione a VPC onde a EC2 está
   - **SubnetIds**: Selecione **2 subnets públicas** (pelo menos)

4. **Avance** e confirme que a stack vai criar recursos IAM

5. **Valide o certificado SSL**: O ACM vai pedir validação via DNS. Crie o registro CNAME no seu provedor de domínio (o nome do registro aparece na stack).

6. Após a stack ser criada, pegue o **DNS do ALB** (ex: `radiante-alb-123456.us-east-1.elb.amazonaws.com`).

7. **No Amplify**, configure a regra de rewrite:
```json
{
  "source": "/api/<*>",
  "target": "https://<DNS_DO_ALB>/api/<*>",
  "status": "200",
  "condition": ""
}
```

8. **OBS**: Se preferir, pode apontar o `API_BASE` diretamente para o DNS do ALB:
   - No console Amplify → Environment variables
   - Adicione: `API_BASE` = `https://<DNS_DO_ALB>`

> **Nota**: O certificado do ACM só funciona para o domínio `radiante.emaster.info` (ou subdomínios). O DNS do ALB (`elb.amazonaws.com`) **não pode receber certificado ACM**. Por isso o template usa o domínio `*.radiante.emaster.info` — você precisa validar o domínio.

### Opção B (Alternativa): Let's Encrypt + Caddy na EC2

Se preferir não criar ALB, pode configurar HTTPS diretamente na EC2 usando **Caddy** (que obtém certificado Let's Encrypt automaticamente).

**Requisito**: Ter um subdomínio apontando para o IP da EC2 (ex: `api.radiante.emaster.info`).

1. **Crie um registro DNS** no seu provedor de domínio:
   - **Tipo**: A
   - **Nome**: `api`
   - **Valor**: `18.208.190.159` (IP público da EC2)
   - **TTL**: 300 (ou o mínimo)

2. **Conecte na EC2 via Session Manager** e execute:
```bash
cd /opt/radiante
sudo python3 dpbc.py --ssl
```

3. O Caddy vai:
   - Obter certificado SSL do Let's Encrypt para `api.radiante.emaster.info`
   - Fazer proxy reverso para o backend na porta 8000
   - Servir HTTPS automaticamente

4. **No Amplify**, adicione a regra de rewrite:
```json
{
  "source": "/api/<*>",
  "target": "https://api.radiante.emaster.info/api/<*>",
  "status": "200",
  "condition": ""
}
```

5. **Remova a variável `API_BASE`** do Amplify (ou deixe vazia) para que o `api.js` use URLs relativas ao mesmo domínio — o Amplify vai fazer o rewrite para o backend.

### Verificação

Após configurar HTTPS, teste:

```bash
# Do terminal local
curl -I https://<DNS_DO_ALB>/api/status
# Ou
curl -I https://api.radiante.emaster.info/api/status
# Deve retornar HTTP/2 200
```

Depois, recarregue o frontend em `https://radiante.emaster.info/` e tente fazer upload. O erro Mixed Content deve desaparecer.

---

## Apêndice: Como criar a IAM Role para CI/CD (se não existir)

Se a Role `github-actions-radiante` ainda não foi criada, você pode usar o script automatizado:

```bash
# No seu terminal local (não na EC2!)
# Configure o AWS CLI com credenciais de admin
aws configure

# Execute o script de setup de infra
bash infra/scripts/setup-aws-infra.sh
```

> 🛑 **Atenção**: Este script requer permissões de administrador na conta AWS. O usuário `radiante-poc` pode não ter essas permissões — execute com um usuário admin.

---

## Checklist Final

Antes de considerar o deploy concluído, confira:

- [ ] Session Manager conectado na EC2
- [ ] Diretório `/opt/radiante/` criado com docker-compose.yml
- [ ] Arquivo `.env` configurado com token Bedrock válido
- [ ] Login no ECR bem-sucedido
- [ ] Imagens do backend e nginx baixadas
- [ ] `docker compose up -d` executado sem erros
- [ ] `curl http://localhost:80/health` retorna `healthy`
- [ ] `curl http://localhost:80/api/status` retorna JSON
- [ ] Serviço systemd habilitado (restart automático)
- [ ] Amplify acessando `http://IP_EC2:8000` corretamente
- [ ] Upload e análise de documento funcionando

---

> **Dúvidas?** Conecte no Session Manager e use `sudo docker compose logs` para diagnosticar.
> Para suporte adicional, abra um chamado com o DevOps.
