#!/usr/bin/env python3
"""Geracao de PDF consolidado para o Radiante v2.

Usa ReportLab para gerar PDF estilizado (Material Design 3)
a partir de texto markdown com as analises juridicas.
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ── Paleta Material Design 3 ──────────────────────────────────────────────
C_PRIMARY = colors.HexColor("#4285f4")
C_SURFACE_1 = colors.HexColor("#f8f9fa")
C_SURFACE_2 = colors.HexColor("#e8eaed")
C_OUTLINE = colors.HexColor("#dadce0")
C_TEXT = colors.HexColor("#1f1f1f")
C_TEXT_MUTED = colors.HexColor("#5f6368")
C_SUCCESS_BG = colors.HexColor("#e6f4ea")
C_SUCCESS = colors.HexColor("#34a853")
C_TABLE_HEADER = colors.HexColor("#e8f0fe")
C_CODE_BG = colors.HexColor("#f1f5f9")

# Largura util do conteudo (A4 - margens)
PAGE_W = A4[0] - 80


# ── Estilos de texto ─────────────────────────────────────────────────────
TITLE_STYLE = ParagraphStyle(
    "T", fontName="Helvetica-Bold", fontSize=16, leading=20,
    textColor=C_PRIMARY, spaceAfter=16, spaceBefore=4,
)
H2_STYLE = ParagraphStyle(
    "H2", fontName="Helvetica-Bold", fontSize=12, leading=15,
    textColor=C_PRIMARY, spaceAfter=8, spaceBefore=0,
)
H3_STYLE = ParagraphStyle(
    "H3", fontName="Helvetica-Bold", fontSize=10, leading=13,
    textColor=C_TEXT, spaceAfter=6, spaceBefore=0,
)
BODY_STYLE = ParagraphStyle(
    "B", fontName="Helvetica", fontSize=9, leading=13,
    textColor=C_TEXT, spaceAfter=6, spaceBefore=0,
)
CALLOUT_STYLE = ParagraphStyle(
    "C", fontName="Helvetica-Bold", fontSize=12, leading=15,
    textColor=C_SUCCESS, spaceAfter=0, spaceBefore=0,
    alignment=1,  # CENTER
)
CODE_STYLE = ParagraphStyle(
    "CD", fontName="Courier", fontSize=7.5, leading=10,
    textColor=C_TEXT, backColor=C_CODE_BG,
    spaceAfter=4, spaceBefore=2,
    leftIndent=6, rightIndent=6,
)


# ── Padroes de busca ─────────────────────────────────────────────────────
RE_HEADING_H1 = re.compile(r"^# (.+)$")
RE_HEADING_H2 = re.compile(r"^## (.+)$")
RE_HEADING_H3 = re.compile(r"^### (.+)$")
RE_CODE_FENCE = re.compile(r"^```")
RE_TABLE_ROW = re.compile(r"^\|")
RE_TABLE_SEPARATOR = re.compile(r"^\|[\s:]*[-]+[\s:|]*$")
RE_ETAPA = re.compile(r"^## (Etapa \d+|Total de Repeticoes)")


def _make_page_callback(total_pages: int):
    """Retorna callback para cabecalho e rodape com total de paginas."""
    def _draw(canvas, doc):
        canvas.saveState()
        # Cabecalho
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(C_TEXT)
        canvas.drawString(40, A4[1] - 30, "Radiante — Análise Jurídica")
        canvas.setStrokeColor(C_OUTLINE)
        canvas.setLineWidth(0.5)
        canvas.line(40, A4[1] - 36, A4[0] - 40, A4[1] - 36)
        # Rodape
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(C_TEXT_MUTED)
        canvas.drawCentredString(A4[0] / 2, 20, f"Página {doc.page} de {total_pages}")
        canvas.restoreState()
    return _draw


def _make_etapa_block(title: str, body: list, is_odd: bool) -> list:
    """Cria bloco visual com fundo colorido para uma etapa."""
    if not body:
        return []
    bg = C_SURFACE_2 if is_odd else C_SURFACE_1
    inner = [Paragraph(title, H2_STYLE)] + body
    block = Table([[inner]], colWidths=[PAGE_W])
    block.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return [block, Spacer(1, 10)]


def _make_callout(text: str) -> Table:
    """Cria callout de destaque verde para o valor total."""
    callout = Table([[Paragraph(text, CALLOUT_STYLE)]], colWidths=[PAGE_W])
    callout.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_SUCCESS_BG),
        ("BOX", (0, 0), (-1, -1), 1.5, C_SUCCESS),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    return callout


def _make_table(cells: list[str], is_header: bool) -> Table:
    """Cria tabela estilizada com grade sutil."""
    n = len(cells)
    col_w = max(PAGE_W / n, 70) if n > 0 else PAGE_W
    t = Table([cells], colWidths=[col_w] * n) if n > 0 else Table([cells])

    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, C_OUTLINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    if is_header:
        style = [
            ("BACKGROUND", (0, 0), (-1, -1), C_TABLE_HEADER),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (-1, -1), C_PRIMARY),
        ] + style

    t.setStyle(TableStyle(style))
    return t


def generate_pdf(text: str, output_path: str | Path) -> str:
    """Gera PDF a partir de texto markdown com design Material Design 3.

    Args:
        text: Conteudo markdown a ser convertido.
        output_path: Caminho de saida do PDF.

    Returns:
        Caminho absoluto do PDF gerado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = text.split("\n")
    elements: list = []

    etapa_body: list = []
    in_etapa = False
    in_code = False
    code_lines: list = []
    etapa_idx = 0
    callout_done = False

    def flush_etapa():
        nonlocal etapa_body, in_etapa, etapa_idx
        if etapa_body:
            block = _make_etapa_block(etapa_title, etapa_body, etapa_idx % 2 == 1)
            elements.extend(block)
            etapa_idx += 1
        etapa_body = []
        in_etapa = False

    etapa_title = ""

    for line in lines:
        stripped = line.strip()

        # ── Code block ───────────────────────────────────────────────
        if RE_CODE_FENCE.match(stripped):
            if in_code:
                # Fecha code block
                if in_etapa:
                    etapa_body.append(Paragraph(
                        "\n".join(code_lines).replace("\n", "<br/>"), CODE_STYLE
                    ))
                else:
                    elements.append(Paragraph(
                        "\n".join(code_lines).replace("\n", "<br/>"), CODE_STYLE
                    ))
                    elements.append(Spacer(1, 4))
                code_lines = []
                in_code = False
            else:
                if in_etapa:
                    flush_etapa()
                in_code = True
            continue

        if in_code:
            code_lines.append(stripped)
            continue

        # ── Linha em branco ──────────────────────────────────────────
        if not stripped:
            if in_etapa:
                etapa_body.append(Spacer(1, 4))
            else:
                elements.append(Spacer(1, 6))
            continue

        # ── # Title (H1) ─────────────────────────────────────────────
        m1 = RE_HEADING_H1.match(stripped)
        if m1:
            if in_etapa:
                flush_etapa()
            elements.append(Paragraph(m1.group(1), TITLE_STYLE))
            continue

        # ── ## Section (H2) ──────────────────────────────────────────
        m2 = RE_HEADING_H2.match(stripped)
        if m2:
            title_text = m2.group(1)
            if RE_ETAPA.match(stripped):
                # Inicia bloco de etapa
                if in_etapa:
                    flush_etapa()
                etapa_title = title_text
                in_etapa = True
            else:
                # Header comum
                if in_etapa:
                    flush_etapa()
                elements.append(Paragraph(title_text, H2_STYLE))
            continue

        # ── ### Subsection (H3) ──────────────────────────────────────
        m3 = RE_HEADING_H3.match(stripped)
        if m3:
            if in_etapa:
                etapa_body.append(Paragraph(m3.group(1), H3_STYLE))
            else:
                elements.append(Paragraph(m3.group(1), H3_STYLE))
            continue

        # ── Tabela markdown ──────────────────────────────────────────
        if RE_TABLE_ROW.match(stripped) and not RE_TABLE_SEPARATOR.match(stripped):
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if not cells:
                continue

            # Detecta cabecalho (linha com valores curtos sem cifrao)
            has_currency = any("R$" in c for c in cells)
            is_header = all(len(c) < 35 for c in cells) and not has_currency

            # Detecta linha de total para callout
            is_total = any("Total" in c for c in cells) and has_currency and not callout_done

            if is_total:
                if in_etapa:
                    flush_etapa()
                # Extrai o texto do total
                total_text = " | ".join(cells)
                elements.append(_make_callout(total_text))
                callout_done = True
                elements.append(Spacer(1, 8))
                continue

            tbl = _make_table(cells, is_header)
            if in_etapa:
                etapa_body.append(tbl)
                etapa_body.append(Spacer(1, 3))
            else:
                elements.append(tbl)
                elements.append(Spacer(1, 3))
            continue

        # ── Texto comum ──────────────────────────────────────────────
        if in_etapa:
            etapa_body.append(Paragraph(stripped, BODY_STYLE))
        else:
            elements.append(Paragraph(stripped, BODY_STYLE))

    # Flush ultimo bloco
    if in_etapa:
        flush_etapa()

    # ── Two-pass build (Página X de Y) ─────────────────────────────────
    # Pass 1: build silencioso para contar paginas
    _counter = [0]

    def _count_pages(canvas, doc):
        _counter[0] += 1

    _tmp_path = str(output_path.with_suffix(".tmp.pdf"))
    doc1 = SimpleDocTemplate(
        _tmp_path, pagesize=A4,
        leftMargin=40, rightMargin=40,
        topMargin=50, bottomMargin=40,
    )
    doc1.build(elements, onFirstPage=_count_pages, onLaterPages=_count_pages)
    total_pages = _counter[0]
    Path(_tmp_path).unlink(missing_ok=True)

    # Pass 2: build final com rodape contendo total de paginas
    page_cb = _make_page_callback(total_pages)
    doc2 = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=40, rightMargin=40,
        topMargin=50, bottomMargin=40,
    )
    doc2.build(elements, onFirstPage=page_cb, onLaterPages=page_cb)
    return str(output_path.resolve())
