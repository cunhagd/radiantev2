# Implementation Plan: Bloco de Metricas de Uso

**Branch**: `016-metrics-usage-block` | **Date**: 2026-06-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/016-metrics-usage-block/spec.md`

## Summary

Criar/integrar o bloco visual "Métricas de Uso" no frontend, posicionado abaixo do bloco "Provisão de Cifras", exibindo tokens de entrada, cache, saída e custo total em USD. As métricas já são coletadas no pipeline (`PipelineMetrics`, `merge_metrics()`) mas precisam ser incluídas no JSON de resultado retornado ao frontend, eliminando a necessidade de chamada separada a `/api/metrics`. No modo 10x, exibir adicionalmente uma tabela com métricas individuais de cada rodada da etapa 3.

## Technical Context

**Language/Version**: Python 3.14, JavaScript (Vanilla), HTML5, CSS3

**Primary Dependencies**: boto3, python-dotenv, openai, reportlab (sem novas dependencias)

**Storage**: Sistema de arquivos local (`data/`) + S3 (`radiante-final`)

**Testing**: pytest (backend), vitest + happy-dom (frontend)

**Target Platform**: Linux (EC2) e Windows (desenvolvimento local)

**Project Type**: Web service (backend HTTP nativo + frontend estatico)

**Performance Goals**: N/A — feature de exibicao de metricas, sem impacto em performance

**Constraints**: 
- Nao adicionar novas dependencias ao projeto
- Bloco deve seguir o padrao visual Material Design 3 ja estabelecido
- As metricas devem vir no mesmo JSON do resultado (FR-007), sem chamada extra

**Scale/Scope**: Arquivos do backend (`app.py`, `pipeline.py`, `metrics.py`) e frontend (`index.html`, `js/metrics.js`, `css/components.css`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates (Radiante v2 Constitution)

1. **GATE-FRAMEWORK**: Sem alteracoes no backend HTTP — mantem `SimpleHTTPRequestHandler`. ✅ OK
2. **GATE-CREDENCIAIS**: Sem alteracoes. ✅ OK
3. **GATE-PIPELINE**: Sem alteracoes no pipeline juridico de 4 etapas. ✅ OK
4. **GATE-CEGUEIRA**: Sem alteracoes. ✅ OK
5. **GATE-CPC25**: Sem alteracoes. ✅ OK
6. **GATE-S3-BUCKET**: Sem alteracoes. ✅ OK
7. **GATE-EXTRACAO**: Sem alteracoes. ✅ OK
8. **GATE-FRONTEND**: Frontend continua sem bundlers ou frameworks JS. Polling ja existe. Apenas adicao de dados no JSON e renderizacao do card existente. ✅ OK
9. **GATE-DEPENDENCIAS**: Nenhuma nova dependencia adicionada. ✅ OK
10. **GATE-DEPLOY**: Sem alteracoes no CI/CD. ✅ OK

**Resultado**: Nenhuma violacao. Feature puramente de exibicao de metricas.

## Project Structure

### Documentation (this feature)

```text
specs/016-metrics-usage-block/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── quickstart.md        # Phase 1 output
```

### Source Code (repository root)

```text
backend/
├── app.py                # Incluir metrics no JSON de resultado
├── pipeline.py           # Garantir que metrics inclua runs no modo 10x
└── metrics.py            # Adicionar suporte a runs individuais no PipelineMetrics

frontend/
├── index.html            # Card #observability-card ja existe, reposicionar abaixo de cifras
├── js/metrics.js         # Renderizar runs do modo 10x a partir do JSON principal
└── css/components.css    # Ajustes de estilo se necessario
```

**Structure Decision**: Mantem a estrutura existente. Apenas modificacoes pontuais em arquivos ja existentes.

## Complexity Tracking

Nenhuma violacao — sem necessidade de justificativa de complexidade.
