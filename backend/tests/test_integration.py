"""Testes de integracao para o Radiante v2."""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from backend.metrics import PipelineMetrics

# Resposta JSON valida para mock das 4 etapas do pipeline
JSON_MOCK = json.dumps({
    "numero_processo": "0000000-00.0000.0.00.0000",
    "autor": "Autor Teste",
    "reu": "Reu Teste",
    "cifras": [
        {"cifra": "Salario", "valor": "R$ 5.000,00",
         "descricao": "Salario base", "probabilidade": "Certa",
         "valor_estimado": "R$ 5.000,00"}
    ],
    "valor_total_estimado": "R$ 5.000,00",
})


class MockStreamChunk:
    """Simula um chunk do streaming OpenAI."""
    def __init__(self, content, usage=None):
        self.choices = [MagicMock()]
        self.choices[0].delta.content = content
        self.choices[0].delta.tool_calls = None
        self.choices[0].finish_reason = "stop"
        self.usage = usage


def _make_openai_stream(text: str):
    """Cria um mock de resposta OpenAI streaming."""
    usage = MagicMock()
    usage.prompt_tokens = 100
    usage.completion_tokens = 50
    usage.prompt_tokens_details = None
    return [MockStreamChunk(text, usage)]


class TestPipelineIntegration:
    """Testa o pipeline completo com dados mockados."""

    @patch("backend.bedrock_client.OpenAI")
    def test_run_once_integration(self, mock_openai, test_config):
        """Pipeline run_once deve completar com mock."""
        from backend.pipeline import run_once

        client = MagicMock()
        mock_chat = MagicMock()
        mock_chat.completions.create.return_value = _make_openai_stream(JSON_MOCK)
        client.chat = mock_chat
        mock_openai.return_value = client

        # Mock S3 upload e PDF
        with patch("backend.pipeline.upload_file", return_value=True):
            with patch("backend.pdf_generator.generate_pdf"):
                result = run_once(
                    test_config,
                    "Contexto de teste para pipeline integrado",
                )

        assert result is not None
        assert result.get("status") == "completed"
        assert "data" in result

    @patch("backend.bedrock_client.OpenAI")
    def test_run_ten_times_integration(self, mock_openai, test_config):
        """Pipeline run_ten_times deve completar com mock."""
        from backend.pipeline import run_ten_times

        client = MagicMock()
        mock_chat = MagicMock()
        mock_chat.completions.create.return_value = _make_openai_stream("Resposta mock")
        client.chat = mock_chat
        mock_openai.return_value = client

        with patch("backend.pipeline.upload_file", return_value=True):
            with patch("backend.pdf_generator.generate_pdf"):
                result = run_ten_times(
                    test_config,
                    "Contexto de teste para 10x",
                )

        assert result is not None
        assert "status" in result

    @patch("backend.bedrock_client.OpenAI")
    def test_pipeline_metrics_propagated(self, mock_openai, test_config):
        """Metricas do pipeline devem ser propagadas corretamente."""
        from backend.pipeline import run_once

        client = MagicMock()
        mock_chat = MagicMock()
        mock_chat.completions.create.return_value = _make_openai_stream(JSON_MOCK)
        client.chat = mock_chat
        mock_openai.return_value = client

        with patch("backend.pipeline.upload_file", return_value=True):
            with patch("backend.pdf_generator.generate_pdf"):
                result = run_once(test_config, "Contexto")

        metrics = result.get("metrics")
        assert metrics is not None
        assert metrics.prompt_tokens > 0
        assert metrics.completion_tokens > 0
        assert "data" in result


class TestExtractIntegration:
    """Testes de integracao para extracao de documentos."""

    def test_pdf_then_docx_then_json(self, test_config, sample_pdf_bytes, sample_docx_bytes, sample_json_bytes):
        """Pipeline de extracao deve processar multiplos formatos."""
        from backend.extract import get_document_text

        pdf_text = get_document_text(test_config, "doc.pdf", sample_pdf_bytes)
        docx_text = get_document_text(test_config, "doc.docx", sample_docx_bytes)
        json_text = get_document_text(test_config, "doc.json", sample_json_bytes)

        assert pdf_text is not None
        assert docx_text is not None
        assert json_text is not None
