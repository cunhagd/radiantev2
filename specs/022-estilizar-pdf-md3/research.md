# Research: Estilizar PDF com Material Design 3

## Visão Geral

Pesquisa sobre como aplicar o sistema de design Material Design 3 ao PDF gerado pelo ReportLab, incluindo paleta de cores, blocos alternados, tabelas estilizadas, blocos de código com borda, página de capa, e títulos coloridos por nível.

---

## R1: Paleta de Cores MD3 no ReportLab

### Decisão
Usar `colors.HexColor()` do ReportLab para definir todas as cores MD3 como constantes no topo do módulo:

```python
# MD3 Color Palette
C_PRIMARY = colors.HexColor("#6750A4")
C_SECONDARY = colors.HexColor("#625B71")
C_TERTIARY = colors.HexColor("#7D5260")
C_SURFACE = colors.HexColor("#FFFBFE")
C_SURFACE_VARIANT = colors.HexColor("#E7E0EC")
C_OUTLINE = colors.HexColor("#79747E")
C_ERROR = colors.HexColor("#B3261E")
C_BACKGROUND = colors.HexColor("#FFFBFE")
C_ON_PRIMARY = colors.HexColor("#FFFFFF")
C_ON_SURFACE = colors.HexColor("#1C1B1F")
C_ON_SURFACE_VARIANT = colors.HexColor("#49454F")
```

### Racional
- MD3 define 12 cores base — usar todas garante consistência visual
- As cores `C_ON_*` garantem contraste adequado (WCAG AA)
- O ReportLab aceita `colors.HexColor()` nativamente em ParagraphStyle e TableStyle

### Alternativas Consideradas
- **Cores fixas sem tema**: Mais simples, mas sem consistência MD3. Rejeitado.

---

## R2: Blocos de Etapa com Distinção Visual (FR-003)

### Contexto — Limitação Crítica do ReportLab
O ReportLab **não quebra conteúdo dentro de Tables entre páginas automaticamente**. Qualquer conteúdo dentro de uma célula de Table que exceda uma página causa "Flowable too large" ou é simplesmente truncado. Portanto, usar Table wrapper para blocos inteiros de etapa (como foi feito na feature 017) **causa o mesmo bug que a feature 021 corrigiu**.

### Decisão
Em vez de fundo colorido em bloco inteiro, usar **accent bar** (barra vertical fina) + **divider horizontal** como marcadores visuais entre etapas, mantendo o conteúdo fluido sem wrapper:

1. **Entre cada etapa**: Inserir um `HRFlowable` (horizontal rule) com 0.5pt na cor `C_OUTLINE` para separar visualmente as etapas
2. **No início de cada etapa**: Inserir uma Table pequena (4pt x 18pt) agindo como "accent bar" — uma marca colorida que identifica o início da etapa
3. **O conteúdo da etapa** (Paragraphs, Tables, Spacers) flui naturalmente sem wrapper

Estrutura:
```python
for etapa_idx, etapa_flowables in enumerate(etapa_blocks):
    # Divisor entre etapas (exceto antes da primeira)
    if etapa_idx > 0:
        elements.append(HRFlowable(width="100%", thickness=0.5, color=C_OUTLINE,
                                    spaceAfter=8, spaceBefore=8))
    
    # Accent bar: Table pequena no inicio da etapa
    accent = Table([[""]], colWidths=[4], rowHeights=[18])
    accent.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(accent)
    
    # Conteudo da etapa flui naturalmente (sem wrapper)
    elements.extend(etapa_flowables)
    elements.append(Spacer(1, 6))
```

### Racional
- Nenhum wrapper Table — cada Paragraph/Table/Spacer quebra página naturalmente
- Accent bar e divider horizontal dão distinção visual entre etapas
- Estilo MD3: MD3 usa dividers e elevation (não blocos pintados) para separar conteúdo

### Alternativas Consideradas
- **Table wrapper com fundo**: CAUSA "Flowable too large". Rejeitado com base no bug conhecido.
- **KeepTogether**: Não aceita cor de fundo nem quebra páginas. Rejeitado.

---

## R3: Border-radius (FR-002) — Limitação do ReportLab

### Decisão
O ReportLab **não suporta border-radius nativamente**. Não há `borderRadius` em TableStyle ou ParagraphStyle.

Solução de compromisso:
- **Blocos de etapa**: Não usar border-radius. Usar divider + accent bar (R2) como substituto visual
- **Blocos de código**: Usar borda simples (`BOX`, 0.5pt, outline) sem arredondamento, com padding generoso

