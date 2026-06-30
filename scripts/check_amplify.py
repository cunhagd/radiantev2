#!/usr/bin/env python3
"""Script de diagnostico do AWS Amplify.

Executa via terminal para verificar se o Amplify esta ativo na conta
AWS configurada, listando aplicativos, ambientes (branches), status
de deploy e URLs.

Uso:
    python scripts/check_amplify.py

Dependencias:
    - boto3 (SDK AWS)
    - python-dotenv (leitura do .env)

Requisitos:
    - Arquivo .env na raiz do projeto com AWS_ACCESS_KEY_ID,
      AWS_SECRET_ACCESS_KEY e REGION configurados.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import (
    ClientError,
    ConnectTimeoutError,
    EndpointConnectionError,
)

# Adiciona a raiz do projeto ao sys.path para importar backend.config
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.config import load_config  # noqa: E402


# ── Helpers ────────────────────────────────────────────────────────────


def format_datetime(value: object) -> str:
    """Converte valor de data/hora para formato brasileiro legivel.

    Aceita objetos datetime (retornados pelo boto3), strings ISO 8601
    ou None. Retorna '-' se a entrada for invalida/None.

    Args:
        value: datetime, string ISO 8601 ou None.

    Returns:
        Data formatada (dd/mm/aaaa HH:MM:SS) ou '-' se invalida.
    """
    if value is None:
        return "-"

    dt: datetime | None = None

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str) and value.strip():
        try:
            dt_str = value.strip()
            if dt_str.endswith("Z"):
                dt_str = dt_str[:-1] + "+00:00"
            dt = datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return value  # fallback: retorna string original

    if dt is None:
        return "-"

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%d/%m/%Y %H:%M:%S")


def infer_branch_status(branch: dict) -> str:
    """Infere o status de um branch Amplify.

    Usa activeJobId para determinar se ha build em andamento.
    Retorna um dos valores: ATIVO, BUILDING.

    Args:
        branch: Dicionario com dados do branch retornado por list_branches.

    Returns:
        String com status inferido.
    """
    if branch.get("activeJobId"):
        return "BUILDING"
    return "ATIVO"


def build_deploy_url(branch_name: str, app_id: str) -> str:
    """Monta a URL de deploy do Amplify.

    Args:
        branch_name: Nome da branch (ex: 'main').
        app_id: ID do aplicativo Amplify (ex: 'd123456').

    Returns:
        URL completa do deploy.
    """
    return f"https://{branch_name}.{app_id}.amplifyapp.com"


# ── Chamadas AWS Amplify ───────────────────────────────────────────────


def get_amplify_status(amplify_client) -> list[dict]:
    """Lista todos os aplicativos Amplify na conta/regiao configurada.

    Args:
        amplify_client: Cliente boto3 'amplify'.

    Returns:
        Lista de dicionarios com dados dos apps:
        {app_id, name, description, create_time}.
    """
    response = amplify_client.list_apps()
    apps = response.get("apps", [])
    result = []
    for app in apps:
        result.append(
            {
                "app_id": app.get("appId", ""),
                "name": app.get("name", ""),
                "description": app.get("description", ""),
                "create_time": app.get("createTime", ""),
            }
        )
    return result


def get_branch_status(amplify_client, app_id: str) -> list[dict]:
    """Lista todos os ambientes (branches) de um aplicativo Amplify.

    Args:
        amplify_client: Cliente boto3 'amplify'.
        app_id: ID do aplicativo Amplify.

    Returns:
        Lista de dicionarios com dados dos branches:
        {branch_name, stage, status, deploy_url, last_update}.
    """
    response = amplify_client.list_branches(appId=app_id)
    branches = response.get("branches", [])
    result = []
    for branch in branches:
        branch_name = branch.get("branchName", "")
        stage = branch.get("stage", "-")
        status = infer_branch_status(branch)
        deploy_url = build_deploy_url(branch_name, app_id)
        last_update = branch.get("createTime", "")
        result.append(
            {
                "branch_name": branch_name,
                "stage": stage,
                "status": status,
                "deploy_url": deploy_url,
                "last_update": last_update,
            }
        )
    return result


# ── Formatacao de Saida ────────────────────────────────────────────────


def print_status(apps: list[dict], region: str) -> None:
    """Exibe o status do Amplify no terminal conforme formato contratado.

    Args:
        apps: Lista de aplicativos Amplify (com branches populados).
        region: Nome da regiao AWS.
    """
    header = f"=== AWS Amplify Status ==="
    print(header)
    print(f"Regiao: {region}")

    if not apps:
        print("Status: INATIVO")
        print(f"Motivo: Nenhum aplicativo Amplify encontrado na regiao {region}.")
        return

    print(f"Status: ATIVO ({len(apps)} {'aplicativo encontrado' if len(apps) == 1 else 'aplicativos encontrados'})")
    print()

    for app in apps:
        print(f"--- App: {app['name']} ---")
        print(f"ID: {app['app_id']}")
        print(f"Criado: {format_datetime(app['create_time'])}")
        print()

        branches = app.get("branches", [])
        if not branches:
            print("  Ambientes: Nenhum")
        else:
            print("  Ambientes:")
            for branch in branches:
                name = branch["branch_name"]
                stage = branch["stage"]
                status = branch["status"]
                url = branch["deploy_url"]
                updated = format_datetime(branch["last_update"])
                print(f"  - {name} [{stage}]  {status:10s}  URL: {url}  (ultima atualizacao: {updated})")

        print()


# ── Fluxo Principal ────────────────────────────────────────────────────


def main() -> int:
    """Funcao principal do script de diagnostico Amplify.

    Returns:
        Exit code: 0 para sucesso, 1 para erro.
    """
    try:
        config = load_config()
    except SystemExit:
        # load_config() ja exibiu a mensagem de erro
        return 1

    if not config.aws_access_key_id or not config.aws_secret_access_key:
        print("=== AWS Amplify Status ===")
        print("Erro: credenciais AWS nao encontradas no .env.")
        print(
            "Verifique se AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY "
            "estao configurados."
        )
        return 1

    try:
        amplify_client = boto3.client(
            "amplify",
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.aws_region,
        )
    except Exception as exc:
        print("=== AWS Amplify Status ===")
        print(f"Erro: nao foi possivel criar o cliente AWS Amplify: {exc}")
        return 1

    try:
        apps = get_amplify_status(amplify_client)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        print("=== AWS Amplify Status ===")
        if error_code == "AccessDeniedException":
            print("Erro: sem permissao para acessar o Amplify.")
            print(
                "Verifique se as credenciais AWS tem a politica "
                "'AmplifyFullAccess' ou similar."
            )
        elif error_code == "UnrecognizedClientException":
            print("Erro: credenciais AWS invalidas ou expiradas.")
        else:
            print(f"Erro: falha ao consultar Amplify ({error_code}).")
        return 1
    except (EndpointConnectionError, ConnectTimeoutError):
        print("=== AWS Amplify Status ===")
        print("Erro: nao foi possivel conectar a AWS.")
        print("Verifique sua conexao de rede e tente novamente.")
        return 1
    except Exception as exc:
        print("=== AWS Amplify Status ===")
        print(f"Erro inesperado: {exc}.")
        print("Verifique o console AWS para mais detalhes.")
        return 1

    # Para cada app, busca os branches
    for app in apps:
        try:
            app["branches"] = get_branch_status(amplify_client, app["app_id"])
        except Exception as exc:
            print(
                f"Aviso: nao foi possivel listar branches do app "
                f"{app['name']}: {exc}",
                file=sys.stderr,
            )
            app["branches"] = []

    print_status(apps, config.aws_region)
    return 0


if __name__ == "__main__":
    sys.exit(main())
