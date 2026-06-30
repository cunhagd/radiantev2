# backend/Dockerfile
# Multi-stage: imagem leve para producao
# Synthesized: 2026-06-28
# Base: python:3.14-slim (~120MB)

# ========== STAGE 1: Dependencias ==========
FROM python:3.14-slim AS builder

WORKDIR /app

# Only copy dependency files first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ========== STAGE 2: Runtime ==========
FROM python:3.14-slim AS runtime

# Create non-root user
RUN addgroup --system --gid 1001 radiante && \
    adduser --system --uid 1001 --gid 1001 radiante

WORKDIR /app

# Garante que imports como "from backend.config" funcionem
ENV PYTHONPATH=/app

# Copy only installed packages from builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy backend source code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create data directory for docs
RUN mkdir -p /app/data/docs && chown -R radiante:radiante /app

USER radiante

# Health check (simple HTTP endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/status')" || exit 1

EXPOSE 8000

CMD ["python", "backend/app.py", "--mode", "web", "--port", "8000"]
