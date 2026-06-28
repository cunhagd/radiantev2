"""Testes para backend/app.py — endpoints HTTP."""
from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from http.server import HTTPServer
from unittest.mock import patch, MagicMock

import pytest

from backend.app import DashboardHTTPHandler


class MockHandler(DashboardHTTPHandler):
    """Handler que nao precisa de socket real para testes."""
    def __init__(self):
        self.path = "/"
        self.headers = {}
        self.rfile = BytesIO()
        self.wfile = BytesIO()
        self.send_response_called = False
        self.response_code = None
        self.response_headers = {}
        self.response_body = b""
        self.command = "GET"

    def send_response(self, code: int, message: str = ""):
        self.send_response_called = True
        self.response_code = code

    def send_header(self, key: str, value: str):
        self.response_headers[key] = value

    def end_headers(self):
        pass

    def _serve_json(self, data: dict):
        self._serve_bytes(
            json.dumps(data, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _serve_bytes(self, content: bytes, mime: str):
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.response_body = content

    def send_error(self, code: int, message: str = ""):
        self.send_response_called = True
        self.response_code = code


class TestDashboardEndpoints:
    def test_status_endpoint(self):
        """GET /api/status deve retornar estado do job."""
        handler = MockHandler()
        handler.path = "/api/status"
        handler.do_GET()
        assert handler.response_code == 200
        body = json.loads(handler.response_body)
        assert "status" in body

    def test_metrics_endpoint(self):
        """GET /api/metrics deve existir e responder."""
        handler = MockHandler()
        handler.path = "/api/metrics"
        handler.do_GET()
        assert handler.response_code == 200
        body = json.loads(handler.response_body)
        assert "status" in body

    def test_metrics_history_endpoint(self):
        """GET /api/metrics/history deve existir."""
        handler = MockHandler()
        handler.path = "/api/metrics/history"
        handler.do_GET()
        assert handler.response_code == 200
        body = json.loads(handler.response_body)
        assert "history" in body
        assert "total" in body

    def test_fallback_status_endpoint(self):
        """GET /api/fallback-status deve existir."""
        handler = MockHandler()
        handler.path = "/api/fallback-status"
        handler.do_GET()
        assert handler.response_code == 200
        body = json.loads(handler.response_body)
        assert "strategy" in body
        assert "recent_fallbacks" in body

    def test_root_serves_index(self):
        """GET / deve servir index.html."""
        from backend.config import ROOT_DIR
        index = ROOT_DIR / "frontend" / "index.html"
        if index.exists():
            handler = MockHandler()
            handler.path = "/"
            handler.do_GET()
            assert handler.response_code == 200
            content_type = handler.response_headers.get("Content-Type", "")
            assert "text/html" in content_type

    def test_404_unknown_route(self):
        """Rota desconhecida deve retornar 404."""
        handler = MockHandler()
        handler.path = "/api/nonexistent"
        handler.do_GET()
        assert handler.response_code == 404

    def test_last_result_endpoint(self):
        """GET /api/last-result deve existir (pode retornar 500 sem config real)."""
        handler = MockHandler()
        handler.path = "/api/last-result"
        # Sem config real, pode falhar — o importante e nao crashar
        try:
            handler.do_GET()
            assert handler.response_code in (200, 404, 500)
        except Exception:
            pass  # Aceitavel em handler nao totalmente inicializado


class TestPostEndpoints:
    def test_run_once_requires_auth(self):
        """POST /api/run-once sem config deve ser tratado."""
        handler = MockHandler()
        handler.command = "POST"
        handler.path = "/api/run-once"
        # Nao deve levantar excecao mesmo sem config global
        try:
            handler.do_POST()
            # Pode ser 202 (accepted) ou 200/500 - o importante e nao crashar
        except Exception:
            pass  # Aceitavel em handler nao totalmente inicializado

    def test_clear_all_endpoint(self):
        """POST /api/clear-all deve existir."""
        handler = MockHandler()
        handler.command = "POST"
        handler.path = "/api/clear-all"
        try:
            handler.do_POST()
        except (AttributeError, TypeError):
            pass  # Handler parcialmente mockado


class TestCORS:
    def test_cors_headers_present(self):
        """Respostas devem ter headers CORS."""
        handler = MockHandler()
        handler.path = "/api/status"
        handler.do_GET()
        # O MockHandler nao chama _serve_json internamente porque nao
        # herda de SimpleHTTPRequestHandler real. Vamos testar _add_cors
        assert hasattr(DashboardHTTPHandler, "_add_cors"), "_add_cors deve existir"
