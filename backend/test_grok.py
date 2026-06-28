#!/usr/bin/env python3
"""Teste rapido de conexao com Grok 4.3 via Bedrock Mantle.

Faz uma chamada simples ao modelo xai.grok-4.3 e exibe a resposta.
Usa as credenciais AWS do ambiente atual (SSO, env vars, etc.).

Uso:
    python backend/test_grok.py
    python backend/test_grok.py --no-stream   (modo sem streaming)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Garante que a raiz do projeto esta no path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import load_config
from backend.bedrock_client import get_fallback_status


def test_grok(use_stream: bool = True) -> None:
    """Testa conexao com Grok 4.3 via Mantle."""
    print("=" * 60)
    print(" TESTE DE CONEXAO - GROK 4.3 (BEDROCK MANTLE) ".center(60, "="))
    print("=" * 60)

    # Carrega config
    try:
        config = load_config()
    except SystemExit as e:
        print(f"\n  ERRO ao carregar config: {e}")
        sys.exit(1)

    print(f"\n  Modelo: {config.model_id}")
    print(f"  Regiao padrao: {config.aws_region}")
    print(f"  Auth: {'Bearer Token' if config.bearer_token else 'AWS SigV4 (SSO)'}")
    print(f"  Reasoning effort: {config.grok_reasoning_effort}")
    print()

    # Importa a funcao de chamada
    from backend.bedrock_client import run_llm_stage_streaming

    prompt = "Voce e um assistente util. Responda APENAS com 'Online! Grok 4.3 esta funcionando.' e mais nada."
    user_msg = "Confirme que esta online."
    context = ""

    try:
        print("  Enviando requisicao para Grok 4.3...")
        print(f"  {'[STREAMING]' if use_stream else '[AGUARDANDO]'}")
        print()

        result, metrics = run_llm_stage_streaming(
            config, prompt, user_msg, context,
            stream_to_console=use_stream,
        )

        print()
        print("-" * 60)
        print(" RESPOSTA ".center(60, "-"))
        print("-" * 60)
        print(f"  {result}")
        print("-" * 60)

        # Exibe metricas
        print()
        print(" METRICAS ".center(60, "-"))
        print(f"  Tokens input:  {metrics.prompt_tokens}")
        print(f"  Tokens output: {metrics.completion_tokens}")
        print(f"  Tokens cache:  {metrics.cache_tokens}")
        print(f"  Custo input:   ${metrics.cost_input:.8f}")
        print(f"  Custo output:  ${metrics.cost_output:.8f}")
        print(f"  Custo total:   ${metrics.cost_total:.8f}")
        print("-" * 60)

        # Exibe status do fallback
        status = get_fallback_status()
        last = status["recent_fallbacks"][-1] if status["recent_fallbacks"] else {}
        print()
        print(" FALLBACK ".center(60, "-"))
        print(f"  Tentativas: {last.get('total_attempts', 'N/A')}")
        print(f"  Duracao total: {last.get('total_duration_ms', 'N/A')}ms")
        if last.get("winner"):
            w = last["winner"]
            print(f"  Regiao vencedora: {w['region']}")
            print(f"  Duracao: {w['duration_ms']}ms")
        print("-" * 60)

        print()
        print("  TESTE CONCLUIDO COM SUCESSO!")
        return 0

    except RuntimeError as e:
        print(f"\n  ERRO: {e}")
        print()
        print("  POSSIVEIS CAUSAS:")
        print("  1. Modelo xai.grok-4.3 nao esta habilitado na conta AWS")
        print("     -> Habilite em: https://console.aws.amazon.com/bedrock/home#/model-access")
        print("  2. Credenciais AWS nao estao configuradas corretamente")
        print("     -> Verifique: aws sts get-caller-identity")
        print("  3. Regiao nao suportada (use us-east-1)")
        print()

        # Tenta diagnosticar
        _diagnose()
        return 1

    except Exception as e:
        print(f"\n  ERRO INESPERADO: {type(e).__name__}: {e}")
        print()
        _diagnose()
        return 1


def _diagnose() -> None:
    """Tenta diagnosticar problemas de conexao."""
    import subprocess

    print(" DIAGNOSTICO ".center(60, "-"))

    # 1. Verifica credenciais AWS
    try:
        r = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            import json
            data = json.loads(r.stdout)
            print(f"  AWS Account: {data.get('Account', '?')}")
            print(f"  AWS User/Role: {data.get('Arn', '?')}")
        else:
            print(f"  AWS CLI error: {r.stderr.strip()[:100]}")
    except FileNotFoundError:
        print("  AWS CLI nao encontrado")
    except Exception as e:
        print(f"  AWS CLI: {e}")

    # 2. Verifica profile e regiao
    print(f"  AWS_PROFILE: {os.getenv('AWS_PROFILE', '(nao definido)')}")
    print(f"  AWS_DEFAULT_REGION: {os.getenv('AWS_DEFAULT_REGION', '(nao definido)')}")

    print("-" * 60)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Teste rapido de conexao com Grok 4.3 via Bedrock Mantle",
    )
    parser.add_argument(
        "--no-stream", action="store_true",
        help="Desabilita streaming (modo aguardar resposta completa)",
    )
    args = parser.parse_args()

    sys.exit(test_grok(use_stream=not args.no_stream))


if __name__ == "__main__":
    main()
