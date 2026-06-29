#!/usr/bin/env python3
"""Pipeline de analise juridica em 4 etapas para o Radiante v2.

Orquestra as etapas: Metadados -> Calculo de Cifras -> Probabilidade
e Risco -> Consolidacao Final (JSON). Suporta execucao unica e modo
10x paralelo com ThreadPoolExecutor.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import backend.prompts as P
from backend.config import Config, ROOT_DIR
from backend.bedrock_client import run_llm_stage_streaming
from backend.metrics import PipelineMetrics, merge_metrics, format_metrics_report
from backend.progress import Progress
from backend.s3_client import upload_file, delete_files


def extract_json_from_markdown(text: str) -> Optional[dict]:
    """Extrai JSON de dentro de bloco markdown ```json ... ```.

    Args:
        text: Texto contendo JSON em bloco markdown.

    Returns:
        Dict parseado ou None se falhar.
    """
    match = re.search(r"```json\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Tenta parsear o texto inteiro como JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def print_title(title: str) -> None:
    """Imprime titulo formatado no console."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def standardize_cifra_name(name: str) -> str:
    """Padroniza nomes de cifras entre rodadas."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name)

    mapping = {
        "hora extra": "Horas Extras (50%)",
        "horas extras": "Horas Extras (50%)",
        "h extras": "Horas Extras (50%)",
        "hora extra 100": "Horas Extras (100%)",
        "hora extra 100%": "Horas Extras (100%)",
        "domingos e feriados": "Horas Extras (100%)",
        "intervalo intrajornada": "Intervalo Intrajornada",
        "sobreaviso": "Sobreaviso",
        "adicional noturno": "Adicional Noturno",
        "periculosidade": "Periculosidade",
        "insalubridade": "Insalubridade",
        "dsr": "DSR",
        "13 salario": "13o Salario",
        "ferias": "Ferias + 1/3",
        "fgts": "FGTS (8%)",
        "dano moral": "Dano Moral",
        "honorarios": "Honorarios Advocaticios Sucumbenciais",
        "honorario": "Honorarios Advocaticios Sucumbenciais",
        "honorarios advocaticios": "Honorarios Advocaticios Sucumbenciais",
        "art 477": "Multa Art. 477",
        "art 477 clt": "Multa Art. 477",
        "multa 477": "Multa Art. 477",
        "desconto irregular trct": "Desconto Irregular TRCT",
        "desconto trct": "Desconto Irregular TRCT",
        "acumulo de funcao": "Acumulo de Funcao",
        "multa rescisoria": "Multa Rescisoria (40%)",
        "pensao": "Pensao / Lucros Cessantes",
        "dano estetico": "Dano Estetico",
    }

    for key, value in mapping.items():
        if key in name:
            return value

    return name.strip().title()


def parse_monetary(value_str: str) -> float:
    """Converte string monetaria brasileira para float.

    Args:
        value_str: String como "1.234,56".

    Returns:
        Valor numerico.
    """
    if not value_str:
        return 0.0
    cleaned = value_str.strip().replace("R$", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def format_monetary(value: float) -> str:
    """Formata float para string monetaria brasileira.

    Args:
        value: Valor numerico.

    Returns:
        String como "1.234,56".
    """
    integer_part = int(value)
    decimal_part = int(round((value - integer_part) * 100))
    int_str = f"{integer_part:,}".replace(",", ".")
    return f"{int_str},{decimal_part:02d}"


def calculate_probability_label(avg_estimado: float, avg_base: float) -> str:
    """Calcula rotulo de probabilidade baseado na proporcao.

    Args:
        avg_estimado: Media dos valores estimados.
        avg_base: Media dos valores base.

    Returns:
        Rotulo: Certa, Provavel, Possivel, Remota ou Improvavel.
    """
    if avg_base == 0:
        return "Remota"
    ratio = avg_estimado / avg_base
    if ratio > 0.80:
        return "Certa"
    elif ratio > 0.50:
        return "Provavel"
    elif ratio > 0.20:
        return "Possivel"
    elif ratio > 0.01:
        return "Remota"
    else:
        return "Improvavel"


def run_single_pipeline(
    config: Config,
    combined_context: str,
    run_idx: int | None = None,
    stream_to_console: bool = True,
) -> dict | None:
    """Executa as 4 etapas do pipeline de analise juridica.

    Args:
        config: Configuracao do sistema.
        combined_context: Contexto combinado dos documentos.
        run_idx: Indice da rodada (para modo 10x).
        stream_to_console: Se True, mostra streaming no console.

    Returns:
        Dict com resultados de todas as etapas ou None se falhar.
    """
    prefix = f"[Rodada {run_idx}] " if run_idx is not None else ""
    is_once = run_idx is None  # Modo once: reporta progresso

    try:
        # --- Etapa 1: Extracao de Metadados ---
        if run_idx is not None:
            print(f"{prefix}Iniciando Etapa 1 (Metadados)...")
        if is_once:
            Progress.etapa1("processing", "Extraindo cabecalhos do processo...")
        etapa1_system = (
            f"{P.BASE_SYSTEM_PROMPT.format(process_state='INICIAL', next_action='Executar ETAPA 1')}"
            f"\n\n--- INSTRUCOES DA ETAPA ATUAL ---\n{P.PROMPT_ETAPA_1}"
        )
        if stream_to_console:
            print_title("Etapa 1: Extracao de Metadados")
        etapa1_raw, etapa1_metrics = run_llm_stage_streaming(
            config, etapa1_system,
            "Execute a Etapa 1 para os documentos fornecidos.",
            combined_context, stream_to_console,
        )
        if is_once:
            Progress.etapa1("completed", "Cabecalhos extraidos com sucesso!")

        # --- Etapa 2: Calculo de Cifras CLT ---
        if run_idx is not None:
            print(f"{prefix}Iniciando Etapa 2 (Calculo de Cifras)...")
        if is_once:
            Progress.etapa2("processing", "Calculando cifras trabalhistas...")
        etapa2_system = (
            f"{P.BASE_SYSTEM_PROMPT.format(process_state='ETAPA_1_VALIDADA', next_action='Executar ETAPA 2')}"
            f"\n\n--- INSTRUCOES DA ETAPA ATUAL ---\n{P.PROMPT_ETAPA_2}"
        )
        if stream_to_console:
            print_title("Etapa 2: Lancamento e Calculo de Cifras")
        etapa2_raw, etapa2_metrics = run_llm_stage_streaming(
            config, etapa2_system,
            f"Execute a Etapa 2.\n\nMetadados da Etapa 1:\n\n{etapa1_raw}",
            combined_context, stream_to_console,
        )
        if is_once:
            Progress.etapa2("completed", "Cifras calculadas com sucesso!")

        # --- Etapa 3: Probabilidade e Risco CPC 25 ---
        if run_idx is not None:
            print(f"{prefix}Iniciando Etapa 3 (Probabilidade e Risco)...")
        if is_once:
            Progress.etapa3(0, "processing", "Calculando probabilidade e risco...")
        etapa3_system = (
            f"{P.BASE_SYSTEM_PROMPT.format(process_state='ETAPA_2_VALIDADA', next_action='Executar ETAPA 3')}"
            f"\n\n--- INSTRUCOES DA ETAPA ATUAL ---\n{P.PROMPT_ETAPA_3}"
        )
        if stream_to_console:
            print_title("Etapa 3: Atribuicao de Probabilidade e Risco")
        etapa3_raw, etapa3_metrics = run_llm_stage_streaming(
            config, etapa3_system,
            f"Execute a Etapa 3.\n\nSaida completa da Etapa 1:\n\n{etapa1_raw}"
            f"\n\nSaida completa da Etapa 2:\n\n{etapa2_raw}",
            combined_context, stream_to_console,
        )
        if is_once:
            Progress.etapa3(0, "completed", "Probabilidade calculada com sucesso!")

        # --- Etapa 4: Consolidacao Final (JSON) ---
        if run_idx is not None:
            print(f"{prefix}Iniciando Etapa 4 (Consolidacao Final)...")
        if is_once:
            Progress.etapa4("processing", "Consolidando resultados finais...")
        etapa4_system = (
            f"{P.BASE_SYSTEM_PROMPT.format(process_state='ETAPA_3_VALIDADA', next_action='Executar ETAPA 4')}"
            f"\n\n--- INSTRUCOES DA ETAPA ATUAL ---\n{P.PROMPT_ETAPA_4}"
        )
        if stream_to_console:
            print_title("Etapa 4: Consolidacao Final")
        etapa4_raw, etapa4_metrics = run_llm_stage_streaming(
            config, etapa4_system,
            f"Execute a Etapa 4 para consolidar os resultados.\n\n"
            f"Saida completa da Etapa 1:\n\n{etapa1_raw}\n\n"
            f"Saida completa da Etapa 2:\n\n{etapa2_raw}\n\n"
            f"Saida completa da Etapa 3:\n\n{etapa3_raw}",
            combined_context, stream_to_console,
        )

        # Parse do JSON da Etapa 4
        parsed_json = extract_json_from_markdown(etapa4_raw)
        if parsed_json is None:
            print(f"ERROR: {prefix}Falha ao parsear JSON na Etapa 4.")
            return None

        if run_idx is not None:
            print(f"{prefix}Etapa 4 concluida com sucesso.")

        if is_once:
            Progress.etapa4("completed", "Consolidacao finalizada com sucesso!")

        # Agrega metricas da rodada
        all_metrics = [etapa1_metrics, etapa2_metrics, etapa3_metrics, etapa4_metrics]
        run_metrics = merge_metrics(all_metrics)

        return {
            "etapa1_raw": etapa1_raw,
            "etapa2_raw": etapa2_raw,
            "etapa3_raw": etapa3_raw,
            "etapa4_raw": etapa4_raw,
            "parsed_json": parsed_json,
            "metrics": run_metrics,
        }

    except Exception as e:
        print(f"ERROR: {prefix}Falha na execucao: {e}")
        if is_once:
            Progress.etapa1("error", f"Falhou: {e}")
        return None


def save_stage_files(
    config: Config,
    s3_prefix: str,
    combined_context: str,
    data: dict,
) -> None:
    """Salva arquivos de cada etapa no S3 e localmente.

    Args:
        config: Configuracao do sistema.
        s3_prefix: Prefixo S3 (ex: results/).
        data: Dict com resultados de run_single_pipeline.
    """
    stages = [
        ("etapa1", data.get("etapa1_raw", "")),
        ("etapa2", data.get("etapa2_raw", "")),
        ("etapa3", data.get("etapa3_raw", "")),
        ("etapa4", data.get("etapa4_raw", "")),
    ]

    combined = data.get("etapa1_system", "")
    for stage_name, stage_raw in stages:
        content = (
            f"# EXECUCAO DA {stage_name.upper()}\n\n"
            f"## CONTEXTO DE ENTRADA\n\n"
            f"### DOCUMENTOS\n\n{combined_context}\n\n"
            f"## RESPOSTA DA IA\n\n{stage_raw}\n"
        )
        s3_key = f"{s3_prefix}/{stage_name}_completo.md"
        upload_file(config, content.encode("utf-8"), s3_key)

    # Adiciona nome do PDF ao JSON salvo
    json_obj = data.get("parsed_json", {}).copy()
    if "pdf_filename" not in json_obj:
        json_obj["pdf_filename"] = "relatorio_consolidado.pdf"

    # Salva JSON final (local + S3)
    json_data = json.dumps(json_obj, indent=2, ensure_ascii=False,)
    local_json_path = ROOT_DIR / "data" / "resultado_final.json"
    local_json_path.parent.mkdir(parents=True, exist_ok=True)
    local_json_path.write_text(json_data, encoding="utf-8")
    upload_file(
        config, json_data.encode("utf-8"),
        f"{s3_prefix}/resultado_final.json",
    )


def clean_artefatos_anteriores(mode: str) -> None:
    """Remove artefatos (PDFs e JSONs) do modo oposto antes de gerar novos.

    Args:
        mode: 'once' ou 'ten' — modo que sera executado.
    """
    pdfs_to_remove = (
        ["relatorio_consolidado_10x.pdf"]
        if mode == "once"
        else ["relatorio_consolidado.pdf"]
    )
    jsons_to_remove = (
        ["consolidado_10x.json"]
        if mode == "once"
        else ["resultado_final.json"]
    )
    for fname in pdfs_to_remove + jsons_to_remove:
        fpath = ROOT_DIR / "data" / fname
        if fpath.exists():
            fpath.unlink()


def run_once(config: Config, combined_context: str) -> dict:
    """Executa pipeline unico, salva resultados e gera PDF.

    Args:
        config: Configuracao do sistema.
        combined_context: Contexto dos documentos.

    Returns:
        Dict com resultado final.
    """
    from backend.pdf_generator import generate_pdf

    result = run_single_pipeline(config, combined_context, stream_to_console=True)
    if result is None:
        return {"status": "error", "message": "Pipeline falhou"}

    # Remove artefatos do modo oposto (10x) antes de gerar novos
    clean_artefatos_anteriores("once")
    delete_files(config, "results/relatorio_consolidado_10x.pdf")
    delete_files(config, "results/consolidado_10x.json")

    # Salva resultados no S3
    save_stage_files(config, "results", combined_context, result)

    # Gera PDF do relatorio
    report_text = (
        f"# Relatorio de Analise Juridica\n\n"
        f"## Etapa 1 - Metadados\n\n{result['etapa1_raw']}\n\n"
        f"## Etapa 2 - Cifras\n\n{result['etapa2_raw']}\n\n"
        f"## Etapa 3 - Risco\n\n{result['etapa3_raw']}\n\n"
        f"## Etapa 4 - Consolidacao\n\n{result['etapa4_raw']}\n"
    )

    pdf_path = ROOT_DIR / "data" / "relatorio_consolidado.pdf"
    generate_pdf(report_text, pdf_path)

    # Upload PDF para S3
    if pdf_path.exists():
        upload_file(
            config, pdf_path.read_bytes(),
            "results/relatorio_consolidado.pdf",
        )

    metrics = result.get("metrics", PipelineMetrics())
    print(f"\n{'=' * 40}")
    print(" RESUMO DA EXECUCAO")
    print(f"{'=' * 40}")
    print(format_metrics_report(metrics))

    # Registra no historico
    record_execution(
        mode="once", status="completed",
        metrics=metrics, summary=result.get("parsed_json"),
    )

    return {
        "status": "completed",
        "data": result.get("parsed_json"),
        "metrics": metrics,
    }


def run_ten_times(config: Config, combined_context: str) -> dict:
    """Executa pipeline otimizado: etapas 1,2,4 uma vez, etapa 3 em 10x.

    A etapa 1 (metadados) e etapa 2 (cifras) executam uma unica vez,
    pois sao deterministicas. A etapa 3 (probabilidade) executa 10 vezes
    em paralelo (max_workers=5) usando sempre o mesmo resultado fixo
    da etapa 2. A etapa 4 (consolidacao) executa uma vez com todos
    os resultados da etapa 3.

    Args:
        config: Configuracao do sistema.
        combined_context: Contexto dos documentos.

    Returns:
        Dict com resultado consolidado.
    """
    from backend.pdf_generator import generate_pdf

    print("\n[10x] Modo otimizado: Etapas 1 e 2 unicas, Etapa 3 em 10x...")
    print()

    # ======================================================================
    # ETAPA 1 (unica): Extracao de Metadados
    # ======================================================================
    print_title("Etapa 1: Extracao de Metadados (unica)")
    Progress.etapa1("processing", "Extraindo cabecalhos do processo...")
    etapa1_system = (
        f"{P.BASE_SYSTEM_PROMPT.format(process_state='INICIAL', next_action='Executar ETAPA 1')}"
        f"\n\n--- INSTRUCOES DA ETAPA ATUAL ---\n{P.PROMPT_ETAPA_1}"
    )
    try:
        etapa1_raw, etapa1_metrics = run_llm_stage_streaming(
            config, etapa1_system,
            "Execute a Etapa 1 para os documentos fornecidos.",
            combined_context, stream_to_console=True,
        )
    except Exception as e:
        print(f"ERROR: Etapa 1 falhou: {e}")
        Progress.etapa1("error", f"Falhou: {e}")
        record_execution(mode="ten", status="error", metrics=None, error=str(e))
        return {"status": "error", "message": f"Etapa 1 falhou: {e}"}
    Progress.etapa1("completed", "Cabecalhos extraidos com sucesso!")
    print()

    # ======================================================================
    # ETAPA 2 (unica): Calculo de Cifras CLT
    # ======================================================================
    print_title("Etapa 2: Lancamento e Calculo de Cifras (unica)")
    Progress.etapa2("processing", "Calculando cifras trabalhistas...")
    etapa2_system = (
        f"{P.BASE_SYSTEM_PROMPT.format(process_state='ETAPA_1_VALIDADA', next_action='Executar ETAPA 2')}"
        f"\n\n--- INSTRUCOES DA ETAPA ATUAL ---\n{P.PROMPT_ETAPA_2}"
    )
    try:
        etapa2_raw, etapa2_metrics = run_llm_stage_streaming(
            config, etapa2_system,
            f"Execute a Etapa 2.\n\nMetadados da Etapa 1:\n\n{etapa1_raw}",
            combined_context, stream_to_console=True,
        )
    except Exception as e:
        print(f"ERROR: Etapa 2 falhou: {e}")
        Progress.etapa2("error", f"Falhou: {e}")
        record_execution(mode="ten", status="error", metrics=None, error=str(e))
        return {"status": "error", "message": f"Etapa 2 falhou: {e}"}
    Progress.etapa2("completed", "Cifras calculadas com sucesso!")
    print()

    # ======================================================================
    # ETAPA 3 (10x paralelo): Probabilidade e Risco CPC 25
    # ======================================================================
    print_title("Etapa 3: Atribuicao de Probabilidade e Risco (10x paralelo)")
    etapa3_system = (
        f"{P.BASE_SYSTEM_PROMPT.format(process_state='ETAPA_2_VALIDADA', next_action='Executar ETAPA 3')}"
        f"\n\n--- INSTRUCOES DA ETAPA ATUAL ---\n{P.PROMPT_ETAPA_3}"
    )
    etapa3_user_msg = (
        f"Execute a Etapa 3.\n\nSaida completa da Etapa 1:\n\n{etapa1_raw}"
        f"\n\nSaida completa da Etapa 2:\n\n{etapa2_raw}"
    )

    etapa3_results: list[tuple[str, PipelineMetrics] | None] = [None] * 10

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for i in range(10):
            run_idx = i + 1
            Progress.etapa3(i, "processing", f"Rodada {run_idx} em andamento...")
            print(f"  [Rodada {run_idx}] Submetendo Etapa 3...")

            def _run_etapa3(idx=run_idx) -> tuple[str, PipelineMetrics]:
                pref = f"[Rodada {idx}] "
                print(f"{pref}Iniciando Etapa 3...")
                r, m = run_llm_stage_streaming(
                    config, etapa3_system,
                    etapa3_user_msg,  # MESMO resultado fixo da etapa 2
                    combined_context, stream_to_console=True,
                )
                print(f"{pref}Etapa 3 concluida.")
                return r, m

            futures[executor.submit(_run_etapa3)] = i

        for future in as_completed(futures):
            idx = futures[future]
            try:
                etapa3_raw_i, etapa3_metrics_i = future.result()
                etapa3_results[idx] = (etapa3_raw_i, etapa3_metrics_i)
                Progress.etapa3(idx, "completed", f"Rodada {idx + 1} - OK")
            except Exception as e:
                print(f"  [Rodada {idx + 1}] Etapa 3 falhou: {e}")
                Progress.etapa3(idx, "error", f"Rodada {idx + 1} - Falhou")

    # Filtra resultados validos da etapa 3
    valid_etapa3 = [
        (raw, metrics) for raw, metrics in etapa3_results if raw is not None
    ]
    if not valid_etapa3:
        print("ERROR: Todas as 10 repeticoes da Etapa 3 falharam.")
        record_execution(mode="ten", status="error", metrics=None, error="Todas as etapas 3 falharam")
        return {"status": "error", "message": "Todas as 10 repeticoes da Etapa 3 falharam"}

    print(f"\n  -> {len(valid_etapa3)}/10 repeticoes da Etapa 3 concluidas com sucesso.")
    print()

    # ======================================================================
    # ETAPA 4 (unica): Consolidacao Final (JSON)
    # ======================================================================
    print_title("Etapa 4: Consolidacao Final (unica)")
    Progress.etapa4("processing", "Consolidando resultados das 10 rodadas...")

    # Concatena todas as saidas da etapa 3 para a etapa 4
    all_etapa3_raw_parts = []
    for i, (raw_i, _) in enumerate(valid_etapa3, 1):
        all_etapa3_raw_parts.append(f"--- Repeticao {i} ---\n{raw_i}")
    all_etapa3_raw = "\n\n".join(all_etapa3_raw_parts)

    etapa4_system = (
        f"{P.BASE_SYSTEM_PROMPT.format(process_state='ETAPA_3_VALIDADA', next_action='Executar ETAPA 4')}"
        f"\n\n--- INSTRUCOES DA ETAPA ATUAL ---\n{P.PROMPT_ETAPA_4}"
    )
    try:
        etapa4_raw, etapa4_metrics = run_llm_stage_streaming(
            config, etapa4_system,
            f"Execute a Etapa 4 para consolidar os resultados.\n\n"
            f"Saida completa da Etapa 1:\n\n{etapa1_raw}\n\n"
            f"Saida completa da Etapa 2:\n\n{etapa2_raw}\n\n"
            f"Saidas completas das {len(valid_etapa3)} repeticoes da Etapa 3:\n\n{all_etapa3_raw}",
            combined_context, stream_to_console=True,
        )
    except Exception as e:
        print(f"ERROR: Etapa 4 falhou: {e}")
        record_execution(mode="ten", status="error", metrics=None, error=str(e))
        return {"status": "error", "message": f"Etapa 4 falhou: {e}"}

    # Parse do JSON da Etapa 4
    parsed_json = extract_json_from_markdown(etapa4_raw)
    if parsed_json is None:
        print("ERROR: Falha ao parsear JSON na Etapa 4.")
        record_execution(mode="ten", status="error", metrics=None, error="Falha ao parsear JSON")
        return {"status": "error", "message": "Falha ao parsear JSON na Etapa 4"}

    print("\nEtapa 4 concluida com sucesso.")
    Progress.etapa4("completed", "Consolidacao finalizada!")

    # ======================================================================
    # Salva resultados no S3
    # ======================================================================
    # Monta um resultado unificado para save_stage_files
    unified_result = {
        "etapa1_raw": etapa1_raw,
        "etapa2_raw": etapa2_raw,
        "etapa3_raw": all_etapa3_raw,
        "etapa4_raw": etapa4_raw,
        "parsed_json": parsed_json,
    }
    save_stage_files(config, "results", combined_context, unified_result)

    # Salva cada repeticao da etapa 3 individualmente
    for i, (raw_i, _) in enumerate(valid_etapa3, 1):
        etapa3_content = (
            f"# EXECUCAO DA ETAPA 3 - REPETICAO {i}\n\n"
            f"## RESPOSTA DA IA\n\n{raw_i}\n"
        )
        upload_file(
            config, etapa3_content.encode("utf-8"),
            f"results/etapa3_repeticao_{i}.md",
        )

    # Gera relatorio de auditoria (local + S3)
    audit_lines = ["# Auditoria de 10 Rodadas (Modo Otimizado)\n"]
    audit_lines.append(f"## Etapas 1 e 2 (unicas)\n")
    audit_lines.append(f"- Etapa 1: {etapa1_metrics.prompt_tokens if etapa1_metrics else 0} tokens\n")
    audit_lines.append(f"- Etapa 2: {etapa2_metrics.prompt_tokens if etapa2_metrics else 0} tokens\n")
    audit_lines.append(f"\n## Etapa 3 ({len(valid_etapa3)}/10 repeticoes)\n")
    for i, (_, m) in enumerate(valid_etapa3, 1):
        audit_lines.append(f"- Repeticao {i}: {m.prompt_tokens if m else 0} in / {m.completion_tokens if m else 0} out / ${m.cost_total if m else 0:.6f}")
    audit_lines.append("")
    audit_lines.append(f"\n## Consolidacao\n")
    audit_lines.append(f"```json\n{json.dumps(parsed_json, indent=2, ensure_ascii=False)}\n```\n")
    audit_text = "\n".join(audit_lines)
    # Salva localmente
    audit_local_path = ROOT_DIR / "data" / "auditoria_10x.md"
    audit_local_path.parent.mkdir(parents=True, exist_ok=True)
    audit_local_path.write_text(audit_text, encoding="utf-8")
    # Upload para S3 (fallback)
    upload_file(config, audit_text.encode("utf-8"), "results/auditoria_10x.md")

    # Remove artefatos do modo oposto (1x) antes de gerar novos
    clean_artefatos_anteriores("ten")
    delete_files(config, "results/relatorio_consolidado.pdf")
    delete_files(config, "results/resultado_final.json")

    # Salva JSON consolidado (local + S3)
    json_obj = parsed_json.copy()
    json_obj["pdf_filename"] = "relatorio_consolidado_10x.pdf"
    json_consolidado = json.dumps(json_obj, indent=2, ensure_ascii=False).encode("utf-8")
    json_local_path = ROOT_DIR / "data" / "consolidado_10x.json"
    json_local_path.parent.mkdir(parents=True, exist_ok=True)
    json_local_path.write_text(json_consolidado.decode("utf-8"), encoding="utf-8")
    upload_file(config, json_consolidado, "results/consolidado_10x.json")

    # Gera PDF consolidado
    report_lines = ["# Relatorio Consolidado - 10 Analises\n"]
    report_lines.append(f"## Total de Repeticoes: {len(valid_etapa3)}/10\n")
    report_lines.append(f"```json\n{json.dumps(parsed_json, indent=2, ensure_ascii=False)}\n```\n")

    report_text = "\n".join(report_lines)
    pdf_path = ROOT_DIR / "data" / "relatorio_consolidado_10x.pdf"
    generate_pdf(report_text, pdf_path)

    if pdf_path.exists():
        upload_file(
            config, pdf_path.read_bytes(),
            "results/relatorio_consolidado_10x.pdf",
        )

    # Agrega metricas totais
    all_metrics_list = [etapa1_metrics, etapa2_metrics, etapa4_metrics]
    all_metrics_list += [m for _, m in valid_etapa3]
    total_metrics = merge_metrics([m for m in all_metrics_list if m is not None])

    print(f"\n{'=' * 40}")
    print(" RESUMO DA EXECUCAO (10x Otimizado)")
    print(f"{'=' * 40}")
    print(format_metrics_report(total_metrics))

    # Registra no historico
    record_execution(
        mode="ten", status="completed",
        metrics=total_metrics, summary=parsed_json,
    )

    # Prepara lista de metricas individuais das rodadas (para exibicao frontend)
    run_metrics_list = []
    for i, (_, m) in enumerate(valid_etapa3, 1):
        if m:
            run_metrics_list.append({
                "run": i,
                "prompt_tokens": m.prompt_tokens,
                "completion_tokens": m.completion_tokens,
                "cache_tokens": m.cache_tokens,
                "cost_input": m.cost_input,
                "cost_output": m.cost_output,
                "cost_cache": m.cost_cache,
                "cost_total": m.cost_total,
            })

    return {
        "status": "completed",
        "data": parsed_json,
        "total_runs": len(valid_etapa3),
        "metrics": total_metrics,
        "run_metrics_list": run_metrics_list,
    }


def aggregate_results(results: list[dict]) -> dict:
    """Agrega resultados de multiplas rodadas (media).

    Args:
        results: Lista de JSONs de resultado.

    Returns:
        Dict consolidado com medias.
    """
    if not results:
        return {}

    consolidated = {
        "numero_processo": results[0].get("numero_processo", ""),
        "autor": results[0].get("autor", ""),
        "adv_reclamante": results[0].get("adv_reclamante", ""),
        "localidade": results[0].get("localidade", ""),
        "juizo": results[0].get("juizo", ""),
        "reclamada": results[0].get("reclamada", ""),
        "segunda_reclamada": results[0].get("segunda_reclamada", ""),
        "inicio_processo": results[0].get("inicio_processo", ""),
        "valor_causa": results[0].get("valor_causa", ""),
        "cifras": [],
        "valor_total_estimado": "0,00",
    }

    cifras_map: dict[str, list[dict]] = {}
    for r in results:
        for c in r.get("cifras", []):
            name = c.get("cifra", "")
            std_name = standardize_cifra_name(name)
            if std_name not in cifras_map:
                cifras_map[std_name] = []
            cifras_map[std_name].append(c)

    total_avg_estimado = 0.0
    for std_name, items in cifras_map.items():
        description = items[0].get("descricao", "")
        for item in items:
            desc = item.get("descricao", "")
            if len(desc) > len(description):
                description = desc

        base_vals = [parse_monetary(item.get("valor", "0")) for item in items]
        estimado_vals = [
            parse_monetary(item.get("valor_estimado", "0")) for item in items
        ]

        avg_base = sum(base_vals) / len(base_vals) if base_vals else 0.0
        avg_estimado = (
            sum(estimado_vals) / len(estimado_vals) if estimado_vals else 0.0
        )

        total_avg_estimado += avg_estimado
        prob = calculate_probability_label(avg_estimado, avg_base)

        consolidated["cifras"].append({
            "cifra": std_name,
            "valor": format_monetary(avg_base),
            "descricao": description,
            "probabilidade": prob,
            "valor_estimado": format_monetary(avg_estimado),
        })

    consolidated["valor_total_estimado"] = format_monetary(total_avg_estimado)
    return consolidated


# ---------------------------------------------------------------------------
# Execution History — historico de execucoes em memoria
# ---------------------------------------------------------------------------
from datetime import datetime

_execution_history: list[dict] = []
_MAX_HISTORY = 50


def record_execution(
    mode: str,
    status: str,
    metrics: PipelineMetrics | None,
    summary: dict | None = None,
    error: str = "",
) -> None:
    """Registra uma execucao no historico.

    Args:
        mode: Modo de execucao ('once' ou 'ten').
        status: Status ('completed', 'error').
        metrics: Metricas da execucao (opcional).
        summary: Resumo JSON do resultado (opcional).
        error: Mensagem de erro (se houve).
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "status": status,
        "error": error,
    }
    if metrics:
        entry["metrics"] = {
            "prompt_tokens": metrics.prompt_tokens,
            "completion_tokens": metrics.completion_tokens,
            "cache_tokens": metrics.cache_tokens,
            "cost_input": metrics.cost_input,
            "cost_output": metrics.cost_output,
            "cost_cache": metrics.cost_cache,
            "cost_total": metrics.cost_total,
        }
    if summary:
        cifras = summary.get("cifras", [])
        entry["summary"] = {
            "total_cifras": len(cifras),
            "valor_total_estimado": summary.get("valor_total_estimado", "0,00"),
            "numero_processo": summary.get("numero_processo", ""),
        }

    _execution_history.append(entry)
    if len(_execution_history) > _MAX_HISTORY:
        _execution_history.pop(0)


def get_execution_history(limit: int = 50) -> list[dict]:
    """Retorna historico de execucoes.

    Args:
        limit: Maximo de entradas a retornar.

    Returns:
        Lista com historico (mais recentes primeiro).
    """
    return list(reversed(_execution_history))[:limit]


def get_last_metrics() -> dict | None:
    """Retorna metricas da ultima execucao.

    Returns:
        Dict com metricas ou None se nao houver execucao.
    """
    if not _execution_history:
        return None
    return _execution_history[-1].get("metrics")


def clear_execution_history() -> None:
    """Limpa todo o historico de execucoes."""
    _execution_history.clear()
