#!/usr/bin/env python3
"""Cliente Grok 4.3 via Amazon Bedrock Mantle.

Suporta dois modos de autenticacao:
  1. AWS SigV4 (SSO/boto3) - metodo principal
  2. Bearer Token (API Key) - fallback se AWS_BEARER_TOKEN_BEDROCK estiver no .env

Fallback regional entre us-east-1, us-west-2, us-east-2,
reasoning configurado via .env (GROK_REASONING_EFFORT) e suporte a streaming.

Referencia: GROK_DOC.md
"""

from __future__ import annotations

import time
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from openai import OpenAI

from backend.config import Config
from backend.metrics import PipelineMetrics, calculate_costs


# ---------------------------------------------------------------------------
# Regioes onde o Grok 4.3 esta disponivel via Mantle (In-Region)
# ---------------------------------------------------------------------------
FALLBACK_REGIONS = ["us-east-1", "us-west-2", "us-east-2"]

RETRY_DELAYS = [2, 4, 8]


@dataclass
class FallbackAttempt:
    """Registro de uma tentativa de chamada ao Grok via Mantle."""
    model_name: str = ""
    region: str = ""
    status: str = ""           # success, throttled, error
    error: str = ""
    duration_ms: int = 0
    timestamp: str = ""


@dataclass
class FallbackMetrics:
    """Metricas de uma sequencia de fallback."""
    total_attempts: int = 0
    successful_attempt: Optional[FallbackAttempt] = None
    all_attempts: list[FallbackAttempt] = field(default_factory=list)
    total_duration_ms: int = 0
    cost_savings_usd: float = 0.0


# Estado global do fallback
_fallback_history: list[FallbackMetrics] = []
_MAX_HISTORY = 20


def get_fallback_status() -> dict:
    """Retorna estado atual do sistema de fallback.

    Returns:
        Dict com historico de fallbacks, estrategia e status.
    """
    return {
        "strategy": [
            {"priority": i + 1, "model": "Grok 4.3", "region": r}
            for i, r in enumerate(FALLBACK_REGIONS)
        ],
        "retry_delays": RETRY_DELAYS,
        "recent_fallbacks": [
            {
                "total_attempts": m.total_attempts,
                "success": m.successful_attempt is not None,
                "winner": (
                    {
                        "model": "Grok 4.3",
                        "region": m.successful_attempt.region,
                        "duration_ms": m.successful_attempt.duration_ms,
                    }
                    if m.successful_attempt
                    else None
                ),
                "total_duration_ms": m.total_duration_ms,
                "cost_savings_usd": m.cost_savings_usd,
                "attempts": [
                    {
                        "model": "Grok 4.3",
                        "region": a.region,
                        "status": a.status,
                        "error": a.error,
                        "duration_ms": a.duration_ms,
                    }
                    for a in m.all_attempts
                ],
            }
            for m in _fallback_history[-5:]
        ],
        "total_recorded_runs": len(_fallback_history),
    }


def _build_client(config: Config, region: str) -> OpenAI:
    """Cria cliente OpenAI apontando para o endpoint Mantle na regiao.

    Usa autenticacao AWS SigV4 (SSO/boto3) se nao houver bearer_token,
    ou Bearer Token se estiver configurado no .env.

    Args:
        config: Configuracao do sistema.
        region: Regiao AWS (ex: us-east-1).

    Returns:
        Instancia de OpenAI configurada.
    """
    base_url = f"https://bedrock-mantle.{region}.api.aws/openai/v1"

    # Se tem bearer token, usa API Key simples (mais rapido)
    if config.bearer_token:
        return OpenAI(
            api_key=config.bearer_token,
            base_url=base_url,
        )

    # Senao, usa AWS SigV4 com httpx + requests-aws4auth
    import httpx
    from requests_aws4auth import AWS4Auth
    import boto3

    session = boto3.Session(profile_name=config.aws_profile, region_name=region)
    credentials = session.get_credentials()
    frozen = credentials.get_frozen_credentials()

    auth = AWS4Auth(
        frozen.access_key,
        frozen.secret_key,
        region,
        "bedrock",
        session_token=frozen.token,
    )

    class SigV4Transport(httpx.BaseTransport):
        """Transporte HTTPX que aplica AWS SigV4 em cada requisicao."""

        def __init__(self, aws_auth: AWS4Auth):
            self.auth = aws_auth

        def handle_request(self, request: httpx.Request) -> httpx.Response:
            import requests as req_lib

            req = req_lib.Request(
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                data=request.content,
            )
            prepared = req.prepare()
            signed = self.auth(prepared)

            session_r = req_lib.Session()
            resp = session_r.send(signed, stream=True)

            return httpx.Response(
                status_code=resp.status_code,
                headers=dict(resp.headers),
                content=resp.content,
                request=request,
            )

    http_client = httpx.Client(transport=SigV4Transport(auth))

    return OpenAI(
        api_key="",  # SigV4 substitui API key
        base_url=base_url,
        http_client=http_client,
    )


