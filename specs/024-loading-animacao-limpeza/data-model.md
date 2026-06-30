# Data Model: Loading Animação para Limpeza

## Visão Geral

Esta feature introduz modelos de dados para comunicação de progresso da operação de limpeza via SSE. Não há persistência de dados — os modelos representam mensagens temporárias entre backend e frontend.

---

## Evento SSE de Progresso

Mensagem enviada pelo backend ao frontend durante a execução do `clear-all`.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `step` | `string` | Sim | Identificador único da etapa (ex.: `local`, `s3_docs`, `s3_markdown`, `s3_results`, `s3_runs`, `reset`) |
| `status` | `enum` | Sim | Estado da etapa: `processing`, `done`, `error` |
| `file` | `string \| null` | Não | Nome do arquivo/diretório sendo processado (ex.: `"docs/"`, `"etapa1.md"`). `null` quando não aplicável. |
| `error` | `string \| null` | Não | Mensagem de erro descritiva. Presente apenas se `status === "error"`. |
| `deleted_count` | `int \| null` | Não | Número de arquivos deletados na etapa (apenas em `status === "done"` para etapas S3). |

**Enum `status`**: `"processing"` | `"done"` | `"error"`

### Exemplos

```json
// Etapa iniciando
{"step":"local","status":"processing","file":"data/docs/"}

// Etapa concluída
{"step":"local","status":"done","file":null}

// Etapa com erro
{"step":"s3_docs","status":"error","file":"docs/","error":"Falha ao limpar S3: AccessDenied"}

// Etapa S3 concluída com contagem
{"step":"s3_docs","status":"done","file":null,"deleted_count":5}
```

---

## Tipos de Evento SSE (event envelope)

O stream SSE utiliza dois tipos de evento no envelope `event:`.

### `event: step`

Evento de progresso de uma etapa individual.

| Campo | Tipo | Descrição |
|---|---|---|
| `step` | `string` | Ver tabela acima |
| `status` | `string` | `processing`, `done` ou `error` |
| `file` | `string\|null` | Arquivo/diretório sendo processado |
| `error` | `string\|null` | Mensagem de erro |
| `deleted_count` | `int\|null` | Contagem de exclusões |

### `event: complete`

Evento final indicando conclusão de toda a operação.

| Campo | Tipo | Descrição |
|---|---|---|
| `status` | `string` | `"ok"` (sucesso total), `"partial"` (erros parciais), ou `"error"` (falha total) |
| `message` | `string` | Mensagem descritiva |
| `errors` | `string[]\|null` | Lista de erros (presente se `status === "partial"` ou `"error"`) |
| `s3_deleted` | `int\|null` | Total de itens deletados do S3 |

---

## Estados da Timeline no Frontend

Cada step na timeline do frontend possui estado local:

| Estado | Badge | Classe CSS | Descrição |
|---|---|---|---|
| `pending` | "Aguardando" | `.m3-step` (default) | Etapa ainda não iniciada |
| `active` | "Limpando..." | `.m3-step.is-active` | Etapa em processamento |
| `done` | "Concluído" | `.m3-step.is-done` | Etapa concluída com sucesso |
| `error` | "Falhou" | `.m3-step.is-error` | Etapa concluída com erro |

### Transições de estado

```
pending → active → done
                  → error
```

**Regras**:
- A transição `pending → active` define qual arquivo está sendo limpo (badge mostra o nome)
- A transição `active → done` marca a etapa como concluída e avança para a próxima
- A transição `active → error` mantém a etapa com destaque vermelho
- O estado `error` não impede a execução das etapas seguintes (erro parcial)

---

## Fluxo de Dados

```
Usuário clica "Limpar tudo"
         │
         ▼
  Modal de confirmação
         │
         └── Confirma → Fecha modal
                        │
                        ▼
              Frontend: exibe loading overlay
              com timeline de 6 etapas (pending)
                        │
                        ▼
              POST /api/clear-all?stream=true
                        │
                        ▼
              Backend: inicia SSE stream
              ├── event: step "local"      → processing → done
              ├── event: step "s3_docs"    → processing → done
              ├── event: step "s3_markdown" → processing → done
              ├── event: step "s3_results" → processing → done
              ├── event: step "s3_runs"    → processing → done
              ├── event: step "reset"      → processing → done
              └── event: complete          → status: ok/error
                        │
                        ▼
              Frontend: timeline atualizada
              ├── Todas done → 0.5s → fecha overlay + limpa tela
              └── Alguma error → 3s → fecha overlay + exibe msg
```
