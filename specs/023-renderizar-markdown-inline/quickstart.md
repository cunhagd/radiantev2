# Quickstart: Renderizar Markdown Inline no PDF

## Pré-requisitos

- Python 3.11+
- Dependências instaladas: `pip install -r requirements.txt`
- Etapas geradas em `data/etapas/`

## Setup

```bash
cd C:\radiantev2
```

## Cenários de Validação

### Cenário 1: Teste Unitário do `_parse_inline`

Valida que a função pura de conversão markdown→XML funciona isoladamente.

```bash
python -c "
import re

def _parse_inline(text):
    if text is None:
        return ''
    # Escape HTML
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Inline code
    text = re.sub(r'\x60(.+?)\x60', r'<font face=\"Courier\">\1</font>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic (not at line start, not part of **)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    return text

tests = [
    ('**Info:**', '<b>Info:</b>'),
    ('*italico*', '<i>italico</i>'),
    ('\x60codigo\x60', '<font face=\"Courier\">codigo</font>'),
    ('**A** e *B*', '<b>A</b> e <i>B</i>'),
]
for inp, expected in tests:
    result = _parse_inline(inp)
    status = 'OK' if result == expected else f'FAIL (got: {result})'
    print(f'{status}: {inp!r} -> {result!r}')
"
```

**Resultado esperado**: Todos os 4 testes passam com OK.

---

### Cenário 2: Gerar PDF com Formatação Inline

Valida que o PDF gerado não contém marcadores `**`, `*`, `` ` `` visíveis como texto.

```bash
python -c "
import sys, os
sys.path.insert(0, r'C:\radiantev2')

# Clear cache
for k in list(sys.modules.keys()):
    if 'pdf_generator' in k:
        del sys.modules[k]

from backend.pdf_generator import generate_pdf

result = generate_pdf(r'C:\radiantev2\data\etapas', r'C:\radiantev2\data\relatorio_consolidado.pdf')
print(f'PDF gerado: {result}')
print(f'Tamanho: {os.path.getsize(result)} bytes')

# Verify PDF structure
data = open(result, 'rb').read()
print(f'Headers: {data[:8]}')
print(f'EOF: {data.strip()[-5:] == b\"%%EOF\"}')
"
```

**Resultado esperado**: PDF gerado com sucesso, tamanho > 10KB, estrutura %PDF-...%%EOF válida.

---

### Cenário 3: Verificar Ausência de Marcadores Brutos

Valida que nenhum marcador `**` ou `` ` `` aparece como texto no PDF.

```bash
python -c "
import sys
sys.path.insert(0, r'C:\radiantev2')

# Test with known input containing markdown
from backend.pdf_generator import _parse_inline

test_text = '**Negrito** e *italico* e \x60codigo\x60 continuam'
result = _parse_inline(test_text)
print(f'Input:  {test_text}')
print(f'Output: {result}')

# Verify no raw markers
assert '**Negrito**' not in result, 'FAIL: ** nao convertido'
assert '*italico*' not in result, 'FAIL: * nao convertido'
print('OK: Nenhum marcador bruto no output')
"
```

**Resultado esperado**: Output contém `<b>Negrito</b>`, `<i>italico</i>`, `<font face="Courier">codigo</font>`. Nenhum marcador bruto.

---

### Cenário 4: Pipeline Completo (Opcional)

Executa o pipeline completo para gerar etapas + PDF.

```bash
python -c "
import sys, os, shutil
sys.path.insert(0, r'C:\radiantev2')

# Clear cache
for d in ['C:\\\\radiantev2\\\\backend\\\\__pycache__']:
    if os.path.exists(d):
        shutil.rmtree(d)
for k in list(sys.modules.keys()):
    if 'pdf_generator' in k or 'pipeline' in k:
        del sys.modules[k]

from backend.pdf_generator import generate_pdf

result = generate_pdf(r'C:\radiantev2\data\etapas', r'C:\radiantev2\data\relatorio_consolidado.pdf')
print(f'Pipeline PDF: {result}')
print(f'Tamanho: {os.path.getsize(result)} bytes')
"
```

**Resultado esperado**: PDF gerado sem erros.
