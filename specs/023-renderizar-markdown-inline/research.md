# Research: Renderizar Markdown Inline no PDF

## Tags XML do ReportLab Paragraph

### Decisão
ReportLab Paragraph aceita tags XML básicas: `<b>`, `<i>`, `<u>`, `<font>`, `<br/>`, `<super>`, `<sub>`, `<img>`, e sequências de escape como `&lt;`, `&gt;`, `&amp;`.

### Validações Realizadas
| Tag | Teste | Resultado |
|-----|-------|-----------|
| `<b>texto</b>` | Paragraph com bold | ✅ OK |
| `<i>texto</i>` | Paragraph com italic | ✅ OK |
| `<font face="Courier">código</font>` | Fonte monoespaçada | ✅ OK |
| `<font color="#49454F">texto</font>` | Cor personalizada | ✅ OK |
| Tags combinadas | `<b>Bold</b> + <i>Italic</i> + `<font>` | ✅ OK |
| `<br/>` | Quebra de linha | ✅ OK |
| `&lt;` `&gt;` | Escape de caracteres especiais | ✅ OK |

### Implicação
A função `_parse_inline()` deve converter markdown inline para estas tags XML.

---

## Padrões Reais Encontrados nas Etapas

Após análise dos 4 arquivos em `data/etapas/`, os seguintes padrões markdown foram identificados:

| Padrão | Ocorrências | Exemplo real |
|--------|------------|--------------|
| `**negrito**` | ~40+ | `**Info:**`, `**Provável**`, `**Valor Total (Etapa 2):**` |
| `*itálico*` | ~15+ | `*Provas Reclamante (+40%):*`, `*Parâmetros Extraídos:*` |
| `> blockquote` | ~30+ | `> 💡 **Info:** Score fixado em 65%...` |
| `**negrito** dentro de `> blockquote | ~25+ | `> 💡 **Info:** texto` |
| `**### ` (bold + hash, não é heading) | ~5 | `**### 📌 Cifra: Indenização por Dano Material` |
| `---` (separador horizontal) | ~5 | Já tratado como Spacer existente |
| `\| tabela \|` | 1 | Tabela na etapa1 — já tratado |

### Decisões de Parsing

#### Negrito (`**texto**`)
- **Padrão**: `\*\*(.+?)\*\*` (non-greedy para evitar capturar múltiplos spans)
- **Substituição**: `<b>\1</b>`
- **Edge case**: `** texto**` (espaço após a abertura) — deve ser tratado como texto normal sem bold
- **Edge case**: `**texto **` (espaço antes do fechamento) — idem

#### Itálico (`*texto*`)
- **Padrão**: `(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)` — garantir que não capture `**`
- **Não aplicar quando**: linha começa com `* ` (já é lista)
- **Substituição**: `<i>\1</i>`

#### Código Inline (`` `codigo` ``)
- **Padrão**: `` `(.+?)` ``
- **Substituição**: `<font face="Courier">\1</font>`
- **Observação**: Não encontrado nas etapas atuais, mas implementado para completude

#### Blockquote (`> `)
- **Tratamento**: Linhas começando com `>` devem ser renderizadas com estilo `BLOCKQUOTE_STYLE` separado
- **Estilo**: leftIndent=20, rightIndent=10, textColor=C_ON_SURFACE_VARIANT, fontSize=10, leading=13
- **Formatação inline dentro do blockquote**: O texto após `> ` deve passar pelo `_parse_inline()` normalmente
- **Decoração visual**: Como ReportLab não suporta borda lateral via ParagraphStyle, usar leftIndent maior e cor diferenciada como substituto visual

#### Ordem de Aplicação
1. Primeiro: Extrair blockquote (`> `) e aplicar estilo especial
2. Segundo: Aplicar `` `código` `` → `<font face="Courier">`
3. Terceiro: Aplicar `**negrito**` → `<b>`
4. Quarto: Aplicar `*itálico*` → `<i>`

---

## Escapamento de XML

