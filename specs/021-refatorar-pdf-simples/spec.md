# Feature Specification: Refatorar PDF para estilo simples

**Feature Branch**: `021-refatorar-pdf-simples`

**Created**: 2026-06-29

**Status**: Draft

**Input**: Refatorar a geração de PDF para um estilo simples e funcional, sem excessos de estilização.

## User Scenarios & Testing

### User Story 1 - Gerar PDF consolidado com estilo simples (Priority: P1)

O usuário (operador do pipeline) pode executar o pipeline de análise jurídica (1x ou 10x) e obter um PDF funcional contendo todo o conteúdo das 4 etapas salvas em `data/etapas/` (etapa1.md a etapa4.md), formatado de forma simples, limpa e organizada.

**Why this priority**: O PDF é a principal saída do sistema. Atualmente a geração está quebrada (erros "Flowable too large", páginas em branco, estilos complexos impedindo a renderização correta). Sem esta correção, o sistema não entrega seu principal artefato.

**Independent Test**: Executar o pipeline (1x) e verificar que o PDF gerado em `data/relatorio_consolidado.pdf` contém todas as informações das 4 etapas, abre corretamente em qualquer leitor de PDF e tem pelo menos 1 página.

**Acceptance Scenarios**:

1. **Given** que as etapas foram geradas em `data/etapas/`, **When** o pipeline finaliza e chama `generate_pdf()`, **Then** o PDF é criado sem erros e contém conteúdo de todas as etapas.
2. **Given** que o PDF foi gerado, **When** aberto em qualquer visualizador (Adobe, Chrome, Edge), **Then** todas as páginas são renderizadas corretamente (sem páginas em branco, sem conteúdo cortado).
3. **Given** que uma etapa tem conteúdo muito longo (ex: tabelas grandes, blocos de código JSON), **When** o PDF é gerado, **Then** o conteúdo quebra entre páginas naturalmente sem erros ou perda de dados.

---

### Edge Cases

- **Conteúdo vazio**: Se `data/etapas/` estiver vazio, o PDF deve ser gerado com mensagem "Nenhum conteúdo disponível para o relatório."
- **Arquivo markdown mal formatado**: Tabelas mal formatadas, cabeçalhos sem conteúdo e blocos de código longos não devem quebrar a geração.
- **Conteúdo muito longo (>100 páginas)**: O PDF deve ser gerado sem erros de "Flowable too large" ou estouro de memória.
- **Caracteres especiais**: Acentos, cedilha e caracteres Latin-1 devem ser renderizados corretamente. Caracteres não-Latin-1 (como emoji `⚖️`, `💡`, travessão `—`) podem não ser suportados pela fonte Helvetica — nestes casos, o PDF deve exibir o conteúdo sem erros, mesmo que o caractere apareça como quadrado ou espaço em branco.

## Requirements

### Functional Requirements

- **FR-001**: O sistema DEVE ler os arquivos markdown de `data/etapas/` (etapa1.md, etapa2.md, etapa3.md, etapa4.md) em ordem alfabética.
- **FR-002**: O PDF DEVE ter formatação simples: fonte Helvetica tamanho 11 para corpo, Helvetica-Bold para títulos, margens uniformes de 2cm.
- **FR-003**: O PDF DEVE exibir o título "Radiante — Análise Jurídica" no topo de cada página.
- **FR-004**: O PDF DEVE numerar páginas no formato "Página X de Y" no rodapé.
- **FR-005**: Os cabeçalhos markdown (`#`, `##`, `###`) DEVEM ser convertidos para títulos no PDF com tamanhos decrescentes (16, 14, 12).
- **FR-006**: Tabelas markdown DEVEM ser convertidas para tabelas PDF com linhas simples.
- **FR-007**: Blocos de código (```) DEVEM ser exibidos em fonte monoespaçada (Courier) com indentação.
- **FR-008**: Linhas iniciadas com `* ` (asterisco + espaço) ou `- ` (hífen + espaço) DEVEM ser exibidas como parágrafos com recuo esquerdo de 15pt em relação ao texto normal, preservando a identação visual.
- **FR-009**: O PDF DEVE permitir quebras de página naturais — blocos de conteúdo (etapas, seções) podem se estender por múltiplas páginas.
- **FR-010**: Em caso de erro durante a geração, o sistema DEVE exibir mensagem clara no terminal e NÃO DEVE deixar arquivos PDF parciais/corrompidos.
- **FR-011**: O PDF gerado DEVE ser validado após a criação (cabeçalho `%PDF-` e marcador `%%EOF` presentes).

### Key Entities

- **Arquivo de Etapa (.md)**: Arquivo markdown em `data/etapas/` contendo a saída de uma etapa do pipeline.
- **PDF Consolidado**: Arquivo PDF em `data/relatorio_consolidado.pdf` contendo a concatenação de todas as etapas.
- **Elementos PDF**: Blocos de conteúdo no PDF — parágrafos, títulos, tabelas, blocos de código, espaçadores.

## Success Criteria

### Measurable Outcomes

- **SC-001**: O PDF é gerado em menos de 5 segundos para um documento de até 50 páginas.
- **SC-002**: O PDF abre corretamente nos 3 principais visualizadores (Adobe Acrobat, navegador Chrome, navegador Edge).
- **SC-003**: 100% do conteúdo textual das etapas markdown está presente no PDF (sem truncamento).
- **SC-004**: O código de geração de PDF tem no máximo 200 linhas (reduzindo a complexidade atual).

## Assumptions

- O ReportLab continuará sendo a biblioteca de geração de PDF.
- A função `generate_pdf()` continuará recebendo o diretório de etapas como parâmetro.
- O pipeline (1x e 10x) continuará chamando `generate_pdf()` ao final.
- O conteúdo markdown pode conter: texto, cabeçalhos, tabelas, blocos de código, listas simples.
- Estilos complexos (cores, fundos, callouts, bordas coloridas) serão removidos.
