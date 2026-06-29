# Feature Specification: Correcao de Consistencia de PDFs e JSONs

**Feature Branch**: `013-fix-pdf-consistency`

**Created**: 2026-06-29

**Status**: Draft

**Input**: Correcao de bugs na geracao e servicao de PDFs/JSONs e garantia de que apenas um arquivo de cada tipo exista na pasta data/

## User Scenarios & Testing

### User Story 1 - Botao "Baixar Relatorio PDF" sempre encontra o PDF correto (Priority: P1)

O usuario faz uma analise 1x ou 10x e, ao finalizar, clica no botao "Baixar Relatorio PDF". O sistema deve baixar o PDF correto gerado pela analise atual, nao importando qual modo foi usado.

**Why this priority**: Sem esta correcao, o botao de download fica quebrado (link 404), impedindo o usuario de obter o relatorio em PDF.

**Independent Test**: Executar analise 1x, aguardar conclusao, clicar em "Baixar Relatorio PDF" e confirmar que o download inicia com o conteudo correto.

**Acceptance Scenarios**:

1. **Given** que uma analise 1x foi concluida com sucesso, **When** o usuario clica em "Baixar Relatorio PDF", **Then** o arquivo baixado e `relatorio_consolidado.pdf` com o conteudo correto.
2. **Given** que uma analise 10x foi concluida com sucesso, **When** o usuario clica em "Baixar Relatorio PDF", **Then** o arquivo baixado e `relatorio_consolidado_10x.pdf` com o conteudo correto.
3. **Given** que o backend retorna o resultado da analise, **When** o frontend renderiza os dados, **Then** o link de download do PDF usa o nome do arquivo informado pelo backend, nao uma heuristica de deteccao de modo.

---

### User Story 2 - Navegacao "/data/relatorio_consolidado.pdf" SEMPRE retorna 200 se o arquivo existe (Priority: P1)

O servidor deve servir corretamente o PDF solicitado pelo frontend, independentemente de query strings ou caracteres especiais no path.

**Why this priority**: O log mostra 404 ao acessar `/data/relatorio_consolidado.pdf`, indicando que a rota de arquivos estaticos na pasta data/ nao esta funcionando corretamente.

**Independent Test**: Acessar `http://localhost:8000/data/relatorio_consolidado.pdf` diretamente no navegador apos uma analise 1x e verificar que o PDF e exibido.

**Acceptance Scenarios**:

1. **Given** que o arquivo `data/relatorio_consolidado.pdf` existe no servidor, **When** o frontend ou usuario acessa `GET /data/relatorio_consolidado.pdf`, **Then** o servidor retorna 200 com o conteudo do PDF.
2. **Given** que o arquivo `data/relatorio_consolidado_10x.pdf` existe no servidor, **When** acessado via `GET /data/relatorio_consolidado_10x.pdf`, **Then** o servidor retorna 200 com o conteudo do PDF.
3. **Given** que o arquivo solicitado nao existe, **Then** o servidor retorna 404 com mensagem apropriada.

---

### User Story 3 - Arquivos antigos sao sempre removidos antes de gerar novos (Priority: P1)

O sistema nunca deve permitir que dois PDFs ou dois JSONs coexistam na pasta `data/` apos uma nova analise. O arquivo gerado anteriormente (de qualquer modo) deve ser removido antes da criacao do novo.

**Why this priority**: Se `relatorio_consolidado.pdf` (modo 1x) e `relatorio_consolidado_10x.pdf` (modo 10x) existirem simultaneamente, o frontend pode servir o arquivo errado, causando divergencia de dados.

**Independent Test**: Executar analise 1x (gera `relatorio_consolidado.pdf`), depois analise 10x — verificar que `relatorio_consolidado.pdf` foi removido e apenas `relatorio_consolidado_10x.pdf` existe.

**Acceptance Scenarios**:

1. **Given** que existe `data/relatorio_consolidado.pdf` de uma analise 1x anterior, **When** uma nova analise 10x e executada, **Then** `relatorio_consolidado.pdf` e deletado antes de gerar `relatorio_consolidado_10x.pdf`.
2. **Given** que existe `data/relatorio_consolidado_10x.pdf` de uma analise 10x anterior, **When** uma nova analise 1x e executada, **Then** `relatorio_consolidado_10x.pdf` e deletado antes de gerar `relatorio_consolidado.pdf`.
3. **Given** que existe `data/resultado_final.json` de uma analise 1x anterior, **When** uma nova analise 10x e executada, **Then** `resultado_final.json` e deletado antes de gerar `consolidado_10x.json`.
4. **Given** que existe `data/consolidado_10x.json` de uma analise 10x anterior, **When** uma nova analise 1x e executada, **Then** `consolidado_10x.json` e deletado antes de gerar `resultado_final.json`.