### Decisão
Como o texto das etapas pode conter caracteres especiais do XML (`<`, `>`, `&`), a função DEVE escapar estes caracteres ANTES de aplicar as substituições de markdown.

### Regras
1. Escapar `&` → `&amp;` (DEVE ser primeiro para evitar duplo escape)
2. Escapar `<` → `&lt;`
3. Escapar `>` → `&gt;`
4. Aplicar substituições markdown inline

### Exemplo
- Input: `**Danos <R$ 50.000>** & *perdas*`
- Após escape: `**Danos &lt;R$ 50.000&gt;** &amp; *perdas*`
- Após markdown: `<b>Danos &lt;R$ 50.000&gt;</b> &amp; <i>perdas</i>`

---

## Integração com Código Existente

### Estrutura de Integração
A função `_parse_inline(text: str) -> str` será uma função pura no topo do arquivo `pdf_generator.py`.

### Pontos de Injeção no Parser Existente
Atualmente, cada linha é processada por tipo (H1, H2, H3, lista, tabela, código) e o texto é passado diretamente para `Paragraph(text, STYLE)`. A formatação inline deve ser aplicada em:

1. **Parágrafos comuns**: `Paragraph(s, BODY_STYLE)` → `Paragraph(_parse_inline(s), BODY_STYLE)`
2. **Listas**: `Paragraph(m.group(1), LIST_STYLE)` → `Paragraph(_parse_inline(m.group(1)), LIST_STYLE)`
3. **Blockquote**: Novo tratamento → `Paragraph(_parse_inline(conteudo), BLOCKQUOTE_STYLE)`
4. **Títulos**: `Paragraph(m.group(1), TITLE_STYLE)` — títulos podem conter negrito/itálico? Verificar... Sim, etapa3 tem `### ⚖️ Cifra:` que é H3. Não contém `**` mas pode conter no futuro. Aplicar `_parse_inline` também nos títulos.

### O que NÃO mudar
- Blocos de código (``` ... ```): Já tratados, não passam pelo parser inline
- Células de tabela: São linhas separadas por `|`, já tratadas como Table
- HR separadores (`---`): Já ignorados

### Estilo BLOCKQUOTE_STYLE
```python
BLOCKQUOTE_STYLE = ParagraphStyle(
    "BQ", fontName="Helvetica", fontSize=10, leading=13,
    textColor=C_ON_SURFACE_VARIANT, spaceAfter=4, spaceBefore=2,
    leftIndent=20, rightIndent=10,
)
```

---

## Alternativas Consideradas

| Alternativa | Racional | Rejeitada porque |
|-------------|----------|------------------|
| Biblioteca externa (mistune, markdown-it) | Parse markdown completo | Adicionaria dependência violando Constitution; só precisamos de 4 padrões inline |
| ReportLab `Paragraph` com `xml` directamente | Já suportado | Precisa de conversão markdown→XML primeiro |
| Substituir `**` manualmente sem regex | Simples demais | Não trataria casos aninhados ou escaped |

---

## Risco: Conflito de Asteriscos

### Problema
O caractere `*` tem múltiplos significados no markdown:
- `**texto**` = negrito
- `*texto*` = itálico
- `* ` no início da linha = lista (já tratado antes do parser inline)
- `***texto***` = negrito + itálico (não presente nas etapas atuais)

### Solução
1. Listas são detectadas antes (regex `^[\*\-] +(.+)$`), então `* ` inicial não chega ao parser inline
2. Para itálico, usar lookbehind/lookahead para garantir que `*` não seja parte de `**`
3. Aplicar negrito (`**`) ANTES de itálico (`*`) para evitar conflitos
4. `***texto***` → primeiro `**texto**` vira `<b>texto</b>`, depois o `*` externo vira `<i>` → `<i><b>texto</b></i>`

### Ordem Final de Substituições
1. Escapar HTML: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`
2. Código inline: `` `...` `` → `<font face="Courier">...</font>`
3. Negrito: `**...**` → `<b>...</b>`
4. Itálico: `*...*` → `<i>...</i>`
