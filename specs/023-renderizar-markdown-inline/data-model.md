# Data Model: Renderizar Markdown Inline no PDF

## Entidades

### `ParserState`
Estado interno do parser de markdown inline (não persistido, apenas em memória).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `html_escaped` | `str` | Texto após escapamento de `&`, `<`, `>` |
| `code_converted` | `str` | Texto após conversão de `` `codigo` `` para `<font>` |
| `bold_converted` | `str` | Texto após conversão de `**negrito**` para `<b>` |
| `italic_converted` | `str` | Texto após conversão de `*italico*` para `<i>` |

### `InlineFormattedText`
Representa o resultado do parser: texto com tags XML prontas para ReportLab Paragraph.

| Propriedade | Tipo | Descrição |
|-------------|------|-----------|
| `xml_text` | `str` | Texto formatado com tags XML (`<b>`, `<i>`, `<font>`). Pode conter também `&lt;`, `&gt;`, `&amp;` para caracteres literais. |

### `Blockquote`
Linha de markdown que começa com `>`.

| Propriedade | Tipo | Descrição |
|-------------|------|-----------|
| `raw_text` | `str` | Texto original incluindo o prefixo `> ` |
| `content` | `str` | Conteúdo após remoção do prefixo `> ` |
| `formatted_content` | `str` | Conteúdo após passar por `_parse_inline()` |
| `style` | `ParagraphStyle` | Estilo `BLOCKQUOTE_STYLE` (leftIndent=20, cor on-surface-variant, fontSize=10) |

## Fluxo de Transformação de Dados

```
Linha .md (raw)
    │
    ▼
Parser identifica tipo:
    ├── Blockquote (> ...)?
    │       │
    │       ▼
    │   Remove prefixo "> "
    │       │
    │       ▼
    │   Aplica _parse_inline() no conteúdo
    │       │
    │       ▼
    │   Paragraph(_parse_inline(content), BLOCKQUOTE_STYLE)
    │
    ├── Parágrafo comum?
    │       │
    │       ▼
    │   Aplica _parse_inline() na linha
    │       │
    │       ▼
    │   Paragraph(_parse_inline(linha), BODY_STYLE)
    │
    ├── Lista (* ou -)?
    │       │
    │       ▼
    │   Extrai texto do item
    │       │
    │       ▼
    │   Aplica _parse_inline() no texto
    │       │
    │       ▼
    │   Paragraph(_parse_inline(texto), LIST_STYLE)
    │
    └── Heading (H1-H3)?
            │
            ▼
        Aplica _parse_inline() no título
            │
            ▼
        Paragraph(_parse_inline(título), TITLE|H2|H3_STYLE)
```

## Ordem de Aplicação (_parse_inline)

```
_parse_inline(raw_text: str) → str:

1. Escape HTML:
   "&"  → "&amp;"
   "<"  → "&lt;"
   ">"  → "&gt;"

2. Código inline:
   `texto`  →  <font face="Courier">texto</font>

3. Negrito:
   **texto**  →  <b>texto</b>

4. Itálico:
   *texto*  →  <i>texto</i>

   Regra: Não capturar * que faz parte de **.
   Regra: Não capturar * no início da linha (já tratado como lista).
```

## Relacionamentos

| Entidade | Relaciona-se com | Descrição |
|----------|-----------------|-----------|
| `_parse_inline()` | `InlineFormattedText` | Produz texto formatado |
| `InlineFormattedText` | `Paragraph` | É passado como primeiro argumento do Paragraph |
| `Blockquote` | `_parse_inline()` | O conteúdo do blockquote é processado por `_parse_inline()` |
| `BLOCKQUOTE_STYLE` | `Paragraph` | Usado como estilo do Paragraph para blockquotes |
