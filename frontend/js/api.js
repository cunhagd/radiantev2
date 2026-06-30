/* ============================================================
   Radiante v2 — API Module
   Comunicacao HTTP com backend
   Depende de: state.js (DOM, STATE)
   ============================================================ */

window.API = {};

(function () {
  var API_BASE = window.API_BASE || '';

  // Se API_BASE for URL relativa ou vazia, endpoints sao resolvidos
  // contra o mesmo dominio (necessita de proxy reverso no Amplify ou nginx)
  if (!API_BASE) {
    var isLocal = window.location.hostname === 'localhost' ||
                  window.location.hostname === '127.0.0.1';
    API_BASE = isLocal ? 'http://localhost:8000' : '';
  }

  API.BASE = API_BASE;

  function apiUrl(endpoint) {
    if (!API_BASE) return endpoint;
    var base = API_BASE.replace(/\/+$/, '');
    var ep = endpoint.replace(/^\/+/, '');
    return base + '/' + ep;
  }

  API.fetchJSON = async function (endpoint) {
    var res = await fetch(apiUrl(endpoint));
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  };

  API.fetchText = async function (endpoint) {
    var res = await fetch(apiUrl(endpoint));
    if (!res.ok) return null;
    return res.text();
  };

  API.post = async function (endpoint, body) {
    return fetch(apiUrl(endpoint), {
      method: 'POST',
      body: body,
    });
  };

  API.uploadFile = async function (file) {
    var url = apiUrl('/api/upload');
    return fetch(url, {
      method: 'POST',
      headers: {
        'X-Filename': encodeURIComponent(file.name),
        'Content-Type': file.type || 'application/octet-stream',
      },
      body: file,
    });
  };

  /** Carrega ultimo resultado e chama callback de render */
  API.loadLastResult = async function () {
    try {
      var data = await API.fetchJSON('/api/last-result');
      if (typeof window.renderAll === 'function') {
        window.renderAll(data);
      }
      return data && data.cifras ? data : null;
    } catch (e) {
      console.error("Erro ao carregar ultimo resultado", e);
      return null;
    }
  };

  /** Inicia analise e retorna resposta */
  API.startAnalysis = async function (mode) {
    var endpoint = mode === 'once' ? '/api/run-once' : '/api/run-ten';
    return API.post(endpoint);
  };

  /** Verifica status da analise */
  API.checkStatus = async function () {
    return API.fetchJSON('/api/status');
  };
})();
