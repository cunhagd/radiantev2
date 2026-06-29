# Feature Specification: Estruturar Etapas do Pipeline em Markdown

**Feature Branch**: `019-estruturar-etapas-pipeline`

**Created**: 2026-06-29

**Status**: Draft

**Input**: Precisamos criar um processo muito bem definido e claro de cada etapa para conseguirmos criar o PDF final da forma correta. O resultado da etapa 1 deve ser salvo no diretório 'etapas' em um markdown etapa1.md, a etapa 2 como etapa2.md, etapa3 como etapa3.md e etapa 4 como etapa4.md. Esses são exatamente os dados que precisamos para gerar o PDF de forma estruturada. Então ajuste o código para gerar o .md em cada etapa de forma estruturada e organizada para o gerador do PDF consumir depois esses .md para montar o PDF.

## User Scenarios & Testing

### User Story 1 - Pipeline salva cada etapa como arquivo markdown estruturado (Priority: P1)

O sistema, ao executar o pipeline de análise jurídica (modo 1x ou 10x), deve salvar o resultado de cada etapa (Etapa 1 a 4) como um arquivo markdown individual no diretório `data/etapas/`. O gerador de PDF (`pdf_generator.py`) deve ser refatorado para ler esses arquivos .md em vez do texto bruto concatenado, garantindo um PDF estruturado e consistente.

**Why this priority**: Sem arquivos de etapa individuais e estruturados, o PDF é gerado a partir de texto bruto da IA sem formatação previsível, causando inconsistências e o problema de PDF inválido (0 páginas). A estruturação das etapas resolve a causa raiz.

**Independent Test**: Ao executar uma análise 1x, os arquivos `data/etapas/etapa1.md`, `etapa2.md`, `etapa3.md` e `etapa4.md` são criados com conteúdo markdown válido. O PDF gerado a partir desses arquivos abre corretamente.

**Acceptance Scenarios**:

1. **Given** que uma análise 1x foi iniciada, **When** cada etapa é concluída, **Then** o resultado é salvo em `data/etapas/etapa{N}.md` com formatação markdown estruturada.
2. **Given** que uma análise 10x foi iniciada, **When** as etapas 1, 2 e 4 são concluídas (executadas uma vez), **Then** os resultados são salvos em `data/etapas/etapa{N}.md`.
3. **Given** que a análise 10x executa a etapa 3 dez vezes, **When** cada rodada é concluída, **Then** os resultados são salvos em `data/etapas/etapa3_rodada{N}.md`.
4. **Given** que os arquivos de etapa existem no diretório `data/etapas/`, **When** o `generate_pdf()` é chamado, **Then** ele lê os arquivos e gera o PDF com o conteúdo de cada etapa.
5. **Given** que uma nova análise é iniciada, **When** o pipeline executa, **Then** o diretório `data/etapas/` é limpo antes de salvar os novos arquivos.

---

### Edge Cases

- **Diretório `data/etapas/` não existe**: O pipeline deve criar o diretório automaticamente.
- **Etapa vazia**: Se uma etapa retornar conteúdo vazio, o arquivo .md deve conter uma mensagem indicativa ("Nenhum conteúdo disponível para esta etapa.").
- **Modo 10x - etapa 3**: Dez arquivos `etapa3_rodada1.md` a `etapa3_rodada10.md` devem ser gerados, cada um com o resultado individual daquela rodada.
- **Arquivos de análise anterior**: Antes de salvar os novos arquivos, o pipeline deve limpar o diretório `data/etapas/` para evitar mistura de resultados de análises diferentes.
- **Falha em uma etapa**: Se uma etapa falhar, o arquivo .md correspondente deve conter a mensagem de erro e o pipeline deve interromper (comportamento existente).

## Requirements

### Functional Requirements

- **FR-001**: O pipeline DEVE criar o diretório `data/etapas/` se ele não existir no início de cada análise.
- **FR-002**: O pipeline DEVE limpar o diretório `data/etapas/` antes de salvar novos arquivos de etapa.
- **FR-003**: O pipeline DEVE salvar o resultado da Etapa 1 em `data/etapas/etapa1.md` com formatação markdown estruturada assim que a etapa for concluída.
- **FR-004**: O pipeline DEVE salvar o resultado da Etapa 2 em `data/etapas/etapa2.md` com formatação markdown estruturada.
- **FR-005**: O pipeline DEVE salvar o resultado da Etapa 3 em `data/etapas/etapa3.md` (modo 1x) ou `data/etapas/etapa3_rodada{N}.md` (modo 10x).
- **FR-006**: O pipeline DEVE salvar o resultado da Etapa 4 em `data/etapas/etapa4.md` com formatação markdown estruturada.
- **FR-007**: O `generate_pdf()` DEVE ser refatorado para ler os arquivos `data/etapas/etapa1.md`, `etapa2.md`, `etapa3.md`, `etapa4.md` e montar o PDF a partir deles, em vez de receber texto concatenado.
- **FR-008**: O `generate_pdf()` DEVE aceitar também o diretório `data/etapas/` como parâmetro, lendo todos os arquivos .md dentro dele.
- **FR-009**: Se uma etapa tiver conteúdo vazio, o arquivo .md correspondente DEVE conter "Nenhum conteúdo disponível para esta etapa."

### Key Entities

- **Arquivo de Etapa (.md)**: Arquivo markdown individual para cada etapa do pipeline, armazenado em `data/etapas/etapa{N}.md`.
- **Diretório `data/etapas/`**: Diretório centralizador de todos os arquivos de etapa, limpo a cada nova análise.
- **PDF Consolidado**: Documento gerado a partir da leitura dos arquivos de etapa estruturados.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Após qualquer análise (1x ou 10x), exatamente 4 arquivos .md (ou 13 no modo 10x: 4 + 10 rodadas) são criados em `data/etapas/`.
- **SC-002**: O PDF gerado a partir dos arquivos de etapa possui pelo menos 1 página e estrutura PDF válida.
- **SC-003**: O conteúdo do PDF reflete exatamente o conteúdo salvo nos arquivos de etapa (verificação por comparação textual).
- **SC-004**: Uma nova análise substitui completamente os arquivos da análise anterior (diretório limpo antes de salvar).

## Assumptions

- O pipeline (`pipeline.py`) continuará chamando as 4 etapas da IA — apenas a forma de armazenamento do resultado muda (de variável em memória para arquivo .md).
- O `generate_pdf()` em `pdf_generator.py` será refatorado para aceitar um diretório como entrada em vez de texto.
- A formatação markdown salva em cada etapa deve ser limpa e organizada (tabelas, cabeçalhos, seções) para facilitar a geração do PDF.
- O diretório `data/etapas/` será incluído no `.gitignore` para não versionar resultados de análise.
