/* ============================================================
   Radiante v2 — Tests: loading.js
   ============================================================ */

import { describe, it, expect, beforeEach, vi } from 'vitest';

import '../js/state.js';
import '../js/api.js';
import '../js/loading.js';

// Mock global alert
global.alert = vi.fn();

describe('Loading Module', () => {
  beforeEach(() => {
    if (typeof window.initDOM === 'function') {
      window.initDOM();
    }
    // Reseta overlay
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
    const loadingTimer = document.getElementById('loading-timer');
    if (loadingTimer) loadingTimer.textContent = '00:00';
    const btnOnce = document.getElementById('btn-once');
    if (btnOnce) btnOnce.disabled = true;
    const btnTen = document.getElementById('btn-ten');
    if (btnTen) btnTen.disabled = true;

    // Reseta STATE timers
    window.STATE.timerId = null;
    window.STATE.intervalId = null;
    window.STATE.pollingId = null;

    vi.clearAllMocks();
  });

  it('cleanupLoading esconde overlay e reabilita botoes', () => {
    document.getElementById('loading-overlay').style.display = 'flex';
    Loading.cleanupLoading();
    expect(document.getElementById('loading-overlay').style.display).toBe('none');
    expect(document.getElementById('btn-once').disabled).toBe(false);
    expect(document.getElementById('btn-ten').disabled).toBe(false);
  });

  it('cleanupLoading limpa STATE timers', () => {
    STATE.timerId = setInterval(() => {}, 100000);
    STATE.pollingId = setInterval(() => {}, 100000);
    Loading.cleanupLoading();
    expect(STATE.timerId).toBeNull();
    expect(STATE.pollingId).toBeNull();
  });

  it('runAnalysis com 409 chama cleanup', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 409,
      json: () => Promise.resolve({ message: 'Em andamento' }),
    });

    await Loading.runAnalysis('once');

    await vi.waitFor(() => {
      expect(document.getElementById('btn-once').disabled).toBe(false);
    }, { timeout: 2000 });
  });

  it('runAnalysis com erro de rede chama alert e cleanup', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    await Loading.runAnalysis('once');

    await vi.waitFor(() => {
      expect(document.getElementById('btn-once').disabled).toBe(false);
    }, { timeout: 2000 });

    expect(global.alert).toHaveBeenCalled();
  });
});
