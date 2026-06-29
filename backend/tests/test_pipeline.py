"""Testes para backend/pipeline.py."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from backend.metrics import PipelineMetrics


class TestExecutionHistory:
    def test_history_starts_empty(self, empty_history):
        """Historico deve comecar vazio."""
        from backend.pipeline import get_execution_history
        assert get_execution_history() == []

    def test_record_execution(self, empty_history):
        """Record deve adicionar entrada no historico."""
        from backend.pipeline import record_execution, get_execution_history
        record_execution("once", "completed", PipelineMetrics(prompt_tokens=100))
        hist = get_execution_history()
        assert len(hist) == 1
        assert hist[0]["mode"] == "once"
        assert hist[0]["status"] == "completed"

    def test_get_last_metrics(self, empty_history):
        """get_last_metrics deve retornar metricas da ultima execucao."""
        from backend.pipeline import record_execution, get_last_metrics
        assert get_last_metrics() is None

        m = PipelineMetrics(prompt_tokens=500, cost_total=0.01)
        record_execution("once", "completed", m)
        last = get_last_metrics()
        assert last is not None
        assert last["prompt_tokens"] == 500

    def test_history_max_size(self, empty_history):
        """Historico nao deve exceder _MAX_HISTORY."""
        from backend.pipeline import record_execution, get_execution_history, _MAX_HISTORY
        for i in range(_MAX_HISTORY + 10):
            record_execution("once", "completed", PipelineMetrics(prompt_tokens=i))
        hist = get_execution_history()
        assert len(hist) <= _MAX_HISTORY

    def test_record_with_error(self, empty_history):
        """Record deve registrar erros."""
        from backend.pipeline import record_execution, get_execution_history
        from backend.metrics import PipelineMetrics
        record_execution("once", "error", PipelineMetrics(), error="Falha na etapa 1")
        hist = get_execution_history()
        assert hist[0]["status"] == "error"
        assert "Falha na etapa 1" in hist[0]["error"]


class TestExtractJson:
    def test_extract_json_from_markdown(self):
        """Deve extrair JSON de dentro de bloco markdown."""
        from backend.pipeline import extract_json_from_markdown
        text = 'Resposta\n```json\n{"key": "value"}\n```\nFim'
        result = extract_json_from_markdown(text)
        assert result is not None
        assert result["key"] == "value"

    def test_extract_json_no_block(self):
        """Sem bloco markdown, deve retornar None."""
        from backend.pipeline import extract_json_from_markdown
        text = "Resposta sem JSON"
        result = extract_json_from_markdown(text)
        assert result is None

    def test_extract_json_invalid(self):
        """JSON invalido deve retornar None."""
        from backend.pipeline import extract_json_from_markdown
        text = '```json\n{invalid json}\n```'
        result = extract_json_from_markdown(text)
        assert result is None


class TestProbabilityLabel:
    def test_remota_probabilidade(self):
        """ratio entre 0.01 e 0.20 deve ser 'Remota'."""
        from backend.pipeline import calculate_probability_label
        # avg_base = 0 retorna "Remota" (sem base para comparar)
        assert calculate_probability_label(0, 0) == "Remota"
        # ratio entre 0.01 e 0.20
        assert calculate_probability_label(0.1, 1.0) == "Remota"  # ratio 0.1
        assert calculate_probability_label(0.19, 1.0) == "Remota"  # ratio 0.19

    def test_possivel_probabilidade(self):
        """0.20 < ratio <= 0.50 deve ser 'Possivel'."""
        from backend.pipeline import calculate_probability_label
        assert calculate_probability_label(0.30, 1.0) == "Possivel"  # ratio 0.30 > 0.20
        assert calculate_probability_label(0.50, 1.0) == "Possivel"  # ratio 0.50, nao > 0.50, entao > 0.20

    def test_provavel_probabilidade(self):
        """0.50 < ratio <= 0.80 deve ser 'Provavel'."""
        from backend.pipeline import calculate_probability_label
        assert calculate_probability_label(0.60, 1.0) == "Provavel"  # ratio 0.60 > 0.50
        assert calculate_probability_label(0.75, 1.0) == "Provavel"  # ratio 0.75 > 0.50
        assert calculate_probability_label(0.80, 1.0) == "Provavel"  # ratio 0.80, nao > 0.80, entao > 0.50

    def test_muito_provavel(self):
        """ratio > 0.80 deve ser 'Certa'."""
        from backend.pipeline import calculate_probability_label
        assert calculate_probability_label(0.81, 1.0) == "Certa"
        assert calculate_probability_label(1.0, 1.0) == "Certa"


class TestMonetaryFormat:
    def test_parse_monetary(self):
        """Deve parsear string monetaria brasileira."""
        from backend.pipeline import parse_monetary
        assert parse_monetary("R$ 1.500,00") == 1500.0
        assert parse_monetary("R$ 1.234.567,89") == 1234567.89
        # Formato alternativo
        assert parse_monetary("1500,00") == 1500.0

    def test_format_monetary(self):
        """Deve formatar numero para string brasileira."""
        from backend.pipeline import format_monetary
        assert format_monetary(1500.0) == "1.500,00"
        assert format_monetary(1234567.89) == "1.234.567,89"

    def test_parse_invalid_returns_zero(self):
        """Valor invalido deve retornar 0."""
        from backend.pipeline import parse_monetary
        assert parse_monetary("") == 0.0
        assert parse_monetary("N/A") == 0.0

    def test_aggregate_results_empty(self):
        """aggregate_results com lista vazia deve retornar dict vazio."""
        from backend.pipeline import aggregate_results
        assert aggregate_results([]) == {}
