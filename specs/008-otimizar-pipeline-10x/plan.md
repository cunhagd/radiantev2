# Implementation Plan: 008-otimizar-pipeline-10x

## Technical Context

**O que mudar**: A funcao `run_ten_times()` em `backend/pipeline.py`.

**Estado atual**: `run_ten_times()` executa `run_single_pipeline()` 10 vezes — cada chamada roda as 4 etapas completas.

**Estado desejado**: Uma nova funcao (ou refatoracao de `run_ten_times()`) que:
1. Executa etapa 1 e etapa 2 uma unica vez (sequencial)
2. Executa etapa 3 em 10 threads paralelas, todas usando o mesmo resultado fixo da etapa 2
3. Executa etapa 4 uma unica vez consolidando os 10 resultados da etapa 3

## Estrutura de Diretorios

```
backend/pipeline.py  (modificado — nova logica 10x)
backend/tests/test_pipeline.py  (modificado — novos testes)
```

## Constitution Check

**Principio III (Compliance Trabalhista)**: Nao violado. O pipeline continua tendo 4 etapas. Apenas a orquestracao do modo 10x muda — etapa 3 repete com variacao de probabilidade, que e o comportamento correto.

**Principio I (Arquitetura Enxuta)**: Nao violado. Nenhum framework novo introduzido.

## Design

### Fluxo Novo do Modo 10x

```
run_ten_times_optimized(config, context):
  1. etapa1_raw, etapa1_metrics = run_llm_stage(config, etapa1)
  2. etapa2_raw, etapa2_metrics = run_llm_stage(config, etapa2, usando etapa1_raw)
  
  3. Para i in 1..10 (ThreadPoolExecutor, max_workers=5):
       etapa3_raw_i, etapa3_metrics_i = run_llm_stage(config, etapa3, usando etapa2_raw FIXO)
  
  4. Agrega os 10 resultados da etapa 3
  5. etapa4_raw, etapa4_metrics = run_llm_stage(config, etapa4, usando etapa1_raw + etapa2_raw + todos etapa3_raw)
  
  6. Salva resultados no S3
  7. Gera PDF consolidado
```

### Mudancas Necessarias

1. **Nova funcao `run_ten_times_optimized()`** em `pipeline.py` — implementa o fluxo acima
2. **Refatorar endpoint em `app.py`** — o modo 10x deve chamar a nova funcao
3. **Reutilizar `run_single_pipeline()`** para o modo "once" (sem alteracoes)

### Reutilizacao

- `run_single_pipeline()` continua existindo para o modo "once" — inalterado
- `run_ten_times()` original pode ser removido ou mantido como legado (removido para evitar confusao)
- As funcoes `save_stage_files()`, `save_audit_log()`, `aggregate_results()` permanecem inalteradas
- `run_llm_stage_streaming()` permanece inalterado — e quem realmente chama o Grok

### Tasks Dependencies

```
1. Criar run_ten_times_optimized() em pipeline.py
2. Atualizar app.py para chamar a nova funcao
3. Atualizar testes
4. Rodar testes e validar
```
