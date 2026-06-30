# Research: Refatorar PDF para estilo simples

## Visão Geral

Pesquisa sobre como refatorar `backend/pdf_generator.py` para remover toda a estilização complexa (Material Design 3) e criar um PDF simples, funcional e robusto.

---

## R1: O que remover do código atual?

### Decisão
Remover completamente os seguintes componentes do `pdf_generator.py` atual:

**Removidos**:
- Paleta de cores MD3 (C_PRIMARY, C_SURFACE_1, C_SURFACE_2, C_OUTLINE, C_TEXT, C_TEXT_MUTED, C_SUCCESS_BG, C_SUCCESS, C_TABLE_HEADER, C_CODE_BG) — ~10 constantes
- `_make_callout()` — função de callout verde (tabela aninhada que não quebra páginas)
- `_make_etapa_block()` — blocos com fundo colorido que clonam estilos de Paragraph
- `CALLOUT_STYLE` — estilo específico para callout
- `RE_ETAPA` + lógica de `in_etapa` / `etapa_body` / `flush_etapa()` — blocos de etapa com fundo alternado (~40 linhas)
- Lógica de detecção de linha de total para callout (dentro do parser de tabelas)
- Constante `PAGE_W` — será substituída por cálculo direto nas margens

**Mantidos**:
- Two-pass build (Página X de Y) 
- `_make_page_callback()` — cabeçalho "Radiante — Análise Jurídica" + rodapé numerado
- `_validate_pdf()` — validação pós-build (%PDF-, %%EOF)
- Tratamento de erro com try/except + limpeza de arquivos parciais
- Parsing de markdown (cabeçalhos H1/H2/H3, tabelas, blocos de código, texto comum)

### Racional
- O `_make_etapa_block()` criava Tables aninhadas que o ReportLab não consegue quebrar entre páginas, causando "Flowable too large"
- O `_make_callout()` usava Table com largura fixa que também não quebrava
- As cores e fundos eram puramente estéticos e não afetam a funcionalidade
- Simplificar o parser: sem estado `in_etapa`, sem acumular body, cada linha vira um elemento diretamente

### Alternativas Consideradas
- **Manter blocos de etapa com cor**: Rejeitado — causa "Flowable too large" e adiciona complexidade desnecessária.

---

## R2: Como estruturar o parser simplificado?

### Decisão
Parser linear e direto: cada linha do markdown é processada individualmente e convertida em um elemento ReportLab (Paragraph, Table, Spacer) sem estado acumulador de blocos.

Fluxo:
```
para cada linha:
  se bloco de código aberto:
    acumular linha em code_lines
  se fechamento de código:
    criar Paragraph com Courier -> adicionar a elements
  se linha vazia:
    adicionar Spacer
  se # H1:
    criar Paragraph com Helvetica-Bold 16pt
  se ## H2:
    criar Paragraph com Helvetica-Bold 14pt
  se ### H3:
    criar Paragraph com Helvetica-Bold 12pt
  se linha de tabela (|):
    criar Table com linhas simples
  senao (texto comum):
    criar Paragraph com Helvetica 11pt
```

### Racional
- Sem estado `in_etapa` — cada elemento é independente e quebra páginas naturalmente
- Sem necessidade de `flush_etapa()` e `etapa_body` — reduz ~40 linhas de código
- O ReportLab gerencia quebras de página automaticamente para Paragraph e Table com `repeatRows`

### Alternativas Consideradas
- **Usar Platypus KeepTogether**: Tentativa anterior que causava "Flowable too large". Rejeitado.

---

## R3: Como simplificar as tabelas?

### Decisão
Tabelas simples com:
- Fonte Helvetica 9pt
- Grid com linhas finas (0.5pt) em cinza claro
- Header em negrito (primeira linha detectada como cabeçalho)
- Largura das colunas: `PAGE_W / n` (distribuição uniforme)
- Sem cores de fundo no header
- Sem callout de total

### Racional
- Tabelas sem cores são mais simples e não causam problemas de renderização
- Grid simples é suficiente para legibilidade
- Largura uniforme evita cálculo complexo de proporções

### Alternativas Consideradas
- **Tabelas sem grid**: Menos legível para conteúdos tabulares. Rejeitado.
- **Tabelas com alternância de cores**: Adiciona complexidade. Rejeitado.

---

## R4: Como tratar blocos de código longos?

### Decisão
Acumular linhas entre ``` e ```, depois criar um único Paragraph com fonte Courier 9pt. O ReportLab quebra Paragraphs longos automaticamente entre páginas.

### Racional
- Blocos de código JSON (como o da etapa4) podem ter 40+ linhas
- Paragraph com Courier quebra páginas naturalmente
- Sem necessidade de Table para código (que não quebraria)

### Alternativas Consideradas
- **Usar Table com fundo**: Mais complexo e propenso a "Flowable too large". Rejeitado.

---

## R5: Margens e layout?

### Decisão
- Margens: 2cm (aproximadamente 56.7pt) em todos os lados
- Fonte corpo: Helvetica 11pt com espaçamento 14pt
- Fonte título H1: Helvetica-Bold 16pt
- Fonte título H2: Helvetica-Bold 14pt
- Fonte título H3: Helvetica-Bold 12pt
- Fonte código: Courier 9pt
- Fonte tabela: Helvetica 9pt

### Racional
- 11pt é tamanho padrão para documentos (equivalente ao Arial 11 do Word)
- HEADER/FOOTER mantém fonte menor (Helvetica 9pt) para não poluir
- Margem de 2cm é padrão ABNT/DOC

### Alternativas Consideradas
- **Margens de 1.5cm**: Muito justo para conteúdos longos. Rejeitado.
- **Fonte 10pt**: Muito pequeno para leitura em tela. Rejeitado.

---

## R6: Estilos — quantos e quais?

### Decisão
Manter APENAS 5 estilos de Paragraph:

| Nome | Fonte | Tamanho | Uso |
|------|-------|---------|-----|
| `TITLE_STYLE` | Helvetica-Bold | 16pt | Título principal (H1) |
| `H2_STYLE` | Helvetica-Bold | 14pt | Seções (H2) |
| `H3_STYLE` | Helvetica-Bold | 12pt | Subseções (H3) |
| `BODY_STYLE` | Helvetica | 11pt | Texto comum |
| `CODE_STYLE` | Courier | 9pt | Blocos de código |

### Racional
- 5 estilos cobre todas as necessidades identificadas nos arquivos markdown de exemplo
- Sem estilos de callout, alerta, ou cores
- Todos em preto (#1f1f1f) — sem cores

### Alternativas Consideradas
- **Manter CALLOUT_STYLE**: Remove necessidade de detecção de total. Rejeitado.

---

## Resumo das Decisões

| # | Decisão | Arquivo | Linhas |
|---|---------|---------|--------|
| R1 | Remover paleta MD3, callouts, fundos, blocos de etapa | `pdf_generator.py` | -100 |
| R2 | Parser linear sem estado acumulador | `pdf_generator.py` | -40 |
| R3 | Tabelas simples sem cores, grid fino | `pdf_generator.py` | -20 |
| R4 | Blocos de código com Paragraph Courier | `pdf_generator.py` | mesmas |
| R5 | Margens 2cm, Helvetica 11pt corpo | `pdf_generator.py` | -5 |
| R6 | Apenas 5 estilos (remover CALLOUT_STYLE) | `pdf_generator.py` | -10 |
