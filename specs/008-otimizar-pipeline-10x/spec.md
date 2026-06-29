# Feature Specification: Otimizar Pipeline 10x

**Feature**: `008-otimizar-pipeline-10x`

**Created**: 2026-06-28

**Status**: Draft

**Input**: Otimizar o pipeline 10x para rodar etapas 1, 2 e 4 uma unica vez e etapa 3 em 10 repeticoes.

## User Scenarios & Testing

### User Story 1 - Execucao 10x otimizada (Priority: P1)

Como usuario do sistema, ao clicar no botao "10x", quero que o sistema execute as etapas de extracao de metadados (etapa 1) e calculo de cifras (etapa 2) apenas uma vez, e somente a etapa de probabilidade e risco (etapa 3) seja executada 10 vezes, resultando em uma analise mais rapida e com mesma qualidade.

**Por que esta prioridade**: E a unica funcionalidade da feature — substitui a logica atual que executa todas as 4 etapas 10x desnecessariamente.

**Teste independente**: Pode ser testado executando o pipeline 10x e verificando que as etapas 1, 2 e 4 aparecem apenas uma vez no log, enquanto a etapa 3 aparece 10 vezes com saidas diferentes.

**Cenarios de aceite**:

1. **Given** que o sistema possui documentos carregados, **When** o usuario aciona o modo 10x, **Then** a etapa 1 (metadados) executa exatamente 1 vez
2. **Given** que a etapa 1 foi concluida, **When** o pipeline continua, **Then** a etapa 2 (cifras) executa exatamente 1 vez usando o resultado da etapa 1
3. **Given** que a etapa 2 foi concluida, **When** o pipeline inicia as repeticoes, **Then** a etapa 3 (probabilidade) executa exatamente 10 vezes, cada uma usando o mesmo resultado fixo da etapa 2
4. **Given** que as 10 repeticoes da etapa 3 foram concluidas, **When** o pipeline consolida, **Then** a etapa 4 (consolidacao final) executa exatamente 1 vez usando todos os resultados da etapa 3
5. **Given** que o pipeline otimizado foi executado, **When** verifico o resultado consolidado, **Then** ele contem a consolidacao das 10 variacoes de probabilidade sobre as mesmas cifras base

---

### Edge Cases

- O que acontece se a etapa 1 falhar? Nenhuma etapa subsequente deve executar.
- O que acontece se a etapa 2 falhar? A etapa 3 nao deve executar.
- O que acontece se algumas das 10 repeticoes da etapa 3 falharem? As bem-sucedidas devem ser consolidadas, as falhas ignoradas (comportamento atual).
- O que acontece se a etapa 4 falhar? O usuario deve receber um erro, mas os resultados parciais devem estar disponiveis.

## Requirements

### Functional Requirements

- **FR-001**: System MUST execute etapa 1 (metadados) exactly once when mode 10x is triggered
- **FR-002**: System MUST execute etapa 2 (cifras) exactly once, using the output of etapa 1
- **FR-003**: System MUST execute etapa 3 (probabilidade) exactly 10 times, each using the SAME fixed output from etapa 2
- **FR-004**: System MUST execute etapa 4 (consolidacao) exactly once, consolidating all 10 results from etapa 3
- **FR-005**: System MUST abort the pipeline if etapa 1 or etapa 2 fail
- **FR-006**: System MUST still consolidate successfully even if some of the 10 etapa 3 repetitions fail (graceful degradation)

### Key Entities

- **PipelineRun**: Representa uma execucao do pipeline, contendo resultado unico das etapas 1/2/4 e multiplos resultados da etapa 3
- **CifrasBase**: Conjunto fixo de cifras calculado na etapa 2, usado como entrada para todas as 10 repeticoes da etapa 3

## Success Criteria

### Measurable Outcomes

- **SC-001**: Pipeline 10x completo executa em aproximadamente 25% do tempo atual (etapas 1/2/4 rodam 1x ao inves de 10x)
- **SC-002**: Resultado consolidado final e funcionalmente identico ao cenario onde todas as etapas rodam 10x (as cifras base sao as mesmas)
- **SC-003**: Nenhuma alteracao na logica interna das etapas individuais — apenas a orquestracao muda

## Assumptions

- A logica interna de cada etapa (1, 2, 3, 4) permanece inalterada
- O resultado da etapa 2 e puramente deterministico (mesmo input = mesmo output)
- A variacao entre rodadas diferentes vem exclusivamente da etapa 3 (probabilidade)
- O formato de saida da etapa 4 (JSON consolidado) permanece o mesmo
