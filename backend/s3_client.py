#!/usr/bin/env python3
"""Cliente S3 para o Radiante v2.

Gerencia upload, download, listagem e delecao de arquivos no bucket
radiante-final, com fallback para modo local (data/) em caso de falha.

As credenciais AWS sao passadas explicitamente via Config.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from backend.config import Config, ROOT_DIR


def _build_s3_params(config: Config) -> dict:
    """Constroi parametros de autenticacao para cliente S3.

    Usa as credenciais explicitamente do Config, sem depender
    de variaveis de ambiente ou profile SSO.
    """
    params: dict = {
        "region_name": config.aws_region,
    }
    if config.aws_access_key_id:
        params["aws_access_key_id"] = config.aws_access_key_id
    if config.aws_secret_access_key:
        params["aws_secret_access_key"] = config.aws_secret_access_key
    return params


def _get_client(config: Config):
    """Retorna cliente S3 configurado."""
    return boto3.client("s3", **(_build_s3_params(config)))


def upload_file(config: Config, file_bytes: bytes, s3_key: str) -> bool:
    """Faz upload de arquivo para o S3.

    Args:
        config: Configuracao do sistema.
        file_bytes: Conteudo do arquivo.
        s3_key: Caminho no S3 (ex: docs/meu-arquivo.pdf).

    Returns:
        True se sucesso, False se falhou.
    """
    try:
        client = _get_client(config)
        client.put_object(Bucket=config.bucket_name, Key=s3_key, Body=file_bytes)
        return True
    except ClientError as e:
        print(f"  [S3] Erro no upload de {s3_key}: {e}", file=sys.stderr)
        return False


def download_file(config: Config, s3_key: str) -> Optional[bytes]:
    """Baixa arquivo do S3.

    Args:
        config: Configuracao do sistema.
        s3_key: Caminho no S3.

    Returns:
        Conteudo do arquivo ou None se nao existir.
    """
    try:
        client = _get_client(config)
        response = client.get_object(Bucket=config.bucket_name, Key=s3_key)
        return response["Body"].read()
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return None
        print(f"  [S3] Erro no download de {s3_key}: {e}", file=sys.stderr)
        return None


def list_files(config: Config, prefix: str) -> list[str]:
    """Lista arquivos em um prefixo S3.

    Args:
        config: Configuracao do sistema.
        prefix: Prefixo S3 (ex: docs/).

    Returns:
        Lista de chaves S3 encontradas.
    """
    try:
        client = _get_client(config)
        keys: list[str] = []
        paginator = client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=config.bucket_name, Prefix=prefix)
        for page in pages:
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys
    except ClientError as e:
        print(f"  [S3] Erro ao listar {prefix}: {e}", file=sys.stderr)
        return []


def delete_files(config: Config, prefix: str) -> int:
    """Deleta todos os arquivos em um prefixo S3.

    Args:
        config: Configuracao do sistema.
        prefix: Prefixo S3 a ser limpo.

    Returns:
        Quantidade de arquivos deletados.
    """
    try:
        client = _get_client(config)
        keys = list_files(config, prefix)
        if not keys:
            return 0
        delete_keys = [{"Key": k} for k in keys]
        response = client.delete_objects(
            Bucket=config.bucket_name,
            Delete={"Objects": delete_keys},
        )
        deleted = len(response.get("Deleted", []))
        return deleted
    except ClientError as e:
        print(f"  [S3] Erro ao deletar {prefix}: {e}", file=sys.stderr)
        return 0


def get_s3_combined_context(config: Config) -> str:
    """Le documentos do diretorio local data/docs/ e extrai texto.

    Se o diretorio local estiver vazio, tenta fallback para S3.

    Args:
        config: Configuracao do sistema.

    Returns:
        String com contexto combinado de todos os documentos.
    """
    from backend.extract import get_document_text, save_markdown

    combined_parts: list[str] = []
    md_dir = config.md_dir
    md_dir.mkdir(parents=True, exist_ok=True)

    docs_dir = config.docs_dir

    # Prioriza diretorio local
    if docs_dir.exists() and any(docs_dir.iterdir()):
        for fpath in sorted(docs_dir.iterdir()):
            if fpath.is_file():
                content = fpath.read_bytes()
                text = get_document_text(config, fpath.name, content)
                combined_parts.append(f"--- Documento: {fpath.name} ---\n{text}")
                save_markdown(md_dir, fpath.name, text)
    else:
        # Fallback para S3
        doc_keys = list_files(config, "docs/")
        if doc_keys:
            for key in sorted(doc_keys):
                content = download_file(config, key)
                if content is None:
                    continue
                filename = Path(key).name
                text = get_document_text(config, filename, content)
                combined_parts.append(f"--- Documento: {filename} ---\n{text}")
                save_markdown(md_dir, filename, text)

    return "\n\n".join(combined_parts)
