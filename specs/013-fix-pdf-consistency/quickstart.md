# Quickstart — PDF e JSON Consistency

## Pre-requisitos

- Servidor rodando: `$env:AWS_PROFILE='radiante'; python dev.py`
- Frontend acessivel em: http://localhost:8000

## Cenarios de Validacao

### Cenario 1: Download de PDF apos analise 1x

1. Faca upload de 1+ documentos
2. Clique em "Analisar 1x"
3. Aguarde a conclusao
4. **Esperado**: Botao "Baixar Relatorio PDF" tem href para `/data/relatorio_consolidado.pdf`
5. Clique no botao — **Esperado**: Download inicia com o PDF correto

### Cenario 2: Download de PDF apos analise 10x

1. Faca upload de 1+ documentos
2. Clique em "Analisar 10x"
3. Aguarde a conclusao
4. **Esperado**: Botao "Baixar Relatorio PDF" tem href para `/data/relatorio_consolidado_10x.pdf`
5. Clique no botao — **Esperado**: Download inicia com o PDF correto

### Cenario 3: Limpeza de artefatos ao alternar modos

1. Execute analise 1x — verifique que `data/relatorio_consolidado.pdf` existe
2. Execute analise 10x — verifique que `data/relatorio_consolidado.pdf` foi removido e apenas `data/relatorio_consolidado_10x.pdf` existe
3. Execute analise 1x novamente — verifique que `data/relatorio_consolidado_10x.pdf` foi removido e `data/relatorio_consolidado.pdf` existe

### Cenario 4: Acesso direto ao PDF

1. Apos analise 1x, acesse `http://localhost:8000/data/relatorio_consolidado.pdf`
2. **Esperado**: PDF exibido no navegador (200)
3. Acesse `http://localhost:8000/data/arquivo_inexistente.pdf`
4. **Esperado**: 404

## API Reference

- `GET /api/last-result` — Veja `contracts/api-last-result.md`
- `GET /data/<filename>` — Arquivo estatico da pasta data/

Veja `data-model.md` para o schema completo.
