# Research: SSE com SimpleHTTPRequestHandler e Timeline de Limpeza

## 1. SSE (Server-Sent Events) com http.server.SimpleHTTPRequestHandler

### Decisão: SSE via query parameter `?stream=true` com resposta manual

**Rationale**: O `SimpleHTTPRequestHandler` do Python padrão suporta SSE sem frameworks, desde que a resposta seja configurada manualmente. O handler precisa:
1. Definir `Content-Type: text/event-stream`
2. Definir `Cache-Control: no-cache`
3. Definir `Connection: keep-alive`
4. Chamar `self.send_response(200)` antes de enviar os cabeçalhos
5. Escrever eventos no formato `data: {json}\n\n` e chamar `self.wfile.flush()`

**Detalhe técnico**: O `Content-Length` não é enviado (streaming). O navegador mantém a conexão aberta e lê os eventos conforme chegam.

### Modos de operação

- **Modo streaming**: `/api/clear-all?stream=true` → retorna SSE com eventos de progresso
- **Modo legado**: `/api/clear-all` sem parâmetro → comportamento atual (resposta JSON única ao final)

### Formato dos eventos SSE

```
event: step
data: {"step":"local","status":"processing","file":"data/docs/"}

event: step
data: {"step":"local","status":"done","file":null}

event: step
data: {"step":"s3_docs","status":"processing","file":"docs/"}

event: step
data: {"step":"s3_docs","status":"done","file":null,\"deleted_count\":5}

event: step
data: {"step":"s3_markdown","status":"processing","file":"markdown_docs/"}

event: step
data: {"step":"s3_markdown","status":"done","file":null,\"deleted_count\":3}

event: step
data: {"step":"s3_results","status":"processing","file":"results/"}

event: step
data: {"step":"s3_results","status":"done","file":null,\"deleted_count\":2}

event: step
data: {"step":"s3_runs","status":"processing","file":"runs/"}

event: step
data: {"step":"s3_runs","status":"done","file":null,\"deleted_count\":1}

event: step
data: {"step":"reset","status":"processing","file":null}

event: step
data: {"step":"reset","status":"done","file":null}

event: complete
data: {"status":"ok","message":"Sistema limpo com sucesso"}
```

### Evento de erro

```
event: step
data: {"step":"s3_docs","status":"error","file":"docs/","error":"Falha ao limpar S3: ..."}

event: complete
data: {"status":"error","message":"Sistema limpo com erros parciais.","errors":["Falha ao limpar S3: ..."]}
```

### Implementação no handler

```python
def _handle_clear(self) -> None:
    # Verifica se é streaming
    is_stream = "stream=true" in self.path
    
    if is_stream:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        def send_sse(event_type, data_dict):
            line = f"event: {event_type}\ndata: {json.dumps(data_dict, ensure_ascii=False)}\n\n"
            self.wfile.write(line.encode("utf-8"))
            self.wfile.flush()
        
        # ... etapas com send_sse() ...
    else:
        # Comportamento original (JSON único)
        ...
```

## 2. Consumo SSE no Frontend

### Decisão: Usar Fetch API com leitura de stream (`response.body.getReader()`)

**Rationale**: `EventSource` nativo do navegador funciona apenas para GET, não POST. Como o endpoint de limpeza já é POST, usaremos Fetch API com `ReadableStream` Reader para processar o stream.

**Alternativas consideradas**: 
- `EventSource` com GET — exigiria modificar o endpoint para GET, o que quebraria a interface atual
- XMLHttpRequest com `onprogress` — API legada, Fetch é mais moderna e adequada

### Implementação no frontend

```javascript
async function consumeClearStream() {
  const response = await fetch(API.BASE + '/api/clear-all?stream=true', { method: 'POST' });
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    
    // Parse SSE events from buffer
    const lines = buffer.split('\n');
    buffer = lines.pop() || ''; // Keep incomplete line in buffer
    
    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        handleEvent(currentEvent, data);
      }
    }
  }
}
```

## 3. Timeline de Limpeza — Reutilização vs Nova Construção

### Decisão: Reutilizar a estrutura visual existente de `m3-step` / `m3-substep` com conteúdo customizado

**Rationale**: O sistema de classes CSS `m3-step`, `m3-step-dot`, `m3-step-line`, `m3-step-label`, `m3-step-badge` já está definido e funcional. A timeline de limpeza usará exatamente os mesmos padrões visuais, apenas com labels e badges diferentes.

**Como funciona**:
- A função `Loading.runClear()` será similar a `Loading.runAnalysis()` mas:
  - Não faz POST para `/api/run-once` nem `/api/run-ten`
  - Em vez de polling `/api/progress`, consome o SSE de `/api/clear-all?stream=true`
  - A timeline tem steps fixos (6 etapas de limpeza) em vez de 4 etapas de análise
  - Não há substeps (substeps são específicos da etapa 3 das análises)
  - Usa `setStep()` e `buildTimelineHTML()` (ou uma nova `buildClearTimelineHTML()`)

## 4. Etapas de Limpeza

| Step | ID | Label | Ação no backend |
|---|---|---|---|
| 1 | `local` | "Limpando dados locais" | Remove arquivos/diretórios em `data/` |
| 2 | `s3_docs` | "Limpando S3 (docs)" | Deleta `docs/` do bucket |
| 3 | `s3_markdown` | "Limpando S3 (markdown_docs)" | Deleta `markdown_docs/` do bucket |
| 4 | `s3_results` | "Limpando S3 (results)" | Deleta `results/` do bucket |
| 5 | `s3_runs` | "Limpando S3 (runs)" | Deleta `runs/` do bucket |
| 6 | `reset` | "Resetando estado do sistema" | Reseta memória, progresso e histórico |

## 5. Alternativas de Arquitetura

### Abordagem via `/api/progress` (polling)

Rejeitada porque:
- A classe `Progress` existente foi projetada para o pipeline de análise, não para operações de limpeza
- Adicionar estado de limpeza ao `Progress` poluiria a abstração
- A operação de limpeza é curta (segundos), SSE é mais adequado que polling com intervalo fixo

### Abordagem WebSocket

Rejeitada porque:
- `SimpleHTTPRequestHandler` não suporta WebSocket nativamente
- SSE é suficiente para comunicação unidirecional (servidor → cliente)

## 6. Comportamento de Erro

- Se uma etapa falha, o SSE envia `"status": "error"` com campo `error` descritivo
- Se o frontend detecta erro, a timeline exibe a etapa em vermelho e fecha o overlay após 3 segundos
- Erro de conexão (fetch falha): frontend exibe mensagem e fecha overlay imediatamente
