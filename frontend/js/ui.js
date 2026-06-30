/* ============================================================
   Radiante v2 — UI Module
   Interacoes de usuario (upload, modal, audit, clear)
   Depende de: state.js (DOM), api.js (API)
   ============================================================ */

window.UI = {};

(function () {
  /**
   * Atualiza estado dos botoes conforme presenca de dados.
   * @param {string} state - 'initial' (sem dados), 'uploaded' (docs enviados), 'has_data' (rodagem concluida)
   */
  function updateButtonsState(state) {
    switch (state) {
      case 'has_data':
        // Dados de rodagem na tela: apenas lixeira disponivel
        DOM.btnUpload.disabled = true;
        DOM.btnOnce.disabled = true;
        DOM.btnTen.disabled = true;
        DOM.btnClear.disabled = false;
        break;
      case 'uploaded':
        // Upload concluido: upload + analise liberados, lixeira bloqueada
        DOM.btnUpload.disabled = false;
        DOM.btnOnce.disabled = false;
        DOM.btnTen.disabled = false;
        DOM.btnClear.disabled = true;
        break;
      case 'initial':
      default:
        // Estado inicial: apenas upload liberado
        DOM.btnUpload.disabled = false;
        DOM.btnOnce.disabled = true;
        DOM.btnTen.disabled = true;
        DOM.btnClear.disabled = true;
        break;
    }
  }

  function showClearModal() {
    DOM.clearModal.style.display = 'flex';
  }

  function closeClearModal() {
    DOM.clearModal.style.display = 'none';
  }

  async function confirmClearAll() {
    DOM.btnClear.disabled = true;
    closeClearModal();

    // Chama o loading visual com timeline (SSE streaming)
    await Loading.runClear();
  }

  function clearAllFrontendData() {
    var metaIds = [
      'meta-processo', 'meta-autor', 'meta-advogado', 'meta-reclamada',
      'meta-tomadora', 'meta-juizo', 'meta-localidade', 'meta-inicio',
      'meta-valor-causa',
    ];
    metaIds.forEach(function (id) {
      document.getElementById(id).textContent = '—';
    });

    DOM.kpiTotal.textContent = 'R$ 0,00';
    DOM.cifrasList.innerHTML =
      '<div class="empty-state">Nenhum dado. Inicie uma analise.</div>';
    DOM.obsCard.style.display = 'none';
    // Apos limpeza, volta ao estado inicial (apenas upload liberado)
    updateButtonsState('initial');
  }

  async function handleFileUpload(input) {
    const files = input.files;
    if (files.length === 0) return;

    DOM.uploadStatus.style.color = '#60a5fa';
    DOM.uploadStatus.textContent = 'Preparando upload de ' + files.length + ' arquivo(s)...';
    DOM.btnOnce.disabled = true;
    DOM.btnTen.disabled = true;
    DOM.btnUpload.disabled = true;

    let successCount = 0;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      DOM.uploadStatus.textContent = 'Enviando arquivo ' + (i + 1) + ' de ' +
        files.length + ': ' + file.name + '...';

      try {
        const response = await API.uploadFile(file);
        if (response.ok) successCount++;
        else console.error('Erro ao enviar ' + file.name + ': status ' + response.status);
      } catch (err) {
        console.error('Erro de rede ao enviar ' + file.name + ':', err);
      }
    }

    DOM.btnUpload.disabled = false;

    if (successCount === files.length) {
      DOM.uploadStatus.style.color = '#34d399';
      DOM.uploadStatus.textContent = successCount +
        ' arquivo(s) enviados com sucesso! Pronto para analise.';
      updateButtonsState('uploaded');
    } else {
      DOM.uploadStatus.style.color = '#f87171';
      DOM.uploadStatus.textContent = 'Falha ao enviar documentos. Enviados: ' +
        successCount + ' de ' + files.length + '.';
    }

    input.value = '';
  }


  UI.showClearModal = showClearModal;
  UI.closeClearModal = closeClearModal;
  UI.confirmClearAll = confirmClearAll;
  UI.clearAllFrontendData = clearAllFrontendData;
  UI.handleFileUpload = handleFileUpload;
  UI.updateButtonsState = updateButtonsState;
})();
