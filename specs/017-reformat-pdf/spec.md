# Feature Specification: Reformatação do PDF Consolidado

**Feature Branch**: `017-reformat-pdf`

**Created**: 2026-06-29

**Status**: Draft

**Input**: Reformatar a saída do PDF do relatório consolidado (1x e 10x) com design profissional seguindo a identidade visual Material Design 3, sem alterar nenhuma informação ou regra de negócio impressa.

## User Scenarios & Testing

### User Story 1 - Visualizar relatório PDF com design profissional (Priority: P1)

O usuário, após executar uma análise (modo 1x ou 10x), deseja baixar o relatório consolidado em PDF com aparência profissional, organizada e de fácil leitura, seguindo a mesma identidade visual do frontend (Material Design 3).

**Why this priority**: O PDF é o principal artefato entregue ao usuário. Um relatório bem formatado transmite profissionalismo e facilita a compreensão das informações jurídicas.

**Independent Test**: Ao completar qualquer análise (1x ou 10x) e baixar o PDF, o documento exibe cabeçalho, rodapé com numeração, blocos coloridos para cada etapa e tabelas estilizadas, sem perda ou alteração de conteúdo.

**Acceptance Scenarios**:

1. **Given** que uma análise 1x foi concluída, **When** o usuário baixa o PDF, **Then** o documento contém exatamente as mesmas informações das 4 etapas (Metadados, Cifras, Risco, Consolidação) com formatação profissional.
2. **Given** que uma análise 10x foi concluída, **When** o usuário baixa o PDF, **Then** o documento contém exatamente as mesmas informações incluindo o resumo das 10 rodadas, com formatação profissional.
3. **Given** que o PDF é aberto, **When** o usuário visualiza o documento, **Then** ele exibe cabeçalho com o título "Radiante — Análise Jurídica" em todas as páginas.
4. **Given** que o PDF possui múltiplas páginas, **When** o usuário navega entre elas, **Then** cada página exibe numeração no formato "Página X de Y" no rodapé.
5. **Given** que o PDF contém as 4 etapas da análise, **When** o usuário visualiza cada seção, **Then** cada etapa é apresentada em um bloco visual distinto com cor de destaque e título hierárquico.

---

### Edge Cases

- **Modo 1x**: O PDF exibe as 4 etapas com formatação completa, sem seção de rodadas.
- **Modo 10x**: O PDF exibe as 4 etapas mais o resumo das rodadas, com formatação completa.
- **Conteúdo extenso**: Tabelas e blocos de texto longos devem quebrar corretamente entre páginas.
- **Caracteres especiais**: Acentos, cedilha e caracteres UTF-8 devem ser renderizados corretamente.
- **PDF vazio**: Se o conteúdo da análise for vazio, o PDF não deve ser gerado (comportamento existente).
- **Fonte ausente**: O PDF deve usar fontes padrão do ReportLab (Helvetica, Courier) que não dependem de instalação externa.

## Requirements

### Functional Requirements

- **FR-001**: O sistema DEVE manter exatamente o mesmo conteúdo textual e estrutura de seções do PDF atual, sem alterar nenhuma informação ou regra de negócio.
- **FR-002**: O PDF DEVE exibir um cabeçalho "Radiante — Análise Jurídica" no topo de cada página.
- **FR-003**: O PDF DEVE exibir numeração de páginas no formato "Página X de Y" no rodapé de cada página.
- **FR-004**: Cada etapa da análise (Metadados, Cifras, Risco, Consolidação) DEVE ser apresentada em um bloco visual distinto com:
  - Fundo levemente colorido (alternando entre tons sutis)
  - Título destacado com cor de destaque
  - Espaçamento adequado entre blocos
- **FR-005**: O valor total estimado (KPI) DEVE ser destacado visualmente com um callout ou box de destaque.
- **FR-006**: Tabelas presentes no conteúdo DEVEM ser estilizadas com grade sutil, células com padding adequado e cabeçalho diferenciado.
- **FR-007**: O design DEVE seguir a paleta de cores Material Design 3 (#4285f4 azul primário, tons de cinza para fundo, bordas sutis).
- **FR-008**: No modo 10x, a seção de resumo das rodadas DEVE ser apresentada com formatação consistente com as demais seções.
- **FR-009**: O PDF DEVE usar exclusivamente as fontes padrão do ReportLab (Helvetica, Helvetica-Bold, Courier) para garantir portabilidade.

### Key Entities

- **PDF Consolidado**: Documento gerado em formato PDF contendo o relatório completo da análise jurídica.
- **Bloco de Etapa**: Seção visual delimitada com fundo e título colorido, representando uma das 4 etapas do pipeline.
- **Callout de Total**: Box destacado visualmente para exibir o valor total estimado da análise.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Ao abrir o PDF gerado em qualquer visualizador, o documento exibe cabeçalho "Radiante — Análise Jurídica" e rodapé com "Página X de Y".
- **SC-002**: Cada uma das 4 etapas da análise é claramente distinguível visualmente (bloco com fundo e título próprio).
- **SC-003**: O valor total estimado é visualmente destacado dos demais elementos (callout ou box diferenciado).
- **SC-004**: Tabelas no conteúdo possuem grid sutil e cabeçalho com destaque.
- **SC-005**: Nenhuma informação ou dado é alterado, adicionado ou removido em relação ao PDF atual — apenas a formatação visual muda.
- **SC-006**: O PDF gerado no modo 10x segue exatamente a mesma identidade visual do modo 1x.

## Assumptions

- O conteúdo textual do relatório (markdown) gerado em `pipeline.py` para `run_once` e `run_ten_times` permanece inalterado.
- A biblioteca ReportLab já está instalada e disponível no ambiente.
- O design segue a paleta Material Design 3 já utilizada no frontend: azul primário #4285f4, tons de superfície (#f8f9fa, #e8eaed), bordas sutis (#dadce0).
- Fontes Helvetica e Courier estão disponíveis em qualquer ambiente onde o ReportLab roda (são fontes padrão).
- O PDF é gerado localmente na pasta `data/` e pode conter de 1 a N páginas dependendo do volume de conteúdo.

---

## Changelog (pós-merge)

### 2026-06-29 — Hotfix: Quebra de conteúdo extenso entre páginas (#flowable-too-large)

**Problema**: O erro `Flowable <Table> too large on page` ocorria quando o conteúdo de uma etapa ultrapassava a altura de uma página. Isso acontecia porque `_make_etapa_block()` usava uma `Table` aninhada, que o ReportLab **não quebra entre páginas**.

**Solução**: Substituiu-se a `Table` aninhada por aplicação direta de `backColor` em cada `Paragraph` individual. Os elementos do bloco são inseridos diretamente na lista de flowables, permitindo que o ReportLab quebre o conteúdo naturalmente entre páginas.

**Arquivo**: `backend/pdf_generator.py` — função `_make_etapa_block()` refatorada.
**Testes**: 73/73 pytest passando. Validação manual com 30 rubricas na Etapa 2 confirmou quebra correta entre páginas sem erro.
