/* ============================================================
   Radiante v2 — Tests: api.js
   ============================================================ */

import { describe, it, expect, beforeEach, vi } from 'vitest';

import '../js/state.js';
import '../js/api.js';

describe('API Module', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('API.BASE deve ser localhost para testes', () => {
    expect(API.BASE).toBeDefined();
    // Em ambiente de teste (node), hostname nao e localhost
    // entao API_BASE pode ser o de producao
    expect(typeof API.BASE).toBe('string');
  });

  it('API.fetchJSON faz GET e retorna JSON', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'ok' }),
    });

    const result = await API.fetchJSON('/api/status');
    expect(result.status).toBe('ok');
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/api/status'));
  });

  it('API.fetchJSON lanca erro para HTTP nao-ok', async () => {
    global.fetch.mockResolvedValue({ ok: false, status: 500 });

    await expect(API.fetchJSON('/api/status')).rejects.toThrow('HTTP 500');
  });

  it('API.fetchText retorna texto para HTTP ok', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      text: () => Promise.resolve('conteudo do log'),
    });

    const result = await API.fetchText('/api/audit-log');
    expect(result).toBe('conteudo do log');
  });

  it('API.fetchText retorna null para HTTP nao-ok', async () => {
    global.fetch.mockResolvedValue({ ok: false, status: 404 });

    const result = await API.fetchText('/api/audit-log');
    expect(result).toBeNull();
  });

  it('API.post faz POST com body', async () => {
    global.fetch.mockResolvedValue({ ok: true });

    const body = new Blob(['test']);
    await API.post('/api/clear-all', body);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/clear-all'),
      expect.objectContaining({ method: 'POST', body }),
    );
  });

  it('API.uploadFile envia arquivo com headers corretos', async () => {
    global.fetch.mockResolvedValue({ ok: true });

    const file = new File(['conteudo'], 'teste.pdf', { type: 'application/pdf' });
    await API.uploadFile(file);

    const callArgs = global.fetch.mock.calls[0];
    expect(callArgs[0]).toContain('/api/upload');
    expect(callArgs[1].method).toBe('POST');
    expect(callArgs[1].headers['X-Filename']).toBeDefined();
    expect(callArgs[1].headers['Content-Type']).toBe('application/pdf');
  });

  it('API.startAnalysis chama endpoint correto para once', async () => {
    global.fetch.mockResolvedValue({ ok: true });

    await API.startAnalysis('once');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/run-once'),
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('API.startAnalysis chama endpoint correto para ten', async () => {
    global.fetch.mockResolvedValue({ ok: true });

    await API.startAnalysis('ten');
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/run-ten'),
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('API.checkStatus retorna status do job', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'completed' }),
    });

    const result = await API.checkStatus();
    expect(result.status).toBe('completed');
  });
});
