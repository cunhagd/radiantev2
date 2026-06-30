# Quickstart: Loading Animação para Limpeza

## Pré-requisitos

- Servidor backend rodando: `python backend/app.py --port 8000`
- Navegador aberto em `http://localhost:8000`
- Pelo menos 1 documento enviado (para haver dados a limpar)

## Cenários de Validação

### Cenário 1: Limpeza com dados locais e S3

**Setup**:
1. Envie 1-2 documentos PDF via upload
2. Execute análise 1x (botão "1x") e aguarde conclusão
3. Dados aparecem na tela (metadados, cifras)

**Execução**:
1. Clique no botão lixeira (limpar)
2. Modal de confirmação aparece
3. Clique "Limpar tudo"

**Resultado esperado**:
- Modal fecha
- Overlay de loading aparece com título "Limpando dados..."
- Cronômetro inicia em `00:00`
- Timeline mostra 6 etapas, sequencialmente:
  1. "Limpando dados locais" → dot verde (Concluído)
  2. "Limpando S3 (docs)" → dot verde (Concluído)
  3. "Limpando S3 (markdown_docs)" → dot verde (Concluído)
  4. "Limpando S3 (results)" → dot verde (Concluído)
  5. "Limpando S3 (runs)" → dot verde (Concluído)
  6. "Resetando estado do sistema" → dot verde (Concluído)
- Overlay fecha automaticamente
- Tela mostra "Nenhum dado. Inicie uma análise."
- Apenas botão Upload habilitado

### Cenário 2: Limpeza rápida (sem dados)

**Setup**: Estado inicial da aplicação (sem uploads)

**Execução**:
1. Clique no botão lixeira
2. Modal aparece → Clique "Limpar tudo"

**Resultado esperado**:
- Overlay aparece, mas as transições são muito rápidas (< 1s total)
- Cada etapa deve permanecer visível por no mínimo 300ms para dar tempo de percepção
- Overlay fecha
- Estado permanece "initial"

### Cenário 3: Cancelamento da limpeza

**Setup**: Dados carregados na tela

**Execução**:
1. Clique no botão lixeira
2. Modal aparece → Clique "Cancelar"

**Resultado esperado**:
- Modal fecha
- Nenhum overlay de loading aparece
- Dados permanecem na tela

### Cenário 4: Verificação do stream SSE (Console)

**Setup**: Abrir DevTools (F12) → Console

**Execução**:
1. Execute limpeza (Cenário 1)

**Resultado esperado**:
- Logs no console mostram: `[CLEAR] Step local: processing (data/docs/)`
- `[CLEAR] Step local: done`
- `[CLEAR] Step s3_docs: processing (docs/)`
- ... etc
- `[CLEAR] Complete: Sistema limpo com sucesso`

### Cenário 5: Erro parcial (simulado)

**Setup**: Para testar, pode-se editar um prefixo S3 inválido no `app.py` temporariamente

**Execução**:
1. Execute limpeza

**Resultado esperado**:
- Etapa com erro aparece com dot vermelho e badge "Falhou"
- Demais etapas progridem normalmente
- Ao final, overlay fecha após ~3s
- Mensagem de erro aparece no console

## Depuração

- **Stream não aparece**: Verificar se `?stream=true` está na URL da requisição no Network tab
- **Overlay não fecha**: Verificar se `clearAllFrontendData()` está sendo chamada corretamente
- **SSE não parseia**: Verificar no console se o formato `data: {...}\n\n` está correto (especialmente quebras de linha)
- **Etapa trava em "processing"**: Backend não está chamando `send_sse()` ou `wfile.flush()` não está sendo executado

## Comandos úteis

```bash
# Iniciar servidor
python backend/app.py --port 8000

# Verificar logs do backend (mostram etapas de limpeza)
python backend/app.py --port 8000 --verbose

# Testar SSE manualmente via curl
curl -X POST "http://localhost:8000/api/clear-all?stream=true" -N
```

## Referências

- Contrato SSE: [contracts/sse-clear-stream.md](contracts/sse-clear-stream.md)
- Data Model: [data-model.md](data-model.md)
- Especificação: [spec.md](spec.md)
