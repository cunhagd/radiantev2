"""Testes para backend/bedrock_client.py."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from backend.bedrock_client import (
    FALLBACK_REGIONS,
    RETRY_DELAYS,
    FallbackAttempt,
    FallbackMetrics,
    get_fallback_status,
    run_llm_stage_streaming,
)


class TestFallbackRegions:
    def test_three_regions(self):
        """Deve ter exatamente 3 regioes de fallback."""
        assert len(FALLBACK_REGIONS) == 3

    def test_contains_expected_regions(self):
        """Regioes esperadas devem estar presentes."""
        assert "us-east-1" in FALLBACK_REGIONS
        assert "us-west-2" in FALLBACK_REGIONS
        assert "us-east-2" in FALLBACK_REGIONS

    def test_retry_delays_structure(self):
        """Retry deve ter 3 delays: 2s, 4s, 8s."""
        assert RETRY_DELAYS == [2, 4, 8]


class TestFallbackDataclasses:
    def test_fallback_attempt_defaults(self):
        """FallbackAttempt deve ter valores padrao."""
        a = FallbackAttempt()
        assert a.model_name == ""
        assert a.status == ""
        assert a.duration_ms == 0

    def test_fallback_attempt_custom(self):
        """FallbackAttempt com valores customizados."""
        a = FallbackAttempt(
            model_name="Grok 4.3",
            region="us-east-1",
            status="success",
            duration_ms=1500,
            timestamp="2026-01-01T00:00:00",
        )
        assert a.model_name == "Grok 4.3"
        assert a.duration_ms == 1500

    def test_fallback_metrics_defaults(self):
        """FallbackMetrics deve comecar vazio."""
        m = FallbackMetrics()
        assert m.total_attempts == 0
        assert m.successful_attempt is None
        assert m.all_attempts == []
        assert m.cost_savings_usd == 0.0

    def test_fallback_metrics_with_attempts(self):
        """FallbackMetrics deve acumular tentativas."""
        m = FallbackMetrics(total_attempts=2)
        m.all_attempts.append(FallbackAttempt(status="throttled"))
        m.all_attempts.append(FallbackAttempt(status="success"))
        m.successful_attempt = m.all_attempts[-1]
        assert len(m.all_attempts) == 2
        assert m.successful_attempt.status == "success"


class TestGetFallbackStatus:
    def test_status_structure(self):
        """get_fallback_status deve retornar estrutura esperada."""
        status = get_fallback_status()
        assert "strategy" in status
        assert "retry_delays" in status
        assert "recent_fallbacks" in status
        assert "total_recorded_runs" in status

    def test_status_strategy_matches_regions(self):
        """Estrategia no status deve refletir FALLBACK_REGIONS."""
        status = get_fallback_status()
        assert len(status["strategy"]) == len(FALLBACK_REGIONS)

    def test_retry_delays_in_status(self):
        """Retry delays devem estar no status."""
        status = get_fallback_status()
        assert status["retry_delays"] == [2, 4, 8]


class TestRunLlmStage:
    def test_successful_call(self, test_config, mock_openai):
        """Chamada bem-sucedida deve retornar texto e metricas."""
        result, metrics = run_llm_stage_streaming(
            test_config, "system prompt", "user msg", "context",
            stream_to_console=False,
        )
        assert result == "Resposta mockada"
        assert metrics is not None
        assert metrics.prompt_tokens == 100
        assert metrics.completion_tokens == 50

    def test_raises_on_all_failures(self, test_config):
        """Se todas as regioes falharem, deve levantar RuntimeError."""
        with patch("backend.bedrock_client.OpenAI") as mock:
            client = MagicMock()
            mock_chat = MagicMock()
            mock_chat.completions.create.side_effect = Exception("API Error")
            client.chat = mock_chat
            mock.return_value = client

            with pytest.raises(RuntimeError, match="todas as regioes"):
                run_llm_stage_streaming(
                    test_config, "prompt", "msg", "ctx",
                    stream_to_console=False,
                )
