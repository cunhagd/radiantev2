# Auditoria de Infraestrutura AWS — Radiante v2

**Data**: 28/06/2026
**Conta**: `406223549358`
**Região**: `us-east-1`
**Auditoria via**: SSO `AWSReservedSSO_eMasterDev` (credenciais temporárias)

---

## ✅ Recursos Existentes e Verificados

### VPC e Rede (provisionado pelo DevOps)
| Recurso | ID / Nome | Status |
|---------|-----------|--------|
| VPC | `vpc-0bf0e0661cd2d10aa` (10.114.0.0/16) | ✅ OK |
| Subnet Privada | `subnet-0d54e5e2bb5e7ef8b` (10.114.10.0/24) | ✅ OK |
| Subnet Privada 2 | `subnet-0b02cc3f53a641e87` (10.114.20.0/24) | ✅ OK |
| Route Table | Associada a ambas subnets | ✅ OK |
| Security Group | `sg-086662153ba8525b8` | ✅ Corrigido |
| NAT Gateway | `nat-0fd5feb8757c393e3` (eipalloc-0ccc2943aaa76bd33) | ✅ OK |

### EC2 (provisionado pelo DevOps)
| Recurso | ID / Nome | Status |
|---------|-----------|--------|
| Instância EC2 | `i-0df8ba5134b0e0b28` (t3a.micro, AL2023) | ✅ Em execução |
| IP Privado | `10.114.10.197` | ✅ OK |
| IAM Role | `radiante-prod-ec2-ssm-role` | ✅ OK |
| SSM Agent | Instalado e funcional | ✅ OK |
| Docker | v25.0.14 | ✅ Instalado |
| Docker Compose | v5.2.0 | ✅ Instalado |
| App Dir | `/opt/radiante/` com `docker-compose.yml` | ✅ OK |
| Data Dir | `/opt/radiante/data/docs` | ✅ OK |

### EC2 Antiga (VPC Default) — ❌ REMOVIDO
| Recurso | Status |
|---------|--------|
| i-0e861fb336712cf00 (t2.micro) | ❌ Terminada |
| Snapshot de segurança | `snap-0301c80b42e12fe94` (vol-07f33a8740a5cfd55) |

### Bucket S3
| Recurso | Status |
|---------|--------|
| `radiante-final` | ✅ Existe, sem políticas públicas |
| Objetos: `docs/`, `markdown_docs/`, `results/` | ✅ OK |

### Repositórios ECR
| Repositório | URI | Status |
|-------------|-----|--------|
| `radiante-backend` | `406223549358.dkr.ecr.us-east-1.amazonaws.com/radiante-backend` | ✅ Criado |
| `radiante-nginx` | `406223549358.dkr.ecr.us-east-1.amazonaws.com/radiante-nginx` | ✅ Criado |

---

## ❌ Pendências (Bloqueantes para CI/CD)

### 1. IAM Role do GitHub Actions (OIDC) não foi criada
- **Problema**: A sessão SSO atual (`AWSReservedSSO_eMasterDev`) não tem permissão `iam:CreateRole`.
- **Impacto**: O CI/CD não pode autenticar na AWS sem chaves fixas.
- **Solução**: O DevOps precisa executar `infra/scripts/setup-aws-infra.sh` com permissões de admin.

#### Passos manuais:
```bash
# 1. Editar GITHUB_ORG no script
nano infra/scripts/setup-aws-infra.sh  # alterar SEU_ORG

# 2. Executar como admin da conta
chmod +x infra/scripts/setup-aws-infra.sh
./infra/scripts/setup-aws-infra.sh

# 3. Adicionar secrets no GitHub Actions (ver output do script)
```

### 2. EC2 sem permissão para ECR
- **Problema**: A IAM Role `radiante-prod-ec2-ssm-role` não tem `AmazonEC2ContainerRegistryReadOnly`.
- **Impacto**: A EC2 não consegue fazer `docker pull` do ECR.
- **Solução**: Executar o comando abaixo (admin necessário):

```bash
aws iam attach-role-policy \
    --role-name radiante-prod-ec2-ssm-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
```

### 3. Secrets não configurados no GitHub
- `AWS_ROLE_ARN`: `arn:aws:iam::406223549358:role/github-actions-radiante`
- `AWS_REGION`: `us-east-1`
- `EC2_INSTANCE_ID`: `i-0df8ba5134b0e0b28`

---

## 🔧 O que já foi resolvido hoje (28/06)

- ✅ Security Group corrigido: portas 8000/8001 removidas para `0.0.0.0/0`
- ✅ EC2 antiga (VPC Default, t2.micro) terminada com snapshot de backup
- ✅ Docker + Docker Compose instalados na EC2 nova via SSM
- ✅ Repositórios ECR criados
- ✅ `.env` limpo (removidas credenciais temporárias)
- ✅ `docker-compose.yml` e diretório de dados preparados na EC2
- ✅ Script de setup para DevOps criado em `infra/scripts/setup-aws-infra.sh`
- ✅ Tool SSM Tunnel criado em `infra/scripts/ssm-tunnel.sh`
- ✅ Pipeline CI/CD documentado em `specs/007-cicd/`

---

## 🚀 Após resolver pendências, o deploy é:

1. **Git push na main** → GitHub Actions executa:
   - Testes (pytest + vitest)
   - Build + Push Docker para ECR
   - SSM SendCommand para EC2

2. **EC2** executa:
   - `docker compose pull` (nova imagem do ECR)
   - `docker compose up -d` (containers atualizados)
   - Health check automático
   - Rollback se falhar

3. **Acesso Público**: Atualmente sem ALB (custos). 
   Acesso restrito à VPN/VPC via SSM Tunnel.
   Se precisar de ALB no futuro, o DevOps pode adicionar via Terraform.