---

### Edge Cases

- **Primeira execucao**: Se nao ha arquivos previos na pasta `data/`, a limpeza nao deve causar erro — o sistema deve gerar os novos arquivos normalmente.
- **Arquivos de outros tipos**: Arquivos `.md` (como `auditoria_10x.md`) e diretorios (`docs/`, `markdown_docs/`) nao sao afetados por esta regra — apenas PDFs e JSONs de resultado.
- **S3 tambem deve refletir a limpeza**: Uploads para S3 devem remover artefatos antigos antes de enviar os novos, mantendo os buckets consistente com o estado local.

---

### User Story 4 - Backend informa explicitamente o nome do PDF gerado (Priority: P2)

O endpoint `/api/last-result` deve incluir o nome do arquivo PDF gerado pela analise atual, eliminando a necessidade de heuristica no frontend para determinar qual PDF servir.

**Why this priority**: A heuristica atual (`data.total_runs !== undefined`) e frágil e pode falhar dependendo do formato dos dados armazenados.

**Independent Test**: Chamar `GET /api/last-result` apos analise 1x e verificar que o campo `pdf_filename` contem `relatorio_consolidado.pdf`.

**Acceptance Scenarios**:

1. **Given** que uma analise 1x foi concluida, **When** o frontend chama `GET /api/last-result`, **Then** a resposta inclui `"pdf_filename": "relatorio_consolidado.pdf"`.
2. **Given** que uma analise 10x foi concluida, **When** o frontend chama `GET /api/last-result`, **Then** a resposta inclui `"pdf_filename": "relatorio_consolidado_10x.pdf"`.
3. **Given** que nao ha resultado disponivel, **When** o frontend chama `GET /api/last-result`, **Then** o campo `pdf_filename` nao esta presente (ou e `null`).

---

## Requirements

### Functional Requirements

- **FR-001**: O backend DEVE garantir que, ao iniciar a geracao de um novo PDF de resultado, todos os PDFs de resultado existentes na pasta `data/` sejam removidos primeiro.
- **FR-002**: O backend DEVE garantir que, ao iniciar a geracao de um novo JSON de resultado, todos os JSONs de resultado existentes na pasta `data/` sejam removidos primeiro.
- **FR-003**: O endpoint `GET /data/<filename>` DEVE servir corretamente arquivos PDF e JSON da pasta `data/`, retornando 200 com o conteudo se o arquivo existir.
- **FR-004**: O endpoint `/api/last-result` DEVE incluir o campo `pdf_filename` com o nome do arquivo PDF gerado pela analise atual.
- **FR-005**: O frontend DEVE usar o campo `pdf_filename` do `/api/last-result` para construir o link de download do PDF, em vez de heuristica de deteccao de modo.
- **FR-006**: A regra de exclusao de arquivos antigos DEVE aplicar-se tambem ao bucket S3 `radiante-final`, removendo artefatos do modo oposto antes do upload do novo.
- **FR-007**: A limpeza de arquivos antigos na pasta `data/` DEVE ocorrer na funcao que gera o resultado (`run_once` e `run_ten_times` em `backend/pipeline.py`), antes da geracao do novo arquivo.

### Key Entities

- **Arquivo PDF de resultado**: `relatorio_consolidado.pdf` (modo 1x) ou `relatorio_consolidado_10x.pdf` (modo 10x)
- **Arquivo JSON de resultado**: `resultado_final.json` (modo 1x) ou `consolidado_10x.json` (modo 10x)
- **Pasta `data/`**: Diretorio local no servidor onde os arquivos sao salvos
- **Bucket S3 `radiante-final`**: Armazenamento secundario para fallback

## Success Criteria

### Measurable Outcomes

- **SC-001**: Apos qualquer analise (1x ou 10x), o botao "Baixar Relatorio PDF" inicia o download correto sem erros 404.
- **SC-002**: Nunca ha mais de um PDF de resultado e mais de um JSON de resultado na pasta `data/` apos a conclusao de uma analise.
- **SC-003**: O endpoint `/api/last-result` sempre inclui `pdf_filename` quando ha dados disponiveis.
- **SC-004**: Navegacao direta para `/data/relatorio_consolidado.pdf` ou `/data/relatorio_consolidado_10x.pdf` retorna 200 se o arquivo existir.

## Assumptions

- O diretorio `data/` pode conter outros arquivos como `auditoria_10x.md` e subdiretorios `docs/`, `markdown_docs/` — estes nao devem ser afetados pelas regras de limpeza de PDFs e JSONs.
- A remocao de arquivos antigos no S3 e um fallback — o armazenamento local e a fonte primaria de verdade.
