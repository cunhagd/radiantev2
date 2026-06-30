# Contract: `_parse_inline(text) -> str`

## Assinatura

```python
def _parse_inline(text: str) -> str
```

## Descrição
Função pura que converte formatação markdown inline para XML compatível com ReportLab Paragraph. Não tem dependências externas além do módulo `re` da stdlib.

## Parâmetros

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `text` | `str` | Texto markdown contendo formatação inline (`**`, `*`, `` ` ``). Pode conter caracteres especiais (`<`, `>`, `&`). |

## Retorno

| Tipo | Descrição |
|------|-----------|
| `str` | Texto formatado com tags XML (`<b>`, `<i>`, `<font face="Courier">`). Caracteres `<`, `>`, `&` são escapados para `&lt;`, `&gt;`, `&amp;`. |

## Pré-condições

- `text` não é `None` (se `None`, a função deve retornar string vazia ou tratar como erro)
- `text` é string UTF-8 válida

## Pós-condições

- Todo `**texto**` no input é convertido para `<b>texto</b>` no output
- Todo `*texto*` no input (exceto `*` no início da linha ou parte de `**`) é convertido para `<i>texto</i>`
- Todo `` `texto` `` no input é convertido para `<font face="Courier">texto</font>`
- Caracteres `<`, `>`, `&` no input são escapados para `&lt;`, `&gt;`, `&amp;`
- Nenhuma outra alteração é feita no texto
- O resultado é seguro para uso como primeiro argumento de `Paragraph(xml, style)`

## Exemplos

| Input | Output |
|-------|--------|
| `**Info:**` | `<b>Info:</b>` |
| `*itálico*` | `<i>itálico</i>` |
| `` `código` `` | `<font face="Courier">código</font>` |
| `**A** e *B*` | `<b>A</b> e <i>B</i>` |
| `> **Info:** texto` | `> <b>Info:</b> texto` (aplicado antes do estilo BLOCKQUOTE) |
| `A & B <br/> C` | `A &amp; B &lt;br/&gt; C` |
| `***bold+italic***` | `<i><b>bold+italic</b></i>` |

## Ordem de Processamento

1. **Escape HTML**: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`
2. **Código inline**: `` `...` `` → `<font face="Courier">...</font>`
3. **Negrito**: `**...**` → `<b>...</b>`
4. **Itálico**: `*...*` → `<i>...</i>` (excluindo `*` que são parte de `**`)

## Erros

A função não deve lançar exceções para inputs válidos. Se o regex falhar em capturar corretamente (ex.: `**` não fechado), o texto permanece inalterado (segurança: não quebrar o PDF).
