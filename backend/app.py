#!/usr/bin/env python3
"""Servidor HTTP do Radiante v2 - Orquestrador leve."""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from backend.config import Config, load_config, ROOT_DIR
from backend.pipeline import run_once, run_ten_times, get_execution_history, get_last_metrics
from backend.bedrock_client import get_fallback_status
from backend.progress import Progress
from backend.s3_client import (
    upload_file, download_file, list_files, delete_files,
    get_s3_combined_context,
)

ANALYSIS_JOBS: dict[str, Any] = {
    "status": "idle", "message": "", "error_details": "",
    "last_result": None,  # Cache do ultimo resultado em memoria
}
jobs_lock = threading.Lock()
config: Config = None  # type: ignore


class DashboardHTTPHandler(SimpleHTTPRequestHandler):
    def _clean_path(self) -> str:
        """Remove query string do path para roteamento."""
        return self.path.split("?")[0]

    def do_GET(self) -> None:
        try:
            path = self._clean_path()
            if path in ("/", "/index.html"):
                self._serve_file(ROOT_DIR / "frontend" / "index.html", "text/html; charset=utf-8")
            elif path == "/api/status":
                self._serve_json(ANALYSIS_JOBS)
            elif path == "/api/progress":
                self._serve_json(Progress.get())
            elif path == "/api/last-result":
                # 1. Tenta cache em memoria primeiro (mais rapido, nao depende de S3)
                with jobs_lock:
                    cached = ANALYSIS_JOBS.get("last_result")
                    if cached is not None:
                        self._serve_json(cached)
                        return

                # 2. Fallback: tenta arquivo local (consolidado_10x.json, depois resultado_final.json)
                local_consolidado = ROOT_DIR / "data" / "consolidado_10x.json"
                local_resultado = ROOT_DIR / "data" / "resultado_final.json"
                parsed = None
                if local_consolidado.exists():
                    try:
                        parsed = json.loads(local_consolidado.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        pass
                if not parsed and local_resultado.exists():
                    try:
                        parsed = json.loads(local_resultado.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        pass
                if parsed:
                    with jobs_lock:
                        ANALYSIS_JOBS["last_result"] = parsed
                    self._serve_json(parsed)
                    return

                # 3. Fallback: tenta S3
                data = download_file(config, "results/consolidado_10x.json")
                if not data:
                    data = download_file(config, "results/resultado_final.json")
                if data:
                    try:
                        parsed = json.loads(data)
                        with jobs_lock:
                            ANALYSIS_JOBS["last_result"] = parsed
                        self._serve_json(parsed)
                    except json.JSONDecodeError:
                        self._serve_json({"status": "error", "message": "JSON invalido"})
                else:
                    self._serve_json({"status": "no_data", "message": "Nenhum resultado encontrado"})
            elif path == "/api/audit-log":
                # 1. Tenta arquivo local primeiro (nao depende de S3)
                local_audit = ROOT_DIR / "data" / "auditoria_10x.md"
                if local_audit.exists():
                    self._serve_file(local_audit, "text/markdown; charset=utf-8")
                    return
                # 2. Fallback: tenta S3
                data = download_file(config, "results/auditoria_10x.md")
                if data:
                    self._serve_bytes(data, "text/markdown; charset=utf-8")
                else:
                    self._serve_json({"status": "no_data"})
            elif path == "/api/fallback-status":
                self._serve_json(get_fallback_status())
            elif path == "/api/metrics":
                metrics = get_last_metrics()
                self._serve_json({"status": "ok", "metrics": metrics} if metrics else {"status": "no_data"})
            elif path == "/api/metrics/history":
                history = get_execution_history()
                self._serve_json({"status": "ok", "history": history, "total": len(history)})
            elif path.startswith("/data/"):
                fpath = ROOT_DIR / path.lstrip("/")
                if fpath.exists():
                    mime = "application/pdf" if fpath.suffix == ".pdf" else "application/octet-stream"
                    self._serve_file(fpath, mime)
                else:
                    self.send_error(404)
            elif path.startswith("/css/") or path.startswith("/js/"):
                # Arquivos estaticos modulares do frontend
                fpath = ROOT_DIR / "frontend" / path.lstrip("/")
                if fpath.exists():
                    mime_map = {".css": "text/css; charset=utf-8", ".js": "application/javascript; charset=utf-8", ".html": "text/html; charset=utf-8"}
                    mime = mime_map.get(fpath.suffix, "application/octet-stream")
                    self._serve_file(fpath, mime)
                else:
                    self.send_error(404)
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self) -> None:
        try:
            path = self._clean_path()
            handlers = {
                "/api/run-once": lambda: self._start_analysis("once"),
                "/api/run-ten": lambda: self._start_analysis("ten"),
                "/api/upload": self._handle_upload,
                "/api/clear-all": self._handle_clear,
            }
            handler = handlers.get(path)
            if handler:
                handler()
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500, str(e))

    def _start_analysis(self, mode: str) -> None:
        Progress.reset(total_runs=1 if mode == "once" else 10)
        with jobs_lock:
            if ANALYSIS_JOBS["status"] == "processing":
                self.send_response(409)
                self._serve_json({"status": "error", "message": "Job ja em processamento"})
                return
            ANALYSIS_JOBS.update(status="processing", message="", error_details="")
        thread = threading.Thread(target=self._run_analysis, args=(mode,), daemon=True)
        thread.start()
        self.send_response(202)
        self._serve_json({"status": "accepted", "message": f"Analise {mode} iniciada"})

    def _run_analysis(self, mode: str) -> None:
        try:
            # Garante que o profile AWS seja propagado para a thread
            if config.aws_profile:
                os.environ["AWS_PROFILE"] = config.aws_profile
                os.environ["AWS_DEFAULT_PROFILE"] = config.aws_profile
            # Remove token poluente que pode estar no ambiente (ex: test-token)
            os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)

            ctx = get_s3_combined_context(config)
            if not ctx.strip():
                raise ValueError("Nenhum documento para analise")
            fn = run_once if mode == "once" else run_ten_times
            result = fn(config, ctx)
            with jobs_lock:
                if result.get("status") == "completed":
                    parsed_data = result.get("data", {}).copy() if result.get("data") else {}
                    # Adiciona o nome do PDF gerado para o frontend usar
                    parsed_data["pdf_filename"] = "relatorio_consolidado_10x.pdf" if mode == "ten" else "relatorio_consolidado.pdf"
                    ANALYSIS_JOBS.update(
                        status="completed",
                        message=json.dumps(parsed_data, ensure_ascii=False),
                        last_result=parsed_data,
                    )
                else:
                    ANALYSIS_JOBS.update(status="error", error_details=result.get("message", "Erro"))
        except Exception as e:
            with jobs_lock:
                ANALYSIS_JOBS.update(status="error", error_details=str(e))
            print(f"ERROR: {e}", file=sys.stderr)

    def _handle_upload(self) -> None:
        cl = int(self.headers.get("Content-Length", 0))
        fn = self.headers.get("X-Filename", "")
        if cl and fn:
            data = self.rfile.read(cl)
            # 1. Salva sempre localmente primeiro
            docs_dir = ROOT_DIR / "data" / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)
            local_path = docs_dir / fn
            local_path.write_bytes(data)

            # 2. Tenta S3 como copia de seguranca (falha silenciosa se token expirou)
            upload_file(config, data, f"docs/{fn}")

            self._serve_json({"status": "ok", "filename": fn})
        else:
            self.send_response(400)
            self._serve_json({"status": "error", "message": "Content-Length ou X-Filename ausente"})

    def _handle_clear(self) -> None:
        # 0. Verifica se ha analise em andamento
        with jobs_lock:
            if ANALYSIS_JOBS["status"] == "processing":
                self.send_response(409)
                self._serve_json({"status": "error", "message": "Nao e possivel limpar durante uma analise em andamento."})
                return

        erros: list[str] = []

        # 1. Limpa diretorio local data/ (docs, markdown_docs, PDFs, JSONs, .md)
        data_root = ROOT_DIR / "data"
        if data_root.exists():
            try:
                import shutil
                for item in data_root.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    elif item.suffix in (".pdf", ".json", ".md"):
                        item.unlink()
                # Recria diretorios necessarios
                (data_root / "docs").mkdir(parents=True, exist_ok=True)
                (data_root / "markdown_docs").mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                erros.append(f"Falha ao limpar diretorio local: {e}")

        # 2. Limpa bucket S3
        try:
            total_s3 = sum(delete_files(config, p) for p in ["docs/", "markdown_docs/", "results/", "runs/"])
        except Exception as e:
            total_s3 = 0
            erros.append(f"Falha ao limpar S3: {e}")

        # 3. Reseta estado em memoria
        with jobs_lock:
            ANALYSIS_JOBS.update(
                status="idle", message="", error_details="",
                last_result=None,
            )

        # 4. Reseta progresso do pipeline
        Progress.reset(total_runs=1)

        # 5. Limpa historico de execucao
        from backend.pipeline import clear_execution_history
        clear_execution_history()

        if erros:
            self._serve_json({
                "status": "partial",
                "message": "Sistema limpo com erros parciais.",
                "errors": erros,
                "s3_deleted": total_s3,
            })
        else:
            self._serve_json({"status": "ok", "message": "Sistema limpo com sucesso", "s3_deleted": total_s3})

    def _serve_json(self, data: dict) -> None:
        self._serve_bytes(json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _serve_file(self, path: Path, mime: str) -> None:
        if path.exists():
            self._serve_bytes(path.read_bytes(), mime)
        else:
            self.send_error(404, f"Arquivo nao encontrado: {path.name}")

    def _serve_bytes(self, content: bytes, mime: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self._add_cors()
        self.end_headers()
        self.wfile.write(content)

    def _add_cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Filename")


def main() -> None:
    global config
    parser = argparse.ArgumentParser(description="Radiante v2 - Analise Juridica")
    parser.add_argument("--mode", choices=["web", "cli"], default="web",
                        help="web: servidor HTTP | cli: terminal interativo")
    parser.add_argument("--port", type=int, default=8000,
                        help="Porta do servidor web (padrao: 8000)")
    parser.add_argument("--docs", type=str, default="",
                        help="Diretorio com documentos para modo CLI")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4], default=0,
                        help="Executar etapa especifica (modo CLI)")
    parser.add_argument("--once", action="store_true",
                        help="Executar analise 1x (modo CLI)")
    parser.add_argument("--ten", action="store_true",
                        help="Executar analise 10x (modo CLI)")
    parser.add_argument("--output", type=str, default="",
                        help="Diretorio para salvar resultados (modo CLI)")
    args = parser.parse_args()

    config = load_config()
    print(f"Radiante v2 - Regiao: {config.aws_region} | Modelo: {config.model_id}")

    if args.mode == "cli":
        _run_cli(args)
    else:
        server = HTTPServer(("0.0.0.0", args.port), DashboardHTTPHandler)
        print(f"Servidor: http://localhost:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
            server.server_close()


def _run_cli(args: argparse.Namespace) -> None:
    """Executa o pipeline em modo CLI.

    Args:
        args: Argumentos da linha de comando.
    """
    from backend.pipeline import run_single_pipeline

    # Determina diretorio de documentos
    docs_dir = Path(args.docs) if args.docs else config.docs_dir
    if not docs_dir.exists():
        print(f"Diretorio de documentos nao encontrado: {docs_dir}")
        sys.exit(1)

    print(f"\nDocumentos: {docs_dir}")

    # Le documentos
    combined_parts = []
    from backend.extract import get_document_text
    for fpath in sorted(docs_dir.iterdir()):
        if fpath.is_file():
            content = fpath.read_bytes()
            text = get_document_text(config, fpath.name, content)
            combined_parts.append(f"--- Documento: {fpath.name} ---\n{text}")
            print(f"  Documento carregado: {fpath.name}")

    combined_context = "\n\n".join(combined_parts)
    if not combined_context.strip():
        print("Nenhum documento valido encontrado.")
        sys.exit(1)

    print(f"\nContexto total: {len(combined_context)} chars")

    # Execucao por etapa ou completa
    if args.step:
        _run_single_step(config, combined_context, args.step)
    elif args.once:
        result = run_once(config, combined_context)
        _save_cli_result(result, args.output)
    elif args.ten:
        result = run_ten_times(config, combined_context)
        _save_cli_result(result, args.output)
    else:
        print(f"\nOpcoes: --once (1x), --ten (10x), --step N (etapa)")
        print(f"Exemplo: python backend/app.py --mode cli --once --docs data/docs")


def _run_single_step(config: Config, context: str, step: int) -> None:
    """Executa uma etapa especifica do pipeline.

    Args:
        config: Configuracao do sistema.
        context: Contexto dos documentos.
        step: Numero da etapa (1-4).
    """
    from backend.pipeline import run_single_pipeline

    print(f"\nExecutando apenas a Etapa {step}...")
    result = run_single_pipeline(config, context, stream_to_console=True)

    if result:
        stage_key = f"etapa{step}_raw"
        output = result.get(stage_key, "Sem saida para esta etapa")
        print(f"\n{'=' * 60}")
        print(f" SAIDA DA ETAPA {step}")
        print(f"{'=' * 60}")
        print(output)
    else:
        print("Falha ao executar etapa.")


def _save_cli_result(result: dict, output_dir: str) -> None:
    """Salva resultado do CLI em arquivo.

    Args:
        result: Resultado da execucao.
        output_dir: Diretorio de saida.
    """
    import json

    if result.get("status") != "completed":
        print(f"\nERRO: {result.get('message', 'Falha desconhecida')}")
        return

    output_path = Path(output_dir) if output_dir else ROOT_DIR / "data" / "results"
    output_path.mkdir(parents=True, exist_ok=True)

    json_path = output_path / "resultado.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result.get("data", {}), f, indent=2, ensure_ascii=False)

    print(f"\nResultado salvo em: {json_path}")
    print(f"Total cifras: {len(result.get('data', {}).get('cifras', []))}")
    print(f"Valor total: R$ {result.get('data', {}).get('valor_total_estimado', '0,00')}")


if __name__ == "__main__":
    main()
