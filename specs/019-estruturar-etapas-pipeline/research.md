# Research: Estruturar Etapas do Pipeline em Markdown

## Visão Geral

Pesquisa sobre como implementar o salvamento de cada etapa do pipeline como arquivo markdown individual e refatorar o gerador de PDF para consumir esses arquivos.

---

## R1: Como salvar cada etapa como arquivo .md no pipeline?

### Decisão
Criar uma função helper `_save_etapa_md(stage_name: str, content: str, run_idx: int | None = None)` que escreve o arquivo em `data/etapas/etapa{N}.md`.

### Racional
- O pipeline já possui `save_stage_files()` para S3 — precisamos de equivalente local
- A função deve ser chamada imediatamente após cada etapa ser concluída (dentro de `run_single_pipeline()`)
- Para o modo 10x, as etapas 1, 2 e 4 são salvas normalmente; a etapa 3 gera `etapa3_rodada{N}.md`
- Usar `Path.write_text(encoding="utf-8")` — já é o padrão no projeto

### Alternativas Consideradas
- **Salvar tudo no final**: Mais simples, mas não oferece checkpoint por etapa em caso de falha. Rejeitado.
- **Banco de dados SQLite**: Overkill para arquivos de texto estruturado. Rejeitado.

---

## R2: Como garantir formatação markdown consistente?

### Decisão
Adicionar cabeçalho `# Etapa N — Nome` no início de cada arquivo .md, seguido do conteúdo bruto da IA. O markdown gerado pela IA já contém formatação (tabelas, listas, seções), então o conteúdo é salvo "as-is".

### Racional
- O `pdf_generator.py` já processa markdown com cabeçalhos H1, H2, H3, tabelas e code blocks
- A formatação existente da IA é adequada para o parser atual
- Etapas vazias recebem conteúdo fallback: "Nenhum conteúdo disponível para esta etapa."

### Formato do Arquivo

```markdown
# Etapa 1 — Extração de Metadados

[conteúdo bruto da IA]
```

### Alternativas Consideradas
- **Estruturar manualmente com seções fixas**: A IA já retorna markdown bem formatado; reestruturar manualmente adicionaria complexidade desnecessária e poderia perder informação.

---

## R3: Como refatorar `generate_pdf()` para consumir arquivos .md?

### Decisão
Modificar a assinatura de `generate_pdf()` para aceitar um diretório (`data/etapas/`) em vez de uma string de texto. A função lê todos os arquivos .md do diretório em ordem numérica (etapa1.md, etapa2.md, ...), concatena o conteúdo e processa o markdown combinado — reutilizando o mesmo parser existente.

```python
def generate_pdf(etapas_dir: str | Path, output_path: str | Path) -> str:
```

### Racional
- O parser markdown existente já funciona corretamente com o formato de saída da IA
- A concatenação preserva a estrutura de títulos (H1, H2) que o parser já reconhece
- Mínima mudança no código de parsing — apenas a origem do texto muda
- O diretório pode ser passado como parâmetro (FR-008)

### Alternativas Consideradas
- **Parser separado para cada arquivo**: Mais complexo e frágil. Rejeitado.
- **Manter assinatura atual e adicionar overload**: Desnecessário — a nova assinatura substitui a antiga.
- **Passar lista de paths**: Funcional, mas diretório é mais flexível e simples.

---

## R4: Limpeza do diretório `data/etapas/`

### Decisão
Criar função `clean_etapas_dir()` que remove todos os arquivos .md do diretório `data/etapas/` no início de cada análise (antes de executar as etapas).

### Racional
- Garante isolamento entre análises (SC-004)
- Evita mistura de resultados de análises diferentes
- Chamada no início de `run_once()` e `run_ten_times()`

### Alternativas Consideradas
- **Timestamps/IDs únicos para cada execução**: Mais complexo para o consumo pelo PDF generator. Rejeitado.

---

## R5: Comportamento para modo 10x (etapa3_rodada{N}.md)

### Decisão
No modo 10x, após a execução paralela da etapa 3, salvar cada rodada individual em `data/etapas/etapa3_rodada{N}.md`. Além disso, o `generate_pdf()` deve ler e incluir todos esses arquivos na ordem correta.

### Racional
- O spec (FR-005) exige explicitamente este formato
- O código atual em `run_ten_times()` já itera sobre as rodadas para salvar no S3 (linhas 599-607)
- Basta adicionar salvamento local equivalente em `data/etapas/`
- O PDF consolidado do modo 10x deve incluir todas as rodadas

### Alternativas Consideradas
- **Agregar todas as rodadas em um único `etapa3.md`**: Perde a granularidade individual. Rejeitado.
- **Manter apenas S3**: O spec exige arquivos locais para o PDF. Rejeitado.

---

## R6: Adicionar `data/etapas/` ao `.gitignore`

### Decisão
Adicionar a linha `data/etapas/` ao `.gitignore`.

### Racional
- O spec menciona explicitamente (Assumptions): "O diretório `data/etapas/` será incluído no `.gitignore` para não versionar resultados de análise."
- Segue o padrão existente (outros diretórios `data/` já estão no `.gitignore`)

---

## Resumo das Decisões

| # | Decisão | Arquivo | Impacto |
|---|---------|---------|---------|
| R1 | Função `_save_etapa_md()` para salvar .md local | `pipeline.py` | Adicionar ~20 linhas |
| R2 | Cabeçalho `# Etapa N` + conteúdo bruto | `pipeline.py` | Padrão de formatação |
| R3 | `generate_pdf(etapas_dir, output_path)` em vez de `generate_pdf(text, output_path)` | `pdf_generator.py` | Refatorar assinatura |
| R4 | `clean_etapas_dir()` no início de cada análise | `pipeline.py` | Adicionar ~15 linhas |
| R5 | `etapa3_rodada{N}.md` para modo 10x | `pipeline.py` | Adicionar ~10 linhas |
| R6 | `data/etapas/` no `.gitignore` | `.gitignore` | 1 linha |
