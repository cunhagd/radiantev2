/* ============================================================
   Radiante v2 — Metrics Module
   Renderizacao do card de metricas/observabilidade
   Depende de: state.js (DOM)
   ============================================================ */

window.Metrics = {};

(function () {
  /** Renderiza card de metricas de observabilidade */
  function renderMetrics(data) {
    if (data.metrics) {
      DOM.obsCard.style.display = 'block';
      DOM.metricsCostTotal.textContent = '$ ' + data.metrics.cost_total.toFixed(4);
      DOM.metricsPromptTokens.textContent = data.metrics.prompt_tokens.toLocaleString();
      DOM.metricsCacheTokens.textContent = data.metrics.cache_tokens.toLocaleString();
      DOM.metricsCompletionTokens.textContent = data.metrics.completion_tokens.toLocaleString();

      if (data.metrics.runs && data.metrics.runs.length > 1) {
        DOM.runsContainer.style.display = 'block';
        DOM.runsBody.innerHTML = '';
        data.metrics.runs.forEach(function (run) {
          var tr = document.createElement('tr');
          tr.innerHTML =
            '<td style="font-weight: 500;">Rodada ' + run.run + '</td>' +
            '<td>' + run.prompt_tokens.toLocaleString() + '</td>' +
            '<td>' + run.cache_tokens.toLocaleString() + '</td>' +
            '<td>' + run.completion_tokens.toLocaleString() + '</td>' +
            '<td style="font-weight: 600; color: var(--info);">$ ' +
              run.cost_total.toFixed(4) + '</td>';
          DOM.runsBody.appendChild(tr);
        });
      } else {
        DOM.runsContainer.style.display = 'none';
      }
    } else {
      DOM.obsCard.style.display = 'none';
    }
  }

  Metrics.renderMetrics = renderMetrics;
})();
