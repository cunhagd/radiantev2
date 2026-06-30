#!/usr/bin/env python3
"""dpbc.py — Deploy Backend Config (EC2/SSM)

Script para configurar o backend na EC2 via AWS Session Manager (SSM).

Adaptado para:
  - Usuario ssm-user (nao root direto — usa sudo internamente)
  - Amazon Linux 2023 (dnf no lugar de yum)
  - Docker ja pre-instalado na AMI
  - Python 3.9+ ja pre-instalado
  - git clone de repositorio publico (sem token)

Uso (via Session Manager no navegavel):
  # Fluxo completo — maquina nova
  cd /tmp
  wget -q https://raw.githubusercontent.com/cunhagd/radiantev2/main/dpbc.py
  sudo python3 dpbc.py --setup

  # Atualizar backend com alteracoes do GitHub
  cd /opt/radiante
  sudo python3 dpbc.py --update

  # Ver status
  sudo python3 dpbc.py --status

  # Logs em tempo real
  sudo python3 dpbc.py --logs
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


APP_DIR = "/opt/radiante"
GIT_REPO = "https://github.com/cunhagd/radiantev2.git"
COMPOSE_FILE = f"{APP_DIR}/docker-compose.yml"
ENV_FILE = f"{APP_DIR}/.env"
BACKEND_SERVICE = "backend"
SYSTEMD_SERVICE = "radiante-backend"
REQUIREMENTS = f"{APP_DIR}/backend/requirements.txt"
NGROK_LOG = f"{APP_DIR}/ngrok.log"


def _run(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """Executa comando e retorna resultado."""
    kwargs: dict = {}
    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    print(f"  >> {' '.join(cmd)}")
    return subprocess.run(cmd, **kwargs)


def _require_root() -> None:
    """Verifica se esta rodando como root (sudo)."""
    if os.geteuid() != 0:
        print("ERRO: Este script precisa ser executado como root (sudo).")
        print("  Use: sudo python3 dpbc.py --setup")
        sys.exit(1)


def _detect_pkg_manager() -> str:
    """Detecta o gerenciador de pacotes da distro."""
    for pm in ["dnf", "yum", "apt-get"]:
        r = _run(["which", pm])
        if r.returncode == 0:
            return pm
    return "dnf"  # fallback para AL2023


def _ensure_ownership() -> None:
    """Garante que o diretorio /opt/radiante pertence ao ssm-user."""
    # Descobre o usuario real (nao root) que iniciou o sudo
    real_user = os.environ.get("SUDO_USER", "ssm-user")
    _run(["chown", "-R", f"{real_user}:{real_user}", APP_DIR])


def cmd_setup() -> None:
    """Configura todo o ambiente do backend na EC2."""
    _require_root()

    PKG_MANAGER = _detect_pkg_manager()

    print(f"\n{'=' * 55}")
    print(" dpbc.py — Setup do Backend Radiante na EC2")
    print(f"{'=' * 55}\n")

    # ── 1. Dependencias do sistema ─────────────────────────────────
    print("[1/9] Instalando dependencias do sistema...")
    _run([PKG_MANAGER, "install", "-y", "git", "curl"], capture=False)
    print("  OK\n")

    # ── 2. Clonar repositorio ──────────────────────────────────────
    print("[2/9] Clonando repositorio...")
    if os.path.exists(APP_DIR):
        print(f"  Diretorio {APP_DIR} ja existe. Atualizando via git pull...")
        r = _run(["git", "-C", APP_DIR, "pull"])
        if r.returncode != 0:
            print(f"  AVISO: git pull falhou: {r.stderr}")
    else:
        _run(["mkdir", "-p", os.path.dirname(APP_DIR)])
        r = _run(["git", "clone", GIT_REPO, APP_DIR])
        if r.returncode != 0:
            print(f"  ERRO: git clone falhou: {r.stderr}")
            sys.exit(1)
    _ensure_ownership()
    print("  OK\n")

    # ── 3. Dependencias Python ─────────────────────────────────────
    print("[3/9] Instalando dependencias Python do backend...")
    _run(["python3", "-m", "pip", "install", "--upgrade", "pip", "-q"], capture=False)
    if os.path.exists(REQUIREMENTS):
        r = _run(["python3", "-m", "pip", "install", "-r", REQUIREMENTS, "-q"], capture=False)
        if r.returncode != 0:
            print(f"  AVISO: pip install teve erros (pode ignorar se for Docker)")
        else:
            print("  OK")
    else:
        print(f"  AVISO: requirements.txt nao encontrado em {REQUIREMENTS}")
    print()

    # ── 4. Arquivo .env ───────────────────────────────────────────
    print("[4/9] Verificando arquivo .env...")
    if not os.path.exists(ENV_FILE):
        print("  ATENCAO: Arquivo .env nao encontrado!")
        print(f"  Crie o arquivo {ENV_FILE} com:")
        print()
        print("""  REGION=us-east-1
  BEDROCK_MODEL_ID=xai.grok-4.3
  AWS_BEARER_TOKEN_BEDROCK=<seu-token>
  AWS_ACCESS_KEY_ID=<sua-access-key>
  AWS_SECRET_ACCESS_KEY=<sua-secret-key>
  GROK_PRICE_INPUT=1.25
  GROK_PRICE_OUTPUT=2.50
  GROK_PRICE_CACHE_READ=0.20
  GROK_REASONING_EFFORT=xhigh""")
        print()
        print("  Dica: voce pode criar o .env direto pelo terminal SSM:")
        print(f'  sudo bash -c \'cat > {ENV_FILE} << "EOF"')
        print("  REGION=us-east-1")
        print("  ...")
        print("  EOF'")
        print()
        print("  Apos criar o .env, execute novamente --setup")
        sys.exit(1)
    print("  OK\n")

    # ── 5. docker-compose.yml ─────────────────────────────────────
    print("[5/9] Verificando docker-compose.yml...")
    if not os.path.exists(COMPOSE_FILE):
        print(f"  ERRO: {COMPOSE_FILE} nao encontrado no repositorio.")
        sys.exit(1)
    print("  OK\n")

    # ── 6. Diretorio de logs ──────────────────────────────────────
    print("[6/9] Configurando diretorio de logs...")
    _run(["mkdir", "-p", f"{APP_DIR}/logs"])
    _ensure_ownership()
    print("  OK\n")

    # ── 7. Docker compose up ──────────────────────────────────────
    print("[7/9] Construindo e subindo containers Docker...")
    os.chdir(APP_DIR)
    r = _run(["docker", "compose", "up", "--build", "-d"], capture=False)
    if r.returncode != 0:
        print(f"  ERRO: docker compose up falhou. Verifique os logs.")
        print("  Comando: docker compose logs")
        sys.exit(1)
    print("  OK\n")

    # ── 8. Health check ───────────────────────────────────────────
    print("[8/9] Aguardando health check (ate 30s)...")
    import time
    for i in range(15):
        time.sleep(2)
        r = _run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                   "http://localhost:8000/api/status"])
        code = r.stdout.strip() if r.returncode == 0 else "000"
        if code in ("200", "202"):
            print(f"  -> Backend respondendo na porta 8000 (HTTP {code})")
            break
        print(f"  Tentativa {i+1}/15 (HTTP {code})...")
    else:
        print("  AVISO: Health check nao confirmado.")
        print("  Verifique: curl http://localhost:8000/api/status")
    print()

    # ── 9. Systemd ────────────────────────────────────────────────
    print("[9/9] Configurando restart automatico (systemd)...")
    _setup_systemd()
    print("  OK\n")

    print(f"{'=' * 55}")
    print(" Setup concluido!")
    print(f" Backend: http://localhost:8000")
    print(f" Logs:    sudo docker compose -f {COMPOSE_FILE} logs -f")
    print(f" Parar:   sudo docker compose -f {COMPOSE_FILE} down")
    print(f" Atualizar: sudo python3 {APP_DIR}/dpbc.py --update")
    print(f"{'=' * 55}")


def cmd_update() -> None:
    """Atualiza o backend com as ultimas alteracoes do GitHub (sem downtime)."""
    _require_root()

    print(f"\n{'=' * 55}")
    print(" dpbc.py — Atualizando Backend Radiante")
    print(f"{'=' * 55}\n")

    # ── 1. Git pull ────────────────────────────────────────────────
    print("[1/4] Baixando alteracoes do GitHub...")
    os.chdir(APP_DIR)
    r = _run(["git", "pull"])
    if r.returncode != 0:
        print(f"  ERRO: git pull falhou: {r.stderr}")
        sys.exit(1)
    for line in r.stdout.strip().split("\n"):
        line = line.strip()
        if line:
            print(f"  {line}")
    print("  OK\n")

    # ── 2. Rebuild do backend ──────────────────────────────────────
    print("[2/4] Reconstruindo imagem do backend...")
    r = _run(["docker", "compose", "build", BACKEND_SERVICE], capture=False)
    if r.returncode != 0:
        print(f"  ERRO: docker compose build falhou: {r.stderr}")
        sys.exit(1)
    print("  OK\n")

    # ── 3. Restart sem derrubar nginx ──────────────────────────────
    print("[3/4] Reiniciando container do backend...")
    r = _run(["docker", "compose", "up", "-d", "--no-deps", BACKEND_SERVICE], capture=False)
    if r.returncode != 0:
        print(f"  ERRO: docker compose up falhou: {r.stderr}")
        sys.exit(1)
    print("  OK\n")

    # ── 4. Health check ────────────────────────────────────────────
    print("[4/4] Verificando health check...")
    import time
    for i in range(10):
        time.sleep(2)
        r = _run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                   "http://localhost:8000/api/status"])
        code = r.stdout.strip() if r.returncode == 0 else "000"
        if code in ("200", "202"):
            print(f"  -> Backend respondendo (HTTP {code})")
            break
        print(f"  Tentativa {i+1}/10 (HTTP {code})...")
    else:
        print("  AVISO: Health check nao confirmado. Verifique manualmente.")
    print()

    print(f"{'=' * 55}")
    print(" Atualizacao concluida!")
    print(f"{'=' * 55}")


def cmd_status() -> None:
    """Exibe status detalhado dos servicos."""
    print(f"\n{'=' * 55}")
    print(" Status do Backend Radiante")
    print(f"{'=' * 55}\n")

    if not os.path.exists(APP_DIR):
        print("  Backend nao configurado (diretorio /opt/radiante nao existe).")
        print("  Execute: sudo python3 dpbc.py --setup")
        return

    os.chdir(APP_DIR)

    # Docker compose ps
    r = _run(["docker", "compose", "ps"])
    if r.returncode == 0 and r.stdout.strip():
        print("Containers:")
        print(r.stdout)
    else:
        print("Containers: Nenhum rodando\n")

    # Health check
    r = _run(["curl", "-s", "http://localhost:8000/api/status"])
    if r.returncode == 0 and r.stdout:
        print(f"Health Check (/api/status): Online")
    else:
        print("Health Check: Offline (porta 8000 nao respondendo)")

    # Systemd
    r = _run(["systemctl", "is-active", SYSTEMD_SERVICE])
    status = r.stdout.strip() if r.returncode == 0 else "inativo"
    print(f"Systemd ({SYSTEMD_SERVICE}): {status}")

    # Disco
    r = _run(["df", "-h", "--output=used,avail,pcent", APP_DIR])
    if r.returncode == 0:
        lines = r.stdout.strip().split("\n")
        if len(lines) >= 2:
            print(f"Disco ({APP_DIR}): {lines[-1].strip()}")

    # Uptime dos containers
    r = _run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"])
    if r.returncode == 0 and r.stdout.strip():
        print(f"\n{r.stdout.strip()}")

    print()


def cmd_ssl() -> None:
    """Configura HTTPS na EC2 via Caddy (proxy reverso com Let's Encrypt).

    Requer que voce crie um registro DNS apontando um subdominio
    (ex: api.radiante.emaster.info) para o IP publico da EC2.

    Uso:
      1. Crie o registro DNS manualmente:
         api.radiante.emaster.info  CNAME ou A  -> <IP_DA_EC2>
      2. Execute:
         sudo python3 /opt/radiante/dpbc.py --ssl
    """
    _require_root()

    print(f"\n{'=' * 55}")
    print(" dpbc.py — Configurando HTTPS com Caddy")
    print(f"{'=' * 55}\n")

    API_DOMAIN = "api.radiante.emaster.info"

    # ── 1. Parar container nginx (porta 80 liberada para Caddy) ────
    print("[1/5] Parando container frontend (nginx) para liberar porta 80...")
    os.chdir(APP_DIR)
    _run(["docker", "compose", "stop", "frontend"], capture=False)
    print("  OK\n")

    # ── 2. Instalar Caddy ───────────────────────────────────────────
    print("[2/5] Instalando Caddy...")
    r = _run(["which", "caddy"])
    if r.returncode == 0:
        print("  Caddy ja instalado.")
    else:
        PKG_MANAGER = _detect_pkg_manager()
        if PKG_MANAGER in ("dnf", "yum"):
            _run([PKG_MANAGER, "install", "-y", "caddy"], capture=False)
        else:
            # Instalar via script oficial
            _run(["sh", "-c",
                  "curl -fsSL https://getcaddy.com | bash"],
                 capture=False)
    print("  OK\n")

    # ── 3. Criar Caddyfile ──────────────────────────────────────────
    print("[3/5] Criando Caddyfile em /etc/caddy/Caddyfile...")

    caddyfile = f"""{API_DOMAIN} {{
    # Proxy reverso para o backend no Docker
    reverse_proxy localhost:8000 {{
        header_up Host {{host}}
        header_up X-Real-IP {{remote_host}}
        header_up X-Forwarded-For {{remote_host}}
        header_up X-Forwarded-Proto https
    }}

    # Logs
    log {{
        output file /var/log/caddy/radiante-api.log
        format json
    }}

    # Rate limiting basico
    rate_limit {{
        zone api {{
            key {{remote_host}}
            events 100
            window 1m
        }}
    }}
}}

# Redirecionar HTTP para HTTPS em todas as portas
http://{API_DOMAIN} {{
    redir https://{{host}}{{uri}} permanent
}}
"""
    _run(["mkdir", "-p", "/etc/caddy"])
    _run(["mkdir", "-p", "/var/log/caddy"])
    with open("/etc/caddy/Caddyfile", "w") as f:
        f.write(caddyfile)
    _run(["chmod", "644", "/etc/caddy/Caddyfile"])
    print("  OK\n")

    # ── 4. Configurar systemd para Caddy ────────────────────────────
    print("[4/5] Configurando servico systemd Caddy...")
    _run(["systemctl", "enable", "caddy"])
    _run(["systemctl", "restart", "caddy"])
    print("  OK\n")

    # ── 5. Health check ────────────────────────────────────────────
    print("[5/5] Verificando se Caddy esta rodando...")
    import time
    for i in range(10):
        time.sleep(2)
        r = _run(["systemctl", "is-active", "caddy"])
        status = r.stdout.strip() if r.returncode == 0 else "inactive"
        if status == "active":
            print(f"  -> Caddy ativo e servindo HTTPS em https://{API_DOMAIN}")
            break
        print(f"  Tentativa {i+1}/10 (status: {status})...")
    else:
        print("  AVISO: Caddy pode nao ter iniciado corretamente.")
        print("  Verifique: systemctl status caddy")
        print("  Logs: journalctl -u caddy -n 50 --no-pager")
    print()

    # ── Teste ────────────────────────────────────────────────────────
    print("Testando conexao HTTPS via localhost...")
    r = _run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
              "http://localhost:8000/api/status"])
    code = r.stdout.strip() if r.returncode == 0 else "000"
    print(f"  Backend local (HTTP): {code}")

    print()
    print(f"{'=' * 55}")
    print(" HTTPS configurado!")
    print(f" URL: https://{API_DOMAIN}")
    print(f" Proxando para: http://localhost:8000")
    print()
    print(" ANTES DE USAR:")
    print(f" 1. Crie o registro DNS: {API_DOMAIN} -> <IP_PUBLICO_EC2>")
    print(" 2. No Amplify, mude API_BASE para https://api.radiante.emaster.info")
    print(" 3. Ou use: https://api.radiante.emaster.info no custom rewrite")
    print()
    print(" Para voltar ao modo HTTP:")
    print("  sudo systemctl stop caddy")
    print("  sudo docker compose -f /opt/radiante/docker-compose.yml start frontend")
    print(f"{'=' * 55}")


def cmd_ngrok(token: str = "") -> None:
    """Instala e inicia tunel HTTPS via ngrok para o backend.

    Cria um tunel HTTPS publico (ngrok-free.app) para
    http://localhost:8000, resolvendo Mixed Content com o Amplify.

    Uso:
      sudo python3 /opt/radiante/dpbc.py --ngrok          # Se ja configurou o token
      sudo python3 /opt/radiante/dpbc.py --ngrok SEU_TOKEN  # Primeira vez (criar conta em https://dashboard.ngrok.com)
    """
    _require_root()

    print(f"\n{'=' * 55}")
    print(" dpbc.py — Configurando tunel HTTPS (ngrok)")
    print(f"{'=' * 55}\n")

    # ── 1. Verificar se ngrok ja esta instalado ────────────────────
    print("[1/5] Verificando ngrok...")
    r = _run(["which", "ngrok"])
    if r.returncode != 0:
        print("  Baixando e instalando ngrok...")
        r = _run(["curl", "-sSL", "-o", "/tmp/ngrok.zip",
                   "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip"])
        if r.returncode != 0:
            print("  ERRO: Falha ao baixar ngrok.", file=sys.stderr)
            sys.exit(1)
        r = _run(["unzip", "-o", "/tmp/ngrok.zip", "-d", "/usr/local/bin/"])
        if r.returncode != 0:
            print("  ERRO: Falha ao descompactar ngrok.", file=sys.stderr)
            sys.exit(1)
        _run(["chmod", "+x", "/usr/local/bin/ngrok"])
        _run(["rm", "-f", "/tmp/ngrok.zip"])
        print("  ngrok instalado.")
    else:
        print("  ngrok ja instalado.")
    print("  OK\n")

    # ── 1.5 Configurar autenticacao (se token fornecido) ───────────
    if token:
        print("[1.5/5] Configurando token de autenticacao...")
        r = _run(["ngrok", "config", "add-authtoken", token])
        if r.returncode != 0:
            print(f"  AVISO: falha ao configurar token: {r.stderr.strip()}")
        else:
            print("  Token configurado.")
        print("  OK\n")
    else:
        # Verificar se ja tem token configurado
        r = _run(["ngrok", "config", "check"])
        if r.returncode != 0:
            print()
            print("  ⚠️  ngrok precisa de autenticacao!")
            print()
            print("  1. Crie uma conta gratis em: https://dashboard.ngrok.com/signup")
            print("  2. Copie seu token em: https://dashboard.ngrok.com/get-started/your-authtoken")
            print("  3. Execute novamente com o token:")
            print()
            print("     sudo python3 /opt/radiante/dpbc.py --ngrok SEU_TOKEN")
            print()
            sys.exit(1)

    # ── 2. Verificar se backend esta rodando ────────────────────────
    print("[2/5] Verificando backend...")
    r = _run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
              "http://localhost:8000/api/status"])
    code = r.stdout.strip() if r.returncode == 0 else "000"
    if code not in ("200", "202"):
        print("  Backend nao responde na porta 8000. Subindo containers...")
        os.chdir(APP_DIR)
        _run(["docker", "compose", "up", "-d"], capture=False)
        import time
        for i in range(10):
            time.sleep(3)
            r = _run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                       "http://localhost:8000/api/status"])
            code = r.stdout.strip() if r.returncode == 0 else "000"
            if code in ("200", "202"):
                break
            print(f"  Tentativa {i+1}/10 (HTTP {code})...")
        if code not in ("200", "202"):
            print("  ERRO: Backend nao iniciou. Verifique os logs.", file=sys.stderr)
            sys.exit(1)
    print(f"  Backend respondendo (HTTP {code})\n")

    # ── 3. Parar frontend (nginx) se estiver rodando ────────────────
    print("[3/5] Parando container frontend...")
    os.chdir(APP_DIR)
    _run(["docker", "compose", "stop", "frontend"], capture=False)
    print("  OK\n")

    # ── 4. Parar ngrok antigo e iniciar novo ────────────────────────
    print("[4/5] Iniciando tunel ngrok...")
    _run(["pkill", "ngrok"], capture=False)
    _run(["mkdir", "-p", os.path.dirname(NGROK_LOG)])
    _run(["bash", "-c",
          f"nohup ngrok http 8000 --log=stdout > {NGROK_LOG} 2>&1 &"],
         capture=False)
    import time
    time.sleep(3)
    print("  OK\n")

    # ── 5. Obter e exibir URL publica (com retry) ──────────────────
    print("[5/5] Obtendo URL publica do tunel...")
    url = None
    for attempt in range(6):
        url = _get_ngrok_url()
        if url:
            break
        if attempt < 5:
            time.sleep(2)
            print(f"  Aguardando tunel (tentativa {attempt + 2}/6)...")
    if url:
        print(f"\n{'=' * 55}")
        print(" TUNEL HTTPS ATIVO!")
        print(f" URL: {url}")
        print(f"{'=' * 55}")
        print()
        print(" Configure no Amplify:")
        print("  Console AWS → Amplify → radiante-final → Environment variables")
        print(f"  API_BASE = {url}")
        print()
        print(" Depois faca um novo deploy da branch main-poc.")
        print()
        print(" Para ver esta URL novamente:")
        print("  sudo python3 /opt/radiante/dpbc.py --ngrok-status")
    else:
        print("  AVISO: Nao foi possivel obter a URL.")
        print(f"  Verifique os logs: tail -f {NGROK_LOG}")
        print("  Ou consulte manualmente:")
        print('''  curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
d = json.load(sys.stdin)
for t in d['tunnels']:
    if t['public_url'].startswith('https'):
        print(t['public_url'])
"''')
        print()

    print(f"{'=' * 55}")
    print(" ngrok configurado!")
    print(f" Logs: tail -f {NGROK_LOG}")
    print(f" Parar: sudo pkill ngrok")
    print(f"{'=' * 55}")


def cmd_ngrok_status() -> None:
    """Exibe a URL publica atual do tunel ngrok."""
    url = _get_ngrok_url()
    if url:
        print(f"\nURL do tunel ngrok: {url}")
        print()
        print("API_BASE para o Amplify:")
        print(f"  {url}")
    else:
        print("ngrok nao esta rodando ou nao foi possivel obter a URL.")
        print("Execute primeiro: sudo python3 /opt/radiante/dpbc.py --ngrok")


def _get_ngrok_url() -> str | None:
    """Consulta a API local do ngrok e retorna a URL https ativa."""
    try:
        import urllib.request
        import json
        req = urllib.request.urlopen("http://localhost:4040/api/tunnels", timeout=5)
        data = json.loads(req.read().decode())
        for tunnel in data.get("tunnels", []):
            url = tunnel.get("public_url", "")
            if url.startswith("https"):
                return url
        return None
    except Exception:
        return None


def cmd_logs() -> None:
    """Exibe logs do backend em tempo real."""
    _require_root()

    if not os.path.exists(APP_DIR):
        print("ERRO: Diretorio /opt/radiante nao encontrado.", file=sys.stderr)
        sys.exit(1)

    os.chdir(APP_DIR)
    print("Logs do backend (Ctrl+C para sair):\n")
    r = _run(["docker", "compose", "logs", "--tail=50", "-f"], capture=False)
    if r.returncode != 0:
        print("  ERRO: docker compose logs falhou.", file=sys.stderr)
        sys.exit(1)


def _setup_systemd() -> None:
    """Cria servico systemd para restart automatico na inicializacao."""
    unit = f"""[Unit]
