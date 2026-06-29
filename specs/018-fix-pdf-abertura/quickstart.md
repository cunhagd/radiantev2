# Quickstart: Corrigir Abertura do PDF Consolidado

## Pre-requisitos

- Servidor rodando: `python dev.py --server` ou `python -m backend.app --mode web --port 8000`
- `.env` configurado com credenciais AWS e precos Grok

## Cenarios de Validacao

### Cenario 1: PDF com conteudo valido abre corretamente

1. Execute o helper de teste:
   ```bash
   python -c "
   import sys; sys.path.insert(0, '.')
   from backend.pdf_generator import generate_pdf
   text = '# Teste\n\n## Etapa 1 - Metadados\n\nConteudo valido'
   print(generate_pdf(text, 'data/test_valid.pdf'))
   "
   ```
2. **Esperado**: PDF gerado com sucesso, abre em qualquer leitor

### Cenario 2: PDF com conteudo extenso quebra corretamente entre paginas

1. Execute o helper com 50 rubricas:
   ```bash
   python -c "
   import sys; sys.path.insert(0, '.')
   from backend.pdf_generator import generate_pdf
   items = '\n'.join(f'| Item {i} | R\\$ {i*100:,.2f} |' for i in range(1, 51))
   text = f'# Relatorio\n\n## Etapa 2 - Cifras\n\n{items}'
   print(generate_pdf(text, 'data/test_extenso.pdf'))
   "
   ```
2. **Esperado**: PDF com multiplas paginas, sem erro "Flowable too large"

### Cenario 3: Pipeline completo (1x e 10x)

1. Suba o servidor
2. Faca upload de um documento juridico
3. Clique em "1x" e aguarde
4. Clique em "Baixar Relatorio PDF"
5. **Esperado**: PDF abre sem erros no navegador
6. Repita com "10x"
7. **Esperado**: PDF 10x tambem abre sem erros

### Cenario 4: Validacao estrutural automatizada

```bash
python -c "
import sys; sys.path.insert(0, '.')
from backend.pdf_generator import generate_pdf
from pathlib import Path

text = '# Teste\n\n## Etapa 1\n\nConteudo'
p = Path(generate_pdf(text, 'data/test_valid.pdf'))
data = p.read_bytes()

assert data.startswith(b'%PDF-'), 'Header PDF ausente'
assert data.strip().endswith(b'%%EOF'), 'EOF marker ausente'
# Verifica pelo menos 1 pagina
assert b'/Count 1' in data or b'/Count 2' in data or b'/Count 3' in data or b'/Kids [' in data, 'Sem paginas'
print('VALIDACAO ESTRUTURAL OK')
"
```
