#!/usr/bin/env bash
# ============================================================
# ssm-tunnel.sh — Tunel SSM para acessar API da EC2 privada
#
# Uso:
#   ./infra/scripts/ssm-tunnel.sh [instance-id] [porta-local]
#
# Exemplo:
#   ./infra/scripts/ssm-tunnel.sh i-0123456789abcdef0 8080
#
# Depois acesse:
#   Frontend: http://localhost:8080
#   API:      http://localhost:8080/api/status
#
# Pre-requisitos:
#   - AWS CLI v2 instalado e configurado
#   - SSM Session Manager plugin instalado
#     (https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)
#   - A EC2 deve ter a IAM Role com permissao SSM
# ============================================================

set -euo pipefail

INSTANCE_ID="${1:-}"
LOCAL_PORT="${2:-8080}"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$INSTANCE_ID" ]; then
    echo -e "${RED}ERRO: Informe o Instance ID da EC2${NC}"
    echo "Uso: $0 i-0123456789abcdef0 [porta-local]"
    echo ""
    echo "EC2s disponiveis via SSM:"
    aws ssm describe-instance-information \
        --query "InstanceInformationList[*].{ID:InstanceId,Nome:ComputerName,IP:IpAddress,Ping:PingStatus}" \
        --output table
    exit 1
fi

echo -e "${GREEN}=== Tunel SSM para EC2 $INSTANCE_ID ===${NC}"
echo ""
echo -e "  Frontend:  ${YELLOW}http://localhost:$LOCAL_PORT${NC}"
echo -e "  API:       ${YELLOW}http://localhost:$LOCAL_PORT/api/status${NC}"
echo -e "  Health:    ${YELLOW}http://localhost:$LOCAL_PORT/health${NC}"
echo ""
echo -e "${YELLOW}Abrindo tunel SSM (pressione Ctrl+C para encerrar)...${NC}"
echo ""

aws ssm start-session \
    --target "$INSTANCE_ID" \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters "{
        \"host\":[\"localhost\"],
        \"portNumber\":[\"80\"],
        \"localPortNumber\":[\"$LOCAL_PORT\"]
    }"
