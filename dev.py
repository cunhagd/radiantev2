#!/usr/bin/env python3
"""
Comando único de desenvolvimento — Radiante v2

Uso:
    python dev.py              Instala deps + sobe servidor
    python dev.py --install    Só instala dependências
    python dev.py --server     Só sobe o servidor
    python dev.py --test       Roda todos os testes
    python dev.py --setup-sso  Configura profile AWS SSO 'radiante'
    python dev.py --help       Mostra ajuda
"""

import subprocess, sys, os, shutil
from pathlib import Path

ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend"

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log(step, msg):
    print(f"{CYAN}{BOLD}[{step}]{RESET} {msg}")


def ok(msg):
    print(f"  {GREEN}\u2713{RESET} {msg}")


def warn(msg):
    print(f"  {YELLOW}\u26a0{RESET} {msg}")


def _find_cmd(name: str) -> str | None:
    """Procura um executavel no PATH e caminhos comuns do Windows."""
    found = shutil.which(name)
    if found:
        return found
    # Caminhos comuns no Windows onde npm costuma estar
    common = [
        Path(os.environ.get("ProgramFiles", "C:\\Program Files"), "nodejs", f"{name}.cmd"),
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "nodejs", f"{name}.cmd"),
        Path(os.environ.get("LOCALAPPDATA", ""), "fnm", "nodejs", f"{name}.cmd"),
        Path(os.environ.get("USERPROFILE", ""), "AppData", "Roaming", "npm", f"{name}.cmd"),
    ]
    for p in common:
        if p.exists():
            return str(p)
    return None


def run(cmd_list, cwd=None, check=True):
    # Se o primeiro argumento for "npm" ou "npx", acha o caminho certo
    if cmd_list and cmd_list[0] in ("npm", "npx"):
        found = _find_cmd(cmd_list[0])
        if found is None:
            print(f"  {RED}COMANDO '{cmd_list[0]}' NAO ENCONTRADO.{RESET}")
            print(f"  {YELLOW}Instale Node.js em: https://nodejs.org{RESET}")
            print(f"  {YELLOW}Depois rode novamente.{RESET}")
            if check:
                sys.exit(1)
            return None
        cmd_list = [found] + cmd_list[1:]
    try:
        r = subprocess.run(cmd_list, cwd=cwd or ROOT)
        if check and r.returncode != 0:
            sys.exit(r.returncode)
        return r
    except FileNotFoundError:
        print(f"  {RED}Comando '{cmd_list[0]}' nao encontrado.{RESET}")
        sys.exit(1)


def install():
    log("INSTALL", "Instalando dependencias do backend...")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    ok("Backend pronto")

    if (FRONTEND / "package.json").exists():
        log("INSTALL", "Instalando dependencias do frontend...")
        run(["npm", "install"], cwd=FRONTEND)
        ok("Frontend pronto")
    else:
        warn("frontend/package.json nao encontrado - pulando npm install")

    log("INSTALL", "Verificando AWS CLI...")
    r = subprocess.run(["aws", "--version"], capture_output=True, text=True)
    if r.returncode == 0:
        ok(f"AWS CLI: {r.stdout.strip()[:60]}")
    else:
        warn("AWS CLI nao encontrado - necessario para S3 e Textract (profile padrao)")

    # Verifica se o bearer token esta configurado
    env_path = ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            env_content = f.read()
        if "AWS_BEARER_TOKEN_BEDROCK" not in env_content or "=" not in env_content.split("AWS_BEARER_TOKEN_BEDROCK")[-1].split("\n")[0]:
            warn("AWS_BEARER_TOKEN_BEDROCK nao configurado no .env")
            print("  Gere uma API Key em: https://console.aws.amazon.com/bedrock/home#/api-keys")
    print()


