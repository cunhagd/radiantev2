from __future__ import annotations
import json
import re
from copy import deepcopy
from datetime import datetime
from io import BytesIO
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, HRFlowable, PageBreak,
    Paragraph, Spacer, Table, TableStyle,
)

MARGIN = 2 * 28.3465
PAGE_W = A4[0] - 2 * MARGIN

# ── MD3 Color Palette ────────────────────────────────────────────────
C_PRIMARY            = colors.HexColor("#6750A4")
C_SECONDARY          = colors.HexColor("#625B71")
C_TERTIARY           = colors.HexColor("#7D5260")
C_SURFACE            = colors.HexColor("#FFFBFE")
C_SURFACE_VARIANT    = colors.HexColor("#E7E0EC")
C_OUTLINE            = colors.HexColor("#79747E")
C_ERROR              = colors.HexColor("#B3261E")
C_BACKGROUND         = colors.HexColor("#FFFBFE")
C_ON_PRIMARY         = colors.HexColor("#FFFFFF")
C_ON_SURFACE         = colors.HexColor("#1C1B1F")
C_ON_SURFACE_VARIANT = colors.HexColor("#49454F")

# ── 9 Paragraph Styles ───────────────────────────────────────────────
def _st(name, font, size, leading, color, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                          textColor=color, **kw)

TITLE_STYLE = _st("T", "Helvetica-Bold", 16, 20, C_PRIMARY, spaceAfter=12, spaceBefore=4)
H2_STYLE = _st("H2", "Helvetica-Bold", 14, 17, C_SECONDARY, spaceAfter=8, spaceBefore=10)
H3_STYLE = _st("H3", "Helvetica-Bold", 12, 15, C_TERTIARY, spaceAfter=6, spaceBefore=6)
BODY_STYLE = _st("B", "Helvetica", 11, 14, C_ON_SURFACE, spaceAfter=4, spaceBefore=0)
CODE_STYLE = _st("CD", "Courier", 9, 12, C_ON_SURFACE, spaceAfter=4, spaceBefore=2, leftIndent=10, rightIndent=10)
LIST_STYLE = _st("L", "Helvetica", 11, 14, C_ON_SURFACE, spaceAfter=4, spaceBefore=0, leftIndent=15)
BLOCKQUOTE_STYLE = _st("BQ", "Helvetica", 10, 13, C_ON_SURFACE_VARIANT,
                       spaceAfter=4, spaceBefore=2, leftIndent=20, rightIndent=10)
COVER_TITLE_STYLE = _st("CT", "Helvetica-Bold", 24, 28, C_PRIMARY, spaceAfter=4, spaceBefore=0, alignment=TA_CENTER)
COVER_SUBTITLE_STYLE = _st("CS", "Helvetica", 14, 17, C_SECONDARY, spaceAfter=4, spaceBefore=0, alignment=TA_CENTER)

RE_H1 = re.compile(r"^# (.+)$")
RE_H2 = re.compile(r"^## (.+)$")
RE_H3 = re.compile(r"^### (.+)$")
RE_LIST = re.compile(r"^[\*\-] +(.+)$")


def _parse_inline(text: str) -> str:
    """Converte markdown inline (*, **, `) para XML do ReportLab."""
    if not text:
        return text
    # 1. Escape HTML (& primeiro para evitar duplo escape)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # 2. Codigo inline: `codigo` → <font face="Courier">codigo</font>
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    # 3. Negrito: **texto** → <b>texto</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # 4. Italico: *texto* → <i>texto</i> (excluindo * que sao parte de **)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def _make_accents() -> list:
    """Cria accent bar (Table 4pt x 18pt cor primary) + divider (HRFlowable)."""
    out = []
    accent = Table([[""]], colWidths=[4], rowHeights=[18])
    accent.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    out.append(accent)
    out.append(Spacer(1, 2))
    return out


