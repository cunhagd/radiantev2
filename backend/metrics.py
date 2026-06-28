#!/usr/bin/env python3
"""Observabilidade e metricas do Radiante v2.

Fornece PipelineMetrics para coleta estruturada de dados de
execucao (tokens, custos, erros) e funcoes de calculo de custos.

Os precos sao carregados do Config (via .env) dinamicamente,
pois o modelo Grok 4.3 usa precos variaveis no Bedrock Mantle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.config import Config


@dataclass
class PipelineMetrics:
    """Metricas de uma execucao do pipeline de 4 etapas.

    Attributes:
        prompt_tokens: Total de tokens de entrada.
        completion_tokens: Total de tokens de saida.
        cache_tokens: Total de tokens lidos do cache.
        cost_input: Custo dos tokens de entrada (USD).
        cost_output: Custo dos tokens de saida (USD).
        cost_cache: Custo dos tokens de cache (USD).
        cost_total: Custo total da rodada (USD).
    """

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_tokens: int = 0
    cost_input: float = 0.0
    cost_output: float = 0.0
    cost_cache: float = 0.0
    cost_total: float = 0.0


def calculate_costs(
    config: Config,
    prompt_tokens: int,
    completion_tokens: int,
    cache_tokens: int,
) -> PipelineMetrics:
    """Calcula custos com base nos precos do Grok 4.3 no .env.

    Args:
        config: Config do sistema (com grok_price_*).
        prompt_tokens: Tokens de entrada.
        completion_tokens: Tokens de saida.
        cache_tokens: Tokens de cache de prompt.

    Returns:
        PipelineMetrics com custos calculados.
    """
    price_input = config.grok_price_input
    price_output = config.grok_price_output
    price_cache = config.grok_price_cache_read

    cost_input = (prompt_tokens / 1_000_000) * price_input
    cost_output = (completion_tokens / 1_000_000) * price_output
    cost_cache = (cache_tokens / 1_000_000) * price_cache
    cost_total = cost_input + cost_output + cost_cache

    return PipelineMetrics(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cache_tokens=cache_tokens,
        cost_input=round(cost_input, 6),
        cost_output=round(cost_output, 6),
        cost_cache=round(cost_cache, 6),
        cost_total=round(cost_total, 6),
    )


def merge_metrics(metrics_list: list[PipelineMetrics]) -> PipelineMetrics:
    """Soma metricas de multiplas etapas.

    Args:
        metrics_list: Lista de PipelineMetrics de cada etapa.

    Returns:
        PipelineMetrics consolidado.
    """
    total = PipelineMetrics()
    for m in metrics_list:
        total.prompt_tokens += m.prompt_tokens
        total.completion_tokens += m.completion_tokens
        total.cache_tokens += m.cache_tokens
        total.cost_input += m.cost_input
        total.cost_output += m.cost_output
        total.cost_cache += m.cost_cache
        total.cost_total += m.cost_total

    total.cost_input = round(total.cost_input, 6)
    total.cost_output = round(total.cost_output, 6)
    total.cost_cache = round(total.cost_cache, 6)
    total.cost_total = round(total.cost_total, 6)
    return total


def format_metrics_report(metrics: PipelineMetrics) -> str:
    """Formata metricas para exibicao amigavel.

    Args:
        metrics: PipelineMetrics a ser formatado.

    Returns:
        String formatada com as metricas.
    """
    return (
        f"Tokens: {metrics.prompt_tokens} in / {metrics.completion_tokens} out"
        f" / {metrics.cache_tokens} cache\n"
        f"Custo: ${metrics.cost_input:.6f} in / ${metrics.cost_output:.6f} out"
        f" / ${metrics.cost_cache:.6f} cache\n"
        f"Total: ${metrics.cost_total:.6f}"
    )
