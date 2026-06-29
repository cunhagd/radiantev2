# Research: Corrigir Abertura do PDF Consolidado

## Problema

O PDF gerado em `data/relatorio_consolidado.pdf` possui 0 paginas (`/Count 0 /Kids [ ]`), impossibilitando sua abertura em qualquer leitor.

## Causa Raiz

O erro ocorria em duas camadas:

### 1. Erro "Flowable too large" (ja corrigido em fix/017-flowable-too-large)

Quando o conteudo de uma etapa era extenso (ex: Etapa 2 - Cifras com 30+ rubricas), a `Table` aninhada usada por `_make_etapa_block()` nao conseguia quebrar entre paginas e o ReportLab emitia:

```
ERROR: Flowable <Table@...> too large on page
```

Isso fazia o `doc.build()` gerar um PDF com **0 paginas** (parcial/corrompido).

**Correcao ja aplicada**: Substituiu-se a `Table` aninhada por aplicacao de `backColor` diretamente em cada `Paragraph`.

### 2. Ausencia de validacao pos-geracao

O sistema nao validava se o PDF gerado tinha pelo menos 1 pagina. Um PDF de 0 paginas era salvo no disco e servido ao frontend sem qualquer verificacao.

## Decisoes de Design

### Decision 1: Validacao estrutural apos geracao

- **O que**: Apos `doc.build()`, verificar se o PDF gerado possui estrutura valida (>= 1 pagina, header, trailer)
- **Por que**: Evitar servir PDF corrompido ao usuario
- **Alternativa rejeitada**: Validar apenas por tamanho do arquivo — arquivos de 931 bytes podem ter 0 paginas

### Decision 2: Tratamento de erro no `generate_pdf`

- **O que**: Encapsular `doc.build()` em try/except para capturar erros do ReportLab e garantir que nenhum PDF parcial seja salvo
- **Por que**: Se o build falhar, o PDF parcial nao deve substituir o anterior
- **Alternativa rejeitada**: Deixar o erro propagar — resultaria em estado inconsistente

### Decision 3: Fallback de conteudo vazio

- **O que**: Se `elements` estiver vazio apos o parser, adicionar um Paragraph padrao ("Nenhum conteudo disponivel")
- **Por que**: Garantir que o PDF nunca tenha 0 paginas
- **Alternativa rejeitada**: Retornar erro — melhor ter um PDF com mensagem do que nenhum PDF

### Decision 4: Robustez do parser contra formatacao inesperada

- **O que**: Qualquer linha que nao corresponda aos padroes conhecidos (#, ##, ###, ```, |, vazio) deve ser tratada como texto comum
- **Por que**: O texto vindo da IA pode conter formatacoes inesperadas (listas, marcadores, `**negrito**`, etc.)
- **Alternativa rejeitada**: Ignorar linhas desconhecidas — resultaria em conteudo faltando

## Riscos

- **ReportLab no Windows/Linux**: Comportamento identico, sem diferencas esperadas
- **Conteudo da IA variavel**: O parser atual ja trata qualquer linha como texto comum (fallback BODY_STYLE), entao o risco e baixo
- **Regressao visual**: Qualquer alteracao no parser deve manter os estilos MD3 ja implementados

## Conclusao

A correcao requer:
1. Validacao pos-build (verificar pagina e estrutura)
2. Try/except no build
3. Elemento padrao se lista vazia
4. Parser ja trata linhas desconhecidas — apenas garantir que nao ha regressao
