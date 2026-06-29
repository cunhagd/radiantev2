# Data Model — PDF e JSON Consistency

## Schema estendido de `/api/last-result`

```json
{
  "numero_processo": "0001271-36.2025.5.11.0002",
  "autor": "RAY BATISTA DA SILVA",
  "adv_reclamante": "ANDERSON ROBERTO MIRANDA DE SOUZA - OAB/RJ 161457",
  "localidade": "Manaus/AM",
  "juizo": "2ª Vara do Trabalho de Manaus",
  "reclamada": "RADIANTE ENGENHARIA DE TELECOMUNICAÇÕES LTDA",
  "segunda_reclamada": "",
  "inicio_processo": "03/10/2025",
  "valor_causa": "59.079,80",
  "cifras": [...],
  "valor_total_estimado": "38.006,93",
  "pdf_filename": "relatorio_consolidado.pdf"
}
```

## Campos adicionados

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `pdf_filename` | string (opcional) | Nome do arquivo PDF gerado na analise. Presente se ha dados. `"relatorio_consolidado.pdf"` para modo 1x, `"relatorio_consolidado_10x.pdf"` para modo 10x. |

## Arquivos gerenciados na pasta `data/`

| Modo | PDF gerado | JSON gerado | Artefatos removidos |
|------|-----------|-------------|---------------------|
| 1x (once) | `relatorio_consolidado.pdf` | `resultado_final.json` | `relatorio_consolidado_10x.pdf`, `consolidado_10x.json` |
| 10x (ten) | `relatorio_consolidado_10x.pdf` | `consolidado_10x.json` | `relatorio_consolidado.pdf`, `resultado_final.json` |

## Regra de consistencia

**NUNCA** devem coexistir na pasta `data/`:

- Mais de um PDF com prefixo `relatorio_consolidado`
- Mais de um JSON de resultado (`resultado_final.json` ou `consolidado_10x.json`)

A limpeza DEVE ocorrer ANTES da geracao do novo arquivo, em `backend/pipeline.py`.
