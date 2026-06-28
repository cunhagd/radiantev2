#!/usr/bin/env python3
"""Geracao de PDF consolidado para o Radiante v2.

Usa ReportLab para gerar PDF estilizado a partir de texto markdown
com as analises juridicas.
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf(text: str, output_path: str | Path) -> str:
    """Gera PDF a partir de texto markdown.

    Args:
        text: Conteudo markdown a ser convertido.
        output_path: Caminho de saida do PDF.

    Returns:
        Caminho absoluto do PDF gerado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    h1_style = ParagraphStyle(
        "CustomH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=12,
        spaceBefore=18,
    )
    h2_style = ParagraphStyle(
        "CustomH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10,
        spaceBefore=14,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8,
    )
    code_style = ParagraphStyle(
        "CustomCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=10,
        backColor=colors.HexColor("#f1f5f9"),
        spaceAfter=6,
    )

    elements: list = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            elements.append(Spacer(1, 6))
        elif stripped.startswith("### "):
            elements.append(Paragraph(stripped[4:], h2_style))
        elif stripped.startswith("## "):
            elements.append(Paragraph(stripped[3:], h1_style))
        elif stripped.startswith("```"):
            continue
        elif stripped.startswith("|"):
            _add_table(elements, stripped, body_style)
        else:
            elements.append(Paragraph(stripped, body_style))

    doc.build(elements)
    return str(output_path.resolve())


def _add_table(
    elements: list,
    row_text: str,
    body_style: ParagraphStyle,
) -> None:
    """Adiciona linha de tabela ao PDF.

    Args:
        elements: Lista de elementos do PDF.
        row_text: Linha de tabela em markdown.
        body_style: Estilo do corpo.
    """
    cells = [c.strip() for c in row_text.split("|") if c.strip()]
    if not cells:
        return

    table = Table([cells], colWidths=[120, 300])

    is_header = any(c.startswith(":---") for c in cells)
    if is_header:
        return

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 4))
