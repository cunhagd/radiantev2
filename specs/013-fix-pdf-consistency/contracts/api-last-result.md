# Contrato: GET /api/last-result

## Descricao

Retorna o resultado da ultima analise executada, incluindo metadados, cifras, valores estimados e o nome do arquivo PDF gerado.

## Request

`GET /api/last-result`

Sem parametros.

## Response (200 OK)

```json
{
  "numero_processo": "string",
  "autor": "string",
  "adv_reclamante": "string",
  "localidade": "string",
  "juizo": "string",
  "reclamada": "string",
  "segunda_reclamada": "string",
  "inicio_processo": "string",
  "valor_causa": "string",
  "cifras": [
    {
      "cifra": "string",
      "valor": "string",
      "descricao": "string",
      "probabilidade": "string",
      "valor_estimado": "string"
    }
  ],
  "valor_total_estimado": "string",
  "pdf_filename": "string (opcional)"
}
```

## Response (204 No Data)

```json
{
  "status": "no_data",
  "message": "Nenhum resultado encontrado"
}
```

## Comportamento esperado

- O campo `pdf_filename` DEVE conter `"relatorio_consolidado.pdf"` para modo 1x
- O campo `pdf_filename` DEVE conter `"relatorio_consolidado_10x.pdf"` para modo 10x
- O campo `pdf_filename` DEVE estar ausente/null quando nao ha dados
