# Data Model: Corrigir Abertura do PDF Consolidado

## Entities

### PDF Consolidado

Documento gerado via ReportLab com a analise juridica completa.

| Campo | Tipo | Descricao | Validacao |
|-------|------|-----------|-----------|
| `output_path` | `str | Path` | Caminho de saida do PDF | Deve existir apos geracao |
| `pages` | `int` | Numero de paginas no documento final | `>= 1` |
| `content` | `str` | Texto markdown de entrada | Nao vazio |
| `elements` | `list[Flowable]` | Elementos platypus do ReportLab | Pode conter Paragraphs, Tables, Spacers |

## Validation Rules

1. **Pos-build**: Apos `doc.build()`, verificar:
   - Arquivo existe no disco
   - Tamanho > 0 bytes
   - `%%EOF` presente no final
   - Conteudo nao esta vazio (pode ser verificado pelo cabecalho `%PDF-`)

2. **Pos-geracao**: Se `elements` estiver vazio, adicionar Paragraph padrao para garantir >= 1 pagina.

3. **Tratamento de erro**: Se `doc.build()` lancar excecao, remover o PDF parcial e relancar o erro.
