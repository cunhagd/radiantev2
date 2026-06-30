/* ============================================================
   Radiante v2 — Help Module
   Manual do usuario em markdown renderizado como modal
   ============================================================ */

window.Help = {};

(function () {
  function qs(id) { return document.getElementById(id); }

  /* ------------------------------------------------------------------ */
  /*  Markdown parser (simples, sem dependencias)                        */
  /* ------------------------------------------------------------------ */
  function mdToHtml(md) {
    var lines = md.split('\n');
    var html = '';
    var inCodeBlock = false;
    var codeBuffer = [];
    var inUl = false;
    var inOl = false;

    function closeUl() { if (inUl) { html += '</ul>\n'; inUl = false; } }
    function closeOl() { if (inOl) { html += '</ol>\n'; inOl = false; } }

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];

      // Code block
      if (line.trim().startsWith('```')) {
        if (inCodeBlock) {
          html += '<pre><code>' + escapeHtml(codeBuffer.join('\n')) + '</code></pre>\n';
          codeBuffer = [];
          inCodeBlock = false;
        } else {
          closeUl(); closeOl();
          inCodeBlock = true;
          codeBuffer = [];
        }
        continue;
      }
      if (inCodeBlock) {
        codeBuffer.push(line);
        continue;
      }

      // Empty line — mantém listas abertas (não quebra a sequência)
      if (line.trim() === '') {
        continue;
      }

      // --- Verificar se a linha é item de lista PRIMEIRO ---
      var _olMatch = line.match(/^\d+\.\s+(.+)$/);
      var _ulMatch = !_olMatch && line.match(/^[-*+]\s+(.+)$/);

      if (_olMatch || _ulMatch) {
        if (_olMatch) {
          // Ordered list
          if (inUl) { closeUl(); }
          if (!inOl) { html += '<ol>\n'; inOl = true; }
          html += '<li>' + parseInline(_olMatch[1]) + '</li>\n';
        } else {
          // Unordered list
          if (inOl) { closeOl(); }
          if (!inUl) { html += '<ul>\n'; inUl = true; }
          html += '<li>' + parseInline(_ulMatch[1]) + '</li>\n';
        }
        continue;
      }

      // Não é item de lista — fecha listas pendentes
      closeUl(); closeOl();

      // HR
      if (/^---+$/.test(line.trim())) {
        html += '<hr>\n';
        continue;
      }

      // Headers
      var hMatch = line.match(/^(#{1,3})\s+(.+)$/);
      if (hMatch) {
        var hLevel = hMatch[1].length;
        var hText = parseInline(hMatch[2]);
        html += '<h' + hLevel + '>' + hText + '</h' + hLevel + '>\n';
        continue;
      }

      // Blockquote
      var bqMatch = line.match(/^>\s+(.+)$/);
      if (bqMatch) {
        html += '<blockquote><p>' + parseInline(bqMatch[1]) + '</p></blockquote>\n';
        continue;
      }

      // Tables
      var tableRow = line.match(/^\|(.+)\|$/);
      if (tableRow) {
        var cells = tableRow[1].split('|').map(function (c) { return c.trim(); });

        // Check if this is a separator row (|---|)
        if (cells.every(function (c) { return /^-+$/.test(c); })) {
          continue;
        }

        // Check if we are in a table
        var prevLine = i > 0 ? lines[i - 1] : '';
        var nextLine = i < lines.length - 1 ? lines[i + 1] : '';
        var prevRow = prevLine.match(/^\|(.+)\|$/);
        var nextRow = nextLine.match(/^\|(.+)\|$/);

        if (!prevRow || /^-+$/.test((prevRow[1] || '').trim())) {
          // This is either a header row (prev is separator) or a new table
          // Check if next line is separator
          var nextSep = nextLine.match(/\|.*---.*\|/);
          if (nextSep) {
            html += '<table><thead><tr>';
            for (var c = 0; c < cells.length; c++) {
              html += '<th>' + parseInline(cells[c]) + '</th>';
            }
            html += '</tr></thead><tbody>\n';
            i++; // skip separator
          } else {
            html += '<table><tbody>\n';
            html += '<tr>';
            for (var c = 0; c < cells.length; c++) {
              html += '<td>' + parseInline(cells[c]) + '</td>';
            }
            html += '</tr>\n';
          }
        } else if (nextRow) {
          html += '<tr>';
          for (var c = 0; c < cells.length; c++) {
            html += '<td>' + parseInline(cells[c]) + '</td>';
          }
          html += '</tr>\n';
        } else {
          html += '<tr>';
          for (var c = 0; c < cells.length; c++) {
            html += '<td>' + parseInline(cells[c]) + '</td>';
          }
          html += '</tr>\n</tbody></table>\n';
        }
        continue;
      }

      // Paragraph (default)
      html += '<p>' + parseInline(line) + '</p>\n';
    }

    closeUl(); closeOl();

    return html;
  }

  function parseInline(text) {
    var t = escapeHtml(text);

    // Bold + Italic ***text***
    t = t.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
    // Bold **text**
    t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Italic *text*
    t = t.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Inline code `text`
    t = t.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Links [text](url)
    t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

    return t;
  }

  function escapeHtml(text) {
    var map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, function (m) { return map[m]; });
  }

  /* ------------------------------------------------------------------ */
  /*  Carregar help.md                                                   */
  /* ------------------------------------------------------------------ */
  async function loadHelp() {
    var body = qs('help-body');
    if (!body) return;

    try {
      var res = await fetch('/help.md?' + Date.now());
      if (!res.ok) throw new Error('HTTP ' + res.status);
      var md = await res.text();
      var html = mdToHtml(md);
      body.innerHTML = html;
    } catch (e) {
      body.innerHTML = '<div class="help-loading">Erro ao carregar o manual. Tente novamente.</div>';
      console.error('[HELP] Erro ao carregar help.md:', e);
    }
  }

  /* ------------------------------------------------------------------ */
  /*  Open / Close                                                       */
  /* ------------------------------------------------------------------ */
  function open() {
    var overlay = qs('help-overlay');
    if (!overlay) return;
    overlay.style.display = 'flex';
    loadHelp();
  }

  function close() {
    var overlay = qs('help-overlay');
    if (!overlay) return;
    overlay.style.display = 'none';
  }

  function isOpen() {
    var overlay = qs('help-overlay');
    return overlay && overlay.style.display === 'flex';
  }

  Help.open = open;
  Help.close = close;
  Help.isOpen = isOpen;
})();