### Racional
- ReportLab não oferece border-radius em nenhum componente
- Dividers e accent bars são elementos válidos do MD3
- Código sem border-radius mas com padding + borda fica visualmente aceitável

### Alternativas Consideradas
- **roundRect no afterPage**: Conteúdo dinâmico impossibilita saber posição exata dos blocos. Rejeitado.

---

## R4: Divisor Visual entre Etapas — HRFlowable

### Decisão
Usar `HRFlowable` do ReportLab para criar divisores horizontais entre etapas:

```python
from reportlab.platypus import HRFlowable

divider = HRFlowable(
    width="100%",
    thickness=0.5,
    color=C_OUTLINE,
    spaceBefore=6,
    spaceAfter=6,
)
```

### Racional
- `HRFlowable` é um flowable nativo do ReportLab que funciona como <hr> em HTML
- Não afeta a quebra de páginas
- Pode ser estilizado com cor, espessura e espaçamento
- Padrão MD3: Dividers são componentes oficiais do MD3 para separar conteúdo

### Alternativas Consideradas
- **Tabela linha horizontal**: Mais complexo e sem vantagens. Rejeitado.

---

## R5: Tabelas MD3 (FR-006)

### Decisão
Tabelas com:
- **Cabeçalho**: Fundo `C_PRIMARY` (`#6750A4`), texto `C_ON_PRIMARY` (`#FFFFFF`), Helvetica-Bold 9pt
- **Corpo**: Linhas alternando entre `C_SURFACE` e `C_SURFACE_VARIANT`
- **Grid**: `INNERGRID` 0.5pt na cor `C_OUTLINE` (`#79747E`)
- **Primeira linha** detectada como cabeçalho, recebe `BACKGROUND` e `FONTNAME` (`Helvetica-Bold`)
- **Padding**: 4pt em todas as células

```python
t = Table(cells, colWidths=col_widths)
style_cmds = [
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
# Alternar fundo das linhas do corpo
for i in range(1, len(cells)):
    bg = C_SURFACE if i % 2 == 0 else C_SURFACE_VARIANT
    style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
t.setStyle(TableStyle(style_cmds))
```

### Racional
- Cabeçalho com fundo primary é padrão MD3 para tabelas
- Alternância de linhas melhora legibilidade
- `INNERGRID` em vez de `GRID` evita borda dupla no perímetro

### Alternativas Consideradas
- **Tabelas sem grid**: Menos legível. Rejeitado.
- **Apenas header colorido sem alternância**: Menos profissional. Rejeitado.

---

## R6: Blocos de Código com Fundo e Borda (FR-007)

### Decisão
Blocos de código serão encapsulados em uma `Table` de 1 célula com fundo `C_SURFACE_VARIANT` e borda `C_OUTLINE`:

```python
code_table = Table([[Paragraph(code_text, CODE_STYLE)]],
                   colWidths=[PAGE_W - 20])
code_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), C_SURFACE_VARIANT),
    ("BOX", (0, 0), (-1, -1), 0.5, C_OUTLINE),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
```

### Racional
- Table com fundo e borda é a única forma nativa de criar um "card" para código
- Padding generoso (10pt) melhora a legibilidade
- A Table não quebra páginas, mas códigos longos (como JSON de etapa4) podem ser problemáticos — manter Paragraph simples sem Table para códigos > 20 linhas

### Alternativas Consideradas
- **Preformatted**: Não aceita background ou border. Rejeitado.
- **Apenas Paragraph com Courier**: Sem distinção visual. Rejeitado para códigos curtos.

---

## R7: Página de Capa (US2 / FR-011)

### Decisão
A capa será gerada como um conjunto separado de elementos inseridos no início da lista `elements`, antes do conteúdo das etapas. A capa ocupará uma página inteira (frame cheio).

Estrutura da capa:
```python
cover_elements = []
cover_elements.append(Spacer(1, A4[1] / 4))  # espaco vertical no topo
cover_elements.append(Paragraph("Radiante", TITLE_STYLE))  # grande
cover_elements.append(Spacer(1, 12))
cover_elements.append(Paragraph("An\u00e1lise Jur\u00eddica", SUBTITLE_STYLE))  # subtitulo
cover_elements.append(Spacer(1, 24))

# Linha separadora
# ...

# Dados do processo
for label, value in [
    ("Processo", metadata.get("numero_processo", "N/A")),
    ("Autor", metadata.get("autor", "N/A")),
    ("Reclamada", metadata.get("reclamada", "N/A")),
    ("Valor Total Estimado", f'R$ {metadata.get("valor_total_estimado", "0,00")}'),
    ("Data de Gera\u00e7\u00e3o", datetime.now().strftime("%d/%m/%Y")),
]:
    cover_elements.append(Paragraph(f"<b>{label}:</b> {value}", BODY_STYLE))
```

