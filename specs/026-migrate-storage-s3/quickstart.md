# Quickstart: Validação da Migração S3

**Date**: 2026-06-30

## Pré-requisitos

- Backend rodando localmente (`python backend/app.py --mode web --port 8000`)
- Bucket S3 `radiante-final` acessível com as credenciais do `.env`
- AWS CLI configurada (opcional, para verificação manual)
- Um documento PDF de teste (ex: `teste.pdf`, < 1MB)

## Cenário 1: Upload de Documento

### Passos

1. Faça upload de um documento pelo frontend (ou via curl):
   ```bash
   curl -X POST http://localhost:8000/api/upload \
     -H "Content-Type: application/pdf" \
     -H "X-Filename: teste.pdf" \
     --data-binary @teste.pdf
   ```

2. Verifique que o arquivo **EXISTE** no S3:
   ```bash
   aws s3 ls s3://radiante-final/docs/teste.pdf
   ```

3. Verifique que o arquivo **NÃO EXISTE** localmente:
   ```bash
   # Não deve retornar nada:
   ls data/docs/teste.pdf 2>&1 || echo "OK - arquivo não existe localmente"
   ```

### Resultado Esperado

- Arquivo presente em `s3://radiante-final/docs/teste.pdf`
- Arquivo ausente em `data/docs/teste.pdf`

---

## Cenário 2: Pipeline de Análise 1x

### Passos

1. Faça upload de um documento (seguindo Cenário 1)

2. Inicie uma análise 1x:
   ```bash
   curl -X POST http://localhost:8000/api/run-once
   ```

3. Aguarde a conclusão (monitore `/api/status`)

4. Verifique os artefatos no S3:
   ```bash
   aws s3 ls s3://radiante-final/results/etapa1_completo.md
   aws s3 ls s3://radiante-final/results/etapa2_completo.md
   aws s3 ls s3://radiante-final/results/etapa3_completo.md
   aws s3 ls s3://radiante-final/results/etapa4_completo.md
   aws s3 ls s3://radiante-final/results/resultado_final.json
   aws s3 ls s3://radiante-final/results/relatorio_consolidado.pdf
   ```

5. Verifique que **NÃO** existem arquivos localmente:
   ```bash
   # Nenhum destes deve existir:
   ls data/etapas/ 2>&1
   ls data/resultado_final.json 2>&1
   ls data/relatorio_consolidado.pdf 2>&1
   ```

### Resultado Esperado

- 6 artefatos no S3 (`results/`)
- 0 artefatos locais em `data/`

---

## Cenário 3: Visualização de Resultados (Pós-reboot)

### Passos

1. Após completar o Cenário 2, **reinicie o servidor** (para limpar cache em memória)

2. Inicie o servidor novamente

3. Consulte o endpoint de resultados:
   ```bash
   curl http://localhost:8000/api/last-result
   ```

### Resultado Esperado

- Resposta JSON com os dados da análise (buscados do S3)
- Sem dependência de arquivos locais

---

## Cenário 4: Download do PDF

### Passos

1. Após completar o Cenário 2, acesse o link do PDF (geralmente `http://localhost:8000/data/relatorio_consolidado.pdf`)

2. Verifique se o PDF é servido corretamente:
   ```bash
   curl -o /tmp/testado.pdf http://localhost:8000/data/relatorio_consolidado.pdf
   file /tmp/testado.pdf
   # Deve retornar: "PDF document, version X.X"
   ```

### Resultado Esperado

- PDF válido baixado (sem erro 404)

---

## Cenário 5: Limpeza de Dados

### Passos

1. Faça upload e execute análises (Cenários 1+2)

2. Chame o endpoint de limpeza com SSE:
   ```bash
   curl -N "http://localhost:8000/api/clear-all?stream=true"
   ```

3. Verifique os eventos SSE recebidos:
   ```
   event: step
   data: {"step":"s3_docs","status":"processing","file":"docs/"}
   
   event: step
   data: {"step":"s3_docs","status":"done","deleted_count":N}
   
   event: step
   data: {"step":"s3_markdown","status":"processing","file":"markdown_docs/"}
   
   ... (s3_results, s3_runs, reset)
   
   event: complete
   data: {"status":"ok","message":"Sistema limpo com sucesso","s3_deleted":N}
   ```

4. **Verifique**: NÃO deve haver evento `step` com `"local"`.

5. Confirme que o S3 está vazio:
   ```bash
   aws s3 ls s3://radiante-final/docs/
   aws s3 ls s3://radiante-final/results/
   # Ambos devem retornar vazio
   ```

### Resultado Esperado

- Timeline SSE sem etapa "local"
- Bucket vazio após limpeza

---

## Cenário 6: Falha de S3 (Upload sem acesso)

### Passos

1. Temporariamente, revogue permissões S3 ou aponte para um bucket inválido

2. Tente fazer upload:
   ```bash
   curl -X POST http://localhost:8000/api/upload \
     -H "Content-Type: application/pdf" \
     -H "X-Filename: teste.pdf" \
     --data-binary @teste.pdf
   ```

### Resultado Esperado

- Resposta HTTP 503 (ou erro 500)
- Mensagem de erro clara sobre S3 indisponível
- **NENHUM** arquivo criado localmente como fallback

---

## Validação Automatizada (Opcional)

Para validação via script:

```bash
# Script de validação rápida
echo "=== Validação Migração S3 ==="

echo "1. Upload direto para S3..."
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/upload \
  -H "Content-Type: application/pdf" -H "X-Filename: validation.pdf" --data-binary @teste.pdf

echo ""
echo "2. Verificando S3..."
aws s3 ls s3://radiante-final/docs/validation.pdf && echo "  [OK] Existe no S3"

echo "3. Verificando local..."
ls data/docs/validation.pdf 2>&1 || echo "  [OK] Não existe localmente"

echo "4. Verificando endpoint /data/..."
curl -o /dev/null -s -w "%{http_code}" http://localhost:8000/data/relatorio_consolidado.pdf

echo ""
echo "=== Fim ==="
```

## Referências

- [Estrutura de Prefixos S3](contracts/s3-prefix-structure.md)
- [Mudanças na API HTTP](contracts/api-changes.md)
- [Data Model](data-model.md)
