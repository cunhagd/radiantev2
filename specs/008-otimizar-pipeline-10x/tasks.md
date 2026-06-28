# Tasks: 008-otimizar-pipeline-10x

## Task 1: Criar funcao run_ten_times_optimized em pipeline.py

**Arquivo**: `backend/pipeline.py`

**Descricao**: Criar nova funcao que implementa o fluxo otimizado:
1. Executa etapa 1 (metadados) uma vez
2. Executa etapa 2 (cifras) uma vez usando resultado da etapa 1
3. Executa etapa 3 (probabilidade) 10x em paralelo (max_workers=5), todas usando o MESMO resultado fixo da etapa 2
4. Executa etapa 4 (consolidacao) uma vez usando os 10 resultados da etapa 3
5. Salva stages no S3, gera auditoria, gera PDF (mesma logica da funcao original)

**Detalhes**:
- Usar `run_llm_stage_streaming()` para cada etapa individualmente (reutilizar funcao existente)
- Usar `ThreadPoolExecutor` com `max_workers=5` para as 10 repeticoes da etapa 3
- Usar `merge_metrics()` para consolidar metricas de todas as etapas
- Usar `save_stage_files()` e `save_audit_log()` da mesma forma que a funcao original
- Remover a funcao `run_ten_times()` antiga (ou substituir seu conteudo)

**Criterios de aceite**:
- Etapa 1 roda 1 vez (verificar logs)
- Etapa 2 roda 1 vez usando output da etapa 1
- Etapa 3 roda 10 vezes, cada uma usando o mesmo `etapa2_raw`
- Etapa 4 roda 1 vez
- Em caso de falha na etapa 1 ou 2, o pipeline aborta com erro
- Se algumas repeticoes da etapa 3 falharem, as bem-sucedidas sao consolidadas

---

## Task 2: Atualizar app.py para usar nova funcao

**Arquivo**: `backend/app.py`

**Descricao**: O endpoint `POST /api/run-10x` (ou similar) deve chamar `run_ten_times_optimized()` em vez da funcao antiga.

**Detalhes**:
- Encontrar onde `run_ten_times()` e chamado e substituir por `run_ten_times_optimized()`
- Garantir que os parametros de entrada sejam os mesmos

---

## Task 3: Atualizar testes

**Arquivo**: `backend/tests/test_pipeline.py` e `backend/tests/test_integration.py`

**Descricao**: Atualizar os testes de integracao que mockam o pipeline 10x para usar a nova funcao.

**Detalhes**:
- `test_run_ten_times_integration` em `test_integration.py` deve mockar a nova funcao
- Verificar se `test_pipeline.py` tem testes que referenciam `run_ten_times()` — atualizar se necessario

---

## Task 4: Rodar todos os testes e validar

**Descricao**: Executar `python -m pytest backend/tests/ -v --tb=short` e garantir que todos os 72+ testes passam.
