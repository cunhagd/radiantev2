# Data Model — Loading Overlay Progress

## Fonte dos dados

Endpoint: `GET /api/progress`
Resposta: JSON com o estado atual do progresso da analise.

## Schema

```json
{
  "etapa1": {
    "status": "pending | processing | completed | error",
    "label": "Etapa 1 — Extracao de Cabecalho"
  },
  "etapa2": {
    "status": "pending | processing | completed | error",
    "label": "Etapa 2 — Calculo de Cifras"
  },
  "etapa3": [
    {
      "status": "pending | processing | completed | error",
      "label": "Rodada 1"
    }
  ],
  "etapa4": {
    "status": "pending | processing | completed | error",
    "label": "Etapa 4 — Consolidacao do Provisionamento"
  },
  "total_runs": 1
}
```

## Estados possiveis

| Status | Significado | Visual na timeline |
|--------|-------------|-------------------|
| `pending` | Aguardando processamento | Circulo vazio, badge "Aguardando" |
| `processing` | Em execucao | Circulo pulsante com gradiente, badge "Processando" |
| `completed` | Concluido com sucesso | Circulo verde com check, badge "Concluido" |
| `error` | Falhou | Circulo vermelho com X, badge "Falhou" |

## Notas

- `total_runs`: 1 para modo "once", 10 para modo "ten"
- `etapa3` e um array. Cada elemento representa uma rodada de calculo de probabilidade
- O tamanho do array `etapa3` define o numero de sub-etapas exibidas na timeline
- Etapas 1, 2 e 4 sao objetos unicos (nao arrays)
