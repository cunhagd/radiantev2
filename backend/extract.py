#!/usr/bin/env python3
"""Extracao de texto de documentos para o Radiante v2.

Suporta PDF (com fallback OCR via Textract), DOCX, JSON e TXT.
"""

from __future__ import annotations

import json
import zipfile
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from backend.config import Config


# Estatisticas globais de extracao
DATA_TREATMENT_STATS: dict[str, float | int] = {
    "processed_documents": 0,
    "native_text_pages": 0,
    "ocr_pages": 0,
    "textract_cost": 0.0,
    "processing_time": 0.0,
}


def extract_pdf_text(config: Config, filename: str, file_bytes: bytes) -> str:
    """Extrai texto de PDF.

    Tenta extracao nativa via PyMuPDF. Se o texto medio for menor que
    100 caracteres por pagina, faz OCR via Amazon Textract.

    Args:
        config: Configuracao do sistema.
        filename: Nome do arquivo (para logging).
        file_bytes: Conteudo binario do PDF.

    Returns:
        Texto extraido do PDF.
    """
    print(f" -> Lendo PDF: {filename}")
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        parts = []
        for i, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if text:
                parts.append(f"[Pagina {i}]\n{text}")

        native_text = "\n\n".join(parts)
        min_chars = len(doc) * 100

        if len(native_text.strip()) >= min_chars:
            DATA_TREATMENT_STATS["native_text_pages"] += len(doc)
            DATA_TREATMENT_STATS["processed_documents"] += 1
            return native_text
    except Exception as e:
        print(f"   -> Erro ao extrair texto nativo: {e}")
        native_text = ""

    print(f" -> PDF escaneado. Iniciando OCR via Textract...")
    return _ocr_pdf(config, file_bytes)


def _ocr_pdf(config: Config, file_bytes: bytes) -> str:
    """OCR em PDF escaneado via Amazon Textract."""
    import boto3

    region = config.aws_region
    client = boto3.client("textract", region_name=region)
    ocr_parts: list[str] = []

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        num_pages = len(doc)
        DATA_TREATMENT_STATS["ocr_pages"] += num_pages
        DATA_TREATMENT_STATS["textract_cost"] += num_pages * 0.0015
        DATA_TREATMENT_STATS["processed_documents"] += 1

        for i, page in enumerate(doc, start=1):
            print(f"   -> OCR na pagina {i}/{num_pages}...")
            try:
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                response = client.detect_document_text(Document={"Bytes": img_bytes})
                blocks = response.get("Blocks", [])
                lines = [
                    b["Text"] for b in blocks
                    if b.get("BlockType") == "LINE" and b.get("Text")
                ]
                page_text = "\n".join(lines)
                if page_text.strip():
                    ocr_parts.append(f"[Pagina {i} - OCR]\n{page_text.strip()}")
                else:
                    ocr_parts.append(f"[Pagina {i} - OCR vazia]")
            except Exception as exc:
                ocr_parts.append(f"[Pagina {i} - Erro OCR: {exc}]")
    except Exception as e:
        return f"[Erro ao abrir PDF para OCR: {e}]"

    return "\n\n".join(ocr_parts)


def extract_docx_text(file_bytes: bytes) -> str:
    """Extrai texto de arquivo DOCX via leitura XML nativa.

    Args:
        file_bytes: Conteudo binario do DOCX.

    Returns:
        Texto extraido.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            doc_xml = z.read("word/document.xml")
            root = ET.fromstring(doc_xml)
            parts: list[str] = []
            for child in root.iter():
                if child.tag.endswith("}p"):
                    parts.append("\n")
                elif child.tag.endswith("}t"):
                    if child.text:
                        parts.append(child.text)
            return "".join(parts).strip()
    except Exception as e:
        return f"[Erro ao extrair DOCX: {e}]"


def get_document_text(
    config: Config,
    filename: str,
    file_bytes: bytes,
) -> str:
    """Seleciona o extrator adequado baseado na extensao do arquivo.

    Args:
        config: Configuracao do sistema.
        filename: Nome do arquivo (determina o extrator).
        file_bytes: Conteudo binario do arquivo.

    Returns:
        Texto extraido do documento.
    """
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        return extract_pdf_text(config, filename, file_bytes)
    elif ext == ".docx":
        print(f" -> Lendo DOCX: {filename}")
        DATA_TREATMENT_STATS["processed_documents"] += 1
        return extract_docx_text(file_bytes)
    elif ext == ".json":
        print(f" -> Lendo JSON: {filename}")
        DATA_TREATMENT_STATS["processed_documents"] += 1
        try:
            data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            return file_bytes.decode("utf-8", errors="ignore")
    else:
        print(f" -> Lendo arquivo: {filename}")
        DATA_TREATMENT_STATS["processed_documents"] += 1
        return file_bytes.decode("utf-8", errors="ignore")


def save_markdown(md_dir: Path, filename: str, text: str) -> None:
    """Salva texto extraido como markdown.

    Args:
        md_dir: Diretorio de saida.
        filename: Nome original do arquivo.
        text: Texto extraido.
    """
    md_name = Path(filename).stem + "_extraido.md"
    md_path = md_dir / md_name
    md_path.write_text(text, encoding="utf-8")
    print(f"   -> Markdown salvo: {md_path}")
