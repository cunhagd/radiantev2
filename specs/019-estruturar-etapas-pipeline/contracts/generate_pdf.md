# Contract: `generate_pdf()`

## Assinatura

```python
def generate_pdf(etapas_dir: str | Path, output_path: str | Path) -> str
```

## Parâmetros

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `etapas_dir` | `str \| Path` | Caminho para o diretório contendo arquivos .md das etapas |
| `output_path` | `str \| Path` | Caminho de saída para o PDF gerado |

## Retorno

`str` — Caminho absoluto do PDF gerado (via `Path.resolve()`).

## Comportamento

1. Lê todos os arquivos `.md` do diretório `etapas_dir`, ordenados alfabeticamente
2. Concatena o conteúdo de todos os arquivos em uma única string markdown
3. Processa o markdown usando o parser existente (blocos de etapa, tabelas, code blocks)
4. Executa two-pass build (contagem de páginas → PDF final com "Página X de Y")
5. Valida a estrutura do PDF gerado
6. Retorna o caminho absoluto do PDF

## Erros

- `FileNotFoundError`: Se `etapas_dir` não existir
- `RuntimeError`: Se falha na validação do PDF (`%PDF-` ausente, `%%EOF` ausente)
- `Exception`: Se falha no build do PDF (arquivo parcial é removido)

## Exemplo de Uso

```python
from backend.pdf_generator import generate_pdf
from pathlib import Path

pdf_path = generate_pdf(
    etapas_dir="data/etapas",
    output_path="data/relatorio_consolidado.pdf",
)
print(f"PDF gerado em: {pdf_path}")
```

## Notas

- A função espera arquivos no formato `etapa{N}.md` ou `etapa3_rodada{N}.md`
- O diretório deve conter APENAS os arquivos da análise atual (limpeza externa)
- A concatenação segue ordem alfabética (etapa1 < etapa2 < etapa3 < etapa3_rodada1 < ... < etapa4)
