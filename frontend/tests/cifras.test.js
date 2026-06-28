/* ============================================================
   Radiante v2 — Tests: cifras.js
   ============================================================ */

import { describe, it, expect, beforeEach } from 'vitest';

// Carrega os modulos necessarios
import '../js/state.js';
import '../js/cifras.js';

describe('Cifras Module', () => {
  beforeEach(() => {
    // Garante que o DOM esta limpo antes de cada teste
    document.getElementById('cifras-fluent-list').innerHTML =
      '<div class="empty-state">Nenhum dado. Inicie uma analise.</div>';
    document.getElementById('kpi-total').textContent = 'R$ 0,00';
    ['meta-processo', 'meta-autor', 'meta-advogado', 'meta-reclamada',
     'meta-tomadora', 'meta-juizo', 'meta-localidade', 'meta-inicio',
     'meta-valor-causa'].forEach(function (id) {
      document.getElementById(id).textContent = '—';
    });
  });

  it('Cifras.renderMetadata preenche campos corretamente', () => {
    const data = {
      numero_processo: '0000000-00.0000.0.00.0000',
      autor: 'Joao Silva',
      adv_reclamante: 'Dr. Oliveira',
      reclamada: 'Empresa X',
      juizo: '1a Vara do Trabalho',
      valor_causa: '50.000,00',
    };

    Cifras.renderMetadata(data);

    expect(document.getElementById('meta-processo').textContent).toBe('0000000-00.0000.0.00.0000');
    expect(document.getElementById('meta-autor').textContent).toBe('Joao Silva');
    expect(document.getElementById('meta-advogado').textContent).toBe('Dr. Oliveira');
    expect(document.getElementById('meta-reclamada').textContent).toBe('Empresa X');
    expect(document.getElementById('meta-juizo').textContent).toBe('1a Vara do Trabalho');
    expect(document.getElementById('meta-valor-causa').textContent).toBe('R$ 50.000,00');
  });

  it('Cifras.renderMetadata usa fallback para — quando campos ausentes', () => {
    Cifras.renderMetadata({});
    expect(document.getElementById('meta-autor').textContent).toBe('-');
    expect(document.getElementById('meta-localidade').textContent).toBe('-');
  });

  it('Cifras.renderCifras mostra lista quando dados sao validos', () => {
    const data = {
      cifras: [
        { cifra: 'Salario', valor: '5.000,00', probabilidade: 'Certa', valor_estimado: '5.000,00', descricao: 'Salario base' },
        { cifra: 'FGTS', valor: '2.000,00', probabilidade: 'Provavel', valor_estimado: '1.500,00' },
      ],
      valor_total_estimado: '6.500,00',
    };

    Cifras.renderCifras(data);

    const listItems = document.querySelectorAll('.cifra-row-item');
    expect(listItems.length).toBe(2);
    expect(listItems[0].querySelector('.cifra-name').textContent).toBe('Salario');
    expect(listItems[1].querySelector('.cifra-name').textContent).toBe('FGTS');
    expect(document.getElementById('kpi-total').textContent).toBe('R$ 6.500,00');
  });

  it('Cifras.renderCifras mostra empty-state quando data.cifras vazio', () => {
    Cifras.renderCifras({ cifras: [] });
    expect(document.getElementById('cifras-fluent-list').innerHTML).toContain('Nenhum pleito');
  });

  it('Cifras.renderCifras lida com null', () => {
    Cifras.renderCifras(null);
    expect(document.getElementById('cifras-fluent-list').innerHTML).toContain('Nenhum pleito');
  });

  it('Badge classes sao aplicadas corretamente', () => {
    const data = {
      cifras: [
        { cifra: 'A', valor: '1', probabilidade: 'Certa', valor_estimado: '1' },
        { cifra: 'B', valor: '1', probabilidade: 'Provavel', valor_estimado: '1' },
        { cifra: 'C', valor: '1', probabilidade: 'Possivel', valor_estimado: '1' },
        { cifra: 'D', valor: '1', probabilidade: 'Remota', valor_estimado: '1' },
      ],
    };

    Cifras.renderCifras(data);

    const badges = document.querySelectorAll('.badge');
    expect(badges[0].className).toContain('badge-certa');
    expect(badges[1].className).toContain('badge-provavel');
    expect(badges[2].className).toContain('badge-possivel');
    expect(badges[3].className).toContain('badge-remota');
  });
});
