# Feature Specification: Estilizar PDF com Material Design 3

**Feature Branch**: `022-estilizar-pdf-md3`

**Created**: 2026-06-29

**Status**: Draft

**Input**: User description: "Agora que temos o pdf sendo criado corretamente, vamos personalizar o PDF com uma estilização, formatação e template mais profissional de acordo com as mlehores praticas de desenvolvimento e ux ui design. VAmos seguir como referencia o design do material3 da google."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — PDF com Estilo Profissional MD3 (Priority: P1)

O operador do pipeline jurídico gera o relatório consolidado em PDF e obtém um documento visualmente profissional, com identidade visual consistente (cores, tipografia, espaçamentos) seguindo o sistema Material Design 3, facilitando a apresentação para clientes e partes interessadas.

**Why this priority**: O PDF é o principal artefato de entrega do sistema. Melhorar sua aparência eleva a percepção de qualidade do serviço jurídico prestado.

**Independent Test**: Gerar o PDF via pipeline e verificar visualmente que os elementos de design MD3 estão presentes em todas as páginas.

**Acceptance Scenarios**:

1. **Given** que o pipeline foi executado com sucesso, **When** o PDF relatorio_consolidado.pdf é aberto, **Then** todas as páginas exibem cabeçalho, rodapé e cores do tema Material Design 3.
2. **Given** que o PDF contém múltiplas etapas, **When** o usuário navega entre as páginas, **Then** cada etapa é visualmente distinguível por accent bar (barra vertical 4pt na cor primary) no início e HRFlowable divider entre etapas consecutivas.
3. **Given** que o PDF contém tabelas, **When** o usuário visualiza uma tabela, **Then** o cabeçalho da tabela tem fundo na cor primary, texto branco, e as linhas alternam entre surface e surface variant para legibilidade.
4. **Given** que o PDF contém blocos de código JSON, **When** o usuário visualiza o bloco, **Then** o código é exibido em fonte monoespaçada com fundo em tom neutro (surface variant) e borda sutil.

---

### User Story 2 — Página de Capa com Resumo (Priority: P2)

O operador do pipeline recebe um PDF com uma página de capa profissional contendo: logo do Radiante, número do processo, autor, reclamada, valor total estimado e data de geração, servindo como resumo executivo do relatório.

**Why this priority**: A capa dá contexto imediato ao leitor sobre o conteúdo do documento, melhorando a experiência de quem recebe o relatório.

**Independent Test**: Gerar o PDF e verificar que a primeira página é uma capa com as informações do processo.

**Acceptance Scenarios**:

1. **Given** que o pipeline foi executado, **When** o PDF é aberto, **Then** a primeira página exibe uma capa com: "Radiante" como título principal, número do processo, autor, reclamada, valor total estimado e data de geração.
2. **Given** que a capa existe, **When** o usuário passa para a segunda página, **Then** o conteúdo das etapas começa a partir da página 2, com cabeçalho e rodapé padrão.

---

### Edge Cases

