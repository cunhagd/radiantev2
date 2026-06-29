# Quickstart: Limpeza Completa do Sistema

## Pre-requisitos

- Servidor rodando (`python backend/app.py` ou `docker compose up`)
- Frontend acessivel em `http://localhost:8000`
- (Opcional) Bucket S3 `radiante-final` acessivel com permissao de delete

## Cenarios de Validacao

### Cenario 1: Limpeza pos-analise (US1)

1. Faca upload de 1 documento PDF pelo frontend
2. Execute uma analise (1x ou 10x)
3. Aguarde a conclusao e confirmacao visual dos resultados
4. Clique no botao lixeira
5. Confirme no modal
6. **Resultado esperado**:
   - `data/` vazio (exceto estrutura `docs/` e `markdown_docs/` vazias)
   - S3 sem objetos sob `docs/`, `markdown_docs/`, `results/`, `runs/`
   - `ANALYSIS_JOBS` com `status: "idle"` e `last_result: None`
   - `Progress.get()` retorna estado inicial
   - `get_execution_history()` retorna `[]`
   - Frontend limpo com botoes habilitados

### Cenario 2: Limpeza sem dados (US3)

1. Abra o sistema pela primeira vez (sem nenhuma analise)
2. Clique no botao lixeira
3. Confirme no modal
4. **Resultado esperado**: Sistema permanece em estado inicial, sem erros

### Cenario 3: Verificacao via API direta

```bash
# Apos executar uma analise:
curl -s http://localhost:8000/api/status | python -m json.tool

# Executar limpeza:
curl -s -X POST http://localhost:8000/api/clear-all | python -m json.tool
# Resposta esperada: {"status": "ok", "message": "Sistema limpo com sucesso", "s3_deleted": N}

# Verificar que esta limpo:
curl -s http://localhost:8000/api/status | python -m json.tool
# {"status": "idle", "message": "", "error_details": "", "last_result": null}
```

### Cenario 4: Tolerancia a falha S3

1. Desconecte a internet ou revogue credenciais AWS
2. Execute uma analise
3. Clique no botao lixeira
4. **Resultado esperado**: Limpeza dos locais acessiveis ocorre mesmo com S3 indisponivel
5. Verificar: `data/` esta limpo, memoria resetada, frontend limpo

## Comandos de Verificacao

```bash
# Verificar diretorio local
ls -la data/docs/ data/markdown_docs/

# Verificar S3 (se credenciais ativas)
aws s3 ls s3://radiante-final/docs/ --summarize
aws s3 ls s3://radiante-final/results/ --summarize

# Verificar estado via API
curl -s http://localhost:8000/api/status
```
