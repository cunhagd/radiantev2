# Feature Specification: Corrigir Abertura do PDF Consolidado

**Feature Branch**: `018-fix-pdf-abertura`

**Created**: 2026-06-29

**Status**: Draft

**Input**: Quando abro o pdf do relatório consolidado no visualizador/navegador ele nao abre. Testei em diversos leitores e nenhum abriu corretamente.

## User Scenarios & Testing

### User Story 1 - Baixar e abrir PDF do relatório consolidado (Priority: P1)

O usuário, após executar uma análise (modo 1x ou 10x), deseja baixar o PDF do relatório consolidado e abri-lo em qualquer visualizador padrão (navegador, Adobe Reader, etc.) sem erros.

**Why this priority**: O PDF é o principal artefato entregue ao usuário. Um PDF que não abre em nenhum leitor torna a análise inutilizável.

**Independent Test**: Ao clicar em "Baixar Relatório PDF" após qualquer análise, o arquivo baixado abre corretamente em pelo menos 3 leitores diferentes (Chrome, Edge, Adobe Reader).

**Acceptance Scenarios**:

1. **Given** que uma análise foi concluída, **When** o usuário clica em "Baixar Relatório PDF", **Then** o arquivo baixado abre sem erros no navegador Chrome.
2. **Given** que uma análise foi concluída, **When** o usuário clica em "Baixar Relatório PDF", **Then** o arquivo baixado abre sem erros no Adobe Reader.
3. **Given** que o PDF do relatório consolidado é gerado no servidor, **When** o arquivo é inspecionado, **Then** ele possui pelo menos 1 página (`/Count > 0`) e estrutura PDF válida.
4. **Given** que o PDF é gerado com conteúdo extenso (múltiplas etapas com dezenas de rubricas), **When** o arquivo é aberto, **Then** ele exibe corretamente todo o conteúdo em múltiplas páginas.

---

### Edge Cases

- **Conteúdo vindo da IA com formatação inesperada**: O texto markdown retornado pela IA pode conter caracteres especiais, quebras de linha inesperadas ou formatação que o parser do PDF não reconhece.
- **Bloco de etapa vazio**: Se uma etapa da análise retornar conteúdo vazio, o PDF não deve quebrar — deve ignorar a etapa ou exibir um placeholder.
- **Caracteres especiais**: Acentos, cedilha, aspas curvas e outros caracteres UTF-8 devem ser renderizados corretamente sem corromper o PDF.
- **Conteúdo muito extenso**: Quando uma etapa contém muitas rubricas (ex: +30 linhas em Etapa 2 - Cifras), o PDF deve quebrar páginas corretamente sem o erro "Flowable too large".

## Requirements

### Functional Requirements

- **FR-001**: O sistema DEVE gerar um PDF com estrutura válida (cabeçalho `%PDF-`, pelo menos 1 página, trailer com `%%EOF`) que possa ser aberto em qualquer visualizador padrão.
- **FR-002**: O sistema DEVE exibir o conteúdo de todas as 4 etapas corretamente, mesmo quando o texto retornado pela IA contiver formatação inesperada (quebras de linha, caracteres especiais, etc.).
- **FR-003**: O sistema NÃO DEVE produzir o erro "Flowable too large" ao processar conteúdo extenso — o PDF deve quebrar automaticamente o conteúdo entre páginas.
- **FR-004**: Se uma etapa retornar conteúdo vazio, o sistema DEVE ignorá-la e continuar gerando o PDF com as demais etapas.
- **FR-005**: O sistema DEVE garantir que caracteres acentuados e UTF-8 sejam renderizados corretamente no PDF, sem caracteres corrompidos ou ilegíveis.

### Key Entities

- **PDF Consolidado**: Documento gerado pelo `pdf_generator.py` com o resultado completo da análise jurídica.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% dos PDFs gerados após qualquer análise (1x ou 10x) possuem pelo menos 1 página (`/Count >= 1`) no dicionário de páginas.
- **SC-002**: 100% dos PDFs gerados passam em validação estrutural: cabeçalho `%PDF-`, trailer com `%%EOF`, cross-reference table íntegra.
- **SC-003**: Nenhum erro "Flowable too large" ou similar aparece nos logs do servidor durante a geração de PDF com conteúdo extenso.
- **SC-004**: O PDF gerado com conteúdo real (vindo da IA) abre corretamente em Chrome, Edge e Adobe Reader sem mensagens de erro ou corrupção.

## Assumptions

- O conteúdo textual (markdown) gerado em `pipeline.py` permanece inalterado — a correção é exclusivamente no parser do `pdf_generator.py`.
- A biblioteca ReportLab está instalada e disponível no ambiente.
- Os testes de abertura em múltiplos leitores são manuais (não automatizados).
- O erro documentado na spec `017-reformat-pdf` (Flowable too large) pode reaparecer se o parser não tratar corretamente conteúdo extenso vindo da IA.
