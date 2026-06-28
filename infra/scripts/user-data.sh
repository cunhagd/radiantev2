#!/bin/bash
# ============================================================
# user-data.sh — Inicializacao EC2 para Radiante v2
# 
# NOTA: Esta EC2 ja foi provisionada pelo DevOps via Terraform.
# Este script apenas configura o runtime da aplicacao.
#
# Pre-requisitos (ja provisionados pelo DevOps):
#   - EC2 t3a.micro em subnet privada
#   - IAM Role com SSM + ECR + S3 + Bedrock
#   - Docker e Docker Compose ja instalados
#   - SSM Agent rodando
# ============================================================

set -euo pipefail

APP_DIR="/opt/radiante"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "[RADIANTE] Iniciando setup da aplicacao em $(date)"

# ==================== 1. Criar diretorio da app ====================
sudo mkdir -p "$APP_DIR"
sudo chown "$(whoami):$(whoami)" "$APP_DIR"
cd "$APP_DIR"

# ==================== 2. Baixar configuracao do S3 ====================
echo "[RADIANTE] Baixando docker-compose e .env do S3..."
# Em producao, armazene docker-compose.yml e .env em um bucket S3 seguro
# aws s3 cp s3://radiante-config/docker-compose.yml .
# aws s3 cp s3://radiante-config/.env .env

# ==================== 3. Login ECR e Pull ====================
echo "[RADIANTE] Autenticando no ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
    sudo docker login --username AWS --password-stdin "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com"

echo "[RADIANTE] Fazendo pull da imagem..."
sudo docker compose pull

echo "[RADIANTE] Subindo containers..."
sudo docker compose up -d --remove-orphans

# ==================== 4. Health check ====================
echo "[RADIANTE] Aguardando health check..."
for i in $(seq 1 15); do
    if curl -sf http://localhost:80/health > /dev/null 2>&1; then
        echo "[RADIANTE] Aplicacao saudavel apos $((i * 2))s!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "[RADIANTE] ERRO: Health check falhou apos 30s"
        sudo docker compose logs --tail=50
        exit 1
    fi
    sleep 2
done

# ==================== 5. Auto-restart ====================
echo "[RADIANTE] Configurando restart automatico..."
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

sudo systemctl daemon-reload
sudo systemctl enable radiante.service

echo "[RADIANTE] Setup concluido em $(date)!"
