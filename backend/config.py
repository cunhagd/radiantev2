#!/usr/bin/env python3
"""Configuracao centralizada do Radiante v2.

Le configuracoes do arquivo .env, valida campos obrigatorios.
A autenticacao com servicos AWS (S3, Textract) usa
AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY do .env.
O Bedrock Mantle (Grok) usa AWS_BEARER_TOKEN_BEDROCK.
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
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
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

    load_dotenv(env_path, override=True)

    result = {}
    for key in (
        "REGION",
        "BEDROCK_MODEL_ID",
        "AWS_BEARER_TOKEN_BEDROCK",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "GROK_PRICE_INPUT",
        "GROK_PRICE_OUTPUT",
        "GROK_PRICE_CACHE_READ",
        "GROK_REASONING_EFFORT",
    ):
        result[key] = os.getenv(key, "").strip().strip("\"'").strip()

    return result


def _validate(env: dict[str, str]) -> None:
    """Valida campos obrigatorios. Aborta se algo faltar.

    Requer:
      1) AWS_BEARER_TOKEN_BEDROCK no .env para Bedrock Mantle (IA/Grok) — OBRIGATORIO
      2) AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY no .env para S3 e Textract — OPCIONAIS
         (se ausentes, boto3 usa IAM Role da EC2 via IMDS)
    """
    has_bearer = bool(env.get("AWS_BEARER_TOKEN_BEDROCK"))

    if not has_bearer:
        print("ERROR: AWS_BEARER_TOKEN_BEDROCK nao encontrado no .env.", file=sys.stderr)
        print(file=sys.stderr)
        print("  Gere uma API Key em: https://console.aws.amazon.com/bedrock/home#/api-keys", file=sys.stderr)
        print("  E adicione AWS_BEARER_TOKEN_BEDROCK=<sua-chave> no .env", file=sys.stderr)
        print(file=sys.stderr)
        sys.exit(1)

    has_access_key = bool(env.get("AWS_ACCESS_KEY_ID")) and bool(env.get("AWS_SECRET_ACCESS_KEY"))
    if not has_access_key:
        print("INFO: AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY nao encontrados no .env.", file=sys.stderr)
        print("  O sistema usara IAM Role da EC2 (IMDS) para S3 e Textract.", file=sys.stderr)
        print("  Se estiver em ambiente local, adicione as chaves no .env.", file=sys.stderr)

    if not env.get("REGION"):
        env["REGION"] = "us-east-1"
    if not env.get("BEDROCK_MODEL_ID"):
        env["BEDROCK_MODEL_ID"] = "xai.grok-4.3"


def _sanitize_env() -> None:
    """Remove variaveis de credenciais do os.environ para evitar
    captura automatica pelo boto3 (IMDS da EC2 tem prioridade).

    Chamado apos load_config() para garantir que apenas as credenciais
    explicitamente passadas nos clientes boto3 sejam usadas.
    """
    for key in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        os.environ.pop(key, None)


def load_config() -> Config:
    """Carrega e valida a configuracao do sistema.

    Returns:
        Config: Objeto de configuracao congelado.

    Raises:
        SystemExit: Se configuracoes obrigatorias estiverem faltando.
    """
    env = _load_env()
    _validate(env)

    cfg = Config(
        aws_region=env.get("REGION", "us-east-1"),
        aws_access_key_id=env.get("AWS_ACCESS_KEY_ID", ""),
        aws_secret_access_key=env.get("AWS_SECRET_ACCESS_KEY", ""),
        bearer_token=env.get("AWS_BEARER_TOKEN_BEDROCK", ""),
        model_id=env.get("BEDROCK_MODEL_ID", "xai.grok-4.3"),
        grok_price_input=float(env.get("GROK_PRICE_INPUT", "0") or "0"),
        grok_price_output=float(env.get("GROK_PRICE_OUTPUT", "0") or "0"),
        grok_price_cache_read=float(env.get("GROK_PRICE_CACHE_READ", "0") or "0"),
        grok_reasoning_effort=env.get("GROK_REASONING_EFFORT", "high"),
    )

    # Remove credenciais do os.environ apos carregar (Principio II)
    _sanitize_env()

    return cfg
