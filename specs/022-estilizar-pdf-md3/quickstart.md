# Quickstart: Estilizar PDF com Material Design 3 (022)

## Pré-requisitos

- Feature 021 concluída (`backend/pdf_generator.py` refatorado com estilo simples)
- `data/etapas/` com arquivos etapa1.md a etapa4.md (gerados pelo pipeline)
- `data/resultado_final.json` com metadados do processo (para a capa)
- Python 3.14+ e `reportlab` instalado

---

## Validação 1 — Gerar PDF com cores MD3

Testa a função `generate_pdf()` com os arquivos de etapa existentes, verificando que as cores MD3 são aplicadas.

```powershell
cd C:\radiantev2
python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas', 'data/teste_md3.pdf'); print(f'PDF gerado: {p}')"
```

**Resultado esperado**: PDF gerado sem erros. Ao abrir:
- Cabeçalho "Radiante — Análise Jurídica" na cor primary (#6750A4)
- Títulos H1 em primary, H2 em secondary, H3 em tertiary
- Entre etapas, divisores HRFlowable + accent bars
- Tabelas com cabeçalho primary e texto branco
- Código com fundo surface variant e borda outline

---

## Validação 2 — Verificar página de capa

```powershell
Start-Process "C:\radiantev2\data\teste_md3.pdf"
```

**Resultado esperado**:
- Primeira página: capa com título "Radiante", subtítulo "Análise Jurídica"
- Dados do processo: número, autor, reclamada, valor total estimado, data
- Capa sem cabeçalho "Radiante — Análise Jurídica" (apenas conteúdo centralizado)

---

## Validação 3 — Gerar pelo pipeline

```powershell
cd C:\radiantev2
python backend/pipeline.py
```

**Resultado esperado**: Pipeline executa sem erros. `data/relatorio_consolidado.pdf` gerado com estilo MD3 completo.

---

## Validação 4 — Fallback sem resultado_final.json

```powershell
cd C:\radiantev2
Move-Item "data/resultado_final.json" "data/resultado_final.json.bak"
python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas', 'data/teste_sem_capa.pdf'); print(f'PDF gerado: {p}')"
Move-Item "data/resultado_final.json.bak" "data/resultado_final.json"
```

**Resultado esperado**: PDF gerado sem capa (começa direto com as etapas), sem erros.

---

## Validação 5 — Fallback sem conteúdo

```powershell
cd C:\radiantev2
New-Item -ItemType Directory -Force -Path "data/etapas_vazio" | Out-Null
python -c "from backend.pdf_generator import generate_pdf; p = generate_pdf('data/etapas_vazio', 'data/teste_vazio.pdf'); print(f'PDF gerado: {p}')"
Remove-Item -Recurse -Force "data/etapas_vazio"
```

**Resultado esperado**: PDF gerado com mensagem "Nenhum conteúdo disponível para o relatório."

---

## Detalhes da Implementação

| Item | Referência |
|------|------------|
| Contrato da função | [contracts/generate_pdf.md](contracts/generate_pdf.md) |
| Data Model | [data-model.md](data-model.md) |
| Pesquisa técnica | [research.md](research.md) |
