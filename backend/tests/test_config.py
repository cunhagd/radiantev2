"""Testes para backend/config.py."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestConfigLoading:
    def test_load_config_success(self, mock_env):
        """Deve carregar config com variaveis de ambiente."""
        from backend.config import load_config
        config = load_config()
        assert config.bearer_token == "test-bearer-token"
        assert config.model_id == "xai.grok-4.3"
        assert config.grok_reasoning_effort == "high"
        assert config.aws_access_key_id == "test-access-key"
        assert config.aws_secret_access_key == "test-secret-key"

    def test_load_config_missing_bearer_token_raises(self):
        """Deve levantar erro se bearer token faltar."""
        from backend.config import _validate
        missing = {
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
        }
        try:
            _validate(missing)
            assert False, "Deveria ter saido"
        except SystemExit:
            pass

    def test_load_config_missing_access_keys_does_not_raise(self):
        """Nao deve levantar erro se access keys faltarem (IMDS/EC2)."""
        from backend.config import _validate, load_config
        import io, sys
        # Simula que bearer token existe mas access keys nao
        missing = {
            "AWS_BEARER_TOKEN_BEDROCK": "test-token",
            "REGION": "us-east-1",
        }
        # Nao deve chamar sys.exit
        _validate(missing)

    def test_sanitize_env_removes_credentials(self):
        """Deve remover AWS_ACCESS_KEY_ID e SECRET do os.environ."""
        os.environ["AWS_ACCESS_KEY_ID"] = "should-be-removed"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "should-be-removed"
        from backend.config import _sanitize_env
        _sanitize_env()
        assert "AWS_ACCESS_KEY_ID" not in os.environ
        assert "AWS_SECRET_ACCESS_KEY" not in os.environ

    def test_root_dir_exists(self):
        """ROOT_DIR deve apontar para diretorio existente."""
        from backend.config import ROOT_DIR
        assert ROOT_DIR.exists()
        assert (ROOT_DIR / "backend").exists()
        assert (ROOT_DIR / "frontend").exists()

    def test_model_id_default(self, test_config):
        """model_id deve ser xai.grok-4.3."""
        assert test_config.model_id == "xai.grok-4.3"

    def test_aws_region_default(self):
        """Regiao padrao deve ser us-east-1 (valor default no codigo)."""
        from backend.config import load_config
        with patch("backend.config._load_env", return_value={
            "AWS_BEARER_TOKEN_BEDROCK": "test",
            "AWS_ACCESS_KEY_ID": "test-key",
            "AWS_SECRET_ACCESS_KEY": "test-secret",
        }):
            c = load_config()
        assert c.aws_region == "us-east-1"

    def test_config_dataclass_fields(self, test_config):
        """Config deve ter todos os campos esperados."""
        assert hasattr(test_config, "bearer_token")
        assert hasattr(test_config, "aws_region")
        assert hasattr(test_config, "aws_access_key_id")
        assert hasattr(test_config, "aws_secret_access_key")
        assert hasattr(test_config, "model_id")
        assert hasattr(test_config, "bucket_name")
        assert hasattr(test_config, "grok_price_input")
        assert hasattr(test_config, "grok_price_output")
        assert hasattr(test_config, "grok_price_cache_read")
        assert hasattr(test_config, "grok_reasoning_effort")
