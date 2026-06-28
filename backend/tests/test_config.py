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

    def test_load_config_missing_all_credentials_raises(self):
        """Deve levantar erro se bearer token e AWS creds faltarem."""
        from backend.config import _validate, _check_aws_credentials
        # Simula que nao ha credenciais AWS
        with patch("backend.config._check_aws_credentials", return_value=False):
            missing = {}
            try:
                _validate(missing)
                assert False, "Deveria ter saido"
            except SystemExit:
                pass

    def test_load_config_with_sso_succeeds(self):
        """Deve aceitar config sem bearer token se houver AWS creds."""
        from backend.config import load_config
        with patch("backend.config._load_env", return_value={
            "REGION": "us-east-1",
            "BEDROCK_MODEL_ID": "xai.grok-4.3",
        }), patch("backend.config._check_aws_credentials", return_value=True):
            c = load_config()
        assert c.model_id == "xai.grok-4.3"
        assert c.bearer_token == ""

    def test_root_dir_exists(self):
        """ROOT_DIR deve apontar para diretorio existente."""
        from backend.config import ROOT_DIR
        assert ROOT_DIR.exists()
        assert (ROOT_DIR / "backend").exists()
        assert (ROOT_DIR / "frontend").exists()

    def test_docs_dir_default(self, test_config):
        """docs_dir deve apontar para data/docs."""
        assert str(test_config.docs_dir).endswith("data\\docs") or str(test_config.docs_dir).endswith("data/docs")

    def test_model_id_default(self, test_config):
        """model_id deve ser xai.grok-4.3."""
        assert test_config.model_id == "xai.grok-4.3"

    def test_aws_region_default(self):
        """Regiao padrao deve ser us-east-1 (valor default no codigo)."""
        from backend.config import load_config
        with patch("backend.config._load_env", return_value={
            "AWS_BEARER_TOKEN_BEDROCK": "test",
        }):
            c = load_config()
        assert c.aws_region == "us-east-1"

    def test_config_dataclass_fields(self, test_config):
        """Config deve ter todos os campos esperados."""
        assert hasattr(test_config, "bearer_token")
        assert hasattr(test_config, "aws_region")
        assert hasattr(test_config, "model_id")
        assert hasattr(test_config, "bucket_name")
        assert hasattr(test_config, "grok_price_input")
        assert hasattr(test_config, "grok_price_output")
        assert hasattr(test_config, "grok_price_cache_read")
        assert hasattr(test_config, "grok_reasoning_effort")
        assert hasattr(test_config, "docs_dir")
        assert hasattr(test_config, "md_dir")
