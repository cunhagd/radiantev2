/* ============================================================
   Radiante v2 — State Module
   Estado global e referencias DOM
   Depende de: nada
   ============================================================ */

window.STATE = {
  timerId: null,
  intervalId: null,
  pollingId: null,
};

window.DOM = {};

/**
 * Inicializa referencias DOM.
 * Pode ser chamada apos o carregamento do HTML.
 */
function initDOM() {
  DOM.uploadInput = document.getElementById('upload-input');
  DOM.btnUpload = document.getElementById('btn-upload');
  DOM.btnOnce = document.getElementById('btn-once');
  DOM.btnTen = document.getElementById('btn-ten');
  DOM.btnClear = document.getElementById('btn-clear');
  DOM.uploadStatus = document.getElementById('upload-status');

  DOM.metaProcesso = document.getElementById('meta-processo');
  DOM.metaAutor = document.getElementById('meta-autor');
  DOM.metaAdvogado = document.getElementById('meta-advogado');
  DOM.metaReclamada = document.getElementById('meta-reclamada');
  DOM.metaTomadora = document.getElementById('meta-tomadora');
  DOM.metaJuizo = document.getElementById('meta-juizo');
  DOM.metaLocalidade = document.getElementById('meta-localidade');
  DOM.metaInicio = document.getElementById('meta-inicio');
  DOM.metaValorCausa = document.getElementById('meta-valor-causa');

  DOM.cifrasList = document.getElementById('cifras-fluent-list');
  DOM.kpiTotal = document.getElementById('kpi-total');

  DOM.downloadPdfBtn = document.getElementById('download-pdf-btn');

  DOM.obsCard = document.getElementById('observability-card');
  DOM.metricsCostTotal = document.getElementById('metrics-cost-total');
  DOM.metricsPromptTokens = document.getElementById('metrics-prompt-tokens');
  DOM.metricsCacheTokens = document.getElementById('metrics-cache-tokens');
  DOM.metricsCompletionTokens = document.getElementById('metrics-completion-tokens');
  DOM.runsContainer = document.getElementById('runs-observability-container');
  DOM.runsBody = document.getElementById('runs-observability-body');

  DOM.loadingOverlay = document.getElementById('loading-overlay');
  DOM.loadingTimer = document.getElementById('loading-timer');

  DOM.clearModal = document.getElementById('clear-modal');
}

// Auto-inicializa se o DOM ja estiver pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDOM);
} else {
  initDOM();
}

// Exporta para uso em testes
window.initDOM = initDOM;
