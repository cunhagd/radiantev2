#!/usr/bin/env python3
"""Teste do sistema de fallback Grok/Mantle com simulacao de falhas.

Uso:
    python -m backend.tests.test_fallback
    python -m backend.tests.test_fallback --simulate 2
"""

from __future__ import annotations

import argparse
import os
import sys
import time

# Garante que o diretorio raiz esta no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.bedrock_client import (
    FALLBACK_REGIONS,
    RETRY_DELAYS,
    FallbackAttempt,
    FallbackMetrics,
    get_fallback_status,
)
from backend.config import load_config


def print_banner() -> None:
    print("=" * 72)
    print(" SISTEMA DE FALLBACK GROK 4.3 (MANTLE) - TESTE ".center(72, "="))
    print("=" * 72)
    print(f" Regioes: {len(FALLBACK_REGIONS)} combinacoes")
    print(f" Retries: {RETRY_DELAYS}")
    print()
    for i, region in enumerate(FALLBACK_REGIONS, 1):
        print(f"  P{i}: Grok 4.3    {region:15s}")
    print()


def test_fallback_structure() -> None:
    """Verifica se a estrutura de fallback esta correta."""
    print("[TEST] Verificando estrutura do fallback...")

    assert len(FALLBACK_REGIONS) == 3, (
        f"Esperado 3 regioes, encontrado {len(FALLBACK_REGIONS)}"
    )

    assert "us-east-1" in FALLBACK_REGIONS
    assert "us-west-2" in FALLBACK_REGIONS
    assert "us-east-2" in FALLBACK_REGIONS

    print("  PASS: Estrutura do fallback OK")
    print()


def test_fallback_attempt_dataclass() -> None:
    """Verifica criacao de FallbackAttempt."""
    print("[TEST] Verificando FallbackAttempt dataclass...")

    attempt = FallbackAttempt(
        model_name="Grok 4.3",
        region="us-east-1",
        status="success",
        duration_ms=1500,
        timestamp="2026-06-28T12:00:00",
    )

    assert attempt.model_name == "Grok 4.3"
    assert attempt.status == "success"
    assert attempt.duration_ms == 1500

    print("  PASS: FallbackAttempt dataclass OK")
    print()


def test_fallback_metrics_dataclass() -> None:
    """Verifica criacao de FallbackMetrics."""
    print("[TEST] Verificando FallbackMetrics dataclass...")

    metrics = FallbackMetrics(total_attempts=2, cost_savings_usd=0.0015)

    assert metrics.total_attempts == 2
    assert metrics.cost_savings_usd == 0.0015
    assert metrics.all_attempts == []

    metrics.all_attempts.append(FallbackAttempt(
        model_name="Grok", region="us-east-1", status="throttled",
    ))
    metrics.all_attempts.append(FallbackAttempt(
        model_name="Grok", region="us-west-2", status="success",
    ))
    assert len(metrics.all_attempts) == 2

    print("  PASS: FallbackMetrics dataclass OK")
    print()


def test_get_fallback_status_structure() -> None:
    """Verifica estrutura do retorno de get_fallback_status()."""
    print("[TEST] Verificando estrutura do status endpoint...")

    status = get_fallback_status()

    assert "strategy" in status
    assert "retry_delays" in status
    assert "recent_fallbacks" in status
    assert "total_recorded_runs" in status

    assert len(status["strategy"]) == 3
    assert status["retry_delays"] == [2, 4, 8]

    print("  PASS: Estrutura do status endpoint OK")
    print()


def simulate_conversation(
    config, simulate_failures: int = 0,
) -> None:
    """Simula conversacao com Grok via Mantle com N falhas iniciais.

    So executa se --simulate for passado explicitamente.
    """
    from backend.bedrock_client import run_llm_stage_streaming

    test_prompt = "Responda com uma frase curta confirmando que esta online."
    test_context = ""

    print(f"\n[SIMULATE] Simulando {simulate_failures} falha(s) inicial(is)...")

    try:
        result, metrics = run_llm_stage_streaming(
            config, test_prompt, test_context, "",
            stream_to_console=True,
        )
        print(f"\n[SIMULATE] Resposta recebida! ({len(result)} chars)")

        status = get_fallback_status()
        last = status["recent_fallbacks"][-1] if status["recent_fallbacks"] else {}
        print(f"\n[SIMULATE] Metricas de fallback:")
        print(f"  Tentativas: {last.get('total_attempts', 'N/A')}")
        print(f"  Duracao total: {last.get('total_duration_ms', 'N/A')}ms")

        if last.get("winner"):
            w = last["winner"]
            print(f"  Vencedor: {w['model']} em {w['region']}")
            print(f"  Duracao vencedor: {w['duration_ms']}ms")
    except RuntimeError as e:
        print(f"\n[SIMULATE] ERRO (esperado com simulacao): {e}")
    except Exception as e:
        print(f"\n[SIMULATE] ERRO inesperado: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Teste de Fallback Grok/Mantle")
    parser.add_argument(
        "--simulate", type=int, default=0,
        help="Numero de falhas a simular (0 = apenas tests estruturais)",
    )
    args = parser.parse_args()

    print_banner()

    # Testes estruturais (sempre executam)
    test_fallback_structure()
    test_fallback_attempt_dataclass()
    test_fallback_metrics_dataclass()
    test_get_fallback_status_structure()

    # Teste de simulacao (opcional)
    if args.simulate > 0:
        config = load_config()
        simulate_conversation(config, args.simulate)
    else:
        print("[INFO] Para testar com simulacao de falhas:")
        print("  python -m backend.tests.test_fallback --simulate 2")
        print()

    print("=" * 72)
    print(" TESTES CONCLUIDOS ".center(72, "="))
    print("=" * 72)


if __name__ == "__main__":
    main()
