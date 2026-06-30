# Contrato: API_BASE Injection

## Propósito

Garantir que o frontend estático tenha acesso à URL do backend EC2 (`http://18.208.190.159:8000`) injetada pelo Amplify no momento do build.

## Mecanismo

### 1. Build Spec

No `amplify.yml` (ou configurado diretamente no console Amplify), o comando de build gera o arquivo `js/env.js`:

```bash
echo "window.API_BASE='$API_BASE';" > js/env.js
```

Onde `$API_BASE` é a variável de ambiente configurada no Amplify com o valor `http://18.208.190.159:8000`.

### 2. Arquivo Gerado (`frontend/js/env.js`)

```js
window.API_BASE = 'http://18.208.190.159:8000';
```

### 3. Leitura no `frontend/js/api.js`

```js
(function () {
  const API_BASE = window.API_BASE || (
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? "http://localhost:8000"
      : "https://jtuuxek832.execute-api.us-east-1.amazonaws.com"
  );

  API.BASE = API_BASE;
  // ... resto do código
})();
```

### 4. Ordem de Carregamento no HTML

O script `js/env.js` DEVE ser carregado ANTES de `js/api.js`:

```html
<!-- Env vars injetadas pelo Amplify (se existir) -->
<script src="js/env.js"></script>
<!-- JS Modules -->
<script src="js/state.js"></script>
<script src="js/api.js"></script>
<script src="js/cifras.js"></script>
<script src="js/metrics.js"></script>
<script src="js/ui.js"></script>
<script src="js/loading.js"></script>
```

## Comportamento por Ambiente

| Ambiente | `window.API_BASE` | Resultado |
|----------|-------------------|-----------|
| Local (dev) | `undefined` | Fallback para `http://localhost:8000` |
| Amplify com env var configurada | `http://18.208.190.159:8000` | Usa a URL do backend EC2 |
| Amplify sem env var | `undefined` | Fallback para API Gateway antigo |