- O PDF com muitas páginas (50+) deve manter a consistência visual sem degradação de performance (geração em < 10s)
- Caracteres especiais e emojis nos textos das etapas não devem quebrar a renderização ou causar "Flowable too large"
- A capa deve ser gerada mesmo que haja apenas uma etapa (mínimo de conteúdo)
- Tabelas com muitas colunas devem ser legíveis sem estourar a largura da página

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O PDF DEVE usar a paleta de cores Material Design 3: primary `#6750A4`, secondary `#625B71`, tertiary `#7D5260`, surface `#FFFBFE`, surface variant `#E7E0EC`, outline `#79747E`, error `#B3261E`, background `#FFFBFE`, on-primary `#FFFFFF`, on-surface `#1C1B1F`, on-surface-variant `#49454F`.
- **FR-002**: O PDF DEVE usar accent bar (barra vertical de 4pt na cor primary `#6750A4`) no início de cada bloco de etapa e HRFlowable divider (linha horizontal 0.5pt na cor outline `#79747E`) entre etapas consecutivas como substituto visual para cantos arredondados (não suportados pelo ReportLab).
- **FR-003**: Cada bloco de etapa (conteúdo de cada arquivo .md) DEVE ser visualmente distinguível através de accent bar (barra vertical 4pt cor primary) no início do bloco e HRFlowable divider entre etapas consecutivas. NÃO deve ser usado Table wrapper com fundo para o bloco inteiro, pois o ReportLab não quebra conteúdo dentro de Tables entre páginas, causando "Flowable too large".
- **FR-004**: O cabeçalho do PDF DEVE exibir "Radiante — Análise Jurídica" com fonte Helvetica-Bold 9pt na cor primary (`#6750A4`), com linha separadora na cor outline (`#79747E`).
- **FR-005**: O rodapé do PDF DEVE exibir "Página X de Y" centralizado, Helvetica 8pt, cor on-surface-variant (`#49454F`).
- **FR-006**: Tabelas markdown DEVEM ter cabeçalho com fundo primary (`#6750A4`) e texto on-primary (`#FFFFFF`), linhas alternando entre surface e surface variant, grid 0.5pt na cor outline.
- **FR-007**: Blocos de código (```) DEVEM ser exibidos com fundo surface variant (`#E7E0EC`), borda 0.5pt outline (`#79747E`), padding interno de 10pt, fonte Courier 9pt.
- **FR-008**: Listas markdown (linhas iniciadas com `* ` ou `- `) DEVEM manter recuo de 15pt com bullet/asterisco substituído por um marcador visual (ex.: bullet "•" ou hífen estilizado).
- **FR-009**: Títulos H1 DEVEM usar primary (`#6750A4`) como cor, Helvetica-Bold 16pt. Títulos H2 DEVEM usar secondary (`#625B71`), Helvetica-Bold 14pt. Títulos H3 DEVEM usar tertiary (`#7D5260`), Helvetica-Bold 12pt.
- **FR-010**: O corpo do texto DEVE usar Helvetica 11pt, cor on-surface (`#1C1B1F`), espaçamento entre linhas de 14pt.
- **FR-011**: A página de capa DEVE ser gerada como primeira página do PDF, contendo: título "Radiante" em destaque (primary, 24pt), número do processo, autor, reclamada, valor total estimado e data de geração. Os metadados DEVEM ser extraídos do arquivo `data/resultado_final.json` (gerado pela Etapa 4 do pipeline), que contém `numero_processo`, `autor`, `reclamada`, `valor_total_estimado`.

### Key Entities *(include if feature involves data)*

- **Tema MD3**: Conjunto de cores, tipografia e espaçamentos definidos pelo sistema Material Design 3, aplicados consistentemente em todos os elementos do PDF.
- **Bloco de Etapa**: Conteúdo de um arquivo .md individual, renderizado como uma seção visualmente distinta com accent bar (barra vertical 4pt cor primary) e HRFlowable divider entre blocos. O conteúdo de cada etapa flui naturalmente sem Table wrapper.
- **Elemento Visual**: Cada Paragraph, Table, Spacer ou bloco de código no PDF, que herda cores e estilos do tema MD3.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: PDF gerado em menos de 10 segundos para até 50 páginas de conteúdo.
- **SC-002**: PDF abre corretamente nos 3 principais leitores (Adobe Acrobat, navegador Chrome, Microsoft Edge) sem erros de renderização.
- **SC-003**: Todas as 4 etapas são visualmente distinguíveis por accent bar (barra primary 4pt) e dividers entre blocos, validado visualmente.
- **SC-004**: Tabelas exibem cabeçalho com fundo primary e texto branco, validado visualmente.
- **SC-005**: Blocos de código exibem fundo surface variant e borda sutil, validado visualmente.
- **SC-006**: Cabeçalho e rodapé aparecem em todas as páginas (exceto capa, se implementada), com cores MD3 corretas.

## Assumptions

- O arquivo `data/resultado_final.json` contém os metadados do processo (processo, autor, reclamada, valor total) para a página de capa (User Story 2).
- O ReportLab suporta todos os recursos visuais necessários (cores, HRFlowable, TableStyle) — border-radius não é suportado nativamente, sendo substituído por accent bar + divider.
- O PDF continua sendo gerado no caminho `data/relatorio_consolidado.pdf`.
- A assinatura da função `generate_pdf(etapas_dir, output_path)` permanece inalterada — o pipeline não precisa ser modificado.
- Apenas o arquivo `backend/pdf_generator.py` será modificado ou criado para esta feature.
