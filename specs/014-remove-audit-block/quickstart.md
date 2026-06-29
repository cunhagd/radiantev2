# Quickstart — Remocao do Bloco "Ver Relatorio de Auditoria"

## Pre-requisitos

- Servidor rodando: `$env:AWS_PROFILE='radiante'; python dev.py`
- Frontend acessivel em: http://localhost:8000

## Cenarios de Validacao

### Cenario 1: Bloco de auditoria nao aparece apos analise 1x

1. Faca upload de 1+ documentos
2. Clique em "Analisar 1x"
3. Aguarde a conclusao
4. **Esperado**: O elemento `.audit-section` (toggle "Ver Relatorio de Auditoria") NAO existe no DOM
5. **Esperado**: O botao "Baixar Relatorio PDF" continua visivel e funcional

### Cenario 2: Bloco de auditoria nao aparece apos analise 10x

1. Faca upload de 1+ documentos
2. Clique em "Analisar 10x"
3. Aguarde a conclusao
4. **Esperado**: O elemento `.audit-section` NAO existe no DOM
5. **Esperado**: O botao "Baixar Relatorio PDF" continua visivel e funcional

### Cenario 3: Rota `/api/audit-log` retorna 404

1. Apos qualquer analise, acesse `http://localhost:8000/api/audit-log`
2. **Esperado**: Resposta 404 (rota removida)
