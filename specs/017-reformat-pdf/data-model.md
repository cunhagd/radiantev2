# Data Model: Reformatação do PDF Consolidado

## PDF Consolidado

Documento gerado pelo módulo `backend/pdf_generator.py` a partir de texto markdown.

### Entrada

```python
text: str        # Conteúdo markdown do relatório (4 etapas)
output_path: str  # Caminho de saída do PDF
```

### Saída

```text
Caminho absoluto do arquivo PDF gerado (.pdf)
```

### Estrutura Visual

| Elemento | Descrição | Cor |
|----------|-----------|-----|
| Cabeçalho | "Radiante — Análise Jurídica" em todas as páginas | #1f1f1f |
| Rodapé | "Página X de Y" centralizado | #5f6368 |
| Bloco Etapa 1 (Metadados) | Fundo #f8f9fa, título azul #4285f4 | par |
| Bloco Etapa 2 (Cifras) | Fundo #e8eaed, título azul #4285f4 | ímpar |
| Bloco Etapa 3 (Risco) | Fundo #f8f9fa, título azul #4285f4 | par |
| Bloco Etapa 4 (Consolidação) | Fundo #e8eaed, título azul #4285f4 | ímpar |
| Callout Total | Fundo #e6f4ea, borda #34a853, texto em negrito | verde |
| Tabelas | Cabeçalho com fundo #e8f0fe, grid #dadce0 | azul claro |
| Código | Fonte Courier, fundo #f1f5f9 | cinza |
