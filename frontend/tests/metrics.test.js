/* ============================================================
   Radiante v2 — Tests: metrics.js
   ============================================================ */

import { describe, it, expect, beforeEach } from 'vitest';

import '../js/state.js';
import '../js/metrics.js';

describe('Metrics Module', () => {
  beforeEach(() => {
    if (typeof window.initDOM === 'function') {
      window.initDOM();
    }
    // Garante estado inicial
    const obsCard = document.getElementById('observability-card');
    if (obsCard) obsCard.style.display = 'none';
    const runsContainer = document.getElementById('runs-observability-container');
    if (runsContainer) runsContainer.style.display = 'none';
  });

  it('renderMetrics mostra card quando metrics existem', () => {
    const data = {
      metrics: {
        cost_total: 0.015,
        prompt_tokens: 1000,
        cache_tokens: 200,
        completion_tokens: 500,
        runs: [],
      },
    };

    Metrics.renderMetrics(data);

    expect(document.getElementById('observability-card').style.display).toBe('block');
    expect(document.getElementById('metrics-cost-total').textContent).toContain('0.015');
    // toLocaleString('en-US') usa virgula; HappyDOM pode usar ponto
    const promptTokens = document.getElementById('metrics-prompt-tokens').textContent;
    const hasCorrectNumber = promptTokens === '1,000' || promptTokens === '1000' || promptTokens === '1.000';
    expect(hasCorrectNumber).toBe(true);
    expect(document.getElementById('metrics-cache-tokens').textContent).toBe('200');
  });

  it('renderMetrics esconde card quando metrics ausentes', () => {
    Metrics.renderMetrics({});
    expect(document.getElementById('observability-card').style.display).toBe('none');
  });

  it('renderMetrics lida com metrics nulo', () => {
    Metrics.renderMetrics({ metrics: null });
    expect(document.getElementById('observability-card').style.display).toBe('none');
  });

  it('renderMetrics mostra tabela de runs para multiplas rodadas', () => {
    const data = {
      metrics: {
        cost_total: 0.03,
        prompt_tokens: 2000,
        cache_tokens: 400,
        completion_tokens: 1000,
        runs: [
          { run: 1, prompt_tokens: 1000, cache_tokens: 200, completion_tokens: 500, cost_total: 0.01 },
          { run: 2, prompt_tokens: 1000, cache_tokens: 200, completion_tokens: 500, cost_total: 0.01 },
        ],
      },
    };

    Metrics.renderMetrics(data);

    const runsContainer = document.getElementById('runs-observability-container');
    expect(runsContainer.style.display).toBe('block');
    const rows = document.getElementById('runs-observability-body').querySelectorAll('tr');
    expect(rows.length).toBe(2);
    expect(rows[0].textContent).toContain('Rodada 1');
    expect(rows[1].textContent).toContain('Rodada 2');
  });

  it('renderMetrics esconde tabela para 1 rodada', () => {
    const data = {
      metrics: {
        cost_total: 0.01,
        prompt_tokens: 1000,
        cache_tokens: 0,
        completion_tokens: 500,
        runs: [{ run: 1, prompt_tokens: 1000, cache_tokens: 0, completion_tokens: 500, cost_total: 0.01 }],
      },
    };

    Metrics.renderMetrics(data);

    expect(document.getElementById('runs-observability-container').style.display).toBe('none');
  });
});
