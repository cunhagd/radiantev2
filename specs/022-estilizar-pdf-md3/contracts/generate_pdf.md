# Contract: `generate_pdf()` — Interface com Estilo MD3

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

### Fluxo Principal com MD3

```
1. Ler todos os arquivos .md de etapas_dir em ordem alfabética
2. Tentar ler data/resultado_final.json para metadados da capa
3. Se JSON existe: gerar elementos da capa (Cover Page) com metadados do processo
4. Para cada linha de cada arquivo .md (em ordem):
   a. Parse markdown → Paragraph/Table/Spacer com estilos MD3
   b. Se bloco de código (```):
      - <= 20 linhas: Table wrapper com fundo C_SURFACE_VARIANT + borda C_OUTLINE
      - > 20 linhas: Paragraph Courier sem wrapper (evita "Flowable too large")
   c. Entre etapas consecutivas: inserir HRFlowable divider (C_OUTLINE, 0.5pt)
   d. No início de cada etapa: inserir accent bar (Table 4pt x 18pt, C_PRIMARY)
5. Two-pass build (deepcopy para evitar bug RL5.0.0):
   - Pass 1: contar páginas (BytesIO)
   - Pass 2: gerar PDF final with afterPage() header/footer MD3
6. Validar PDF (%PDF- + %%EOF)
7. Retornar caminho absoluto
```

### Página de Capa (Cover Page)

| Elemento | Fonte | Tamanho | Cor | Detalhe |
|----------|-------|---------|-----|---------|
| Título "Radiante" | Helvetica-Bold | 24pt | C_PRIMARY | Centralizado, com espaço vertical no topo |
| Subtítulo "Análise Jurídica" | Helvetica | 14pt | C_SECONDARY | Abaixo do título |
| Linha separadora | HRFlowable | 0.5pt | C_OUTLINE | width=60%, centralizado |
| Rótulos dos campos | Helvetica | 11pt | C_ON_SURFACE | "Processo:", "Autor:", etc. |
| Valores dos campos | Helvetica | 11pt | C_ON_SURFACE | Ao lado dos rótulos |
| Data de geração | Helvetica | 9pt | C_ON_SURFACE_VARIANT | No final da capa |

### Formatação MD3

| Elemento | Fonte | Tamanho | Cor Fundo | Cor Texto | Borda |
|----------|-------|---------|-----------|-----------|-------|
| Cabeçalho (header) | Helvetica-Bold | 9pt | — | C_PRIMARY | Linha C_OUTLINE 0.5pt |
| Rodapé (footer) | Helvetica | 8pt | — | C_ON_SURFACE_VARIANT | — |
| Título H1 | Helvetica-Bold | 16pt | — | C_PRIMARY | — |
| Título H2 | Helvetica-Bold | 14pt | — | C_SECONDARY | — |
| Título H3 | Helvetica-Bold | 12pt | — | C_TERTIARY | — |
| Corpo | Helvetica | 11pt | — | C_ON_SURFACE | — |
| Código (≤20 linhas) | Courier | 9pt | C_SURFACE_VARIANT | C_ON_SURFACE | C_OUTLINE 0.5pt |
| Código (>20 linhas) | Courier | 9pt | — | C_ON_SURFACE | — |
| Tabela - cabeçalho | Helvetica-Bold | 9pt | C_PRIMARY | C_ON_PRIMARY | — |
| Tabela - corpo (par) | Helvetica | 9pt | C_SURFACE | C_ON_SURFACE | Grid C_OUTLINE |
| Tabela - corpo (ímpar) | Helvetica | 9pt | C_SURFACE_VARIANT | C_ON_SURFACE | Grid C_OUTLINE |
| Accent bar (etapa) | — | — | C_PRIMARY | — | — |
| Divider (entre etapas) | — | 0.5pt | — | — | C_OUTLINE |

### Margens

| Margem | Valor |
|--------|-------|
| Esquerda | 2cm (~56.7pt) |
| Direita | 2cm |
| Superior | 2cm (+ 1cm para cabeçalho) |
| Inferior | 2cm (+ 1cm para rodapé) |

---

## Tratamento de Erros

| Situação | Comportamento | Exceção |
|----------|--------------|---------|
| `etapas_dir` não existe | Retorna erro imediatamente | `FileNotFoundError` |
| Nenhum `.md` no diretório | Gera PDF com fallback | N/A |
| `data/resultado_final.json` não existe | Gera PDF sem capa (graceful) | N/A |
| Bloco de código > 20 linhas | Paragraph simples (sem Table wrapper) | N/A |
| Erro no build do PDF | Remove arquivos parciais, relança | `Exception` |
| PDF gerado inválido | Remove arquivo, relança | `RuntimeError` |

---

## Estilos MD3 (8 no total)

```python
TITLE_STYLE = ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=16, leading=20,
                              textColor=C_PRIMARY, spaceAfter=12, spaceBefore=4)
H2_STYLE = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=14, leading=17,
                           textColor=C_SECONDARY, spaceAfter=8, spaceBefore=10)
H3_STYLE = ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=12, leading=15,
                           textColor=C_TERTIARY, spaceAfter=6, spaceBefore=6)
BODY_STYLE = ParagraphStyle("B", fontName="Helvetica", fontSize=11, leading=14,
                              textColor=C_ON_SURFACE, spaceAfter=4, spaceBefore=0)
CODE_STYLE = ParagraphStyle("CD", fontName="Courier", fontSize=9, leading=12,
                              textColor=C_ON_SURFACE, spaceAfter=4, spaceBefore=2,
                              leftIndent=10, rightIndent=10)
LIST_STYLE = ParagraphStyle("L", fontName="Helvetica", fontSize=11, leading=14,
                              textColor=C_ON_SURFACE, spaceAfter=4, spaceBefore=0,
                              leftIndent=15)
COVER_TITLE_STYLE = ParagraphStyle("CT", fontName="Helvetica-Bold", fontSize=24, leading=28,
                                    textColor=C_PRIMARY, spaceAfter=4, spaceBefore=0,
                                    alignment=TA_CENTER)
COVER_SUBTITLE_STYLE = ParagraphStyle("CS", fontName="Helvetica", fontSize=14, leading=17,
                                       textColor=C_SECONDARY, spaceAfter=4, spaceBefore=0,
                                       alignment=TA_CENTER)
```
