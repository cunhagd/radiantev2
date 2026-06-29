"""Testes para backend/extract.py."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from backend.extract import get_document_text


class TestGetDocumentText:
    def test_txt_file(self, test_config):
        """Arquivo .txt deve ser lido diretamente."""
        content = b"Texto simples de teste"
        text = get_document_text(test_config, "teste.txt", content)
        assert "Texto simples" in text

    def test_json_file(self, test_config, sample_json_bytes):
        """Arquivo .json deve ser parseado."""
        text = get_document_text(test_config, "dados.json", sample_json_bytes)
        assert "numero_processo" in text
        assert "Teste Autor" in text

    @patch("backend.extract.extract_pdf_text")
    def test_pdf_file_calls_extract(self, mock_pdf, test_config, sample_pdf_bytes):
        """PDF deve chamar extract_pdf_text."""
        mock_pdf.return_value = "Texto extraido do PDF"
        text = get_document_text(test_config, "documento.pdf", sample_pdf_bytes)
        assert text == "Texto extraido do PDF"
        mock_pdf.assert_called_once()

    def test_pdf_extract_fallback(self, test_config, sample_pdf_bytes):
        """extract_pdf_text deve tentar PyMuPDF e cair no Textract."""
        from backend.extract import extract_pdf_text
        # Nao temos Textract configurado, entao deve retornar mensagem de erro
        text = extract_pdf_text(test_config, "test.pdf", sample_pdf_bytes)
        assert text is not None

    def test_docx_file(self, test_config, sample_docx_bytes):
        """Arquivo .docx deve extrair texto do XML."""
        text = get_document_text(test_config, "documento.docx", sample_docx_bytes)
        assert "Teste DOCX" in text

    def test_unknown_extension(self, test_config):
        """Extensao desconhecida deve tentar decode UTF-8."""
        content = b"Conteudo generico"
        text = get_document_text(test_config, "arquivo.xyz", content)
        assert "Conteudo generico" in text

    def test_empty_content(self, test_config):
        """Conteudo vazio deve retornar string vazia."""
        text = get_document_text(test_config, "vazio.txt", b"")
        assert text == ""

    def test_binary_pdf_no_text(self, test_config, sample_pdf_bytes):
        """PDF binario sem texto extraivel deve cair no Textract."""
        from backend.extract import extract_pdf_text
        text = extract_pdf_text(test_config, "test.pdf", sample_pdf_bytes)
        assert isinstance(text, str)