Os metadados são lidos de `data/resultado_final.json`. Se o arquivo não existir, a capa não é gerada sem erro (graceful fallback).

### Racional
- Capa como página separada é o padrão profissional
- Dados centralizados na página com espaçamento generoso
- `graceful fallback` se JSON não existir — evita quebrar o pipeline

### Alternativas Consideradas
- **Capa gerada via afterPage**: Complexo e difícil de centralizar conteúdo. Rejeitado.

---

## R8: Cabeçalho e Rodapé com Cores MD3 (FR-004, FR-005)

### Decisão
Manter a abordagem `afterPage()` (já testada e funcional) e atualizar as cores:
- Cabeçalho: "Radiante — Análise Jurídica" em `C_PRIMARY` (antes preto)
- Linha separadora: `C_OUTLINE` (já estamos usando)
- Rodapé: "Página X de Y" em `C_ON_SURFACE_VARIANT` (antes cinza genérico)

### Racional
- `afterPage()` funciona e não tem o bug de 931 bytes
- Mudança apenas de cores — sem alteração estrutural
- Cores MD3 nos metadados de página reforçam a identidade visual

### Alternativas Consideradas
- **PageTemplate com onPage**: Bug no RL5.0.0 — corrompe o PDF. Já testado e rejeitado.

---

## R9: Títulos Coloridos por Nível (FR-009)

### Decisão
Usar 3 ParagraphStyle distintos com cores MD3:

| Estilo | Cor | Fonte | Tam. | Uso |
|--------|-----|-------|------|-----|
| `TITLE_STYLE` | `C_PRIMARY` (#6750A4) | Helvetica-Bold | 16pt | H1 |
| `H2_STYLE` | `C_SECONDARY` (#625B71) | Helvetica-Bold | 14pt | H2 |
| `H3_STYLE` | `C_TERTIARY` (#7D5260) | Helvetica-Bold | 12pt | H3 |

### Racional
- MD3 usa primary/secondary/tertiary para hierarquia visual
- A cor do título indica seu nível sem necessidade de numeração
- Todas as cores têm contraste adequado com fundo surface (#FFFBFE)

### Alternativas Consideradas
- **Todos os títulos em primary**: Menos hierarquia visual. Rejeitado.

---

## R10: Listas MD3 (FR-008)

### Decisão
Manter `LIST_STYLE` com `leftIndent=15` e substituir o marcador visual:

```python
LIST_STYLE = ParagraphStyle(
    "L", fontName="Helvetica", fontSize=11, leading=14,
    textColor=C_ON_SURFACE, spaceAfter=4, spaceBefore=0,
    leftIndent=15, bulletIndent=0,  # alinhar bullet à esquerda
)

# No parser, quando encontra * ou -, cria:
elements.append(Paragraph(
    f"\u2022 {content}", LIST_STYLE  # bullet unicode •
))
```

### Racional
- O bullet Unicode `•` (U+2022) é suportado pela fonte Helvetica
- `leftIndent=15` com `bulletIndent=0` alinha o texto corretamente
- Simples e funcional

### Alternativas Consideradas
- **Mantendo o texto literal "* "**: Menos profissional. Rejeitado.

---

## Resumo das Decisões

| # | Decisão | Abordagem |
|---|---------|-----------|
| R1 | Paleta MD3 | 12 constantes HexColor |
| R2 | Blocos alternados | Accent bar + HRFlowable divider (sem Table wrapper) |
| R3 | Border-radius | Não suportado — accent bar como substituto |
| R4 | Divisor de etapa | HRFlowable com cor outline |
| R5 | Tabelas MD3 | Header primary + alternância surface |
| R6 | Código com borda | Table wrapper com fundo e borda (apenas para códigos ≤ 20 linhas; >20 linhas usar Paragraph simples) |
| R7 | Capa | Elementos separados no início, metadados de resultado_final.json |
| R8 | Cabeçalho/rodapé MD3 | afterPage() com cores MD3 |
| R9 | Títulos coloridos | Primary → Secondary → Tertiary |
| R10 | Listas | Bullet Unicode • com leftIndent=15 |