Description=Radiante Backend
After=network-online.target docker.service
Wants=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory={APP_DIR}
ExecStart=/usr/bin/docker compose -f {COMPOSE_FILE} up --build -d
ExecStop=/usr/bin/docker compose -f {COMPOSE_FILE} down
ExecReload=/usr/bin/docker compose -f {COMPOSE_FILE} restart
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    unit_path = f"/etc/systemd/system/{SYSTEMD_SERVICE}.service"
    with open(unit_path, "w") as f:
        f.write(unit)

    _run(["systemctl", "daemon-reload"])
    _run(["systemctl", "enable", SYSTEMD_SERVICE])
    _run(["systemctl", "start", SYSTEMD_SERVICE])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="dpbc.py — Deploy Backend Config (EC2/SSM)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Uso tipico no Session Manager (terminal da EC2):

  --- MAQUINA NOVA ---
  # Baixar o script e executar setup completo:
  cd /tmp
  wget -q https://raw.githubusercontent.com/cunhagd/radiantev2/main/dpbc.py
  sudo python3 dpbc.py --setup
  # Quando pedir, crie o arquivo /opt/radiante/.env e rode --setup novamente

  --- ATUALIZAR BACKEND ---
  cd /opt/radiante
  sudo python3 dpbc.py --update

  --- VER STATUS ---
  sudo python3 dpbc.py --status

  --- LOGS EM TEMPO REAL ---
  sudo python3 dpbc.py --logs
  --- HTTPS (ngrok) ---
  sudo python3 dpbc.py --ngrok           # Instalar e iniciar tunel HTTPS
  sudo python3 dpbc.py --ngrok-status     # Ver URL atual do tunel
""",
    )
    parser.add_argument("--setup", action="store_true", help="Configurar ambiente completo do zero")
    parser.add_argument("--update", action="store_true", help="Atualizar backend com git pull + rebuild")
    parser.add_argument("--status", action="store_true", help="Exibir status dos servicos")
    parser.add_argument("--logs", action="store_true", help="Exibir logs em tempo real")
    parser.add_argument("--ssl", action="store_true", help="(deprecated) Configurar HTTPS via Caddy")
    parser.add_argument("--ngrok", nargs="?", const="", default=None,
                        help="Instalar e iniciar tunel HTTPS via ngrok. Opcional: passar token de autenticacao.")
    parser.add_argument("--ngrok-status", action="store_true", help="Exibir URL atual do tunel ngrok")
    args = parser.parse_args()

    if args.setup:
        cmd_setup()
    elif args.update:
        cmd_update()
    elif args.status:
        cmd_status()
    elif args.logs:
        cmd_logs()
    elif args.ssl:
        cmd_ssl()
    elif args.ngrok is not None:
        cmd_ngrok(args.ngrok)
    elif args.ngrok_status:
        cmd_ngrok_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
