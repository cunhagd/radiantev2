# Implementation Plan: Correcao de Consistencia de PDFs e JSONs

**Branch**: `013-fix-pdf-consistency` | **Date**: 2026-06-29 | **Spec**: `specs/013-fix-pdf-consistency/spec.md`

**Input**: Feature specification from `specs/013-fix-pdf-consistency/spec.md`

## Summary

Corrigir bugs de servicao de PDFs/JSONs estaticos na pasta `data/`, garantir limpeza cruzada de artefatos antigos ao alternar entre modos 1x e 10x, e adicionar `pdf_filename` ao endpoint `/api/last-result` para que o frontend nao dependa de heuristica para determinar qual PDF baixar.

## Technical Context

**Language/Version**: Python 3.14, JavaScript Vanilla (ES5/6)

**Primary Dependencies**: Nenhuma nova — apenas `http.server`, `pathlib`, manipulacao de arquivos nativa

**Storage**: Sistema de arquivos local (`data/`) como fonte primaria; S3 (`radiante-final`) como fallback

**Testing**: Vitest + Happy-DOM (frontend), pytest (backend — testes existentes)

**Target Platform**: Browser (Chrome, Firefox, Edge) + servidor local Python

**Performance Goals**: PDF servido em <100ms; limpeza de arquivos em <10ms

**Constraints**:
- Nao adicionar novas dependencias (Constitution Stack)
- Manter compatibilidade com SimpleHTTPRequestHandler (Constitution I)
- Arquivos .md e diretorios (docs/, markdown_docs/) NAO devem ser afetados

**NEEDS CLARIFICATION**: Nenhum — todos os detalhes estao claros na spec.

## Constitution Check

*GATE: Passed. A correcao nao viola nenhum principio da Constitution: usa apenas manipulacao nativa de arquivos e paths (Principio I), nao adiciona dependencias novas (Stack), e o frontend continua sem frameworks/bundlers (Principio V).*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK** (Principio I): ✅ Correcao usa apenas `SimpleHTTPRequestHandler` e `pathlib` — zero frameworks.

2. **GATE-CREDENCIAIS** (Principio II): ✅ Nao mexe em credenciais AWS.

3. **GATE-PIPELINE** (Principio III): ✅ Nao altera o pipeline de 4 etapas.

4. **GATE-CEGUEIRA** (Principio III — Regras 1, 14): ✅ Nao mexe em regras de negocio.

5. **GATE-CPC25** (Principio III): ✅ Nao mexe em classificacao de risco.

6. **GATE-S3-BUCKET** (Principio IV): ✅ Apenas ajusta limpeza de prefixos existentes.

7. **GATE-EXTRACAO** (Principio IV): ✅ Nao mexe em extracao.

8. **GATE-FRONTEND** (Principio V): ✅ Frontend continua sem frameworks/bundlers.

9. **GATE-DEPENDENCIAS** (Stack): ✅ Nenhuma nova dependencia.

10. **GATE-DEPLOY** (Infraestrutura): ✅ Nao mexe em deploy.

## Project Structure

### Source Code (repository root)

```text
backend/
├── app.py              # Rota /data/, /api/last-result com pdf_filename
└── pipeline.py         # Limpeza cruzada de PDFs e JSONs em run_once e run_ten_times

frontend/
├── index.html           # Usar pdf_filename da API em vez de heuristica
└── tests/
    └── loading.test.js  # Testes atualizados
```

## Phases

### Phase 0: Outline & Research — N/A

Nao ha duvidas tecnicas — os bugs e correcoes necessarias estao claramente identificados:

1. **Bug `/data/` rota**: `self.path.lstrip("/")` deve usar `path` (limpo) em vez de `self.path` para evitar que query strings contaminem o caminho do arquivo.

2. **Limpeza cruzada incompleta**: Em `run_once`, remover apenas `relatorio_consolidado_10x.pdf` mas nao `consolidado_10x.json`. Em `run_ten_times`, remover apenas `relatorio_consolidado.pdf` mas nao `resultado_final.json`.

3. **Falta `pdf_filename`**: Adicionar campo ao `last_result` salvo em memoria em `app.py`, e ao JSON salvo em disco em `pipeline.py`.

4. **Frontend heuristico**: Substituir `isTenMode` por leitura direta de `pdf_filename` do `last-result`.

5. **S3**: Upload de novos arquivos para S3 deve remover artefatos do modo oposto primeiro.

### Phase 1: Design & Contracts

#### Data Model

**`/api/last-result` response** (estendido):
```json
{
  "numero_processo": "...",
  "autor": "...",
  "cifras": [...],
  "valor_total_estimado": "...",
  "pdf_filename": "relatorio_consolidado.pdf"
}
```

**Arquivos gerenciados**:

| Modo | PDF gerado | JSON gerado | Artefato oposto a remover |
|------|-----------|-------------|--------------------------|
| 1x | `relatorio_consolidado.pdf` | `resultado_final.json` | `relatorio_consolidado_10x.pdf` + `consolidado_10x.json` |
| 10x | `relatorio_consolidado_10x.pdf` | `consolidado_10x.json` | `relatorio_consolidado.pdf` + `resultado_final.json` |

#### Funcao auxiliar: `clean_artefatos_anteriores(mode: str)`

Centralizar a logica de limpeza em uma funcao reutilizavel:

```python
def clean_artefatos_anteriores(mode: str) -> None:
    """
    Remove artefatos (PDFs e JSONs) do modo oposto antes de gerar novos.
    mode: 'once' ou 'ten'
    """
    pdfs_to_remove = ["relatorio_consolidado_10x.pdf"] if mode == "once" else ["relatorio_consolidado.pdf"]
    jsons_to_remove = ["consolidado_10x.json"] if mode == "once" else ["resultado_final.json"]
    
    for fname in pdfs_to_remove + jsons_to_remove:
        fpath = ROOT_DIR / "data" / fname
        if fpath.exists():
            fpath.unlink()
```

#### Artefatos

1. **data-model.md** — Documentar schema estendido de `/api/last-result`
2. **contracts/api-last-result.md** — Contrato formal do endpoint
3. **quickstart.md** — Roteiro de validacao dos 4 cenarios

## Complexity Tracking

Nenhuma violacao da Constitution. Feature de baixa complexidade (correcao de bugs).

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Nenhuma | — | — |
