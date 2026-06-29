# Quickstart — Loading Overlay Timeline

## Pre-requisitos

- Servidor rodando: `$env:AWS_PROFILE='radiante'; python dev.py`
- Frontend acessivel em: http://localhost:8000

## Cenarios de Validacao

### Cenario 1: Timeline no modo 1x

1. Faca upload de 1+ documentos
2. Clique em "Analisar 1x"
3. **Esperado**: Overlay aparece com:
   - Titulo: "Analise unica em andamento"
   - 4 etapas na timeline vertical
   - Etapa 3 com apenas 1 sub-etapa
   - Timer contando (MM:SS)
4. **Esperado**: A cada ~1.2s os status das etapas atualizam
5. **Esperado**: Ao finalizar, overlay fecha apos 600ms e relatorio aparece

### Cenario 2: Timeline no modo 10x

1. Faca upload de 1+ documentos
2. Clique em "Analisar 10x"
3. **Esperado**: Overlay aparece com:
   - Titulo: "Analise 10x em andamento"
   - Subtitulo: "Executando 10 analises de probabilidade"
   - Etapa 3 com 10 sub-etapas
4. **Esperado**: Badge da etapa 3 mostra contador (ex: "3/10 (2 em andamento)")
5. **Esperado**: Ao finalizar, badge mostra "10/10 concluidas"

### Cenario 3: Tratamento de erro

1. Simule um erro (ex: pare o servidor durante analise)
2. **Esperado**: Overlay exibe alerta com mensagem de erro e fecha

### Cenario 4: Conflito de analise

1. Inicie uma analise
2. Tente iniciar outra enquanto a primeira roda
3. **Esperado**: Alerta "Ja existe uma analise em andamento"

## API Reference

- `GET /api/progress` — Progresso detalhado por etapa
- `GET /api/status` — Estado consolidado da analise
- `POST /api/run-once` — Iniciar analise 1x
- `POST /api/run-ten` — Iniciar analise 10x

Veja `data-model.md` para o schema completo de `/api/progress`.
