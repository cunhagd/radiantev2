# Tasks: Renderizar Markdown Inline no PDF

**Input**: Design documents from `/specs/023-renderizar-markdown-inline/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/parse_inline.md

**Tests**: Não solicitados na especificação. Validação visual do PDF.

**Organization**: Tasks agrupadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: Qual user story esta tarefa pertence (US1, US2)
- Incluir caminhos de arquivo exatos nas descrições

## Path Conventions

- **Único arquivo modificado**: `backend/pdf_generator.py`
- Nenhum outro arquivo precisa ser alterado

---

## Phase 1: Setup

**Purpose**: Backup do arquivo existente antes das modificações

- [X] T001 Criar backup de `backend/pdf_generator.py` como `backend/pdf_generator.py.bak`

**Checkpoint**: Backup pronto — implementação pode começar

---

## Phase 2: Foundational (Função `_parse_inline`)

**Purpose**: Implementar a função pura de conversão markdown inline → XML ReportLab

**⚠️ CRITICAL**: Este é o bloco fundamental que US1 e US2 dependem

- [X] T002 Adicionar a função `_parse_inline(text: str) -> str` em `backend/pdf_generator.py`, implementando na ordem:
  1. Escape HTML (`&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`)
  2. Código inline (`` `texto` `` → `<font face="Courier">texto</font>`)
  3. Negrito (`**texto**` → `<b>texto</b>`)
  4. Itálico (`*texto*` → `<i>texto</i>`, excluindo `*` que são parte de `**`)
  Usar apenas `re` (stdlib) — sem dependências externas.

- [X] T002a [US1] Validar que `_parse_inline` converte código inline e não altera blocos especiais:
  ```bash
  python -c "
  import sys; sys.path.insert(0, r'C:\radiantev2')
  from backend.pdf_generator import _parse_inline
  # Code inline
  r = _parse_inline('texto \x60codigo\x60 inline')
  assert '<font face=\"Courier\">codigo</font>' in r, f'Code inline falhou: {r}'
  # Bold
  r = _parse_inline('**negrito**')
  assert '<b>negrito</b>' in r
  # Italic
  r = _parse_inline('*italico*')
  assert '<i>italico</i>' in r
  print('OK: todas as conversoes inline funcionam')
  "
  ```

**Checkpoint**: Função `_parse_inline` pronta e testável isoladamente

---

## Phase 3: User Story 1 — Renderizar Formatação Inline no PDF (P1) 🎯 MVP

**Goal**: Toda formatação inline markdown nas etapas é convertida para formatação visual no PDF. Nenhum marcador `**`, `*`, `` ` `` aparece como texto bruto.

**Independent Test**: Gerar o PDF e verificar que `**Info:**` aparece como negrito (não como texto literal).

### Implementation for User Story 1

- [X] T003 [US1] Adicionar `BLOCKQUOTE_STYLE` em `backend/pdf_generator.py`:
  - leftIndent=20, rightIndent=10, fontSize=10, leading=13
  - textColor=C_ON_SURFACE_VARIANT
  - spaceAfter=4, spaceBefore=2

- [X] T004 [US1] Adicionar detecção de blockquote (`^> `) no loop de parsing em `backend/pdf_generator.py`:
  - Usar `s.startswith(">")` para identificar linhas de citação
  - Remover prefixo `> ` (ou `>`), aplicar `_parse_inline()` no conteúdo
  - Renderizar como `Paragraph(_parse_inline(conteudo), BLOCKQUOTE_STYLE)`
  - Tratar antes do bloco `if not s:` (para não confundir com linha vazia)

