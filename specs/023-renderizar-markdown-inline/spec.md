# Feature Specification: Renderizar Markdown Inline no PDF

**Feature Branch**: `023-renderizar-markdown-inline`

**Created**: 2026-06-29

**Status**: Draft

**Input**: User description: "eu quero que você analise o texto bruto que recebemos dos .md das etapas, eles chega com formatação de .md, porém no pdf essa formatação continua sem exposta sem estilizar, por exemplo, temos **Info** que deveria se transformar em um negrito no pdf mas continua aparecendo como **Info** no pdf, eu quero que essas formatções que chegam do .md sejam estilizadas no pdf e nao apareçam como código bruto."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Renderizar Formatação Inline Markdown no PDF (Priority: P1)

O operador do pipeline jurídico gera o relatório consolidado em PDF e todas as formatações de texto inline presentes nos arquivos .md das etapas são convertidas para a formatação visual correspondente no PDF. Texto em **negrito** aparece em negrito, *itálico* aparece em itálico, `código inline` aparece em fonte monoespaçada, e blocos de citação (`>`) aparecem com recuo e estilização apropriada.

**Why this priority**: A formatação inline markdown é extensivamente usada nas etapas (negrito em títulos de seção, itálico em raciocínios, código inline em termos técnicos). Exibir esses marcadores como texto bruto prejudica a legibilidade e a percepção profissional do documento.

**Independent Test**: Gerar o PDF e verificar visualmente que marcadores como `**texto**` e `*texto*` não aparecem mais como código bruto, sendo substituídos pela formatação visual correspondente.

**Acceptance Scenarios**:

1. **Given** que uma etapa contém `**Info:**`, **When** o PDF é gerado, **Then** o texto aparece em **negrito** (fonte Helvetica-Bold) sem os asteriscos visíveis.
2. **Given** que uma etapa contém `*texto em itálico*`, **When** o PDF é gerado, **Then** o texto aparece em *itálico* (fonte Helvetica-Oblique) sem os asteriscos visíveis.
3. **Given** que uma etapa contém `` `código inline` ``, **When** o PDF é gerado, **Then** o texto aparece em fonte Courier (monoespaçada) sem os backticks visíveis.
4. **Given** que uma etapa contém `> bloco de citação`, **When** o PDF é gerado, **Then** o bloco aparece com recuo à esquerda (leftIndent 20pt), cor on-surface-variant, e borda lateral esquerda sutil para distinção visual.
5. **Given** que o texto contém formatação aninhada como `> 💡 **Info:** texto`, **When** o PDF é gerado, **Then** o emoji 💡 é preservado, e o `**Info:**` aparece em negrito dentro do bloco de citação.

---

### User Story 2 — Títulos Falsos (H4+) Mantidos como Texto (Priority: P2)

Algumas etapas contêm linhas iniciadas com `####` ou `**###` que não são headers válidos do markdown padrão (apenas H1-H3 devem ser títulos). Estas linhas DEVEM ser renderizadas como parágrafo normal, mas com a formatação inline aplicada (negrito/itálico dentro delas preservado).

**Why this priority**: Evita que linhas como `**### 📌 Cifra: ...` sejam ignoradas ou exibidas incorretamente, garantindo que todo o conteúdo das etapas apareça no PDF.

**Independent Test**: Verificar que a linha `**### 📌 Cifra: ...` aparece como texto formatado (com negrito no `**...**`) no PDF, e não como título.

**Acceptance Scenarios**:

1. **Given** que uma linha começa com `**### `, **When** o PDF é gerado, **Then** o conteúdo é renderizado como parágrafo com `**Cifra:` em negrito, sem tratamento de heading.

---

### Edge Cases

