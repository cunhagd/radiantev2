# Quickstart: Estruturar Etapas do Pipeline em Markdown

## Pré-requisitos

- Ambiente Python configurado (`.venv` ativado)
- Dependências instaladas: `pip install -r requirements.txt`
- Arquivo `.env` configurado (credenciais AWS, Bearer Token Bedrock)

## Cenários de Validação

### Cenário 1: Pipeline 1x gera arquivos .md

```powershell
# 1. Limpe qualquer execução anterior
Remove-Item -Path "data/etapas/*.md" -Force -ErrorAction SilentlyContinue

# 2. Execute a análise 1x (use um documento de teste)
python -c "
from backend.pipeline import run_once
from backend.config import Config
from pathlib import Path

config = Config()
combined_context = Path('data/markdown_docs/Documento_ab43f07_extraido.md').read_text(encoding='utf-8')
result = run_once(config, combined_context)
print('Status:', result.get('status'))
"
```

**Resultado esperado**: Os arquivos `data/etapas/etapa1.md`, `etapa2.md`, `etapa3.md` e `etapa4.md` foram criados com conteúdo markdown válido.

```powershell
# Verificar
Get-ChildItem -Path "data/etapas/*.md" | Select-Object Name, Length
```

---

### Cenário 2: Pipeline 10x gera arquivos .md com rodadas

```powershell
# Execute a análise 10x
python -c "
from backend.pipeline import run_ten_times
from backend.config import Config
from pathlib import Path

config = Config()
combined_context = Path('data/markdown_docs/Documento_ab43f07_extraido.md').read_text(encoding='utf-8')
result = run_ten_times(config, combined_context)
print('Status:', result.get('status'))
"
```

**Resultado esperado**: Os arquivos `etapa1.md`, `etapa2.md`, `etapa3_rodada1.md` ... `etapa3_rodada{N}.md` e `etapa4.md` foram criados.

```powershell
# Verificar (13 arquivos esperados: 4 etapas + 10 rodadas da etapa 3)
Get-ChildItem -Path "data/etapas/*.md" | Measure-Object | Select-Object Count
Get-ChildItem -Path "data/etapas/*.md" | Select-Object Name
```

---

### Cenário 3: `generate_pdf()` consome arquivos .md e gera PDF válido

```powershell
# Execute apenas a geração do PDF a partir dos arquivos existentes
python -c "
from backend.pdf_generator import generate_pdf
from pathlib import Path

pdf_path = generate_pdf(
    etapas_dir='data/etapas',
    output_path='data/relatorio_consolidado.pdf',
)
print(f'PDF gerado em: {pdf_path}')

# Verificar
pdf_bytes = Path(pdf_path).read_bytes()
print(f'Tamanho: {len(pdf_bytes)} bytes')
print(f'Inicia com %%PDF: {pdf_bytes.startswith(b\"%%PDF-\")}')
print(f'Termina com %%%%EOF: {pdf_bytes.strip().endswith(b\"%%%%EOF\")}')
"
```

**Resultado esperado**: PDF gerado com pelo menos 1 página, cabeçalho `%PDF-` presente e trailer `%%EOF` presente. O PDF abre corretamente em qualquer visualizador.

---

### Cenário 4: Limpeza automática entre análises

```powershell
# 1. Execute uma análise 1x
python -c "from backend.pipeline import run_once; from backend.config import Config; from pathlib import Path; run_once(Config(), Path('data/markdown_docs/Documento_ab43f07_extraido.md').read_text(encoding='utf-8'))"

# 2. Execute novamente (deve limpar e recriar)
python -c "from backend.pipeline import run_once; from backend.config import Config; from pathlib import Path; run_once(Config(), Path('data/markdown_docs/Documento_ab43f07_extraido.md').read_text(encoding='utf-8'))"

# 3. Verificar se há apenas 4 arquivos
$count = (Get-ChildItem -Path "data/etapas/*.md").Count
Write-Host "Arquivos em data/etapas/: $count (esperado: 4)"
```

**Resultado esperado**: `$count` é exatamente 4 (ou 13 no modo 10x), sem arquivos residuais de execuções anteriores.

---

### Cenário 5: Etapa vazia (edge case)

```python
# Teste unitário: salvar etapa com conteúdo vazio
from backend.pipeline import _save_etapa_md
from pathlib import Path

_save_etapa_md("etapa1", "", run_idx=None)
content = Path("data/etapas/etapa1.md").read_text(encoding="utf-8")
assert "Nenhum conteúdo disponível para esta etapa." in content
print("OK: Etapa vazia contém fallback")
```

---

### Cenário 6: `generate_pdf()` com diretório vazio

```python
# Teste unitário: PDF a partir de diretório com arquivos vazios
# (deve gerar PDF com fallback)
```

---

## Verificação Rápida

```powershell
# Verificar integridade de todos os cenários de uma vez
Write-Host "=== Verificacao Rapida ==="
Write-Host ""

# 1. Arquivos existem?
$files = Get-ChildItem -Path "data/etapas/*.md"
Write-Host "Arquivos em data/etapas/: $($files.Count)"

# 2. PDF gerado?
$pdf = Get-Item -Path "data/relatorio_consolidado.pdf" -ErrorAction SilentlyContinue
if ($pdf) {
    $bytes = $pdf.Length
    Write-Host "PDF: $($pdf.Name) ($bytes bytes)"
} else {
    Write-Host "PDF: Nao encontrado"
}

# 3. Gitignore?
$gitignore = Get-Content -Path ".gitignore" -Encoding utf8
$has_etapas = $gitignore -match "^data/etapas/"
Write-Host "Gitignore data/etapas/: $has_etapas"
```

## Contratos

Consulte [contracts/generate_pdf.md](contracts/generate_pdf.md) para a assinatura completa da função `generate_pdf()`.
