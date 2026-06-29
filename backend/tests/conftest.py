"""Fixtures compartilhadas para os testes do Radiante v2."""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

# Garante que o diretorio raiz esta no path para imports
_THIS_DIR = Path(__file__).resolve().parent  # backend/tests
_ROOT_DIR = _THIS_DIR.parent.parent  # c:/radiantev2
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

import pytest

from backend.config import Config


@pytest.fixture
def mock_env() -> Generator[None, None, None]:
    """Configura variaveis de ambiente minimas para teste (Grok/Mantle)."""
    env_vars = {
        "AWS_BEARER_TOKEN_BEDROCK": "test-bearer-token",
        "BEDROCK_MODEL_ID": "xai.grok-4.3",
        "AWS_DEFAULT_REGION": "us-east-1",
        "GROK_PRICE_INPUT": "0.00000125",
        "GROK_PRICE_OUTPUT": "0.00000250",
        "GROK_PRICE_CACHE_READ": "0.00000020",
        "GROK_REASONING_EFFORT": "high",
    }
    for k, v in env_vars.items():
        os.environ[k] = v
    yield
    for k in env_vars:
        os.environ.pop(k, None)


@pytest.fixture
def test_config(mock_env: None) -> Config:
    """Retorna uma Config valida para testes."""
    from backend.config import load_config
    return load_config()


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Retorna bytes de um PDF minimo valido."""
    return (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
        b"/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n"
        b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
        b"5 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td"
        b" (Hello World) Tj ET\nendstream\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n"
        b"0000000009 00000 n \n0000000058 00000 n \n"
        b"0000000115 00000 n \n0000000266 00000 n \n"
        b"0000000359 00000 n \ntrailer<</Size 6/Root 1 0 R>>\n"
        b"startxref\n454\n%%EOF"
    )


@pytest.fixture
def sample_docx_bytes() -> bytes:
    """Retorna bytes de um DOCX valido (minimo)."""
    import zipfile
    import io

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", (
            b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            b'<w:body><w:p><w:r><w:t>Teste DOCX</w:t></w:r></w:p></w:body>'
            b'</w:document>'
        ))
        zf.writestr("[Content_Types].xml", (
            b'<?xml version="1.0"?>'
            b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            b'<Default Extension="xml" ContentType="application/xml"/>'
            b'</Types>'
        ))
    return buf.getvalue()


@pytest.fixture
def sample_json_bytes() -> bytes:
    """Retorna bytes de um JSON valido."""
    return json.dumps({
        "numero_processo": "0000000-00.0000.0.00.0000",
        "autor": "Teste Autor",
        "reu": "Teste Reu",
    }).encode("utf-8")


@pytest.fixture
def mock_openai() -> Generator[MagicMock, None, None]:
    """Mock para OpenAI client usado pelo bedrock_client."""
    with patch("backend.bedrock_client.OpenAI") as mock:
        client = MagicMock()

        # Mock chat completion com streaming
        def make_stream(text: str = "Resposta mockada") -> list:
            class MockChunk:
                def __init__(self, content):
                    self.choices = [MagicMock()]
                    self.choices[0].delta.content = content
                    self.choices[0].delta.tool_calls = None
                    self.choices[0].finish_reason = "stop"
                    self.usage = MagicMock()
                    self.usage.prompt_tokens = 100
                    self.usage.completion_tokens = 50
                    self.usage.prompt_tokens_details = None

            return [MockChunk(text)]

        mock_chat = MagicMock()
        mock_chat.completions.create.side_effect = lambda **kw: make_stream()
        client.chat = mock_chat
        mock.return_value = client
        yield mock


@pytest.fixture
def empty_history() -> Generator[None, None, None]:
    """Limpa historico de execucao antes do teste."""
    from backend.pipeline import _execution_history
    _execution_history.clear()
    yield
    _execution_history.clear()
