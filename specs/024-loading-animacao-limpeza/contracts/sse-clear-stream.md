# Contrato: SSE Clear Progress Stream

## Identificador

`sse-clear-stream`

## Descrição

Contrato de comunicação entre backend (`/api/clear-all`) e frontend para transmissão de progresso em tempo real da operação de limpeza de dados.

## Endpoint

```
POST /api/clear-all?stream=true

Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

## Formato do Stream

Cada mensagem segue o formato SSE padrão:

```
event: {tipo_evento}
data: {json_payload}

```

### Tipo: `step`

Evento de progresso de uma etapa individual.

**Payload**:

```typescript
{
  "step": string,          // "local" | "s3_docs" | "s3_markdown" | "s3_results" | "s3_runs" | "reset"
  "status": string,        // "processing" | "done" | "error"
  "file": string | null,   // Nome do arquivo/diretório (ex.: "docs/", "etapa1.md")
  "error": string | null,  // Apenas se status === "error"
  "deleted_count": int | null  // Apenas se status === "done" para etapas S3
}
```

### Tipo: `complete`

Evento final da operação.

**Payload**:

```typescript
{
  "status": string,         // "ok" | "partial" | "error"
  "message": string,
  "errors": string[] | null, // Presente se status === "partial" ou "error"
  "s3_deleted": int | null
}
```

## Sequência Esperada

```
event: step
data: {"step":"local","status":"processing","file":"data/docs/"}

event: step
data: {"step":"local","status":"done","file":null}

event: step
data: {"step":"s3_docs","status":"processing","file":"docs/"}

event: step
data: {"step":"s3_docs","status":"done","file":null,"deleted_count":5}

event: step
data: {"step":"s3_markdown","status":"processing","file":"markdown_docs/"}

event: step
data: {"step":"s3_markdown","status":"done","file":null,"deleted_count":3}

event: step
data: {"step":"s3_results","status":"processing","file":"results/"}

event: step
data: {"step":"s3_results","status":"done","file":null,"deleted_count":2}

event: step
data: {"step":"s3_runs","status":"processing","file":"runs/"}

event: step
data: {"step":"s3_runs","status":"done","file":null,"deleted_count":1}

event: step
data: {"step":"reset","status":"processing","file":null}

event: step
data: {"step":"reset","status":"done","file":null}

event: complete
data: {"status":"ok","message":"Sistema limpo com sucesso","s3_deleted":11}
```

## Contrato de Erro

### Erro no meio do stream

```json
// Step com erro
event: step
data: {"step":"s3_docs","status":"error","file":"docs/","error":"Falha ao limpar S3: AccessDenied"}

// Continua para próxima etapa mesmo com erro

// Final
event: complete
data: {"status":"partial","message":"Sistema limpo com erros parciais.","errors":["Falha ao limpar S3: AccessDenied"],"s3_deleted":0}
```

### Erro de análise em andamento (sem stream)

```json
// Resposta HTTP 409
{"status":"error","message":"Nao e possivel limpar durante uma analise em andamento."}
```

## Comportamento do Cliente (Frontend)

1. Fazer POST para `/api/clear-all?stream=true`
2. Se resposta HTTP 409: exibir alerta e não abrir overlay
3. Se resposta HTTP 200: iniciar leitura do stream
4. Para cada `event: step` com `status: "processing"`: atualizar o step correspondente na timeline com badge "Limpando..."
5. Para cada `event: step` com `status: "done"`: marcar step como concluído
6. Para cada `event: step` com `status: "error"`: marcar step em vermelho
7. Ao receber `event: complete`: 
   - Se `status: "ok"`: fechar overlay em 500ms, limpar dados da tela
   - Se `status: "partial"` ou `"error"`: manter overlay por 3s, exibir mensagem de erro, fechar

## Compatibilidade Retroativa

A requisição sem o parâmetro `?stream=true` mantém o comportamento atual (resposta JSON única).