def _make_table(cells: list[str]) -> Table:
    """Tabela MD3: header primary, body alternado."""
    n = len(cells)
    rows = [[c.strip() for c in cells]]
    t = Table(rows, colWidths=[PAGE_W / n] * n)
    cmds = [
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), C_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_ON_PRIMARY),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, C_OUTLINE),
        ("BOX", (0, 0), (-1, -1), 0.5, C_OUTLINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i in range(1, len(rows)):
        bg = C_SURFACE if i % 2 == 0 else C_SURFACE_VARIANT
        cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(cmds))
    return t


def _make_code_block(code_text: str) -> list:
    """Bloco de codigo com fundo/borda (<=20 linhas) ou Paragraph simples (>20)."""
    lines = code_text.count("<br/>") + 1
    p = Paragraph(code_text, CODE_STYLE)
    if lines > 20:
        return [p]
    ct = Table([[p]], colWidths=[PAGE_W - 10])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_SURFACE_VARIANT),
        ("BOX", (0, 0), (-1, -1), 0.5, C_OUTLINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [ct]


def _validate_pdf(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"Falha: PDF {path} nao foi criado")
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        raise RuntimeError(f"Falha: cabecalho %%PDF- ausente em {path}")
    if not data.strip().endswith(b"%%EOF"):
        raise RuntimeError(f"Falha: marcador %%EOF ausente em {path}")


class _PdfDoc(BaseDocTemplate):
    """DocTemplate MD3: cabecalho/rodape via afterPage()."""

    def __init__(self, filename, total_pages=1, **kw):
        self._total = total_pages
        frame = Frame(MARGIN, MARGIN + 5, PAGE_W, A4[1] - 2 * MARGIN - 15,
                      id="normal", leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)
        BaseDocTemplate.__init__(self, filename, pagesize=A4, **kw)
        self.addPageTemplates([PageTemplate(id="main", frames=[frame])])

    def afterPage(self):
        c = self.canv
        c.saveState()
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(C_PRIMARY)
        c.drawString(MARGIN, A4[1] - 25, "Radiante - Analise Juridica")
        c.setStrokeColor(C_OUTLINE)
        c.setLineWidth(0.5)
        c.line(MARGIN, A4[1] - 30, A4[0] - MARGIN, A4[1] - 30)
        c.setFont("Helvetica", 8)
        c.setFillColor(C_ON_SURFACE_VARIANT)
        c.drawCentredString(A4[0] / 2, 15, f"Pagina {self.page} de {self._total}")
        c.restoreState()


def _build(elements, dest, total_pages=1):
    doc = _PdfDoc(dest, total_pages=total_pages)
    doc.build(elements)


def _count_pages(elements) -> int:
    class _C(BaseDocTemplate):
        def afterPage(self):
            self._n = getattr(self, "_n", 0) + 1
    frame = Frame(MARGIN, MARGIN + 5, PAGE_W, A4[1] - 2 * MARGIN - 15,
                  id="normal", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc = _C(BytesIO(), pagesize=A4)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
    doc._n = 0
    doc.build(elements)
    return max(doc._n, 1)


def generate_pdf(etapas_dir: str | Path, output_path: str | Path) -> str:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    etapas_path = Path(etapas_dir)
    if not etapas_path.exists():
        raise FileNotFoundError(f"Diretorio de etapas nao encontrado: {etapas_dir}")

    md_files = sorted(etapas_path.glob("*.md"))
    if not md_files:
        _build([Paragraph("Nenhum conteudo disponivel para o relatorio.", BODY_STYLE)],
               str(output_path), total_pages=1)
        _validate_pdf(output_path)
        return str(output_path.resolve())

    # ── Cover page ──────────────────────────────────────────────────
    cover_elements: list = []
    json_path = etapas_path.parent / "resultado_final.json"
    if json_path.exists():
        try:
            meta = json.loads(json_path.read_text(encoding="utf-8"))
            cover_elements.append(Spacer(1, A4[1] / 4))
            cover_elements.append(Paragraph("Radiante", COVER_TITLE_STYLE))
            cover_elements.append(Spacer(1, 6))
            cover_elements.append(Paragraph("Analise Juridica", COVER_SUBTITLE_STYLE))
            cover_elements.append(Spacer(1, 12))
            cover_elements.append(HRFlowable(width="60%", thickness=0.5, color=C_OUTLINE,
                                              spaceBefore=6, spaceAfter=16))
            fields = [
                ("Processo", meta.get("numero_processo", "N/A")),
                ("Autor", meta.get("autor", "N/A")),
                ("Reclamada", meta.get("reclamada", "N/A")),
                ("Valor Total Estimado", f'R$ {meta.get("valor_total_estimado", "0,00")}'),
                ("Data de Geracao", datetime.now().strftime("%d/%m/%Y")),
            ]
            for label, value in fields:
                cover_elements.append(Paragraph(
                    f'<b>{label}:</b>  {value}', BODY_STYLE))
            cover_elements.append(PageBreak())
        except (json.JSONDecodeError, KeyError):
            pass

    # ── Parser markdown → elements ─────────────────────────────────
    all_flowables: list = []
    in_code = False
    code_lines: list[str] = []

    def flush_code():
        nonlocal code_lines, in_code
        if code_lines:
            text = "\n".join(code_lines).replace("\n", "<br/>")
            all_flowables.extend(_make_code_block(text))
            all_flowables.append(Spacer(1, 4))
            code_lines = []
            in_code = False

    for fpath in md_files:
        text = fpath.read_text(encoding="utf-8")
        content_elements: list = []

        for raw_line in text.split("\n"):
            s = raw_line.strip()

            if s == "```":
                if in_code:
                    flush_code()
                else:
                    in_code = True
                continue

            if in_code:
                code_lines.append(raw_line)
                continue

            # Blockquote (> ...)
            if s.startswith(">"):
                content = s.lstrip(">").strip()
                if content:
                    content_elements.append(Paragraph(
                        _parse_inline(content), BLOCKQUOTE_STYLE))
                continue

            if not s:
                content_elements.append(Spacer(1, 6))
                continue

            m = RE_H1.match(s)
            if m:
                content_elements.append(Paragraph(
                    _parse_inline(m.group(1)), TITLE_STYLE))
                continue

            m = RE_H2.match(s)
            if m:
                content_elements.append(Paragraph(
                    _parse_inline(m.group(1)), H2_STYLE))
                continue

            m = RE_H3.match(s)
            if m:
                content_elements.append(Paragraph(
                    _parse_inline(m.group(1)), H3_STYLE))
                continue

            if s.startswith("|") and not s.lstrip("|").startswith("-"):
                cells = [c.strip() for c in s.split("|") if c.strip()]
                if cells:
                    content_elements.append(_make_table(cells))
                    content_elements.append(Spacer(1, 3))
                continue

            m = RE_LIST.match(s)
            if m:
                content_elements.append(Paragraph(
                    f"\u2022 {_parse_inline(m.group(1))}", LIST_STYLE))
                continue

            content_elements.append(Paragraph(_parse_inline(s), BODY_STYLE))

        if in_code:
            flush_code()

        # Wrap etapa with accent bar + divider
        if content_elements:
            if all_flowables:
                all_flowables.append(HRFlowable(width="100%", thickness=0.5, color=C_OUTLINE,
                                                 spaceBefore=6, spaceAfter=6))
            all_flowables.extend(_make_accents())
            all_flowables.extend(content_elements)
            all_flowables.append(Spacer(1, 6))

    # Assemble final elements: cover (if any) + content
    final_elements = cover_elements + all_flowables

    try:
        total = _count_pages(deepcopy(final_elements))
        _build(deepcopy(final_elements), str(output_path), total_pages=total)
        _validate_pdf(output_path)
    except Exception:
        output_path.unlink(missing_ok=True)
        raise

    return str(output_path.resolve())
