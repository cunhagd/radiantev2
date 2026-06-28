/* ============================================================
   Radiante v2 — Cifras Module
   Renderizacao de metadados e lista de cifras
   Depende de: state.js (DOM)
   ============================================================ */

window.Cifras = {};

(function () {
  /** Renderiza metadados do processo */
  function renderMetadata(data) {
    DOM.metaProcesso.textContent = data.numero_processo || '-';
    DOM.metaAutor.textContent = data.autor || '-';
    DOM.metaAdvogado.textContent = data.adv_reclamante || '-';
    DOM.metaReclamada.textContent = data.reclamada || '-';
    DOM.metaTomadora.textContent = data.segunda_reclamada || '-';
    DOM.metaJuizo.textContent = data.juizo || '-';
    DOM.metaLocalidade.textContent = data.localidade || '-';
    DOM.metaInicio.textContent = data.inicio_processo || '-';
    DOM.metaValorCausa.textContent = data.valor_causa ? 'R$ ' + data.valor_causa : '-';
  }

  /** Determina classe CSS do badge baseado na probabilidade */
  function getBadgeClass(probabilidade) {
    const prob = (probabilidade || '').toLowerCase();
    if (prob.includes('certa')) return 'badge-certa';
    if (prob.includes('provavel') || prob.includes('provável')) return 'badge-provavel';
    if (prob.includes('possivel') || prob.includes('possível')) return 'badge-possivel';
    if (prob.includes('improvavel') || prob.includes('improvável')) return 'badge-improvavel';
    if (prob.includes('remota')) return 'badge-remota';
    return 'badge-remota';
  }

  /** Renderiza lista de cifras */
  function renderCifras(data) {
    DOM.cifrasList.innerHTML = '';

    if (!data || !data.cifras || data.cifras.length === 0) {
      DOM.cifrasList.innerHTML =
        '<div class="empty-state">Nenhum pleito identificado.</div>';
      return;
    }

    data.cifras.forEach(function (c) {
      const badgeClass = getBadgeClass(c.probabilidade);
      const formattedProb = c.probabilidade.charAt(0).toUpperCase() +
        c.probabilidade.slice(1).toLowerCase();

      const rowItem = document.createElement('div');
      rowItem.className = 'cifra-row-item';

      rowItem.innerHTML =
        '<div class="cifra-row-header">' +
          '<div class="cifra-info-block">' +
            '<div class="cifra-name">' + escapeHtml(c.cifra) + '</div>' +
            '<div><span class="badge ' + badgeClass + '">' +
              formattedProb + '</span></div>' +
          '</div>' +
          '<div class="cifra-values-wrapper">' +
            '<div class="cifra-value-pill">' +
              '<span class="cifra-value-label">Valor Base</span>' +
              '<span class="cifra-value-amount">R$ ' + escapeHtml(c.valor) + '</span>' +
            '</div>' +
            '<div class="cifra-value-pill">' +
              '<span class="cifra-value-label">Provisao</span>' +
              '<span class="cifra-value-amount allocated">R$ ' +
                escapeHtml(c.valor_estimado) + '</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
        (c.descricao
          ? '<div class="cifra-row-body">' + escapeHtml(c.descricao) + '</div>'
          : '');

      DOM.cifrasList.appendChild(rowItem);
    });

    // KPI total
    DOM.kpiTotal.textContent = data.valor_total_estimado
      ? 'R$ ' + data.valor_total_estimado
      : 'R$ 0,00';
  }

  function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  Cifras.renderMetadata = renderMetadata;
  Cifras.renderCifras = renderCifras;
})();
