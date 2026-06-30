# Contract: `generate_pdf()` — Interface Refatorada

## Assinatura

```python
def generate_pdf(etapas_dir: str | Path, output_path: str | Path) -> str: ...
```

**Parâmetros**:

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `etapas_dir` | `str \| Path` | Diretório contendo arquivos `.md` das etapas |
| `output_path` | `str \| Path` | Caminho de saída do PDF |

**Retorno**: `str` — caminho absoluto do PDF gerado.

**Exceções**: `FileNotFoundError`, `RuntimeError`

---

## Comportamento Detalhado

### Fluxo Principal

```
1. Ler todos os arquivos .md de etapas_dir em ordem alfabética
2. Se nenhum arquivo encontrado:
     elements = [Paragraph("Nenhum conteúdo disponível para o relatório.")]
3. Para cada linha de cada arquivo (em ordem):
   - Se bloco de código (```): acumular linhas, ao fechar criar Paragraph Courier 9pt
   - Se #: criar Paragraph Helvetica-Bold 16pt
   - Se ##: criar Paragraph Helvetica-Bold 14pt
   - Se ###: criar Paragraph Helvetica-Bold 12pt
   - Se |: criar Table com grid simples (0.5pt, #cccccc)
   - Se linha iniciada com "* " ou "- ": criar Paragraph Helvetica 11pt com leftIndent=15
   - Se linha vazia: criar Spacer(1, 6)
   - Senao: criar Paragraph Helvetica 11pt
4. Two-pass build:
   - Pass 1: contar páginas (arquivo temporário)
   - Pass 2: gerar PDF final com Página X de Y
5. Validar PDF (%PDF- + %%EOF)
6. Retornar caminho absoluto
```

### Formatação Visual

| Elemento | Fonte | Tamanho | Cor |
|----------|-------|---------|-----|
| Header (topo) | Helvetica-Bold | 9pt | Preto (#1f1f1f) |
| Footer (rodapé) | Helvetica | 8pt | Cinza (#5f6368) |
| Título H1 | Helvetica-Bold | 16pt | Preto |
| Título H2 | Helvetica-Bold | 14pt | Preto |
| Título H3 | Helvetica-Bold | 12pt | Preto |
| Corpo | Helvetica | 11pt | Preto |
| Código | Courier | 9pt | Preto |
| Tabela | Helvetica | 9pt | Preto |

### Margens

| Margem | Valor |
|--------|-------|
| Esquerda | 2cm (~56.7pt) |
| Direita | 2cm |
| Superior | 2cm (+ 1cm para cabeçalho) |
| Inferior | 2cm (+ 1cm para rodapé) |

### Cabeçalho e Rodapé

- **Cabeçalho**: "Radiante — Análise Jurídica" (Helvetica-Bold 9pt) com linha separadora
- **Rodapé**: "Página X de Y" (Helvetica 8pt) centralizado

---

## Tratamento de Erros

| Situação | Comportamento | Exceção |
|----------|--------------|---------|
| `etapas_dir` não existe | Retorna erro imediatamente | `FileNotFoundError` |
| Nenhum `.md` no diretório | Gera PDF com fallback | N/A |
| Erro no build do PDF | Remove arquivos parciais, relança | `Exception` |
| PDF gerado inválido | Remove arquivo, relança | `RuntimeError` |

---

## Estilos (5 no total)

```python
TITLE_STYLE = ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=16, leading=20,
                              textColor=colors.HexColor("#1f1f1f"), spaceAfter=12, spaceBefore=4)
H2_STYLE = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=14, leading=17,
                           textColor=colors.HexColor("#1f1f1f"), spaceAfter=8, spaceBefore=10)
H3_STYLE = ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=12, leading=15,
                           textColor=colors.HexColor("#1f1f1f"), spaceAfter=6, spaceBefore=6)
BODY_STYLE = ParagraphStyle("B", fontName="Helvetica", fontSize=11, leading=14,
                              textColor=colors.HexColor("#1f1f1f"), spaceAfter=4, spaceBefore=0)
CODE_STYLE = ParagraphStyle("CD", fontName="Courier", fontSize=9, leading=12,
                              textColor=colors.HexColor("#1f1f1f"), spaceAfter=4, spaceBefore=2,
                              leftIndent=10, rightIndent=10)
```
