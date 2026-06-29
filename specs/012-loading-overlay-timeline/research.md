# Research — Loading Overlay com Timeline Interativa

## Decisoes

### 1. Polling rate: 1.2s

**Decisao**: 1200ms entre cada ciclo de polling.

**Racional**: A Constitution (V.95) especifica polling a cada 3s para `/api/status`. Para a timeline, um intervalo menor (1.2s) proporciona atualizacoes mais fluidas sem sobrecarregar o servidor, ja que o backend e single-threaded.

**Alternativas consideradas**:
- 3s (constitution): muito lento para feedback de timeline em tempo real
- 500ms: muito agressivo para um servidor single-thread

### 2. Dois endpoints de polling: /api/status + /api/progress

**Decisao**: Usar `Promise.all` para consultar ambos simultaneamente.

**Racional**: `/api/status` contem o estado consolidado (idle/processing/completed/error). `/api/progress` contem o detalhamento por etapa. Separar as responsabilidades permite que o frontend decida o que fazer com cada um.

### 3. Modo 1x vs 10x na timeline

**Decisao**: O parametro `totalRuns` (1 ou 10) controla:
- O titulo da overlay ("Analise unica" vs "Analise 10x")
- O numero de sub-etapas na Etapa 3 (1 vs 10)
- O texto do badge (contador "3/10" vs "Concluido")

**Racional**: Reutilizar o mesmo componente de timeline para ambos os modos evita duplicacao de codigo.

### 4. Forcar todos os steps como "done" ao finalizar

**Decisao**: Quando o backend reporta `status: "completed"`, a funcao `forceAllDone()` marca visualmente qualquer etapa que ainda esteja como "pending" como "done".

**Racional**: O backend pode finalizar antes de atualizar o ultimo progresso. Forcar o estado visual evita que o usuario veja etapas "pendentes" quando a analise ja terminou.
