/* ============================================================
   Radiante v2 — Tests: state.js
   ============================================================ */

import { describe, it, expect, beforeAll } from 'vitest';

// Carrega o modulo
import '../js/state.js';

describe('State Module', () => {
  beforeAll(() => {
    // Garante que initDOM foi chamado. Se o import ja chamou, isso e no-op.
    if (typeof window.initDOM === 'function') {
      window.initDOM();
    }
  });

  it('STATE existe e inicia com timers null', () => {
    expect(window.STATE).toBeDefined();
    expect(window.STATE.timerId).toBeNull();
    expect(window.STATE.intervalId).toBeNull();
    expect(window.STATE.pollingId).toBeNull();
  });

  it('DOM existe apos setup', () => {
    expect(window.DOM).toBeDefined();
  });

  it('DOM.btnOnce existe', () => {
    expect(window.DOM.btnOnce).toBeDefined();
    expect(window.DOM.btnOnce.id).toBe('btn-once');
  });

  it('DOM.btnTen existe', () => {
    expect(window.DOM.btnTen).toBeDefined();
    expect(window.DOM.btnTen.id).toBe('btn-ten');
  });

  it('DOM.cifrasList existe', () => {
    expect(window.DOM.cifrasList).toBeDefined();
    expect(window.DOM.cifrasList.id).toBe('cifras-fluent-list');
  });

  it('DOM.kpiTotal existe', () => {
    expect(window.DOM.kpiTotal).toBeDefined();
    expect(window.DOM.kpiTotal.id).toBe('kpi-total');
  });

  it('DOM.loadingOverlay existe', () => {
    expect(window.DOM.loadingOverlay).toBeDefined();
    expect(window.DOM.loadingOverlay.id).toBe('loading-overlay');
  });

  it('DOM.clearModal existe', () => {
    expect(window.DOM.clearModal).toBeDefined();
    expect(window.DOM.clearModal.id).toBe('clear-modal');
  });
});