def _call_grok_streaming(
    config: Config,
    system_prompt: str,
    user_message: str,
    context: str,
    stream_to_console: bool = True,
) -> tuple[Optional[str], Optional[PipelineMetrics]]:
    """Tenta chamar Grok 4.3 via Mantle com fallback regional e streaming.

    Args:
        config: Configuracao do sistema.
        system_prompt: System prompt da etapa.
        user_message: Mensagem do usuario.
        context: Contexto dos documentos.
        stream_to_console: Se True, faz streaming no console.

    Returns:
        Tupla (texto_resposta, metrics) ou (None, None) se todas falharem.
    """
    full_message = f"{context}\n\n{user_message}" if context else user_message
    last_error: Optional[str] = None
    fb_metrics = FallbackMetrics()
    start_time = time.time()

    for region in FALLBACK_REGIONS:
        for retry_idx in range(len(RETRY_DELAYS) + 1):
            attempt_start = time.time()
            fb_metrics.total_attempts += 1
            fb_attempt = FallbackAttempt(
                model_name="Grok 4.3",
                region=region,
                timestamp=datetime.now().isoformat(),
            )

            try:
                client = _build_client(config, region)

                response = client.chat.completions.create(
                    model=config.model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_message},
                    ],
                    temperature=0.0,
                    stream=True,
                    extra_body={
                        "reasoning": {"effort": config.grok_reasoning_effort},
                    },
                )

                # Streaming
                full_text: list[str] = []
                for chunk in response:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        full_text.append(delta.content)
                        if stream_to_console:
                            print(delta.content, end="", flush=True)

                if stream_to_console:
                    print()

                result = "".join(full_text)

                # Usage do ultimo chunk
                usage = None
                if hasattr(response, "usage") and response.usage:
                    usage = response.usage
                elif hasattr(chunk, "usage") and chunk.usage:
                    usage = chunk.usage

                prompt_tokens = usage.prompt_tokens if usage else 0
                completion_tokens = usage.completion_tokens if usage else 0
                cache_tokens = getattr(usage, "prompt_tokens_details", None)
                cache_tokens = getattr(cache_tokens, "cached_tokens", 0) if cache_tokens else 0
                if not cache_tokens:
                    cache_tokens = 0

                metrics = calculate_costs(
                    config, prompt_tokens, completion_tokens, cache_tokens,
                )

                # Registra sucesso
                elapsed_ms = int((time.time() - attempt_start) * 1000)
                fb_attempt.status = "success"
                fb_attempt.duration_ms = elapsed_ms
                fb_metrics.all_attempts.append(fb_attempt)
                fb_metrics.successful_attempt = fb_attempt
                fb_metrics.total_duration_ms = int(
                    (time.time() - start_time) * 1000
                )

                _fallback_history.append(fb_metrics)
                if len(_fallback_history) > _MAX_HISTORY:
                    _fallback_history.pop(0)

                return result, metrics

            except Exception as e:
                elapsed_ms = int((time.time() - attempt_start) * 1000)
                fb_attempt.duration_ms = elapsed_ms
                error_str = str(e)

                is_throttled = (
                    "throttl" in error_str.lower()
                    or "429" in error_str
                    or "rate" in error_str.lower()
                )

                if is_throttled and retry_idx < len(RETRY_DELAYS):
                    fb_attempt.status = "throttled"
                    fb_attempt.error = error_str
                    fb_metrics.all_attempts.append(fb_attempt)

                    delay = RETRY_DELAYS[retry_idx]
                    print(
                        f"  [RETRY {retry_idx + 1}/{len(RETRY_DELAYS)}]"
                        f" Throttling em {region}. Retry em {delay}s...",
                    )
                    time.sleep(delay)
                    continue
                else:
                    fb_attempt.status = "error" if not is_throttled else "throttled"
                    fb_attempt.error = error_str
                    fb_metrics.all_attempts.append(fb_attempt)
                    last_error = error_str
                    print(
                        f"  [FALLBACK] Erro em {region}: {error_str[:120]}",
                    )
                    break

    # Todas falharam
    fb_metrics.total_duration_ms = int((time.time() - start_time) * 1000)
    _fallback_history.append(fb_metrics)
    if len(_fallback_history) > _MAX_HISTORY:
        _fallback_history.pop(0)

    print(
        f"  [FATAL] Todas as {len(FALLBACK_REGIONS)} regioes esgotadas."
        f" Ultimo erro: {last_error}",
        file=sys.stderr,
    )
    return None, None


def run_llm_stage_streaming(
    config: Config,
    system_prompt: str,
    user_message: str,
    context: str,
    stream_to_console: bool = True,
) -> tuple[str, PipelineMetrics]:
    """Executa etapa do LLM com Grok 4.3, streaming e fallback regional.

    Args:
        config: Configuracao do sistema.
        system_prompt: System prompt da etapa.
        user_message: Mensagem do usuario.
        context: Contexto dos documentos.
        stream_to_console: Se True, mostra streaming no console.

    Returns:
        Tupla (texto_resposta, metricas).

    Raises:
        RuntimeError: Se todas as regioes de fallback falharem.
    """
    result, metrics = _call_grok_streaming(
        config, system_prompt, user_message, context, stream_to_console,
    )

    if result is None:
        raise RuntimeError(
            "Falha ao executar etapa do LLM apos todas as regioes de fallback."
            " Verifique conectividade com Bedrock Mantle e credenciais AWS."
        )

    return result, metrics or PipelineMetrics()