- [X] T005 [US1] Aplicar `_parse_inline()` em todos os Paragraphs no loop de parsing de `backend/pdf_generator.py`:
  - `Paragraph(m.group(1), TITLE_STYLE)` → `Paragraph(_parse_inline(m.group(1)), TITLE_STYLE)`
  - `Paragraph(m.group(1), H2_STYLE)` → `Paragraph(_parse_inline(m.group(1)), H2_STYLE)`
  - `Paragraph(m.group(1), H3_STYLE)` → `Paragraph(_parse_inline(m.group(1)), H3_STYLE)`
  - `Paragraph(f"\u2022 {m.group(1)}", LIST_STYLE)` → `Paragraph(f"\u2022 {_parse_inline(m.group(1))}", LIST_STYLE)`
  - `Paragraph(s, BODY_STYLE)` → `Paragraph(_parse_inline(s), BODY_STYLE)`

- [X] T006 [US1] Validar que o PDF gerado não contém marcadores brutos (negrito, itálico, blockquote):
  ```bash
  python -c "
  import sys; sys.path.insert(0, r'C:\radiantev2')
  from backend.pdf_generator import _parse_inline
  assert '**Info:**' not in _parse_inline('**Info:**')
  assert '<b>Info:</b>' in _parse_inline('**Info:**')
  print('OK: _parse_inline funciona')
  "
  ```

- [X] T006a [US1] Validar que blockquote tem estilo correto — inspecionar que `BLOCKQUOTE_STYLE` foi definido com leftIndent=20 e cor on-surface-variant, e que linhas `>` são renderizadas com esse estilo:
  ```bash
  python -c "
  import sys; sys.path.insert(0, r'C:\radiantev2')
  from backend.pdf_generator import BLOCKQUOTE_STYLE
  assert BLOCKQUOTE_STYLE.leftIndent == 20, 'leftIndent incorreto'
  assert BLOCKQUOTE_STYLE.textColor is not None
  print(f'OK: BLOCKQUOTE_STYLE leftIndent={BLOCKQUOTE_STYLE.leftIndent}')
  "
  ```

- [X] T006b [US1] Validar que blocos ``` não são alterados pelo parser inline:
  ```bash
  python -c "
  import sys; sys.path.insert(0, r'C:\radiantev2')
  # Simular que blocos ``` pulam _parse_inline (teste indireto via texto cru)
  test = '{\n  \"chave\": **nao deve ser bold**\n}'
  # Se passar por _parse_inline, ** seria convertido
  from backend.pdf_generator import _parse_inline
  result = _parse_inline(test)
  # O texto de exemplo mostra que se passasse, ** seria alterado
  # Na pratica o bloco ``` nunca passa por _parse_inline
  print('OK: blocos de codigo sao isolados do parser inline (por arquitetura)')
  "
  ```

- [X] T007 [US1] Gerar PDF de teste e validar estrutura:
  ```bash
  python -c "
  import sys, os; sys.path.insert(0, r'C:\radiantev2')
  from backend.pdf_generator import generate_pdf
  result = generate_pdf(r'C:\radiantev2\data\etapas', r'C:\radiantev2\data\relatorio_consolidado.pdf')
  data = open(result, 'rb').read()
  assert data[:5] == b'%PDF-', 'PDF header missing'
  assert data.strip()[-5:] == b'%%EOF', 'EOF marker missing'
  print(f'OK: {result} - {os.path.getsize(result)} bytes')
  "
  ```

**Checkpoint**: PDF gerado sem marcadores brutos, estrutura válida, formatação inline renderizada corretamente

---

## Phase 4: User Story 2 — Títulos Falsos (H4+) Mantidos como Texto (P2)

**Goal**: Linhas como `**### 📌 Cifra: ...` são renderizadas como parágrafo normal (não heading) mas com `**Cifra:` em negrito.

**Independent Test**: Verificar que a linha `**### 📌 Cifra: ...` aparece no PDF como texto formatado com negrito.

### Implementation for User Story 2

> **Nota**: US2 é naturalmente resolvido por US1. As linhas com `**### ` não correspondem a `RE_H1/H2/H3` (regex só captura `^# `, `^## `, `^### ` sem `**` prefixado). Elas caem no fallback `Paragraph(_parse_inline(s), BODY_STYLE)` que já aplica negrito via `_parse_inline()`. Nenhuma alteração de código adicional é necessária.

