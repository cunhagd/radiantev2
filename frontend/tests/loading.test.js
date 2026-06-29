/* ============================================================
   Radiante v2 — Tests: loading.js
   ============================================================ */

import { describe, it, expect, beforeEach, vi } from 'vitest';

import '../js/state.js';
import '../js/api.js';
import '../js/loading.js';

// Mock global alert
global.alert = vi.fn();

/**
 * Cria o HTML minimo necessario para os testes de timeline.
 */
function createTimelineFixture() {
  document.body.innerHTML = `
    <div id="loading-overlay" style="display:none">
      <div id="loading-timer">00:00</div>
      <div id="loading-title"></div>
      <div id="loading-subtitle"></div>
      <div id="timeline-container">
        <div id="m3-timeline"></div>
      </div>
    </div>
    <button id="btn-upload" disabled>Upload</button>
    <button id="btn-once" disabled>1x</button>
    <button id="btn-ten" disabled>10x</button>
    <button id="btn-clear" disabled>Clear</button>
  `;
  if (typeof window.initDOM === 'function') {
    window.initDOM();
  }
}

describe('Loading Module', () => {
  beforeEach(() => {
    createTimelineFixture();

    // Reseta STATE timers
    window.STATE.timerId = null;
    window.STATE.intervalId = null;
    window.STATE.pollingId = null;

    vi.clearAllMocks();
  });

  /* ============================================================
     T016 — buildTimelineHTML
  ============================================================ */
  describe('buildTimelineHTML', () => {
    it('gera 4 steps principais para modo 1x (totalRuns=1)', () => {
      var html = Loading._buildTimelineHTML(1);
      document.getElementById('m3-timeline').innerHTML = html;

      var steps = document.querySelectorAll('.m3-step');
      expect(steps.length).toBe(4);

      var substeps = document.querySelectorAll('.m3-substep');
      expect(substeps.length).toBe(1); // etapa 3 com 1 sub-step
    });

    it('gera 4 steps e 10 sub-steps para modo 10x (totalRuns=10)', () => {
      var html = Loading._buildTimelineHTML(10);
      document.getElementById('m3-timeline').innerHTML = html;

      var steps = document.querySelectorAll('.m3-step');
      expect(steps.length).toBe(4);

      var substeps = document.querySelectorAll('.m3-substep');
      expect(substeps.length).toBe(10); // etapa 3 com 10 sub-steps
    });

    it('usa default 10 se nenhum parametro passado', () => {
      var html = Loading._buildTimelineHTML();
      document.getElementById('m3-timeline').innerHTML = html;

      var substeps = document.querySelectorAll('.m3-substep');
      expect(substeps.length).toBe(10);
    });
  });

  /* ============================================================
     T017 — setStep
  ============================================================ */
  /**
   * Helper: insere a timeline HTML no DOM para testes.
   */
  function renderTimeline(n) {
    document.getElementById('m3-timeline').innerHTML = Loading._buildTimelineHTML(n);
  }

  describe('setStep', () => {
    beforeEach(function () {
      renderTimeline(1);
    });

    it('aplica classe is-pending para status pending', () => {
      Loading._setStep(1, 'pending', 'Teste', 'Aguardando');
      var el = document.getElementById('m3-step-1');
      expect(el.className).toContain('m3-step');
      expect(el.className).not.toContain('is-'); // pending nao adiciona classe
    });

    it('aplica classe is-active para status active', () => {
      Loading._setStep(1, 'active', 'Teste', 'Processando');
      var el = document.getElementById('m3-step-1');
      expect(el.className).toContain('is-active');
    });

    it('aplica classe is-done para status done', () => {
      Loading._setStep(1, 'done', 'Teste', 'Concluído');
      var el = document.getElementById('m3-step-1');
      expect(el.className).toContain('is-done');
    });

    it('aplica classe is-error para status error', () => {
      Loading._setStep(1, 'error', 'Teste', 'Falhou');
      var el = document.getElementById('m3-step-1');
      expect(el.className).toContain('is-error');
    });

    it('atualiza label e badge', () => {
      Loading._setStep(2, 'done', 'Minha etapa', 'Concluído');
      var lbl = document.querySelector('#m3-step-2 .m3-step-label');
      expect(lbl.textContent).toBe('Minha etapa');
      var badge = document.querySelector('#m3-step-2 .m3-step-badge');
      expect(badge.textContent).toBe('Concluído');
    });
  });

  /* ============================================================
     T018 — setSubStep
  ============================================================ */
  describe('setSubStep', () => {
    beforeEach(function () {
      renderTimeline(10);
    });

    it('aplica classes CSS corretas para cada status', () => {
      Loading._setSubStep(0, 'active', 'Rodando...');
      var el = document.getElementById('m3-sub-0');
      expect(el.className).toContain('is-active');
      var badge = el.querySelector('.m3-substep-badge');
      expect(badge.textContent).toBe('Processando');
    });

    it('exibe badge "Concluído" quando status done', () => {
      Loading._setSubStep(5, 'done', 'OK');
      var badge = document.querySelector('#m3-sub-5 .m3-substep-badge');
      expect(badge.textContent).toBe('Concluído');
    });

    it('exibe badge "Falhou" quando status error', () => {
      Loading._setSubStep(3, 'error', 'Falha');
      var badge = document.querySelector('#m3-sub-3 .m3-substep-badge');
      expect(badge.textContent).toBe('Falhou');
    });

    it('nao quebra para indices inexistentes', () => {
      renderTimeline(1);
      // So existe m3-sub-0
      expect(() => Loading._setSubStep(99, 'done', 'Nope')).not.toThrow();
    });
  });

  /* ============================================================
     T019 — updateTimeline
  ============================================================ */
  describe('updateTimeline', () => {
    beforeEach(function () {
      renderTimeline(1);
    });

    it('retorna sem erro se progress for null/undefined', () => {
      expect(() => Loading._updateTimeline(null)).not.toThrow();
      expect(() => Loading._updateTimeline(undefined)).not.toThrow();
    });

    it('mapeia status corretamente para cada etapa', () => {
      var progress = {
        etapa1: { status: 'completed', label: 'Etapa 1' },
        etapa2: { status: 'processing', label: 'Etapa 2' },
        etapa3: [{ status: 'pending', label: 'Analise' }],
        etapa4: { status: 'pending', label: 'Etapa 4' },
        total_runs: 1,
      };

      Loading._updateTimeline(progress);

      var step1 = document.getElementById('m3-step-1');
      expect(step1.className).toContain('is-done');

      var step2 = document.getElementById('m3-step-2');
      expect(step2.className).toContain('is-active');

      var step3 = document.getElementById('m3-step-3');
      expect(step3.className).not.toContain('is-'); // pending = sem classe

      var step4 = document.getElementById('m3-step-4');
      expect(step4.className).not.toContain('is-'); // pending = sem classe
    });

    it('atualiza badge da etapa 3 com contador para 10x', () => {
      renderTimeline(10);

      var etapa3 = [];
      for (var i = 0; i < 10; i++) {
        etapa3.push({ status: i < 3 ? 'completed' : i === 3 ? 'processing' : 'pending', label: 'Rodada ' + (i + 1) });
      }

      var progress = {
        etapa3: etapa3,
        total_runs: 10,
      };

      Loading._updateTimeline(progress);

      var badge = document.querySelector('#m3-step-3 .m3-step-badge');
      expect(badge.textContent).toContain('3/10'); // 3 completed, 1 processing
      expect(badge.textContent).toContain('em andamento');

      expect(document.getElementById('m3-step-3').className).toContain('is-active');
    });

    it('exibe "10/10 concluídas" quando todas as 10 rodadas done', () => {
      renderTimeline(10);

      var etapa3 = [];
      for (var i = 0; i < 10; i++) {
        etapa3.push({ status: 'completed', label: 'Rodada ' + (i + 1) });
      }

      var progress = {
        etapa3: etapa3,
        total_runs: 10,
      };

      Loading._updateTimeline(progress);

      var badge = document.querySelector('#m3-step-3 .m3-step-badge');
      expect(badge.textContent).toContain('10/10');
      expect(document.getElementById('m3-step-3').className).toContain('is-done');
    });

    it('trata dados incompletos graciosamente (etapas faltando)', () => {
      renderTimeline(1);

      // Apenas etapa3, sem etapa1/etapa2/etapa4
      var progress = {
        etapa3: [{ status: 'completed', label: 'Unica' }],
        total_runs: 1,
      };

      expect(() => Loading._updateTimeline(progress)).not.toThrow();

      // Nao deve ter quebrado
      var step1 = document.getElementById('m3-step-1');
      expect(step1.className).toContain('m3-step');
    });

    it('mapeia status error corretamente', () => {
      renderTimeline(1);

      var progress = {
        etapa1: { status: 'error', label: 'Falhou' },
        total_runs: 1,
      };

      Loading._updateTimeline(progress);

      var step1 = document.getElementById('m3-step-1');
      expect(step1.className).toContain('is-error');
      var badge = document.querySelector('#m3-step-1 .m3-step-badge');
      expect(badge.textContent).toBe('Falhou');
    });
  });

  /* ============================================================
     T020 — forceAllDone
  ============================================================ */
  describe('forceAllDone', () => {
    beforeEach(function () {
      renderTimeline(1);
    });

    it('forca todas as etapas para done, mesmo se ausentes', () => {

      Loading._forceAllDone({ total_runs: 1 });

      for (var i = 1; i <= 4; i++) {
        var step = document.getElementById('m3-step-' + i);
        expect(step.className).toContain('is-done');
      }
    });

    it('etapa 3 marca sub-steps como done', () => {
      renderTimeline(10);

      var etapa3 = [];
      for (var i = 0; i < 10; i++) {
        etapa3.push({ status: 'pending', label: 'Rodada ' + (i + 1) });
      }

      Loading._forceAllDone({ etapa3: etapa3, total_runs: 10 });

      var substeps = document.querySelectorAll('.m3-substep');
      substeps.forEach(function (el) {
        expect(el.className).toContain('is-done');
      });
    });

    it('nao sobrescreve etapas ja concluidas no progress', () => {
      renderTimeline(1);

      // Etapa 1 ja esta completed, etapa 2 nao
      var progress = {
        etapa1: { status: 'completed', label: 'Feito' },
        total_runs: 1,
      };

      Loading._forceAllDone(progress);

      // Etapa 1 ja estava completed, entao deve manter label original "Etapa 1 — Extração de Cabeçalho"
      var lbl = document.querySelector('#m3-step-1 .m3-step-label');
      expect(lbl.textContent).toContain('Extra');

      // Etapa 2 deve ser forcada
      var lbl2 = document.querySelector('#m3-step-2 .m3-step-label');
      expect(lbl2.textContent).toBe('Cifras calculadas');
    });
  });

  /* ============================================================
     T021 — cleanupLoading
  ============================================================ */
  describe('cleanupLoading', () => {
    it('esconde overlay e reabilita botoes', () => {
      document.getElementById('loading-overlay').style.display = 'flex';
      Loading.cleanupLoading();
      expect(document.getElementById('loading-overlay').style.display).toBe('none');
      expect(document.getElementById('btn-once').disabled).toBe(false);
      expect(document.getElementById('btn-ten').disabled).toBe(false);
    });

    it('limpa STATE timers', () => {
      STATE.timerId = setInterval(() => {}, 100000);
      STATE.pollingId = setInterval(() => {}, 100000);
      Loading.cleanupLoading();
      expect(STATE.timerId).toBeNull();
      expect(STATE.pollingId).toBeNull();
    });
  });

  /* ============================================================
     runAnalysis — test coverage
  ============================================================ */
  describe('runAnalysis', () => {
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

    it('runAnalysis("once") define titulo correto', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        status: 202,
        json: () => Promise.resolve({ status: 'completed' }),
      });

      // Mock API.checkStatus para retornar completed na primeira chamada
      API.checkStatus = vi.fn().mockResolvedValue({ status: 'completed' });

      // Mock API.loadLastResult
      API.loadLastResult = vi.fn().mockResolvedValue(null);

      Loading.runAnalysis('once');

      await vi.waitFor(() => {
        expect(document.getElementById('loading-title').textContent).toBe('Análise única em andamento');
      }, { timeout: 3000 });
    });

    it('runAnalysis("ten") define titulo correto', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        status: 202,
        json: () => Promise.resolve({ status: 'completed' }),
      });

      API.checkStatus = vi.fn().mockResolvedValue({ status: 'completed' });
      API.loadLastResult = vi.fn().mockResolvedValue(null);

      Loading.runAnalysis('ten');

      await vi.waitFor(() => {
        expect(document.getElementById('loading-title').textContent).toBe('Análise 10x em andamento');
      }, { timeout: 3000 });
    });
  });
});
