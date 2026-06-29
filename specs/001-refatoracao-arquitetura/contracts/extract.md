# Contract: Document Extraction Module (backend/extract.py)

## Public Interface

```python
def extract_pdf_text(filename: str, file_bytes: bytes) -> str:
    """Extrai texto de PDF. Tenta PyMuPDF nativo, fallback Textract OCR."""
    ...

def extract_docx_text(file_bytes: bytes) -> str:
    """Extrai texto de DOCX via leitura XML."""
    ...

def get_document_text(filename: str, file_bytes: bytes) -> str:
    """Dispatcher: seleciona extrator baseado na extensao do arquivo."""
    ...
```

## Dependencies

- fitz (PyMuPDF)
- boto3 (Textract, para OCR)
- config.Config