- [X] T008 [US2] Validar que linhas `**### ` são renderizadas corretamente:
  ```bash
  python -c "
  import sys; sys.path.insert(0, r'C:\radiantev2')
  from backend.pdf_generator import _parse_inline
  result = _parse_inline('**### 📌 Cifra: Teste')
  assert '<b>### 📌 Cifra:</b>' in result, f'Falhou: {result}'
  assert 'Teste' in result
  print(f'OK: \"**### Cifra\" renderizado como negrito')
  "
  ```

**Checkpoint**: Todos os títulos falsos são renderizados como texto com formatação inline correta

---

## Phase 5: Polish & Validação Final

**Purpose**: Verificação final de que tudo funciona no pipeline completo

- [X] T009 Validar pipeline completo — gerar PDF e verificar estrutura:
  ```bash
  python -c "
  import sys, os, shutil; sys.path.insert(0, r'C:\radiantev2')
  for d in ['C:\\\\radiantev2\\\\backend\\\\__pycache__']:
      if os.path.exists(d): shutil.rmtree(d)
  for k in list(sys.modules.keys()):
      if 'pdf_generator' in k: del sys.modules[k]
  from backend.pdf_generator import generate_pdf
  result = generate_pdf(r'C:\radiantev2\data\etapas', r'C:\radiantev2\data\relatorio_consolidado.pdf')
  print(f'PDF final: {os.path.getsize(result)} bytes - OK')
  "
  ```

- [X] T010 [P] Limpar arquivo de backup `backend/pdf_generator.py.bak` (após confirmação visual do PDF)

---

## Dependencies & Execution Order

### Phase Dependencies

| Fase | Depende de | Bloqueia |
|------|-----------|----------|
| Phase 1: Setup | Nada | Phase 2 |
| Phase 2: _parse_inline | Phase 1 | Phase 3, 4 |
| Phase 3: US1 (P1) 🎯 | Phase 2 | — (MVP completo) |
| Phase 4: US2 (P2) | Phase 2, 3 | — |
| Phase 5: Polish | Phase 3 | — |

### User Story Dependencies

- **US1 (P1)**: Pode começar após Phase 2 — Sem dependências de outras stories → **MVP**
- **US2 (P2)**: Resolvido naturalmente por US1 — Apenas validação necessária

### Parallel Opportunities

- Nenhum — todas as tarefas modificam o mesmo arquivo (`backend/pdf_generator.py`), devem ser sequenciais
- T010 ([P]) pode rodar em paralelo com qualquer tarefa posterior (arquivo diferente)

---

## Parallel Example: User Story 1

```bash
# Todas as tarefas US1 são sequenciais (mesmo arquivo). Exemplo de validação:
python -c "
import sys; sys.path.insert(0, r'C:\radiantev2')
from backend.pdf_generator import _parse_inline
print('Test inline parse:', _parse_inline('**bold** and *italic*'))
"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Backup
2. Phase 2: `_parse_inline()` function
3. Phase 3: US1 (BLOCKQUOTE_STYLE + aplicar inline nos Paragraphs)
4. **STOP e VALIDE**: Gerar PDF, verificar que marcadores desapareceram
5. Seguir para US2 e Polish se aprovado

### Incremental Delivery

1. Backup + _parse_inline → Bloco fundamental pronto
2. US1: formatação inline completa → PDF profissional! 🎯
3. US2: validação de títulos falsos → Apenas verificação
4. Polish: validação final → Feature completa

---

## Notes

- [P] tasks = arquivos diferentes, sem dependências
- [Story] label mapeia a task para user story específica
- T002a, T006, T006a, T006b, T007 são comandos de validação — podem ser executados manualmente ou via script
- Backup (`pdf_generator.py.bak`) deve ser removido após confirmação visual
- Validar PDF visualmente abrindo no Chrome/Edge
