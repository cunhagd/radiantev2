# Contract: PDF Generator Module (backend/pdf_generator.py)

## Public Interface

```python
def generate_pdf(text: str, output_path: str) -> str:
    """Gera PDF a partir de texto markdown usando ReportLab."""
    ...
```

## Dependencies

- reportlab
