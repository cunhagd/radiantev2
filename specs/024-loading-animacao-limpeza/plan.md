# Implementation Plan: Loading Animação para Limpeza

**Branch**: `` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/024-loading-animacao-limpeza/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command.

## Summary

Substituir o atual feedback textual do botão "Limpar tudo" por um overlay de loading com timeline interativa no mesmo padrão visual das análises 1x/10x. O backend passará a emitir eventos SSE (Server-Sent Events) de progresso durante a limpeza, e o frontend consumirá esses eventos para atualizar uma timeline com 6 etapas, cada uma exibindo status (Aguardando/Processando/Concluído/Erro) e nomes dos arquivos sendo limpos.

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript Vanilla ES6 (frontend)

**Primary Dependencies**: Nenhuma nova dependência. `http.server` nativo no backend. Fetch API / EventSource no frontend.

**Storage**: Sistema de arquivos local (`data/`) + bucket S3 `radiante-final`

**Testing**: Validação manual com inspeção visual do overlay de loading e verificação dos eventos SSE no console do navegador

**Target Platform**: Navegadores modernos (Chrome, Firefox, Edge) — desktop

**Project Type**: Web application (backend nativo Python + frontend HTML/CSS/JS)

**Performance Goals**: Overlay aparece em < 200ms após confirmação. Transições entre etapas ocorrem sem travamentos perceptíveis.

**Constraints**: Backend usa exclusivamente `http.server.SimpleHTTPRequestHandler` — sem frameworks. Frontend sem bundlers ou frameworks JS. A implementação SSE deve usar `self.wfile.write()` + `self.wfile.flush()` com `Content-Type: text/event-stream`.

**Scale/Scope**: Única operação de limpeza por vez. Número de arquivos no bucket S3 pode variar de 0 a ~50.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: O backend utiliza exclusivamente `http.server.SimpleHTTPRequestHandler`? NENHUM framework web externo foi introduzido? — ✅ **PASS**. SSE será implementado via `self.wfile.write()` + `self.wfile.flush()` no handler nativo.
2. **GATE-CREDENCIAIS**: As credenciais AWS são lidas do `.env` via `python-dotenv`, passadas explicitamente nos clientes boto3 e removidas do `os.environ`? — ✅ **PASS**. A feature não altera o fluxo de credenciais.
3. **GATE-PIPELINE**: O pipeline segue exatamente 4 etapas encadeadas? — ✅ **PASS**. A feature não modifica o pipeline de análise.
4. **GATE-CEGUEIRA**: A Etapa 2 recalcula valores do zero sem copiar cifras da petição? — ✅ **PASS**. Não afeta o pipeline.
5. **GATE-CPC25**: A Etapa 3 classifica risco como Provável >50%, Possível 25-50%, Remota <25%? — ✅ **PASS**. Não afeta o pipeline.
6. **GATE-S3-BUCKET**: Bucket `radiante-final` com prefixos definidos? — ✅ **PASS**. A limpeza S3 respeita os mesmos prefixos.
7. **GATE-EXTRACAO**: PDF usa PyMuPDF com fallback Textract? — ✅ **PASS**. Não afeta extração.
8. **GATE-FRONTEND**: Frontend é arquivo único `frontend/index.html` sem bundlers ou frameworks JS? Usa polling a cada 3s? — ✅ **PASS**. O frontend permanece em JS Vanilla. O loading da limpeza usará EventSource/streaming em vez de polling.
9. **GATE-DEPENDENCIAS**: Nenhuma dependência além de `boto3`, `pymupdf`, `openai`, `python-dotenv`, `reportlab` sem justificativa? — ✅ **PASS**. Nenhuma nova dependência é introduzida.
10. **GATE-DEPLOY**: CI/CD via GitHub Actions com rsync + SSH para EC2 na branch `main-poc`? — ✅ **PASS**. Não afeta deploy.

**Resultado**: TODOS os 10 gates aprovados. Nenhuma violação.

## Project Structure

### Documentation (this feature)

```text
specs/024-loading-animacao-limpeza/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── sse-clear-stream.md
└── tasks.md             # Phase 2 output (NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── app.py              # SSE progresso na limpeza (MODIFICADO)

frontend/
├── index.html          # Ajustes mínimos (MODIFICADO)
├── js/
│   ├── ui.js           # confirmClearAll chama loading (MODIFICADO)
│   └── loading.js      # Nova função runClear() + timeline (MODIFICADO)
├── css/
│   ├── components.css  # CSS para step de erro (MODIFICADO, opcional)
│   └── animations.css  # Animações se necessário (MODIFICADO, opcional)
```

**Structure Decision**: A estrutura existente é mantida integralmente. Apenas adições e modificações pontuais em arquivos existentes.

## Complexity Tracking

Nenhuma violação de gates. Não aplicável.
