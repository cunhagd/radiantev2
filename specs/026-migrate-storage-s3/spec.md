# Feature Specification: Migrar Armazenamento Local para S3

**Feature Branch**: `026-migrate-storage-s3`

**Created**: 2026-06-30

**Status**: Draft

**Input**: Migrar 100% o armazenamento de dados que hoje utilizam a pasta data localmente, para o nosso s3 radiante-final. Não iremos mais armazenar dados localmente, contudo, upload, limpeza de dados devem considerar sempre o bucket radiante-final no s3 e não mais a pasta data local.

## User Scenarios & Testing

### User Story 1 - Upload de Documentos Direto para o S3 (Priority: P1)

Como usuário do sistema, ao fazer upload de um documento PDF ou JSON, quero que ele seja armazenado diretamente no bucket S3 `radiante-final`, sem depender de armazenamento local em disco, para que o sistema funcione de forma confiável em produção sem risco de perda de dados por falha de disco ou reinicialização da instância.

**Why this priority**: O upload é a porta de entrada de todo o fluxo de análise. Sem ele funcionando exclusivamente via S3, nenhuma análise pode ser executada.

**Independent Test**: Pode ser testado fazendo upload de um documento PDF pelo frontend e verificando sua presença no bucket S3 sob o prefixo `docs/`, sem que nenhum arquivo seja criado no diretório `data/docs/` do servidor.

**Acceptance Scenarios**:

1. **Given** que o usuário está na tela inicial, **When** ele faz upload de um arquivo PDF válido, **Then** o arquivo é salvo no S3 em `docs/{filename}` e **nenhum arquivo** é criado em `data/docs/` no servidor local.
2. **Given** que o upload foi concluído com sucesso, **When** o sistema precisa ler os documentos para iniciar uma análise, **Then** ele baixa os arquivos do S3 (prefixo `docs/`) sem procurar em diretório local.
3. **Given** que o bucket S3 está inacessível (ex: falha de rede), **When** o usuário tenta fazer upload, **Then** o sistema retorna erro informando que o serviço de armazenamento está indisponível.

---

### User Story 2 - Pipeline de Análise com Leitura/Escrita no S3 (Priority: P1)

Como operador do sistema, ao executar uma análise (modo 1x ou 10x), quero que todas as etapas do pipeline (etapas 1-4, JSON final, PDF, auditoria) sejam lidas e escritas exclusivamente no bucket S3 `radiante-final`, eliminando qualquer dependência do sistema de arquivos local para dados persistentes.

**Why this priority**: O pipeline é o coração do sistema. Garantir que ele opere 100% via S3 elimina problemas de sincronização entre instâncias e viabiliza o deploy em ambientes efêmeros (containers).

**Independent Test**: Pode ser testado executando uma análise 1x e verificando que os arquivos `results/etapa1_completo.md`, `results/resultado_final.json` e `results/relatorio_consolidado.pdf` existem no S3, enquanto o diretório `data/` local permanece vazio ou não é criado.

**Acceptance Scenarios**:

1. **Given** que existem documentos no S3 em `docs/`, **When** o usuário inicia uma análise 1x, **Then** o pipeline lê os documentos do S3, processa as 4 etapas, e salva cada etapa como `results/etapaN_completo.md` no S3 — sem criar arquivos em `data/etapas/`.
2. **Given** que a análise 1x foi concluída, **When** o pipeline gera o JSON final e o PDF, **Then** `results/resultado_final.json` e `results/relatorio_consolidado.pdf` são salvos no S3 — sem criar `data/resultado_final.json` ou `data/relatorio_consolidado.pdf` localmente.
3. **Given** que o usuário executa uma análise 10x, **When** todas as repetições são concluídas, **Then** os arquivos `results/consolidado_10x.json`, `results/relatorio_consolidado_10x.pdf` e `results/auditoria_10x.md` são salvos no S3 — sem versões locais em `data/`.

---

### User Story 3 - Visualização de Resultados via S3 (Priority: P2)

Como usuário do sistema, ao acessar o resultado de uma análise ou fazer download do PDF, quero que o sistema busque esses artefatos diretamente do S3, sem depender de cache local em disco.

**Why this priority**: Embora menos crítica que o upload e o pipeline, a visualização de resultados precisa funcionar sem armazenamento local para que o sistema seja resiliente em produção.

**Independent Test**: Pode ser testado executando uma análise, limpando manualmente o diretório `data/` local (simulando uma reinicialização), e verificando que os resultados e o PDF ainda são acessíveis pela interface.

**Acceptance Scenarios**:

1. **Given** que uma análise foi concluída, **When** o usuário acessa a página inicial, **Then** o endpoint `/api/last-result` retorna os dados buscando exclusivamente da memória cache ou do S3 (`results/consolidado_10x.json` ou `results/resultado_final.json`), sem fallback para arquivos locais.
2. **Given** que o usuário clica no link de download do PDF, **When** o frontend solicita o arquivo, **Then** o backend serve o PDF diretamente do S3 (streaming) sem depender de arquivo local em `data/`.
3. **Given** que o cache em memória foi limpo (ex: reinicialização do servidor), **When** o usuário acessa `/api/last-result`, **Then** o sistema busca o resultado mais recente diretamente do S3.

---

### User Story 4 - Limpeza de Dados Exclusivamente no S3 (Priority: P2)

Como operador do sistema, ao clicar em "Limpar Tudo", quero que apenas os dados no bucket S3 `radiante-final` sejam removidos, sem etapas de limpeza de sistema de arquivos local.

**Why this priority**: A limpeza de dados deve refletir que o S3 é a única fonte de verdade. Remover a etapa de limpeza local simplifica o código e evita falsa sensação de segurança.

**Independent Test**: Pode ser testado fazendo upload de documentos, executando análises, e então clicando em "Limpar Tudo" — deve mostrar apenas etapas S3 na timeline de limpeza (sem etapa "local") e o bucket deve ficar vazio.

**Acceptance Scenarios**:

1. **Given** que existem dados no S3, **When** o usuário clica em "Limpar Tudo", **Then** a timeline de progresso mostra apenas as etapas de limpeza S3: `docs/`, `markdown_docs/`, `results/`, `runs/` — sem a etapa "local".
2. **Given** que a limpeza foi concluída, **When** o sistema lista os arquivos no bucket, **Then** os prefixos `docs/`, `markdown_docs/`, `results/` e `runs/` estão vazios.

---

### Edge Cases

- **Bucket vazio e pipeline**: Se o bucket S3 `docs/` estiver vazio e o usuário tentar executar uma análise sem fazer upload, o sistema deve retornar erro "Nenhum documento disponível para análise" — sem tentar ler de diretório local.
- **Falha de rede no S3 durante upload**: Se a conexão com o S3 falhar durante o upload, o sistema deve retornar erro imediatamente, sem salvar cópia local como fallback.
- **Múltiplas instâncias**: Como o S3 é a única fonte de verdade, duas instâncias do backend apontando para o mesmo bucket devem ver exatamente os mesmos dados.
- **Permissões S3**: Se as credenciais AWS não tiverem permissão de escrita no bucket, o sistema deve falhar de forma clara e visível, e não silenciosamente.
- **PDF corrompido ou incompleto no S3**: O sistema deve validar a integridade do PDF antes de servir ao usuário.
- **Migração retroativa**: Dados existentes no diretório `data/` local (de sessões anteriores) não precisam ser migrados automaticamente para o S3 como parte desta feature. Apenas dados novos serão 100% S3.

## Requirements

### Functional Requirements

- **FR-001**: O upload de documentos (`POST /api/upload`) DEVE salvar o arquivo diretamente no S3 (`docs/{filename}`) e NÃO DEVE criar cópia local em `data/docs/`.
- **FR-002**: A leitura de contexto para análise (`get_s3_combined_context`) DEVE baixar documentos exclusivamente do prefixo `docs/` no S3, sem fallback para `data/docs/` local.
- **FR-003**: O pipeline DEVE salvar cada etapa (1-4) como `results/etapaN_completo.md` diretamente no S3, sem passar por `data/etapas/` local.
- **FR-004**: O JSON final de resultado (`resultado_final.json` modo 1x, `consolidado_10x.json` modo 10x) DEVE ser salvo exclusivamente no S3 (`results/`), sem versão local em `data/`.
- **FR-005**: O PDF consolidado DEVE ser salvo exclusivamente no S3 (`results/relatorio_consolidado.pdf`), sem versão local em `data/`.
- **FR-006**: O arquivo de auditoria (modo 10x) DEVE ser salvo exclusivamente no S3 (`results/auditoria_10x.md`), sem versão local em `data/`.
- **FR-007**: O endpoint `/api/last-result` DEVE buscar resultados apenas da memória cache ou do S3 (`results/consolidado_10x.json` → `results/resultado_final.json`), removendo o fallback para arquivos locais (`data/consolidado_10x.json` ou `data/resultado_final.json` do disco).
- **FR-008**: O endpoint `/data/{filename}` DEVE servir arquivos (PDFs) diretamente do S3, baixando para memória e transmitindo ao cliente, sem depender de arquivo local em `data/`.
- **FR-009**: A limpeza de dados (`POST /api/clear-all`) DEVE remover exclusivamente os dados do S3 (prefixos `docs/`, `markdown_docs/`, `results/`, `runs/`), sem limpar o diretório `data/` local.
- **FR-010**: A timeline SSE de limpeza (`loading.js`) NÃO DEVE mais incluir a etapa "local" — apenas as etapas S3 (`s3_docs`, `s3_markdown`, `s3_results`, `s3_runs`).
- **FR-011**: O gerador de PDF (`pdf_generator.py`) DEVE receber os dados das etapas e do JSON final por parâmetro (em memória), em vez de ler arquivos de `data/etapas/` e `data/resultado_final.json` do disco.
- **FR-012**: A função `clean_artefatos_anteriores` no pipeline DEVE operar apenas no S3, sem deletar arquivos locais.
- **FR-013**: A função `clean_etapas_dir` DEVE ser removida ou desativada, já que etapas não serão mais salvas localmente.
- **FR-014**: A configuração (`Config`) DEVE remover ou tornar opcionais os campos `docs_dir` e `md_dir` que apontam para diretórios locais, já que não serão mais usados para armazenamento persistente.
- **FR-015**: Em caso de falha de conexão com o S3 durante upload ou escrita de resultados, o sistema DEVE retornar erro ao usuário — sem fallback para armazenamento local.
- **FR-016**: O modo CLI (`--mode cli`) DEVE também operar 100% via S3 para leitura de documentos e salvamento de resultados, sem usar diretórios locais.

