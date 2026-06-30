# Data Model: Estilizar PDF com Material Design 3

## Entities

### MD3 Color Theme

Conjunto de constantes de cor que definem o tema Material Design 3 do PDF.

| Campo | Cor | Uso |
|-------|-----|-----|
| `C_PRIMARY` | `#6750A4` | Títulos H1, cabeçalho de tabelas, accent bar, cabeçalho de página |
| `C_SECONDARY` | `#625B71` | Títulos H2 |
| `C_TERTIARY` | `#7D5260` | Títulos H3 |
| `C_SURFACE` | `#FFFBFE` | Fundo padrão da página |
| `C_SURFACE_VARIANT` | `#E7E0EC` | Fundo de blocos de código, etapas ímpares |
| `C_OUTLINE` | `#79747E` | Linhas de grid, bordas, separadores |
| `C_ERROR` | `#B3261E` | (reservado para uso futuro) |
| `C_BACKGROUND` | `#FFFBFE` | Fundo do documento (mesmo que surface) |
| `C_ON_PRIMARY` | `#FFFFFF` | Texto sobre fundo primary |
| `C_ON_SURFACE` | `#1C1B1F` | Texto do corpo |
| `C_ON_SURFACE_VARIANT` | `#49454F` | Texto do rodapé, metadados secundários |

**Relacionamentos**:
- Todas as cores derivam do tema MD3 padrão (Dynamic Color seed `#6750A4`)
- Cores `ON_*` são usadas exclusivamente como `textColor` em estilos aplicados sobre fundos da cor base correspondente

---

### Paragraph Style

Cada estilo de parágrafo no PDF herda cores do MD3 Theme.

| Estilo | Fonte | Tam. | Cor | Espaçamento | Uso |
|--------|-------|------|-----|-------------|-----|
| `TITLE_STYLE` | Helvetica-Bold | 16pt | C_PRIMARY | after=12, before=4 | Títulos H1 |
| `H2_STYLE` | Helvetica-Bold | 14pt | C_SECONDARY | after=8, before=10 | Títulos H2 |
| `H3_STYLE` | Helvetica-Bold | 12pt | C_TERTIARY | after=6, before=6 | Títulos H3 |
| `BODY_STYLE` | Helvetica | 11pt | C_ON_SURFACE | after=4, before=0 | Texto comum |
| `CODE_STYLE` | Courier | 9pt | C_ON_SURFACE | after=4, before=2, left/rightIndent=10 | Código |
| `LIST_STYLE` | Helvetica | 11pt | C_ON_SURFACE | after=4, before=0, leftIndent=15 | Listas |
| `COVER_TITLE_STYLE` | Helvetica-Bold | 24pt | C_PRIMARY | after=4, before=0 | Título da capa |
| `COVER_LABEL_STYLE` | Helvetica | 11pt | C_ON_SURFACE | after=2, before=0 | Rótulos na capa |

---

### Etapa Block

Conteúdo renderizado de um único arquivo `.md`.

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `filename` | `str` | Nome do arquivo (ex.: `etapa1.md`) |
| `flowables` | `list` | Lista de flowables gerados do parsing markdown |
| `accent_bar` | `Table` | Table 4pt x 18pt na cor primary (marcador visual) |
| `divider` | `HRFlowable` | Linha horizontal separadora (se não for o primeiro bloco) |

**Regras de Validação**:
- Etapas consecutivas DEVEM ser separadas por HRFlowable
- Cada etapa DEVE ter um accent bar no início
- Nenhum flowable de etapa DEVE estar dentro de Table wrapper (evita "Flowable too large")

---

### PDF Output

O PDF final gerado.

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `output_path` | `Path` | Caminho de saída do PDF |
| `elements` | `list` | Lista de flowables (cover + divisores + etapas) |
| `total_pages` | `int` | Número total de páginas (two-pass build) |
| `header_text` | `str` | "Radiante — Análise Jurídica" (cor primary) |
| `footer_format` | `str` | "Página {page} de {total}" (cor on-surface-variant) |

**Relacionamentos**:
- 1 PDF contém 0 ou 1 capa (Cover Page)
- 1 PDF contém 1 ou mais blocos de etapa (Etapa Block)
- 1 PDF contém exatamente 1 tema MD3 (MD3 Color Theme)

---

### Cover Page Metadata

Dados extraídos de `data/resultado_final.json` para a página de capa.

| Campo | Fonte no JSON | Obrigatório | Fallback |
|-------|---------------|-------------|----------|
| `numero_processo` | `numero_processo` | Sim | `"N/A"` |
| `autor` | `autor` | Sim | `"N/A"` |
| `reclamada` | `reclamada` | Sim | `"N/A"` |
| `valor_total_estimado` | `valor_total_estimado` | Sim | `"0,00"` |
| `data_geracao` | Data atual | Sim | Data atual formatada |

**Regras de Validação**:
- Se `data/resultado_final.json` não existir, a capa NÃO é gerada (graceful fallback)
- Todos os campos da capa usam `str` — valores numéricos são convertidos para string formatada (ex.: `"R$ 185.200,31"`)
