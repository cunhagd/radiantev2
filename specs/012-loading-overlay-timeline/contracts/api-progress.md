# Contrato: GET /api/progress

## Descricao

Retorna o estado atual do progresso da analise em execucao. Usado pelo frontend para alimentar a timeline interativa em tempo real.

## Metodo

`GET /api/progress`

## Parametros

Nenhum. O cache e evitado via query parameter `?_=<timestamp>`.

## Resposta (200 OK)

```json
{
  "etapa1": {
    "status": "completed",
    "label": "Etapa 1 — Extracao de Cabecalho"
  },
  "etapa2": {
    "status": "completed",
    "label": "Etapa 2 — Calculo de Cifras"
  },
  "etapa3": [
    {
      "status": "completed",
      "label": "Rodada 1"
    },
    {
      "status": "processing",
      "label": "Rodada 2"
    }
  ],
  "etapa4": {
    "status": "pending",
    "label": "Etapa 4 — Consolidacao do Provisionamento"
  },
  "total_runs": 10
}
```

## Campos

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `etapa1` | object | Progresso da etapa 1 (extracao de cabecalho) |
| `etapa2` | object | Progresso da etapa 2 (calculo de cifras) |
| `etapa3` | array | Progresso de cada rodada da etapa 3 (calculo de probabilidade) |
| `etapa4` | object | Progresso da etapa 4 (consolidacao) |
| `total_runs` | number | 1 para modo once, 10 para modo ten |

## Estados possiveis

| Status | Descricao |
|--------|-----------|
| `pending` | Aguardando processamento |
| `processing` | Em execucao |
| `completed` | Concluido |
| `error` | Falhou |

## Notas

- O array `etapa3` tem tamanho igual a `total_runs`
- Etapas 1, 2 e 4 sao objetos simples com `status` e `label`
- O frontend faz cache-busting via `?_=<timestamp>` para evitar cache do navegador
