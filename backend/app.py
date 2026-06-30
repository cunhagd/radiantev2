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

                # 2. Fallback: tenta S3
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
            elif path == "/api/fallback-status":
                self._serve_json(get_fallback_status())
            elif path == "/api/metrics":
                metrics = get_last_metrics()
                self._serve_json({"status": "ok", "metrics": metrics} if metrics else {"status": "no_data"})
            elif path == "/api/metrics/history":
                history = get_execution_history()
                self._serve_json({"status": "ok", "history": history, "total": len(history)})
            elif path.startswith("/data/"):
                filename = path.lstrip("/data/")
                if not filename:
                    self.send_error(400, "Nome de arquivo nao fornecido")
                    return
                data = download_file(config, f"results/{filename}")
                if data is None:
                    self.send_error(404, f"Arquivo nao encontrado: {filename}")
                    return
                # Validacao de integridade para PDF
                if filename.lower().endswith(".pdf"):
                    if not data.startswith(b"%PDF-"):
                        self.send_response(502)
                        self._serve_json({
                            "status": "error",
                            "message": "Arquivo PDF corrompido ou incompleto no servidor",
                        })
                        return
                    self._serve_bytes(data, "application/pdf")
                else:
                    mime = "application/octet-stream"
                    if filename.endswith(".json"):
                        mime = "application/json; charset=utf-8"
                    self._serve_bytes(data, mime)
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

    def do_OPTIONS(self) -> None:
        """Responde preflight CORS para requests cross-origin."""
        self.send_response(200)
        self._add_cors()
        self.end_headers()

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
                    # Inclui metricas consolidadas no JSON principal (FR-007)
                    raw_metrics = result.get("metrics")
                    if raw_metrics:
                        metrics_dict = {
                            "prompt_tokens": raw_metrics.prompt_tokens,
                            "completion_tokens": raw_metrics.completion_tokens,
                            "cache_tokens": raw_metrics.cache_tokens,
                            "cost_input": raw_metrics.cost_input,
                            "cost_output": raw_metrics.cost_output,
                            "cost_cache": raw_metrics.cost_cache,
                            "cost_total": raw_metrics.cost_total,
                        }
                        # Inclui runs individuais no modo 10x
                        run_metrics_list = result.get("run_metrics_list")
                        if run_metrics_list:
                            metrics_dict["runs"] = run_metrics_list
                        parsed_data["metrics"] = metrics_dict
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
            # Salva exclusivamente no S3, sem copia local
            if not upload_file(config, data, f"docs/{fn}"):
                self.send_response(503)
                self._serve_json({
                    "status": "error",
                    "message": "Servico de armazenamento (S3) indisponivel. Tente novamente.",
                })
                return

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

        # Detecta se o cliente quer streaming SSE
        is_stream = "stream=true" in self.path

        erros: list[str] = []
        total_s3 = 0

        def send_step(step_id: str, status: str, file: str | None = None, error: str | None = None, deleted_count: int | None = None) -> None:
            if is_stream:
                payload: dict[str, Any] = {"step": step_id, "status": status}
                if file is not None:
                    payload["file"] = file
                if error is not None:
                    payload["error"] = error
                if deleted_count is not None:
                    payload["deleted_count"] = deleted_count
                self._send_sse("step", payload)

        if is_stream:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

        # 1. Limpa S3 docs/
        send_step("s3_docs", "processing", "docs/")
        try:
            deleted = delete_files(config, "docs/")
            total_s3 += deleted
            send_step("s3_docs", "done", deleted_count=deleted)
        except Exception as e:
            erros.append(f"Falha ao limpar S3 docs: {e}")
            send_step("s3_docs", "error", file="docs/", error=str(e))

        # 2. Limpa S3 markdown_docs/
        send_step("s3_markdown", "processing", "markdown_docs/")
        try:
            deleted = delete_files(config, "markdown_docs/")
            total_s3 += deleted
            send_step("s3_markdown", "done", deleted_count=deleted)
        except Exception as e:
            erros.append(f"Falha ao limpar S3 markdown_docs: {e}")
            send_step("s3_markdown", "error", file="markdown_docs/", error=str(e))

        # 3. Limpa S3 results/
        send_step("s3_results", "processing", "results/")
        try:
            deleted = delete_files(config, "results/")
            total_s3 += deleted
            send_step("s3_results", "done", deleted_count=deleted)
        except Exception as e:
            erros.append(f"Falha ao limpar S3 results: {e}")
            send_step("s3_results", "error", file="results/", error=str(e))

        # 4. Limpa S3 runs/
        send_step("s3_runs", "processing", "runs/")
        try:
            deleted = delete_files(config, "runs/")
            total_s3 += deleted
            send_step("s3_runs", "done", deleted_count=deleted)
        except Exception as e:
            erros.append(f"Falha ao limpar S3 runs: {e}")
            send_step("s3_runs", "error", file="runs/", error=str(e))

        # 3. Reseta estado em memoria
        send_step("reset", "processing")
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
        send_step("reset", "done")

        # Resposta final
        if is_stream:
            if erros:
                self._send_sse("complete", {
                    "status": "partial",
                    "message": "Sistema limpo com erros parciais.",
                    "errors": erros,
                    "s3_deleted": total_s3,
                })
            else:
                self._send_sse("complete", {
                    "status": "ok",
                    "message": "Sistema limpo com sucesso",
                    "s3_deleted": total_s3,
                })
            # Forca fechamento da conexao apos o stream SSE para evitar
            # estado residual que corrompe requisicoes seguintes
            self.close_connection = True
        else:
            # Modo legado (sem stream)
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

    def _send_sse(self, event_type: str, data: dict) -> None:
        """Envia um evento SSE (Server-Sent Event) para o cliente.

        Args:
            event_type: Tipo do evento ('step' ou 'complete').
            data: Dicionario com os dados do evento.
        """
        line = f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        self.wfile.write(line.encode("utf-8"))
        self.wfile.flush()

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
                        help="Ignorado - documentos lidos do S3 (prefixo docs/)")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4], default=0,
                        help="Executar etapa especifica (modo CLI)")
    parser.add_argument("--once", action="store_true",
                        help="Executar analise 1x (modo CLI)")
    parser.add_argument("--ten", action="store_true",
                        help="Executar analise 10x (modo CLI)")
    parser.add_argument("--output", type=str, default="",
                        help="Ignorado - resultados salvos no S3 (results/)")
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

    # Le documentos do S3 (prefixo docs/)
    from backend.s3_client import get_s3_combined_context
    combined_context = get_s3_combined_context(config)

    if not combined_context.strip():
        print("Nenhum documento encontrado no S3 (prefixo docs/).")
        sys.exit(1)

    print(f"\nContexto total: {len(combined_context)} chars (lido do S3)")

    # Execucao por etapa ou completa
    if args.step:
        _run_single_step(config, combined_context, args.step)
    elif args.once:
        result = run_once(config, combined_context)
        _save_cli_result(config, result, args.output)
    elif args.ten:
        result = run_ten_times(config, combined_context)
        _save_cli_result(config, result, args.output)
    else:
        print(f"\nOpcoes: --once (1x), --ten (10x), --step N (etapa)")
        print(f"Exemplo: python backend/app.py --mode cli --once")


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


def _save_cli_result(config: Config, result: dict, output_dir: str) -> None:
    """Salva resultado do CLI no S3.

    Args:
        config: Configuracao do sistema.
        result: Resultado da execucao.
        output_dir: Diretorio de saida (opcional, mantido para compatibilidade).
    """
    import json

    if result.get("status") != "completed":
        print(f"\nERRO: {result.get('message', 'Falha desconhecida')}")
        return

    json_data = json.dumps(result.get("data", {}), indent=2, ensure_ascii=False).encode("utf-8")
    upload_file(config, json_data, "results/resultado.json")

    print(f"\nResultado salvo no S3: results/resultado.json")
    print(f"Total cifras: {len(result.get('data', {}).get('cifras', []))}")
    print(f"Valor total: R$ {result.get('data', {}).get('valor_total_estimado', '0,00')}")


if __name__ == "__main__":
    main()