- Emoji 💡 dentro de blocos de citação deve ser preservado na íntegra
- Negrito aninhado dentro de itálico ou vice-versa (`***texto***`) deve renderizar corretamente
- Texto com múltiplos spans de formatação na mesma linha (ex.: `**Info:** texto *importante*`) deve aplicar cada formatação no trecho correto
- Caracteres especiais (acentos, cedilha) não devem ser afetados pelo parser de markdown
- Blocos de código (```) já são tratados separadamente e não devem ser afetados por esta feature
- Tabelas markdown continuam sendo tratadas pelo parser de tabelas existente
- Linhas de separação (`---`) continuam sendo ignoradas (já tratadas como Spacer)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O parser de markdown inline DEVE converter `**texto**` para `<b>texto</b>` (negrito) no XML do ReportLab.
- **FR-002**: O parser DEVE converter `*texto*` para `<i>texto</i>` (itálico) no XML do ReportLab. Para evitar conflito com marcadores de lista (`* ` no início da linha), o parser só DEVE aplicar itálico quando o asterisco não estiver no início da linha ou quando estiver cercado por espaços/palavras.
- **FR-003**: O parser DEVE converter `` `código inline` `` para `<font face="Courier">código inline</font>` no XML do ReportLab.
- **FR-004**: O parser DEVE converter linhas iniciadas com `>` (blockquote) em parágrafos com estilo especial: leftIndent 20pt, rightIndent 10pt, cor on-surface-variant (`#49454F`), espaçamento antes/depois reduzido. A indentação com cor diferenciada substitui a barra vertical (não suportada pelo ReportLab).
- **FR-005**: O parser DEVE preservar formatação aninhada: dentro de blockquote, `**negrito**` e `*itálico*` ainda DEVEM ser convertidos.
- **FR-006**: O parser NÃO DEVE modificar conteúdo dentro de blocos de código (``` ... ```) ou dentro de células de tabela.
- **FR-007**: Linhas iniciadas com `**### ` ou padrões similares (negrito + hashes) NÃO DEVEM ser tratadas como heading, mas sim como parágrafo com formatação inline aplicada.
- **FR-008**: A implementação DEVE ser uma função pura `_parse_inline(text: str) -> str` que recebe texto markdown e retorna XML do ReportLab, sem dependências externas (apenas regex Python padrão).
- **FR-009**: O parser DEVE tratar múltiplas ocorrências de formatação na mesma linha (ex.: `**A** e *B* e \`C\` na mesma linha`).
- **FR-010**: O parser DEVE ignorar `*` e `**` quando usados para outros propósitos (como `* ` no início de linha para listas — estas já são tratadas pelo parser de listas existente).

### Key Entities *(include if feature involves data)*

- **Parser Inline Markdown**: Função que converte marcação markdown inline (negrito, itálico, código, blockquote) para XML compatível com ReportLab Paragraph.
- **Bloco de Citação (Blockquote)**: Linhas iniciadas com `>`, renderizadas com recuo e cor diferenciada, podendo conter formatação inline adicional.
- **Texto Formatado**: Parágrafo cujo conteúdo XML contém tags `<b>`, `<i>`, `<font>` aplicadas aos trechos correspondentes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Nenhum marcador `**` ou `*` (usado para formatação) aparece como texto visível no PDF gerado — 100% deles são convertidos para formatação visual.
- **SC-002**: Blocos de citação (`>`) são visualmente distinguíveis do corpo do texto por recuo e/ou cor, validado visualmente em 100% das ocorrências nas 4 etapas.
- **SC-003**: Código inline (`` ` ``) aparece em fonte monoespaçada em todas as ocorrências.
- **SC-004**: Conteúdo dentro de blocos de código (``` ... ```) não é alterado pelo parser inline.
- **SC-005**: O PDF continua sendo gerado com sucesso (sem erros de "Flowable too large" ou XML malformado) e válido (%PDF-1.4 com %%EOF).

## Assumptions

- Apenas o arquivo `backend/pdf_generator.py` será modificado para adicionar a função `_parse_inline` e ajustar o parser de linhas.
- O ReportLab Paragraph já suporta as tags XML `<b>`, `<i>`, `<font>`, `<br/>` — nenhuma dependência adicional é necessária.
- Blocos de código (```) e tabelas continuam sendo tratados pelos parsers existentes e não precisam de alteração.
- A função `_parse_inline` será uma função pura e testável independentemente.
- A estrutura de blockquote no markdown das etapas é sempre de linha única (cada linha `>` é independente), não blockquote multilinha aninhado.
