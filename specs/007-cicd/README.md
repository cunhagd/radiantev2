# Arquitetura CI/CD — Radiante v2

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Estratégia de Deploy](#2-estratégia-de-deploy)
3. [Estrutura de Repositório](#3-estrutura-de-repositório)
4. [Pipeline CI/CD Passo a Passo](#4-pipeline-cicd-passo-a-passo)
5. [Frontend vs Backend: Como Funciona](#5-frontend-vs-backend-como-funciona)
6. [Arquitetura AWS](#6-arquitetura-aws)
7. [Segurança: OIDC e IAM](#7-segurança-oidc-e-iam)
8. [Rollback Automático](#8-rollback-automático)
9. [Fluxo de Trabalho do Desenvolvedor](#9-fluxo-de-trabalho-do-desenvolvedor)
10. [Setup Inicial Único](#10-setup-inicial-único)
11. [Monitoramento](#11-monitoramento)
12. [Custos](#12-custos)

---

## 1. Visão Geral

O Radiante v2 usa GitHub Actions com OIDC para CI/CD totalmente automatizado na AWS. O fluxo é:

```
Push no main → Testes (pytest + vitest) → Build Docker → Push ECR → Deploy EC2 via SSM
```

### Principais características:
- **Segurança**: Autenticação OIDC (sem chaves AWS estáticas)
- **Separação**: Frontend e backend em containers separados
- **Rollback**: Tag `:previous` mantida no ECR para rollback instantâneo
- **Sem SSH**: Deploy via AWS Systems Manager (SSM)
- **Artifact Attestations**: Garantia de integridade das imagens

---

## 2. Estratégia de Deploy

### Arquitetura em Produção

```
                        ┌─────────────┐
                        │  Route 53   │
                        │  (DNS)      │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │    ALB      │
                        │ (HTTPS:443) │
                        └──────┬──────┘
                               │
                   ┌───────────┴───────────┐
                   │                       │
         ┌─────────▼─────────┐   ┌─────────▼─────────┐
         │  Target Group 1   │   │  Target Group 2   │
         │  (Blue / Active)  │   │  (Green / Standby)│
         └─────────┬─────────┘   └─────────┬─────────┘
                   │                       │
         ┌─────────▼─────────┐   ┌─────────▼─────────┐
         │  Auto Scaling     │   │  Auto Scaling     │
         │  Group (Blue)     │   │  Group (Green)    │
         └─────────┬─────────┘   └─────────┬─────────┘
                   │                       │
         ┌─────────▼─────────┐   ┌─────────▼─────────┐
         │  EC2 Instance(s)  │   │  EC2 Instance(s)  │
         │  ┌─────────────┐  │   │  ┌─────────────┐  │
         │  │ Nginx (80)  │  │   │  │ Nginx (80)  │  │
         │  │ Python (8000)│  │   │  │ Python (8000)│  │
         │  └─────────────┘  │   │  └─────────────┘  │
         └───────────────────┘   └───────────────────┘
```

### Estratégia de Deploy: Blue/Green com ALB

1. **Blue**: ambiente atual em produção (target group ativo)
2. **Green**: nova versão (target group inativo)
3. **Deploy**: CI/CD constrói nova imagem, EC2 faz pull, valida health check
4. **Cutover**: ALB redireciona tráfego para o Green
5. **Rollback**: Se falhar, ALB volta para o Blue imediatamente

Para o MVP (fase inicial), usamos **deploy rolling simples** com uma instância EC2 atrás do ALB. A estratégia Blue/Green é implementada na etapa de maturidade seguinte.

---

## 3. Estrutura de Repositório

```
radiantev2/
├── backend/
│   ├── Dockerfile              # Multi-stage Docker (python:3.14-slim)
│   ├── app.py                  # Servidor HTTP
│   └── ...                     # Demais módulos
├── frontend/
│   ├── index.html              # SPA (HTML puro)
│   ├── css/                    # CSS modular
│   ├── js/                     # JS modular
│   └── tests/                  # Testes vitest
├── infra/
│   ├── nginx/
│   │   ├── Dockerfile          # nginx:1.27-alpine
│   │   └── nginx.conf          # Proxy reverso + estático
│   └── scripts/
│       ├── user-data.sh        # Bootstrap EC2
│       └── .env.production     # Template .env
├── docker-compose.yml          # Orquestração local + produção
├── .github/
│   └── workflows/
│       └── deploy.yml          # Pipeline CI/CD completo
└── specs/
    └── 007-cicd/               # Esta documentação
```

---

## 4. Pipeline CI/CD Passo a Passo

### Gatilhos

| Evento | Ação |
|--------|------|
| **Push no `main`** | CI completo (testes + build + deploy) |
| **Pull Request** | Apenas testes (CI) |
| **Workflow Dispatch** | Manual com opções (force rebuild, skip tests) |

### Fluxo Detalhado

```
┌─────────────────────────────────────────────────────────┐
│                   1. Push no main                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           2. test-backend (pytest)                       │
│   • python -m pytest backend/tests/ --cov=backend       │
│   • Coverage mínima: 70%                                │
│   • Upload artifact: coverage report                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           3. test-frontend (vitest)                      │
│   • npx vitest run                                      │
│   • 34 testes (state, api, cifras, metrics, loading)    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│       4. build-and-push (ECR)  ←── roda EM PARALELO     │
│                                                         │
│   4a. OIDC: Assume IAM Role (sem keys estáticas)        │
│   4b. Login Amazon ECR                                  │
│   4c. Build Backend Image (multi-stage, cache)          │
│       • Tag: ${{ github.sha }}                          │
│       • Tag: latest                                     │
│   4d. Build Nginx Image                                 │
│       • Tag: ${{ github.sha }}                          │
│       • Tag: latest                                     │
│   4e. Artifact Attestation (SLSA)                       │
│   4f. Tag anterior como :previous (rollback)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│             5. deploy (EC2 via SSM)                      │
│                                                         │
│   5a. OIDC: Assume IAM Role                             │
│   5b. SSM SendCommand para EC2:                         │
│       • docker compose pull                             │
│       • docker compose up -d                            │
│       • Health check (curl /health)                     │
│       • Se falhar → rollback (pull :previous)           │
│   5c. Polling de status do SSM (máx 5 min)              │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Frontend vs Backend: Como Funciona

### Como são tratados separadamente?

| Aspecto | Backend | Frontend |
|---------|---------|----------|
| **Código** | Python (backend/) | HTML+CSS+JS (frontend/) |
| **Container** | `backend/Dockerfile` | `infra/nginx/Dockerfile` |
| **Imagem ECR** | `radiante-backend` | `radiante-nginx` |
| **Porta** | 8000 (interno) | 80 (externo, nginx) |
| **Testes** | pytest (`backend/tests/`) | vitest (`frontend/tests/`) |
| **Build** | Multi-stage Python slim | Cópia de arquivos estáticos |
| **Cache** | `--cache-from` layers | Simples (só arquivos) |

### Como o nginx integra os dois?

```nginx
# Proxy reverso: /api/* → backend:8000
location /api/ {
    proxy_pass http://backend:8000;
}

# Estático: /* → /usr/share/nginx/html/
location / {
    root /usr/share/nginx/html;
    try_files $uri /index.html;
}

# Health check para ALB
location /health {
    return 200 "healthy\n";
}
```

O nginx serve **diretamente** os arquivos CSS e JS modulares (sem build step). Não existe webpack, vite ou bundler — o Radiante é HTML+CSS+JS puro.

### Benefício dessa separação:

1. **Escalabilidade independente**: Backend pode escalar verticalmente (mais memória/CPU), frontend escala horizontalmente (mais instâncias nginx)
2. **Cache de assets**: Arquivos estáticos (CSS/JS) são cacheados com `expires 1y` e `immutable`
3. **Segurança**: Backend nunca exposto diretamente (só via proxy reverso)
4. **Atualização**: Pode atualizar só o frontend (trocando a imagem nginx) sem tocar no backend

---

## 6. Arquitetura AWS

### Recursos Necessários

| Recurso | Configuração | Custo Estimado |
|---------|-------------|----------------|
| **EC2 (t3.medium)** | 2 vCPU, 4GB RAM, 20GB gp3 | ~$30/mês |
| **Application Load Balancer** | 1 ALB, 1 listener HTTP:80 | ~$20/mês |
| **ECR** | 2 repositórios (backend + nginx) | ~$1/mês (storage) |
| **SSM** | Gratuito (agent incluso) | $0 |
| **Route 53** | 1 hosted zone (se tiver domínio) | ~$0.50/mês |
| **S3** | Bucket radiante-final (já existe) | ~$5/mês |
| **Bedrock** | Claude Sonnet 4.6 | Pay-per-use |

> **Total estimado**: ~$55-60/mês para ambiente de produção mínimo

### Topologia de Rede

```
Internet ──► Route53 ──► CloudFront (futuro) ──► ALB ──► EC2 (subnet privada)
                                                          │
                                                          ├── S3 (bucket)
                                                          └── Bedrock API
```

---

## 7. Segurança: OIDC e IAM

### Por que OIDC em vez de Access Keys?

O método tradicional de CI/CD armazena `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` como Secrets do GitHub. Isso é **arriscado** porque:

- As chaves são **long-lived** (nunca expiram)
- Vazamento = acesso completo à conta AWS
- Rotação manual é propensa a erros

**OIDC resolve isso**:

```
GitHub Actions ──► Assume Role (STS) ──► Credenciais temporárias (1h)
                                                        ↑
                                                  (sem chaves estáticas)
```

### IAM Role Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:SEU_ORG/radiantev2:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### Instance Profile (EC2)

A EC2 **não precisa** de access keys. Ela usa **Instance Profile** (IAM Role anexada à instância) com as seguintes permissões:

- `AmazonEC2ContainerRegistryReadOnly` — Pull de imagens do ECR
- `AmazonSSMManagedInstanceCore` — Gerenciamento via SSM
- `AmazonS3ReadOnlyAccess` — Acesso ao bucket de documentos

---

## 8. Rollback Automático

### Estratégia de Tags no ECR

| Tag | Propósito |
|-----|-----------|
| `latest` | Imagem atual em produção |
| `${{ github.sha }}` | Imagem específica do commit |
| `previous` | Imagem anterior (para rollback) |

### Como o rollback funciona

O deploy job no GitHub Actions executa estes comandos no EC2 via SSM:

```bash
# Deploy normal:
docker compose pull          # Pull da nova imagem (:latest)
docker compose up -d         # Sobe com a nova versão
curl /health                 # Valida se está saudável

# Se health check falhar → rollback automático:
docker compose pull          # Pull da tag :previous
docker compose up -d         # Volta para versão anterior
```

### Rollback manual (via GitHub)

```bash
# No EC2:
cd /opt/radiante

# Voltar para versão anterior
docker pull $ECR_REGISTRY/radiante-backend:previous
docker tag $ECR_REGISTRY/radiante-backend:previous $ECR_REGISTRY/radiante-backend:latest
docker compose up -d
```

---

## 9. Fluxo de Trabalho do Desenvolvedor

### Dia a dia: "Só subir o push"

O workflow é desenhado para ser o mais simples possível:

```bash
# 1. Desenvolver localmente
git checkout -b feature/nova-funcionalidade

# 2. Rodar testes localmente
cd backend && python -m pytest backend/tests/
cd frontend && npx vitest run

# 3. Commitar e fazer push
git add .
git commit -m "feat: nova funcionalidade X"
git push -u origin feature/nova-funcionalidade

# 4. Abrir Pull Request (testes rodam automaticamente)
#    GitHub Actions executa: test-backend + test-frontend

# 5. Mergear para main (CI/CD completo dispara)
#    GitHub Actions executa:
#      test-backend → test-frontend → build-and-push → deploy

#     ~5-8 minutos depois, está em produção!
```

### O que o desenvolvedor NÃO precisa fazer:

- ❌ Não precisa buildar Docker localmente
- ❌ Não precisa fazer SSH no servidor
- ❌ Não precisa gerenciar chaves AWS
- ❌ Não precisa configurar nada além do push
- ❌ Não precisa se preocupar com rollback

---

## 10. Setup Inicial Único

### Passo 1: Configurar OIDC no AWS

```bash
# Criar Identity Provider no IAM
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com

# Criar IAM Role para GitHub Actions
aws iam create-role \
    --role-name github-actions-radiante \
    --assume-role-policy-document file://infra/scripts/oidc-trust-policy.json
```

### Passo 2: Configurar Secrets no GitHub

No repositório GitHub, adicionar:

| Secret | Valor |
|--------|-------|
| `AWS_ROLE_ARN` | `arn:aws:iam::406223549358:role/github-actions-radiante` |
| `AWS_REGION` | `us-east-1` |
| `ECR_REPOSITORY_BACKEND` | `radiante-backend` |
| `ECR_REPOSITORY_NGINX` | `radiante-nginx` |
| `EC2_INSTANCE_ID` | `i-xxxxxxxxxxxxxxxxx` |

### Passo 3: Criar ECR Repositories

```bash
aws ecr create-repository --repository-name radiante-backend
aws ecr create-repository --repository-name radiante-nginx
```

### Passo 4: Lançar EC2 com User Data

Ao criar a EC2, anexar:
- **IAM Role**: `EC2-radiante-role` (com SSM + ECR + S3)
- **User Data**: conteúdo de `infra/scripts/user-data.sh`
- **Security Group**: porta 80 (HTTP) liberada (ou via ALB)

### Passo 5: Configurar ALB (opcional, para produção)

- Target group apontando para EC2:80
- Health check: `/health`
- SSL: ACM certificate (se tiver domínio)

---

## 11. Monitoramento

### Logs do Deploy

Todos os deploys são auditados via:
- **GitHub Actions**: Logs completos em cada execução
- **CloudTrail**: Cada comando SSM é registrado
- **EC2**: Logs da aplicação em `/opt/radiante/` (docker compose logs)

### Health Checks

| Camada | Endpoint | Frequência |
|--------|----------|------------|
| **ALB** | `/health` (nginx) | 30s |
| **Docker** | `HEALTHCHECK` no Dockerfile | 30s |
| **GitHub Actions** | `curl /health` pós-deploy | 1x |

### Métricas CloudWatch (recomendado para futuro)

- `CPUUtilization` da EC2
- `HealthyHostCount` do ALB
- Latência do ALB (`TargetResponseTime`)
- Alarmes para deploy com `UnHealthyHostCount`

---

## 12. Custos

### Breakdown Mensal (produção mínima)

| Item | Custo | Notas |
|------|-------|-------|
| EC2 t3.medium (1 instância) | ~$30 | 2 vCPU, 4GB RAM |
| ALB | ~$20 | 1 listener HTTP |
| ECR storage | ~$1 | 2 imagens (~500MB) |
| S3 (bucket existente) | ~$5 | Documentos + resultados |
| Bedrock (Claude Sonnet) | ~$5-50 | Pay-per-use (variável) |
| Route 53 | ~$0.50 | Se tiver domínio |
| **Total** | **~$55-110/mês** | |

### Otimizações Futuras

1. **Reserved Instance** na EC2: economia de ~40%
2. **Spot Instance** no ASG: economia de ~60% (se tolerar interrupção)
3. **CloudFront** para assets estáticos: reduz carga no ALB
4. **Lambda + API Gateway**: substituir EC2 por serverless (elimina custo de EC2)