### Key Entities

- **Bucket `radiante-final`**: Bucket S3 centralizador. Única fonte de verdade para todos os dados persistentes do sistema.
  - Prefixo `docs/`: Documentos enviados pelo usuário (PDF, JSON, DOCX, TXT).
  - Prefixo `results/`: Artefatos de análise (etapas 1-4 em markdown, JSON final, PDF consolidado, auditoria).
  - Prefixo `runs/`: (Reservado) Dados individuais de cada repetição no modo 10x.
  - Prefixo `markdown_docs/`: Texto extraído dos documentos em formato markdown.

- **Diretório `data/` (local)**: Após a migração, DEVE deixar de ser usado para armazenamento persistente. Pode permanecer vazio ou ser removido. Nenhuma operação de negócio depende mais dele.

- **Memória cache (`ANALYSIS_JOBS["last_result"]`)**: Cache volátil em memória RAM do último resultado da análise. Usado pelo endpoint `/api/last-result` como primeira fonte (mais rápida). Perde o conteúdo ao reiniciar o servidor, quando então busca do S3.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Após fazer upload de um documento, o arquivo existe em `s3://radiante-final/docs/{filename}` e **não existe** em `data/docs/{filename}` no servidor.
- **SC-002**: Após executar uma análise 1x completa, os arquivos `results/etapa{1-4}_completo.md`, `results/resultado_final.json` e `results/relatorio_consolidado.pdf` existem no S3, e o diretório `data/` local está vazio (exceto subdiretórios vazios).
- **SC-003**: Após executar uma análise 10x, os arquivos `results/consolidado_10x.json`, `results/relatorio_consolidado_10x.pdf` e `results/auditoria_10x.md` existem no S3, sem equivalentes locais.
- **SC-004**: Ao clicar "Limpar Tudo", a interface mostra apenas 4 etapas S3 na timeline (docs, markdown_docs, results, runs), e após a conclusão o bucket tem esses prefixos vazios.
- **SC-005**: Ao reiniciar o servidor (perda de cache em memória) e acessar a página inicial, o resultado da última análise ainda é carregado normalmente via S3.
- **SC-006**: Se o S3 estiver inacessível, o upload falha com mensagem de erro clara — sem salvamento "silencioso" local.
- **SC-007**: Todos os testes existentes continuam passando após a migração (ajustados para não dependerem de arquivos locais).

## Assumptions

- O bucket S3 `radiante-final` já existe e está acessível com as credenciais configuradas no `.env` ou via IAM Role da EC2.
- As credenciais AWS têm permissões de leitura e escrita no bucket `radiante-final` (s3:GetObject, s3:PutObject, s3:ListBucket, s3:DeleteObject).
- Dados existentes no diretório `data/` local (de sessões anteriores) não serão migrados automaticamente — podem ser descartados ou copiados manualmente para o S3 se necessário.
- O diretório `data/` local pode permanecer na estrutura do projeto (para compatibilidade) mas não será mais usado para operações de negócio.
- O sistema continuará suportando desenvolvimento local com servidor HTTP rodando em `localhost:8000`, mas o armazenamento local será substituído pelo S3 mesmo em desenvolvimento.
- A latência adicional de operações via S3 (vs. disco local) é aceitável para os volumes esperados (documentos de até ~10MB, algumas dezenas por sessão).
- O `Config.docs_dir` e `Config.md_dir` podem ser removidos da dataclass, já que não serão mais referenciados para armazenamento persistente.