def setup_sso():
    log("SSO", "Configurando profile AWS SSO 'radiante'...")
    print()
    print("  Para usar SSO, voce precisa de:")
    print("    1. AWS IAM Identity Center (SSO) habilitado na conta")
    print("    2. URL de inicio SSO (ex: https://d-123456789.awsapps.com/start)")
    print("    3. Regiao: us-east-1")
    print()
    run(["aws", "configure", "sso", "--profile", "radiante"])
    print()
    log("SSO", "Profile 'radiante' configurado!")
    print("  Faca login com: aws sso login --profile radiante")
    print()


def server():
    log("SERVER", "Iniciando servidor em http://localhost:8000")
    print(f"  {YELLOW}Pressione Ctrl+C para parar{RESET}")
    env = os.environ.copy()
    env.pop("AWS_PAGER", None)
    # Garante que o profile radiante seja usado (se setado via variavel de ambiente)
    profile = os.environ.get("AWS_PROFILE") or os.environ.get("AWS_DEFAULT_PROFILE")
    if profile:
        env["AWS_PROFILE"] = profile
        env["AWS_DEFAULT_PROFILE"] = profile
        ok(f"Profile AWS: {profile}")
    else:
        warn("AWS_PROFILE nao definido. Use: $env:AWS_PROFILE='radiante'")
    # Remove variavel poluente do ambiente (test-token)
    env.pop("AWS_BEARER_TOKEN_BEDROCK", None)
    try:
        subprocess.run(
            [sys.executable, "-m", "backend.app", "--mode", "web", "--port", "8000"],
            env=env,
        )
    except KeyboardInterrupt:
        print("\n  Servidor encerrado.")


def test():
    log("TEST", "Rodando testes do backend...")
    env = os.environ.copy()
    env["AWS_BEARER_TOKEN_BEDROCK"] = "test-token"
    env["BEDROCK_MODEL_ID"] = "xai.grok-4.3"
    env["GROK_PRICE_INPUT"] = "0.00000125"
    env["GROK_PRICE_OUTPUT"] = "0.00000250"
    env["GROK_PRICE_CACHE_READ"] = "0.00000020"
    env["GROK_REASONING_EFFORT"] = "high"
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests/", "-v", "--tb=short"],
        env=env,
    )
    if r.returncode == 0:
        ok("Testes do backend concluidos")
    else:
        sys.exit(r.returncode)

    if (FRONTEND / "node_modules").exists():
        log("TEST", "Rodando testes do frontend...")
        subprocess.run(["npm", "test"], cwd=FRONTEND)
        ok("Testes do frontend concluidos")
    else:
        warn("Frontend nao instalado - rode 'python dev.py --install' primeiro")


def show_help():
    print(f"""{BOLD}Radiante v2 - Ambiente de Desenvolvimento{RESET}

{"=" * 50}

USO:
    python dev.py               Instala deps + sobe servidor
    python dev.py --install     So instala dependencias
    python dev.py --server      So sobe o servidor
    python dev.py --test        Roda todos os testes
    python dev.py --setup-sso   Configura profile AWS SSO 'radiante'
    python dev.py --help        Mostra esta ajuda

EXEMPLOS:
    python dev.py               -> setup completo + servidor rodando
    python dev.py --server      -> so sobe o servidor (se ja instalou)
    python dev.py --test        -> pytest + vitest

APOS SUBIR O SERVIDOR, ABRA:
    -> http://localhost:8000

OBS: O servidor usa o profile 'radiante' da AWS.
    Se nao tiver, configure com: python dev.py --setup-sso
""")


if __name__ == "__main__":
    os.environ["PYTHONIOENCODING"] = "utf-8"

    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit(0)

    if "--install" in sys.argv:
        install()
        sys.exit(0)

    if "--server" in sys.argv:
        server()
        sys.exit(0)

    if "--test" in sys.argv:
        test()
        sys.exit(0)

    if "--setup-sso" in sys.argv:
        setup_sso()
        sys.exit(0)

    # Default: install + server
    install()
    server()
