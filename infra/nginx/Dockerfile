# infra/nginx/Dockerfile
# Servidor nginx para servir frontend estatico + proxy reverso para backend
# Radiante v2 - Producao (Single EC2 com HTTPS)
#
# Certificados SSL montados como volume:
#   /etc/letsencrypt/ (ro) — certificados Let's Encrypt
#   /var/www/certbot/ — webroot para renovacao

FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY infra/nginx/nginx.conf /etc/nginx/conf.d/radiante.conf

# Copy frontend static files
COPY frontend/ /usr/share/nginx/html/

# Criar diretorio para webroot do Certbot (renovacao)
RUN mkdir -p /var/www/certbot

EXPOSE 80 443

# Health check (HTTP ainda funciona na porta 80)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --output-document=/dev/null http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
