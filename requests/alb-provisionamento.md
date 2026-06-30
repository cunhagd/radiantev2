# Solicitação de Provisionamento — ALB com HTTPS para Radiante v2

**Solicitante**: [Seu Nome]
**Projeto**: Radiante v2
**Data**: 30/06/2026
**Prioridade**: Alta (bloqueando produção)

---

## Resumo

Precisamos de um **Application Load Balancer (ALB)** na AWS para servir como proxy HTTPS para o backend do Radiante v2, que roda em uma EC2. Atualmente o frontend (Amplify, HTTPS) não consegue se comunicar com o backend (EC2, HTTP) devido a erro de **Mixed Content** bloqueado pelo navegador.

---

## Arquitetura Desejada

```
🌐 Usuário
    │  https://radiante.emaster.info/api/*
    ▼
┌─────────────────────┐
│  Amplify (CloudFront)│  ← Já configurado, rewrite para ALB
│  HTTPS               │
└────────┬────────────┘
         │  rewrite: /api/<*> → https://<ALB_DNS>/api/<*>
         ▼
┌─────────────────────┐
│  ALB (HTTPS)        │  ← O QUE DEVE SER CRIADO
│  Porta 443          │
└────────┬────────────┘
         │  forward para EC2 porta 80
         ▼
┌─────────────────────┐
│  EC2 (Nginx)        │  ← Já existe (i-0df8ba5134b0e0b28)
│  Porta 80 → :8000   │
└─────────────────────┘
```

---

## O que precisa ser criado

### 1. Security Group do ALB

| Parâmetro | Valor |
|-----------|-------|
| Nome | `radiante-alb-sg` |
| VPC | Mesma VPC da EC2 `i-0df8ba5134b0e0b28` |
| Regras de entrada | |
| - HTTPS (443) | Origem: `0.0.0.0/0` |
| - HTTP (80) | Origem: `0.0.0.0/0` (para redirect) |

### 2. Target Group

| Parâmetro | Valor |
|-----------|-------|
| Nome | `radiante-tg` |
| Tipo | **Instance** (não IP) |
| Protocolo | HTTP |
| Porta | **80** |
| VPC | Mesma da EC2 |
| Health Check | |
| - Path | `/api/status` |
| - Protocolo | HTTP |
| - Porta | traffic-port |
| - Intervalo | 30s |
| - Timeout | 10s |
| - Healthy threshold | 3 |
| - Unhealthy threshold | 3 |
| - Códigos esperados | 200, 202 |

**Registrar target:** EC2 `i-0df8ba5134b0e0b28` na porta **80**

### 3. Application Load Balancer

| Parâmetro | Valor |
|-----------|-------|
| Nome | `radiante-alb` |
| Esquema | **internet-facing** |
| Tipo | **application** |
| IP Address Type | ipv4 |
| VPC | Mesma da EC2 |
| Subnets | **2 subnets públicas** (pelo menos) |
| Security Group | `radiante-alb-sg` (criado acima) |

### 4. Listeners

**Listener HTTP (porta 80):**
- Ação: **Redirect** para HTTPS
- Redirect config:
  - Protocolo: HTTPS
  - Porta: 443
  - Host: `#{host}`
  - Path: `/#{path}`
  - Query: `#{query}`
  - Status Code: HTTP_301

**Listener HTTPS (porta 443):**
- Protocolo: HTTPS
- SSL Policy: `ELBSecurityPolicy-TLS13-1-2-2021-06`
- Certificado SSL: **ACM** (solicitar ou usar existente)
- Ação padrão: **Forward** para `radiante-tg`

### 5. Certificado SSL (ACM)

Se não houver certificado SSL disponível, solicitar um novo:

| Parâmetro | Valor |
|-----------|-------|
| Domínio | `radiante.emaster.info` |
| SANs | `*.radiante.emaster.info` |
| Método de validação | DNS |

> ⚠️ **Nota**: O DevOps vai precisar criar os registros CNAME no DNS para validar o certificado.

---

## Dados da EC2

| Parâmetro | Valor |
|-----------|-------|
| Instance ID | `i-0df8ba5134b0e0b28` |
| IP Privado | (consultar no console) |
| VPC | (consultar no console — mesma das subnets do ALB) |
| Security Group atual | Deve permitir tráfego do ALB (porta 80) |
| Porta do serviço | **80** (Nginx faz proxy para backend :8000) |

---

## Ações necessárias na EC2 (se aplicável)

Verificar se o Security Group da EC2 permite tráfego na porta **80** vindo do Security Group do ALB. Se não, adicionar regra de entrada:

- **Tipo**: HTTP (80)
- **Origem**: Security Group do ALB (`radiante-alb-sg`)
- **Descrição**: "Permitir tráfego do ALB"

---

## Após a criação

O DevOps deve fornecer o **DNS do ALB** (ex: `radiante-alb-123456789.us-east-1.elb.amazonaws.com`).

De posse desse DNS, vou configurar:
1. Regra de **rewrite no Amplify**: `/api/<*>` → `https://<ALB_DNS>/api/<*>` (status 200)
2. Opcional: variável de ambiente `API_BASE` no Amplify apontando para o ALB

---

## CloudFormation (alternativa)

Se o DevOps preferir usar CloudFormation, o template já está pronto no repositório:

```
infra/alb/create-alb.yaml
```

Ele cria todos os recursos acima automaticamente. Basta:
1. Fazer upload do template no Console AWS → CloudFormation
2. Preencher os parâmetros:
   - `InstanceId`: `i-0df8ba5134b0e0b28`
   - `InstancePort`: `80`
   - `VpcId`: (VPC da EC2)
   - `SubnetIds`: (2 subnets públicas)
3. Validar o certificado ACM via DNS

---

## Contato

Qualquer dúvida, me avise. Posso fornecer mais detalhes se necessário.
