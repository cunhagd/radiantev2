# infra/nginx/Dockerfile
# Servidor nginx para servir frontend estatico + proxy reverso para backend
# Synthesized: 2026-06-28

FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY infra/nginx/nginx.conf /etc/nginx/conf.d/radiante.conf

# Copy frontend static files
COPY frontend/ /usr/share/nginx/html/

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --output-document=/dev/null http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
