#!/usr/bin/env python3
"""Gerenciamento de progresso em tempo real do pipeline (thread-safe).

Fornece funcoes para atualizar o dicionario PROGRESS compartilhado
entre o pipeline.py e o app.py, permitindo que o frontend acompanhe
cada etapa em tempo real via polling.

Uso:
    from backend.progress import Progress

    Progress.reset()
    Progress.etapa1("processing", "Extraindo cabecalhos...")
    # ... faz a etapa 1 ...
    Progress.etapa1("completed", "Cabecalhos extraidos!")
"""

from __future__ import annotations

import copy
import threading
from typing import Any


class _Progress:
    """Gerenciador singleton do progresso do pipeline (thread-safe)."""

    _data: dict[str, Any] = {}
    _lock = threading.Lock()

    @classmethod
    def reset(cls, total_runs: int = 1) -> None:
        with cls._lock:
            cls._data = {
                "etapa1": {"status": "pending", "label": "Aguardando..."},
                "etapa2": {"status": "pending", "label": "Aguardando..."},
                "etapa3": [
                    {"status": "pending", "label": f"Rodada {i+1}", "resultado": ""}
                    for i in range(total_runs)
                ],
                "etapa4": {"status": "pending", "label": "Aguardando..."},
                "total_runs": total_runs,
            }

    @classmethod
    def get(cls) -> dict[str, Any]:
        with cls._lock:
            return copy.deepcopy(cls._data)

    @classmethod
    def _set(cls, key: str, value: Any) -> None:
        with cls._lock:
            cls._data[key] = value

    @classmethod
    def etapa1(cls, status: str, label: str) -> None:
        cls._set("etapa1", {"status": status, "label": label})

    @classmethod
    def etapa2(cls, status: str, label: str) -> None:
        cls._set("etapa2", {"status": status, "label": label})

    @classmethod
    def etapa3(cls, idx: int, status: str, label: str, resultado: str = "") -> None:
        """Atualiza uma rodada especifica da etapa 3 (0-based)."""
        with cls._lock:
            etapa3 = cls._data.get("etapa3", [])
            if 0 <= idx < len(etapa3):
                etapa3[idx] = {
                    "status": status,
                    "label": label,
                    "resultado": resultado,
                }

    @classmethod
    def etapa4(cls, status: str, label: str) -> None:
        cls._set("etapa4", {"status": status, "label": label})


# Instancia global para uso direto
Progress = _Progress()
Progress.reset()
