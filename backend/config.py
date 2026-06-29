#!/usr/bin/env python3
"""Configuracao centralizada do Radiante v2.

Le configuracoes do arquivo .env, valida campos obrigatorios.
A autenticacao com o Bedrock Mantle e feita via AWS SigV4
usando as credenciais do boto3 (profile SSO, variaveis de ambiente,
ou IMDS/ECS). O Bearer Token e opcional (para fallback se disponivel).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from dataclasses import dataclass, field

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    """Configuracoes do sistema, carregadas uma vez na inicializacao.

    Todos os campos sao propriedades congeladas (frozen=True) para
    garantir imutabilidade apos a inicializacao.
    """

    bearer_token: str = ""
    aws_region: str = "us-east-1"
    aws_profile: str = ""
    model_id: str = "xai.grok-4.3"
    bucket_name: str = "radiante-final"
    grok_price_input: float = 0.0
    grok_price_output: float = 0.0
    grok_price_cache_read: float = 0.0
    grok_reasoning_effort: str = "high"
    docs_dir: Path = field(default_factory=lambda: ROOT_DIR / "data" / "docs")
    md_dir: Path = field(default_factory=lambda: ROOT_DIR / "data" / "markdown_docs")


def _load_env() -> dict[str, str]:
    """Carrega .env e retorna dict com valores limpos."""
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        print(f"ERROR: Arquivo .env nao encontrado em {env_path}", file=sys.stderr)
        print("Copie .env.example para .env e preencha as configuracoes.", file=sys.stderr)
        sys.exit(1)

    load_dotenv(env_path)

    result = {}
    for key in (
        "REGION",
        "BEDROCK_MODEL_ID",
        "AWS_BEARER_TOKEN_BEDROCK",
        "GROK_PRICE_INPUT",
        "GROK_PRICE_OUTPUT",
        "GROK_PRICE_CACHE_READ",
        "GROK_REASONING_EFFORT",
    ):
        result[key] = os.getenv(key, "").strip().strip("\"'").strip()

    return result


def _validate(env: dict[str, str]) -> None:
    """Valida campos obrigatorios. Aborta se algo faltar.

    Aceita dois modos de autenticacao:
      1) Bearer Token: AWS_BEARER_TOKEN_BEDROCK no .env
      2) AWS SigV4: perfil SSO configurado via aws configure
    
    Pelo menos um dos dois deve estar disponivel.
    """
    has_bearer = bool(env.get("AWS_BEARER_TOKEN_BEDROCK"))
    # Verifica se ha credenciais AWS disponiveis (SSO, env vars, etc.)
    has_aws_creds = _check_aws_credentials()

    if not has_bearer and not has_aws_creds:
        print("ERROR: Nenhuma credencial encontrada para Bedrock Mantle.", file=sys.stderr)
        print(file=sys.stderr)
        print("Opcao 1 - Bearer Token (API Key):", file=sys.stderr)
        print("  Gere uma API Key em: https://console.aws.amazon.com/bedrock/home#/api-keys", file=sys.stderr)
        print("  E adicione AWS_BEARER_TOKEN_BEDROCK=<sua-chave> no .env", file=sys.stderr)
        print(file=sys.stderr)
        print("Opcao 2 - AWS SigV4 (SSO):", file=sys.stderr)
        print("  Configure o SSO: aws configure sso --profile radiante", file=sys.stderr)
        print("  Faca login: aws sso login --profile radiante", file=sys.stderr)
        print("  Export: AWS_PROFILE=radiante", file=sys.stderr)
        print(file=sys.stderr)
        sys.exit(1)

    if not env.get("REGION"):
        env["REGION"] = "us-east-1"
    if not env.get("BEDROCK_MODEL_ID"):
        env["BEDROCK_MODEL_ID"] = "xai.grok-4.3"


def _check_aws_credentials() -> bool:
    """Verifica se ha credenciais AWS viaveis (SSO, env vars ou IMDS).

    Returns:
        True se credenciais estao disponiveis.
    """
    # 1. Variaveis de ambiente explicitas
    if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        return True

    # 2. Profile configurado
    if os.getenv("AWS_PROFILE"):
        return True

    # 3. Arquivo de configuracao padrao (~/.aws/config ou ~/.aws/credentials)
    aws_dir = Path.home() / ".aws"
    config_file = aws_dir / "config"
    creds_file = aws_dir / "credentials"
    if config_file.exists() or creds_file.exists():
        return True

    # 4. IMDS (EC2) - nao testamos diretamente, assumimos false
    return False


def load_config() -> Config:
    """Carrega e valida a configuracao do sistema.

    Returns:
        Config: Objeto de configuracao congelado.

    Raises:
        SystemExit: Se configuracoes obrigatorias estiverem faltando.
    """
    env = _load_env()
    _validate(env)

    return Config(
        aws_region=env.get("REGION", "us-east-1"),
        aws_profile=os.getenv("AWS_PROFILE", ""),
        bearer_token=env.get("AWS_BEARER_TOKEN_BEDROCK", ""),
        model_id=env.get("BEDROCK_MODEL_ID", "xai.grok-4.3"),
        grok_price_input=float(env.get("GROK_PRICE_INPUT", "0") or "0"),
        grok_price_output=float(env.get("GROK_PRICE_OUTPUT", "0") or "0"),
        grok_price_cache_read=float(env.get("GROK_PRICE_CACHE_READ", "0") or "0"),
        grok_reasoning_effort=env.get("GROK_REASONING_EFFORT", "high"),
    )
