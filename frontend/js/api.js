/* ============================================================
   Radiante v2 — API Module
   Comunicacao HTTP com backend
   Depende de: state.js (DOM, STATE)
   ============================================================ */

window.API = {};

(function () {
  const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://localhost:8000"
    : "https://jtuuxek832.execute-api.us-east-1.amazonaws.com";

  API.BASE = API_BASE;

  API.fetchJSON = async function (endpoint) {
    const res = await fetch(API_BASE + endpoint);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  };

  API.fetchText = async function (endpoint) {
    const res = await fetch(API_BASE + endpoint);
    if (!res.ok) return null;
    return res.text();
  };

  API.post = async function (endpoint, body) {
    return fetch(API_BASE + endpoint, {
      method: 'POST',
      body: body,
    });
  };

  API.uploadFile = async function (file) {
    return fetch(API_BASE + '/api/upload', {
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
      const data = await API.fetchJSON('/api/last-result');
      if (typeof window.renderAll === 'function') {
        window.renderAll(data);
      }
    } catch (e) {
      console.error("Erro ao carregar ultimo resultado", e);
    }
  };

  /** Carrega log de auditoria */
  API.loadAuditLog = async function () {
    try {
      const text = await API.fetchText('/api/audit-log');
      if (text) {
        DOM.auditContent.innerText = text;
      } else {
        DOM.auditContent.innerText = "Nenhum relatorio de auditoria gerado ainda. Execute uma analise 10x para criar o log de auditoria.";
      }
    } catch (e) {
      console.error("Erro ao carregar log de auditoria", e);
    }
  };

  /** Inicia analise e retorna resposta */
  API.startAnalysis = async function (mode) {
    const endpoint = mode === 'once' ? '/api/run-once' : '/api/run-ten';
    return API.post(endpoint);
  };

  /** Verifica status da analise */
  API.checkStatus = async function () {
    return API.fetchJSON('/api/status');
  };
})();
