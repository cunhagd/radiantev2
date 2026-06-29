# Research: Reformatação do PDF Consolidado

## Decision Record

### Design: Material Design 3 para PDF

**Decision**: Usar paleta Material Design 3 adaptada para PDF via ReportLab.

**Rationale**:
- Consistência com a identidade visual do frontend
- Profissionalismo e legibilidade
- Sem dependências externas — ReportLab suporta cores e estilos nativamente

**Paleta Definida**:

| Função | Cor | Uso |
|--------|-----|-----|
| Azul Primário | `#4285f4` | Títulos de etapa, destaques |
| Fundo Claro (par) | `#f8f9fa` | Fundo de blocos de etapa (pares) |
| Fundo Claro (ímpar) | `#e8eaed` | Fundo de blocos de etapa (ímpares) |
| Borda Sutil | `#dadce0` | Bordas de tabelas e blocos |
| Texto Primário | `#1f1f1f` | Corpo do texto |
| Texto Secundário | `#5f6368` | Metadados, labels |
| Verde Sucesso | `#34a853` | Valor total estimado (callout) |
| Branco | `#ffffff` | Fundo de página |

### Fontes: Helvetica e Courier

**Decision**: Usar exclusivamente fontes padrão do ReportLab.
- **Helvetica**: Corpo do texto, cabeçalhos, tabelas
- **Helvetica-Bold**: Títulos, destaques
- **Courier**: Blocos de código

**Rationale**: Portabilidade garantida em qualquer ambiente sem instalação de fontes.

### Estrutura do PDF

**Decision**: Usar `SimpleDocTemplate` com `onFirstPage`/`onLaterPages` para cabeçalho/rodapé.

**Elementos**:
1. **Cabeçalho**: "Radiante — Análise Jurídica" alinhado à esquerda, linha separadora abaixo
2. **Rodapé**: "Página X de Y" alinhado ao centro
3. **Blocos de etapa**: `Table` com fundo colorido, título e conteúdo
4. **Callout de total**: `Table` com fundo verde claro e borda verde, texto em negrito
5. **Tabelas**: `Table` com grid sutil, cabeçalho com fundo azul claro
6. **Código**: Fonte Courier, fundo cinza claro

### Implementacao

A função `generate_pdf()` em `backend/pdf_generator.py` será completamente reescrita mantendo a mesma assinatura e contrato de entrada/saída.

### Alternativas Consideradas

- **FPDF2**: Rejeitado — ReportLab já está instalado e é maduro
- **WeasyPrint**: Rejeitado — dependência pesada, instalação complexa no Windows
- **HTML -> PDF**: Rejeitado — adicionaria dependências desnecessárias
