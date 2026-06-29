# Quickstart: Reformatação do PDF Consolidado

## Pré-requisitos

- Servidor rodando: `python dev.py --server` ou `python -m backend.app --mode web --port 8000`
- `.env` configurado com credenciais AWS e preços Grok

## Cenários de Validação

### Cenário 1: PDF 1x com formatação profissional

1. Faça upload de um documento jurídico
2. Clique em "1x"
3. Aguarde a análise completar
4. Clique em "Baixar Relatório PDF"
5. **Esperado**:
   - Cabeçalho "Radiante — Análise Jurídica" no topo de cada página
   - Rodapé com "Página X de Y"
   - 4 blocos visualmente distintos para cada etapa
   - Tabelas com grade sutil e cabeçalho destacado
   - Valor total em callout verde destacado
   - Mesmo conteúdo textual do relatório anterior

### Cenário 2: PDF 10x com formatação profissional

1. Faça upload de um documento jurídico
2. Clique em "10x"
3. Aguarde a análise completar
4. Clique em "Baixar Relatório PDF"
5. **Esperado**: Mesmo layout do Cenário 1, incluindo seção de resumo das rodadas com formatação consistente

### Cenário 3: Consistência entre 1x e 10x

1. Gere PDF no modo 1x e modo 10x
2. **Esperado**: Ambos os PDFs seguem exatamente a mesma identidade visual (cabeçalho, rodapé, blocos, fontes, cores)

## Contrato de Dados

Ver `data-model.md` para a estrutura visual do PDF.
