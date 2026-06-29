#!/usr/bin/env bash
# ============================================================
# setup-aws-infra.sh — Setup de infraestrutura AWS para Radiante v2
# 
# O QUE FAZ:
#   1. Cria repositórios ECR (backend + nginx) — se não existirem
#   2. Cria OIDC Provider para GitHub Actions — se não existir
#   3. Cria IAM Role para GitHub Actions (push to ECR + SSM deploy)
#   4. Adiciona permissão ECR à Role da EC2 existente
#
# PRÉ-REQUISITOS (executar como admin da conta AWS 406223549358):
#   - AWS CLI v2 instalado
#   - Credenciais com permissões IAM Full / Admin
#   - GitHub repo configurado (GITHUB_ORG)
#
# USO:
#   chmod +x infra/scripts/setup-aws-infra.sh
#   ./infra/scripts/setup-aws-infra.sh
# ============================================================

set -euo pipefail

# ==================== CONFIGURAÇÃO ====================
AWS_ACCOUNT_ID="406223549358"
AWS_REGION="us-east-1"
GITHUB_ORG="SEU_ORG"              # ← ALTERE AQUI (ex: gustavohsousa)
GITHUB_REPO="radiantev2"
ECR_BACKEND="radiante-backend"
ECR_NGINX="radiante-nginx"
ROLE_NAME="github-actions-radiante"
EC2_ROLE_NAME="radiante-prod-ec2-ssm-role"  # Role JÁ EXISTENTE da EC2
# ======================================================

echo "=== Setup Infraestrutura AWS para Radiante v2 ==="
echo "Conta: $AWS_ACCOUNT_ID"
echo "Região: $AWS_REGION"
echo "GitHub: $GITHUB_ORG/$GITHUB_REPO"
echo ""

# ==================== 1. ECR ====================
echo ">>> 1. Verificando repositórios ECR..."
for repo in "$ECR_BACKEND" "$ECR_NGINX"; do
    if aws ecr describe-repositories --repository-names "$repo" --region "$AWS_REGION" &>/dev/null; then
        echo "  [OK] $repo já existe."
    else
        echo "  [CRIANDO] $repo..."
        aws ecr create-repository \
            --repository-name "$repo" \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        echo "  [OK] $repo criado!"
    fi
done

# ==================== 2. OIDC Provider ====================
echo ""
echo ">>> 2. Configurando OIDC Provider para GitHub Actions..."

OIDC_URL="token.actions.githubusercontent.com"
OIDC_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_URL}"
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_ARN" &>/dev/null; then
    echo "  [OK] OIDC Provider já existe."
else
    echo "  [CRIANDO] OIDC Provider..."
    aws iam create-open-id-connect-provider \
        --url "https://${OIDC_URL}" \
        --client-id-list "sts.amazonaws.com"
    echo "  [OK] OIDC Provider criado!"
fi

# ==================== 3. IAM Role - GitHub Actions ====================
echo ""
echo ">>> 3. Criando IAM Role para GitHub Actions..."

TRUST_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "${OIDC_ARN}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${GITHUB_REPO}:ref:refs/heads/main"
        }
      }
    }
  ]
}
EOF
)

if aws iam get-role --role-name "$ROLE_NAME" &>/dev/null; then
    echo "  [OK] Role $ROLE_NAME já existe."
else
    echo "  [CRIANDO] Role $ROLE_NAME..."
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document "$TRUST_POLICY"
    echo "  [OK] Role $ROLE_NAME criada!"
fi

echo "  [ATTACH] Policies para GitHub Actions..."
aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser" 2>/dev/null || \
    echo "  [WARN] AmazonEC2ContainerRegistryPowerUser já anexada ou erro"

aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore" 2>/dev/null || \
    echo "  [WARN] AmazonSSMManagedInstanceCore já anexada ou erro"

# Policy customizada para SSM SendCommand
echo "  [ATTACH] Policy customizada ssm-send-command..."
aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "ssm-send-command" \
    --policy-document "$(cat <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:SendCommand",
        "ssm:ListCommands",
        "ssm:ListCommandInvocations",
        "ssm:GetCommandInvocation",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    }
  ]
}
POLICY
)" 2>/dev/null || echo "  [WARN] Policy ssm-send-command já existe"

# ==================== 4. EC2 Role - Adicionar permissão ECR ====================
echo ""
echo ">>> 4. Adicionando permissão ECR à Role da EC2 ($EC2_ROLE_NAME)..."

# Verificar se a role existe
if aws iam get-role --role-name "$EC2_ROLE_NAME" &>/dev/null; then
    # Attach ECR ReadOnly (necessário para docker pull)
    aws iam attach-role-policy \
        --role-name "$EC2_ROLE_NAME" \
        --policy-arn "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly" 2>/dev/null && \
        echo "  [OK] AmazonEC2ContainerRegistryReadOnly anexada à EC2 Role!" || \
        echo "  [WARN] AmazonEC2ContainerRegistryReadOnly já estava anexada ou erro"

    # Também garantir S3 ReadOnly (para baixar .env / docker-compose do S3)
    aws iam attach-role-policy \
        --role-name "$EC2_ROLE_NAME" \
        --policy-arn "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" 2>/dev/null && \
        echo "  [OK] AmazonS3ReadOnlyAccess anexada à EC2 Role!" || \
        echo "  [WARN] AmazonS3ReadOnlyAccess já estava anexada ou erro"
else
    echo "  [ERRO] Role $EC2_ROLE_NAME não encontrada!"
    echo "  A EC2 foi provisionada pelo DevOps com esta role?"
    echo "  Verifique manualmente: aws iam get-role --role-name $EC2_ROLE_NAME"
fi

# ==================== FINAL ====================
echo ""
echo "============================================"
echo "  SETUP CONCLUÍDO!"
echo "============================================"
echo ""
echo "PRÓXIMOS PASSOS MANUAIS:"
echo ""
echo "1. Adicionar Secrets no GitHub ($GITHUB_ORG/$GITHUB_REPO):"
echo "   - AWS_ROLE_ARN: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
echo "   - AWS_REGION: ${AWS_REGION}"
echo "   - EC2_INSTANCE_ID: i-0df8ba5134b0e0b28"
echo ""
echo "2. EC2 já está rodando com:"
echo "   - Instance ID: i-0df8ba5134b0e0b28"
echo "   - IAM Role: ${EC2_ROLE_NAME}"
echo "   - Docker + Docker Compose já instalados"
echo "   - Security Group corrigido (sem portas expostas)"
echo ""
echo "3. Após configurar secrets, fazer git push na main"
echo "   para testar o pipeline CI/CD completo."
echo ""
echo "4. Para acesso SSH/terminal via Session Manager:"
echo "   aws ssm start-session --target i-0df8ba5134b0e0b28"
echo "   (ou: bash infra/scripts/ssm-tunnel.sh)"
echo ""
