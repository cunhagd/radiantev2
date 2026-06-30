# Quickstart: Refatorar PDF para estilo simples (021)

## Pré-requisitos

- Projeto Radiante v2 clonado e configurado
- `data/etapas/` com arquivos etapa1.md a etapa4.md (gerados pelo pipeline)
- Python 3.14+
- `reportlab` instalado (já presente em `requirements.txt`)

---

## Validação 1 — Gerar PDF manualmente via Python

Testa a função `generate_pdf()` diretamente com os arquivos de etapa existentes:

```powershell
cd C:\radiantev2
python -c "from backend.pdf_generator import generate_pdf; import pathlib; p = generate_pdf('data/etapas', 'data/teste_simples.pdf'); print(f'PDF gerado: {p}')"
```

**Resultado esperado**: PDF gerado em `data/teste_simples.pdf`, sem erros.

---

## Validação 2 — Abrir o PDF gerado

```powershell
Start-Process "C:\radiantev2\data\teste_simples.pdf"
```

**Resultado esperado**: PDF abre corretamente no visualizador padrão, com:
- Cabeçalho "Radiante — Análise Jurídica" em todas as páginas
- Rodapé "Página X de Y"
- Todas as etapas visíveis (etapa1 a etapa4)
- Tabelas com linhas simples

---

## Validação 3 — Gerar sem arquivos de etapa (fallback)

```powershell
cd C:\radiantev2
mkdir data/etapas_vazio
python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas_vazio', 'data/teste_vazio.pdf'); print(f'PDF gerado: {p}')"
rmdir data/etapas_vazio
```

**Resultado esperado**: PDF gerado com mensagem "Nenhum conteúdo disponível para o relatório."

---

## Validação 4 — Gerar pelo pipeline 1x

```powershell
cd C:\radiantev2
python backend/pipeline.py
```

**Resultado esperado**: Pipeline executa sem erros e gera `data/relatorio_consolidado.pdf` com todas as etapas.

---

## Validação 5 — Verificar código (máx 200 linhas)

```powershell
(Get-Content backend/pdf_generator.py).Count
```

**Resultado esperado**: Número <= 200 linhas.

---

## Detalhes da Implementação

| Item | Referência |
|------|------------|
| Contrato da função | [contracts/generate_pdf.md](contracts/generate_pdf.md) |
| Data Model | [data-model.md](data-model.md) |
| Pesquisa técnica | [research.md](research.md) |
