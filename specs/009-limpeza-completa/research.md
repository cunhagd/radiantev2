# Research: Limpeza Completa do Sistema

## Decisoes Tecnicas

### 1. Mecanismo de Limpeza Local
- **Decisao**: Usar `shutil.rmtree()` para subdiretorios e `Path.unlink()` para arquivos na raiz de `data/`
- **Rationale**: `shutil.rmtree` remove recursivamente diretorios inteiros de forma atomica e confiavel.
  Arquivos soltos na raiz (PDFs, JSONs) sao removidos individualmente por extensao.
- **Alternativas consideradas**:
  - `os.remove()` em loop manual: menos robusto para subdiretorios aninhados
  - `subprocess` chamando `rm -rf`: dependente de sistema operacional

### 2. Ordem de Limpeza
- **Decisao**: Local -> S3 -> Memoria -> Progress -> Historico -> Frontend
- **Rationale**: 
  1. Local primeiro (mais rapido, sem dependencia de rede)
  2. S3 em segundo (pode falhar — nao deve bloquear os demais)
  3. Memoria/Progress/Historico sao resets de variaveis (instantaneos)
  4. Frontend por ultimo (resposta HTTP ja foi enviada, frontend processa o callback)

### 3. Tolerancia a Falhas
- **Decisao**: Falhas parciais (ex: S3 indisponivel) nao interrompem a limpeza dos demais locais
- **Rationale**: O sistema deve maximizar a limpeza possivel mesmo em cenarios de erro.
  Cada etapa e isolada em seu proprio bloco try/except.
- **Alternativas consideradas**:
  - Rollback em caso de falha: complexo demais para o escopo do projeto

### 4. Reset de Memoria
- **Decisao**: Resetar ANALYSIS_JOBS via `.update()` para estado inicial, nao recriar o dict
- **Rationale**: Evita problemas de referencia se alguma thread ainda estiver segurando
  o objeto antigo. `update()` mantem a mesma referencia na memoria.
