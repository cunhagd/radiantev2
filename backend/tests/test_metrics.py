"""Testes para backend/metrics.py."""
from __future__ import annotations

from unittest.mock import MagicMock

from backend.metrics import (
    PipelineMetrics, calculate_costs, merge_metrics, format_metrics_report,
)
from backend.config import Config


def _make_config(price_input=3.0, price_output=15.0, price_cache=0.30):
    """Helper para criar Config mockada com precos."""
    return MagicMock(spec=Config(
        grok_price_input=price_input,
        grok_price_output=price_output,
        grok_price_cache_read=price_cache,
    ))


class TestPipelineMetrics:
    def test_default_values(self):
        """Metricas devem comecar com valores padrao 0."""
        m = PipelineMetrics()
        assert m.prompt_tokens == 0
        assert m.completion_tokens == 0
        assert m.cache_tokens == 0
        assert m.cost_total == 0.0

    def test_custom_values(self):
        """Metricas devem aceitar valores customizados."""
        m = PipelineMetrics(
            prompt_tokens=1000,
            completion_tokens=500,
            cost_total=0.015,
        )
        assert m.prompt_tokens == 1000
        assert m.cost_total == 0.015


class TestCalculateCosts:
    def test_grok_cost(self, test_config):
        """Calcular custo Grok com tokens."""
        # Usa 1M tokens para preencher precos pequenos (micro-dolar por token)
        m = calculate_costs(test_config, prompt_tokens=1_000_000, completion_tokens=500_000, cache_tokens=0)
        assert m.prompt_tokens == 1_000_000
        assert m.completion_tokens == 500_000
        # Precos do .env (GROK_PRICE_INPUT=0.00000125, GROK_PRICE_OUTPUT=0.00000250)
        expected_input = 0.00000125
        expected_output = 0.00000125
        assert abs(m.cost_input - expected_input) < 0.0001
        assert abs(m.cost_output - expected_output) < 0.0001
        assert m.cost_total > 0

    def test_cache_cost_reduction(self, test_config):
        """Cache tokens devem ser registrados separadamente."""
        m = calculate_costs(test_config, 1000, 500, 200)
        assert m.cache_tokens == 200

    def test_zero_tokens(self, test_config):
        """Zero tokens deve resultar em custo zero."""
        m = calculate_costs(test_config, 0, 0, 0)
        assert m.cost_total == 0.0


class TestMergeMetrics:
    def test_merge_two_metrics(self):
        """Merge de 2 metricas deve somar tokens e custos."""
        m1 = PipelineMetrics(prompt_tokens=100, completion_tokens=50, cost_total=0.005)
        m2 = PipelineMetrics(prompt_tokens=200, completion_tokens=100, cost_total=0.010)
        merged = merge_metrics([m1, m2])
        assert merged.prompt_tokens == 300
        assert merged.completion_tokens == 150
        assert merged.cost_total == 0.015

    def test_merge_empty_list(self):
        """Merge de lista vazia deve retornar metricas vazias."""
        merged = merge_metrics([])
        assert merged.prompt_tokens == 0

    def test_merge_single(self):
        """Merge de lista com 1 item deve retornar o mesmo."""
        m = PipelineMetrics(prompt_tokens=500, cost_total=0.01)
        merged = merge_metrics([m])
        assert merged.prompt_tokens == 500


class TestFormatMetricsReport:
    def test_format_contains_keys(self):
        """Relatorio formatado deve conter informacoes chave."""
        m = PipelineMetrics(prompt_tokens=1000, completion_tokens=500, cost_total=0.015)
        report = format_metrics_report(m)
        assert "Tokens" in report
        assert "Custo" in report
        assert str(m.cost_total) in report

    def test_format_empty_metrics(self):
        """Metricas vazias devem ser formatadas sem erro."""
        m = PipelineMetrics()
        report = format_metrics_report(m)
        assert "0" in report
