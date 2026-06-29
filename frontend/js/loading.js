/* ============================================================
   Radiante v2 — Loading Module (Material3 Timeline)
   Overlay com timeline interativa para 1x e 10x
   Depende de: state.js (DOM, STATE), api.js (API)
   ============================================================ */

window.Loading = {};

(function () {
  function qs(id) { return document.getElementById(id); }

  /* ------------------------------------------------------------------ */
  /*  Helpers da Timeline                                                */
  /* ------------------------------------------------------------------ */
  function setStep(etapa, status, label, badgeText) {
    var el = qs('m3-step-' + etapa);
    if (!el) return;
    el.className = 'm3-step';
    if (status !== 'pending') el.classList.add('is-' + status);
    var lbl = el.querySelector('.m3-step-label');
    if (lbl) lbl.textContent = label;
    var badge = el.querySelector('.m3-step-badge');
    if (badge) {
      badge.className = 'm3-step-badge is-' + status;
      badge.textContent = badgeText || '';
    }
    var dot = el.querySelector('.m3-step-dot');
    if (dot) {
      dot.className = 'm3-step-dot';
      if (status !== 'pending') dot.classList.add('is-' + status);
    }
    var conn = el.querySelector('.m3-step-line');
    if (conn) {
      conn.className = 'm3-step-line';
      if (status === 'active' || status === 'done') conn.classList.add('is-' + status);
    }
  }

  function setSubStep(idx, status, label) {
    var el = qs('m3-sub-' + idx);
    if (!el) return;
    el.className = 'm3-substep';
    if (status !== 'pending') el.classList.add('is-' + status);
    var lbl = el.querySelector('.m3-substep-label');
    if (lbl) lbl.textContent = label;
    var badge = el.querySelector('.m3-substep-badge');
    if (badge) {
      badge.className = 'm3-substep-badge is-' + status;
      badge.textContent = status === 'pending' ? 'Aguardando'
        : status === 'active' ? 'Processando'
        : status === 'done' ? 'Conclu\u00eddo'
        : 'Falhou';
    }
    var dot = el.querySelector('.m3-substep-dot');
    if (dot) {
      dot.className = 'm3-substep-dot';
      if (status !== 'pending') dot.classList.add('is-' + status);
    }
  }

  function buildTimelineHTML(totalRuns) {
    totalRuns = totalRuns || 10;
    var h = '';
    var labels = [
      'Etapa 1 \u2014 Extra\u00e7\u00e3o de Cabe\u00e7alho',
      'Etapa 2 \u2014 C\u00e1lculo de Cifras',
      'Etapa 3 \u2014 C\u00e1lculo de Probabilidade' + (totalRuns > 1 ? ' (10x)' : ''),
      'Etapa 4 \u2014 Consolida\u00e7\u00e3o do Provisionamento',
    ];

    function step(n, label, substeps) {
      h += '<div class="m3-step" id="m3-step-' + n + '">';
      h += '  <div class="m3-step-visual">';
      h += '    <div class="m3-step-dot" id="m3-dot-' + n + '"></div>';
      if (n < 4) h += '    <div class="m3-step-line" id="m3-line-' + n + '"></div>';
      h += '  </div>';
      h += '  <div class="m3-step-body">';
      h += '    <span class="m3-step-label">' + label + '</span>';
      h += '    <span class="m3-step-badge is-pending" id="m3-badge-' + n + '">Aguardando</span>';
      h += '  </div>';
      h += '</div>';
      if (substeps) {
        h += '<div class="m3-substeps">';
        for (var i = 0; i < substeps; i++) {
          var num = i + 1;
          h += '<div class="m3-substep" id="m3-sub-' + i + '">';
          h += '  <div class="m3-substep-dot" id="m3-subdot-' + i + '"></div>';
          h += '  <span class="m3-substep-label' + (substeps === 1 ? '" style="font-weight:500;color:#1f1f1f"' : '"') + '>An\u00e1lise de probabilidade' + (substeps > 1 ? ' (' + num + ')' : '') + '</span>';
          h += '  <span class="m3-substep-badge is-pending">Aguardando</span>';
          h += '</div>';
        }
        h += '</div>';
      }
    }

    for (var e = 0; e < 4; e++) {
      if (e === 2) {
        step(e + 1, labels[e], totalRuns);
      } else {
        step(e + 1, labels[e]);
      }
    }

    return h;
  }

  /* ------------------------------------------------------------------ */
  /*  Atualiza timeline a partir do JSON do backend                      */
  /* ------------------------------------------------------------------ */
  function updateTimeline(progress) {
    if (!progress) return;

    var statusMap = { pending: 'pending', processing: 'active', completed: 'done', error: 'error' };
    function map(s) { return statusMap[s] || 'pending'; }

    if (progress.etapa1) {
      var st = map(progress.etapa1.status);
      setStep(1, st, progress.etapa1.label,
        st === 'done' ? 'Conclu\u00eddo' : st === 'active' ? 'Processando' : st === 'error' ? 'Falhou' : 'Aguardando');
    }

    if (progress.etapa2) {
      var st2 = map(progress.etapa2.status);
      setStep(2, st2, progress.etapa2.label,
        st2 === 'done' ? 'Conclu\u00eddo' : st2 === 'active' ? 'Processando' : st2 === 'error' ? 'Falhou' : 'Aguardando');
    }

    // Etapa 3
    var totalRuns = progress.total_runs || 1;
    var e3Status = 'pending';
    var e3Badge = 'Aguardando';
    var e3Label = 'Etapa 3 \u2014 C\u00e1lculo de Probabilidade' + (totalRuns > 1 ? ' (10x)' : '');

    if (progress.etapa3 && Array.isArray(progress.etapa3)) {
      var done = 0, proc = 0, err = 0;
      for (var i = 0; i < progress.etapa3.length; i++) {
        var r = progress.etapa3[i];
        var rs = map(r && r.status ? r.status : 'pending');
        setSubStep(i, rs,
          (r && r.label) || (totalRuns > 1 ? 'Rodada ' + (i + 1) : 'An\u00e1lise de probabilidade'));
        if (rs === 'done') done++;
        else if (rs === 'active') proc++;
        else if (rs === 'error') err++;
      }

      if (done === totalRuns) {
        e3Status = 'done';
        e3Badge = totalRuns > 1 ? '10/10 conclu\u00eddas' : 'Conclu\u00eddo';
      } else if (err === totalRuns) {
        e3Status = 'error';
        e3Badge = 'Falhou';
      } else if (proc > 0 || done > 0) {
        e3Status = 'active';
        e3Badge = totalRuns > 1 ? (done + '/' + totalRuns + ' (' + (proc || err) + ' em andamento)') : 'Processando...';
      }
    }
    setStep(3, e3Status, e3Label, e3Badge);

    if (progress.etapa4) {
      var st4 = map(progress.etapa4.status);
      setStep(4, st4, progress.etapa4.label,
        st4 === 'done' ? 'Conclu\u00eddo' : st4 === 'active' ? 'Processando' : st4 === 'error' ? 'Falhou' : 'Aguardando');
    }
  }

  /* ------------------------------------------------------------------ */
  /*  Forca todos os steps como done (usado ao finalizar)               */
  /* ------------------------------------------------------------------ */
  function forceAllDone(progress) {
    if (!progress) return;
    var totalRuns = progress.total_runs || 1;

    if (!progress.etapa1 || progress.etapa1.status !== 'completed')
      setStep(1, 'done', 'Extra\u00e7\u00e3o conclu\u00edda', 'Conclu\u00eddo');
    if (!progress.etapa2 || progress.etapa2.status !== 'completed')
      setStep(2, 'done', 'Cifras calculadas', 'Conclu\u00eddo');

    if (progress.etapa3 && Array.isArray(progress.etapa3)) {
      for (var i = 0; i < progress.etapa3.length; i++) {
        if (!progress.etapa3[i] || progress.etapa3[i].status !== 'completed') {
          setSubStep(i, 'done',
            totalRuns > 1 ? 'Rodada ' + (i + 1) + ' \u2014 OK' : 'Probabilidade calculada');
        }
      }
    }
    setStep(3, 'done', 'Probabilidade calculada',
      totalRuns > 1 ? '10/10' : 'Conclu\u00eddo');

    if (!progress.etapa4 || progress.etapa4.status !== 'completed')
      setStep(4, 'done', 'Consolidado com sucesso', 'Conclu\u00eddo');
  }

  /* ------------------------------------------------------------------ */
  /*  Cleanup                                                            */
  /* ------------------------------------------------------------------ */
  function cleanupLoading() {
    DOM.loadingOverlay.style.display = 'none';
    DOM.btnOnce.disabled = false;
    DOM.btnTen.disabled = false;

    [STATE.timerId, STATE.pollingId].forEach(function (id) {
      if (id) { clearInterval(id); }
    });
    STATE.timerId = null;
    STATE.pollingId = null;
  }

  /* ------------------------------------------------------------------ */
  /*  runAnalysis — usado por 1x e 10x                                   */
  /* ------------------------------------------------------------------ */
  async function runAnalysis(mode) {
    DOM.btnOnce.disabled = true;
    DOM.btnTen.disabled = true;

    var timelineContainer = qs('timeline-container');
    var timelineEl = qs('m3-timeline');
    var titleEl = qs('loading-title');
    var subtitleEl = qs('loading-subtitle');

    // Modo once: define totalRuns=1, modo ten: totalRuns=10
    var totalRuns = mode === 'ten' ? 10 : 1;

    // Prepara timeline
    if (timelineEl) timelineEl.innerHTML = buildTimelineHTML(totalRuns);
    if (timelineContainer) timelineContainer.style.display = 'block';

    if (mode === 'ten') {
      if (titleEl) titleEl.textContent = 'An\u00e1lise 10x em andamento';
      if (subtitleEl) subtitleEl.textContent = 'Executando 10 an\u00e1lises de probabilidade';
    } else {
      if (titleEl) titleEl.textContent = 'An\u00e1lise \u00fanica em andamento';
      if (subtitleEl) subtitleEl.textContent = 'Processando documentos jur\u00eddicos';
    }

    // Timer
    var elapsedSeconds = 0;
    var timerEl = qs('loading-timer');
    if (timerEl) timerEl.textContent = '00:00';
    STATE.timerId = setInterval(function () {
      elapsedSeconds++;
      var m = Math.floor(elapsedSeconds / 60).toString().padStart(2, '0');
      var s = (elapsedSeconds % 60).toString().padStart(2, '0');
      if (timerEl) timerEl.textContent = m + ':' + s;
    }, 1000);

    DOM.loadingOverlay.style.display = 'flex';

    try {
      var res = await API.startAnalysis(mode);

      if (res.status === 202 || res.status === 200) {
        STATE.pollingId = setInterval(async function () {
          try {
            var statusPromise = API.checkStatus();
            var progressPromise = fetch(API.BASE + '/api/progress?_=' + Date.now())
              .then(function (r) { return r.ok ? r.json() : null; })
              .catch(function () { return null; });

            var results = await Promise.all([statusPromise, progressPromise]);
            var statusData = results[0];
            var progressData = results[1];

            // Atualiza timeline com o progresso
            if (progressData) {
              updateTimeline(progressData);
            }

            // Atualiza subtitulo com info de progresso
            if (subtitleEl && progressData) {
              if (progressData.etapa4 && progressData.etapa4.status === 'processing') {
                subtitleEl.textContent = 'Consolidando resultados...';
              } else if (progressData.etapa4 && progressData.etapa4.status === 'completed') {
                subtitleEl.textContent = 'Finalizando...';
              } else if (progressData.etapa3 && Array.isArray(progressData.etapa3)) {
                var done = progressData.etapa3.filter(function (x) { return x && x.status === 'completed'; }).length;
                var total = progressData.total_runs || 1;
                if (total > 1) {
                  subtitleEl.textContent = done + '/' + total + ' rodadas de probabilidade conclu\u00eddas';
                } else if (done === 1) {
                  subtitleEl.textContent = 'Probabilidade calculada';
                } else if (progressData.etapa2 && progressData.etapa2.status === 'completed') {
                  // pass
                }
              }
            }

            // Se completou
            if (statusData && statusData.status === 'completed') {
              clearInterval(STATE.pollingId);
              STATE.pollingId = null;

              // Forca timeline como concluida
              if (progressData) forceAllDone(progressData);

              // Recarrega dados
              await API.loadLastResult();
              await API.loadAuditLog();

              setTimeout(function () { cleanupLoading(); }, 600);
            } else if (statusData && statusData.status === 'error') {
              clearInterval(STATE.pollingId);
              STATE.pollingId = null;
              alert('Erro no processamento: ' + (statusData.error_details || 'Erro desconhecido'));
              cleanupLoading();
            }
          } catch (err) {
            console.error('Erro no polling:', err);
          }
        }, 1200);

      } else if (res.status === 409) {
        var conflictData = await res.json();
        alert(conflictData.message || 'J\u00e1 existe uma an\u00e1lise em andamento.');
        cleanupLoading();
      } else {
        alert('Erro ao iniciar a an\u00e1lise no servidor.');
        cleanupLoading();
      }
    } catch (e) {
      console.error(e);
      alert('Erro de conex\u00e3o ao servidor.');
      cleanupLoading();
    }
  }

  Loading.runAnalysis = runAnalysis;
  Loading.cleanupLoading = cleanupLoading;
  Loading._setStep = setStep;
  Loading._setSubStep = setSubStep;
  Loading._buildTimelineHTML = buildTimelineHTML;
  Loading._updateTimeline = updateTimeline;
  Loading._forceAllDone = forceAllDone;
})();
