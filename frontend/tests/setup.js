/* ============================================================
   Radiante v2 — Test Setup
   Configura o DOM virtual antes de cada suite de teste
   ============================================================ */

// Substitui o DOM com o HTML base
const baseHTML = `
<!DOCTYPE html>
<html>
<head>
  <title>Radiante - Test</title>
  <style>
    :root[theme="light"] {
      --bg-main: #f0f4f9;
      --bg-surface: #ffffff;
      --bg-surface-variant: #f3f6fc;
      --text-primary: #1f1f1f;
      --text-secondary: #474747;
      --text-muted: #757575;
      --accent-blue: #0b57d0;
      --border-subtle: #e3e3e3;
      --success: #146c2e;
      --info: #0b57d0;
      --warning: #b06000;
      --danger: #b3261e;
      --radius-sm: 0.5rem;
      --radius-md: 1.0rem;
      --radius-lg: 1.75rem;
      --radius-pill: 9999px;
    }
  </style>
</head>
<body>
  <header>
    <div class="actions-group">
      <div class="actions">
        <input type="file" id="upload-input" multiple style="display: none;">
        <button class="btn btn-upload" id="btn-upload">Upload</button>
        <button class="btn" id="btn-once" disabled>1x</button>
        <button class="btn btn-primary" id="btn-ten" disabled>10x</button>
        <button class="btn btn-clear" id="btn-clear" title="Limpar"></button>
      </div>
      <div id="upload-status" class="status-text"></div>
    </div>
  </header>

  <div class="container">
    <div class="card">
      <div class="meta-grid">
        <div class="meta-item"><span class="meta-label">Processo</span><span class="meta-value" id="meta-processo">—</span></div>
        <div class="meta-item"><span class="meta-label">Autor</span><span class="meta-value" id="meta-autor">—</span></div>
        <div class="meta-item"><span class="meta-label">Advogado</span><span class="meta-value" id="meta-advogado">—</span></div>
        <div class="meta-item"><span class="meta-label">Reclamada</span><span class="meta-value" id="meta-reclamada">—</span></div>
        <div class="meta-item"><span class="meta-label">Tomadora</span><span class="meta-value" id="meta-tomadora">—</span></div>
        <div class="meta-item"><span class="meta-label">Juizo</span><span class="meta-value" id="meta-juizo">—</span></div>
        <div class="meta-item"><span class="meta-label">Localidade</span><span class="meta-value" id="meta-localidade">—</span></div>
        <div class="meta-item"><span class="meta-label">Inicio</span><span class="meta-value" id="meta-inicio">—</span></div>
        <div class="meta-item"><span class="meta-label">Valor da Causa</span><span class="meta-value" id="meta-valor-causa">—</span></div>
      </div>
    </div>

    <div class="card">
      <div id="cifras-fluent-list" class="cifras-list">
        <div class="empty-state">Nenhum dado. Inicie uma analise.</div>
      </div>
      <div class="kpi-footer">
        <span class="kpi-label">Total Estimado</span>
        <span class="kpi-value" id="kpi-total">R$ 0,00</span>
      </div>
      <div class="download-row">
        <a href="#" download class="btn btn-download" id="download-pdf-btn">Baixar Relatorio PDF</a>
      </div>
    </div>

    <div class="card" id="observability-card" style="display: none;">
      <div class="metrics-grid">
        <div class="metric-card"><span class="metric-label">Custo Total</span><span class="metric-value highlight" id="metrics-cost-total">$0.00</span></div>
        <div class="metric-card"><span class="metric-label">Tokens Entrada</span><span class="metric-value" id="metrics-prompt-tokens">0</span></div>
        <div class="metric-card"><span class="metric-label">Tokens em Cache</span><span class="metric-value" id="metrics-cache-tokens">0</span></div>
        <div class="metric-card"><span class="metric-label">Tokens Saida</span><span class="metric-value" id="metrics-completion-tokens">0</span></div>
      </div>
      <div id="runs-observability-container" style="display:none;">
        <table>
          <tbody id="runs-observability-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="loading-overlay" id="loading-overlay">
    <div class="loading-text" id="loading-text">Analisando...</div>
    <div class="loading-timer" id="loading-timer">00:00</div>
    <div class="progress-container" id="loading-progress-container" style="display:none">
      <div class="progress-bar" id="loading-progress"></div>
    </div>
  </div>

  <div class="modal-overlay" id="clear-modal" style="display: none;">
    <div class="modal-content alert-dialog">
      <div class="modal-body"><p>Isso excluira todos os dados.</p></div>
      <div class="modal-actions">
        <button class="btn" id="modal-cancel">Cancelar</button>
        <button class="btn btn-danger" id="modal-confirm-clear">Limpar tudo</button>
      </div>
    </div>
  </div>
</body>
</html>
`;

document.documentElement.innerHTML = baseHTML;
