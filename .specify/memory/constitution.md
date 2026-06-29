<!--
  Sync Impact Report — Constitution v1.1.0
  Version change: 1.0.0 → 1.1.0
  Modified principles: V (MINOR — permit multi-file CSS/JS modular, no bundlers)
  Added sections: N/A
    - Core Principles: 5 princípios (Arquitetura, Nuvem, Compliance, Dados, UI/UX)
    - Stack Tecnológico e Dependências
    - Estrutura de Diretórios e Artefatos
    - Governance
  Removed sections: N/A (first edition)
  Templates requiring updates:
    - .specify/templates/plan-template.md: ⚠ pending (Constitution Check gates)
    - .specify/templates/spec-template.md: ✅ no changes needed
    - .specify/templates/tasks-template.md: ⚠ pending (task categories)
  Follow-up TODOs: N/A — all placeholders resolved.
-->

# Radiante v2 Constitution

## Core Principles

### I. Arquitetura Enxuta — Backend Nativo sem Frameworks

O backend DEVE rodar exclusivamente com `http.server.SimpleHTTPRequestHandler`
do Python padrão. É PROIBIDA a introdução de frameworks web externos como
FastAPI, Flask, Django ou qualquer outra abstração HTTP. O servidor DEVE ser
inicializado via `HTTPServer` diretamente no `__main__`. Toda a lógica de
roteamento (GET/POST), parsing de requisições e serialização de respostas DEVE
ser implementada manualmente, sem bibliotecas de roteamento automático.

### II. Isolamento e Segurança de Credenciais AWS

Credenciais AWS (Access Key, Secret Key, Session Token) DEVEM ser lidas do
arquivo `.env` via `python-dotenv` e passadas explicitamente como parâmetros
nomeados na instanciação de cada cliente boto3 (`aws_access_key_id`,
`aws_secret_access_key`, `region_name`). Imediatamente após a leitura, as
variáveis DEVEM ser removidas do `os.environ` para evitar que o SDK as
capture automaticamente, prevenindo conflitos de escopo em ambientes EC2,
Lambda ou containers.

### III. Compliance Trabalhista — Pipeline Jurídico em 4 Etapas com CPC 25

O pipeline de análise jurídica DEVE executar exatamente 4 etapas sequenciais e
encadeadas:

1. **Etapa 1 — Extração de Metadados**: Identificar número do processo, autor,
   advogado, localidade, juízo, reclamadas, início do processo.
2. **Etapa 2 — Cálculo de Cifras CLT**: Aplicar as 18 regras de negócio
   trabalhistas (cegueira de valores liquidados, dicionário estrito de
   fórmulas, prescrição quinquenal, trava de ponto eletrônico, alerta de
   divergência, etc.).
3. **Etapa 3 — Probabilidade e Risco (CPC 25)**: Classificar cada cifra como
   Provável (>50%), Possível (25-50%) ou Remota (<25%), aplicando as 11 regras
   de arbitramento (Art. 477 binário, dano moral entre R$ 15k-R$ 25k, trava
   de ponto ≤20%, etc.).
4. **Etapa 4 — Consolidação Final**: Gerar JSON estruturado com metadados,
   cifras, probabilidades e valor total estimado.

Cada etapa DEVE receber como contexto as saídas completas das etapas
anteriores (encadeamento progressivo). A persona do agente ("Buddy Agente
Jurídico") DEVE evoluir seu estado: `INICIAL` → `ETAPA_1_VALIDADA` →
`ETAPA_2_VALIDADA` → `ETAPA_3_VALIDADA`.

### IV. Dados e Documentos — Extração, OCR e Armazenamento S3

Documentos enviados DEVEM ser processados conforme seu formato:

| Formato | Método Primário | Fallback |
|---------|----------------|----------|
| PDF | PyMuPDF (fitz) — extração de texto nativo | OCR via Amazon Textract ($0.0015/página) se < 100 chars/página |
| DOCX | Leitura XML via zipfile + ElementTree | — |
| JSON | `json.loads()` | — |
| TXT/outros | `decode("utf-8")` | — |

O bucket S3 centralizador é `radiante-final` com a seguinte estrutura de
prefixos:

- `docs/` — Documentos originais enviados pelo usuário
- `markdown_docs/` — Texto extraído convertido para markdown
- `results/` — Artefatos finais (etapas 1-4, PDF, auditoria)
- `runs/run_{i}/` — Resultados individuais de cada rodada (modo 10x)

### V. Interface e Experiência do Usuário — Frontend Autossuficiente

O frontend DEVE ser servido estaticamente a partir de `frontend/`, podendo
conter múltiplos arquivos CSS e JS organizados por responsabilidade (modular).
É PROIBIDO o uso de bundlers (Webpack, Vite), frameworks JS (React, Vue,
Angular) ou qualquer dependência de frontend compilada. O design DEVE seguir o
sistema Material Design 3 / Gemini com:

- **Paleta**: Gradiente `#4285f4 → #9b51e0 → #e91e63 → #fbbc05`
- **Tipografia**: Google Sans, Google Sans Text, Google Sans Mono
- **Feedback de loading**: Overlay com timeline interativa mostrando o
  progresso de cada etapa da analise em tempo real
- **Polling**: Requisições a cada 1.2s para `/api/status` e `/api/progress`
  durante análise, com cache-busting via query parameter
- **Responsividade**: Breakpoints em 768px e 480px

> **Emenda MINOR v1.1.0**: A versão original exigia um único arquivo HTML com
> tudo inline. A modularização (CSS e JS em arquivos separados) foi permitida
> para garantir testabilidade e manutenção, mantendo o espírito da regra (sem
> frameworks, sem bundlers). Nenhuma funcionalidade ou API foi alterada.

## Stack Tecnológico e Dependências

### Backend (Python 3.x)

| Dependência | Uso |
|---|---|
| `boto3` | SDK AWS (S3, Bedrock, Textract) |
| `pymupdf` (fitz) | Extração de texto de PDFs |
| `openai` | SDK para modelos Grok via Bedrock Mantle |
| `python-dotenv` | Leitura de variáveis de ambiente do `.env` |
| `reportlab` | Geração de PDFs consolidados |

NENHUMA outra dependência deve ser adicionada sem justificativa explícita no
plano de implementação.

### Frontend (Zero dependências externas)

- HTML5 semântico
- CSS3 com variáveis nativas (design tokens)
- JavaScript Vanilla assíncrono (Fetch API)

### Infraestrutura AWS

- **S3**: Bucket `radiante-final` para armazenamento de documentos e resultados
- **Bedrock**: Claude Sonnet 4.6 (`us.anthropic.claude-sonnet-4-6`) como modelo
  primário via Converse API com streaming e cache de prompt
- **Textract**: OCR para PDFs escaneados
- **EC2**: Servidor Ubuntu para deploy em produção
- **CI/CD**: GitHub Actions com rsync + SSH para EC2 na branch `main-poc`

### Modelos de IA

- **Primário**: `us.anthropic.claude-sonnet-4-6` (cross-region US)
- **Fallback**: `us.anthropic.claude-opus-4-6-v1` com rotação regional
  (us-west-2 → us-east-1 → eu-central-1)
- **Alternativo**: Grok via Bedrock Mantle (`OpenAI(bedrock-mantle...)`)
- **Configuração**: `temperature=0.0`, retry com backoff exponencial (2s, 4s, 8s)

## Estrutura de Diretórios e Artefatos

```
radiante-final/
├── backend/
│   ├── app.py              # Servidor HTTP + Pipeline de IA
│   └── prompts.py           # Prompts das 4 etapas (regras de negócio)
├── frontend/
│   └── index.html           # Interface web única
├── .env                     # Credenciais AWS (NÃO versionar)
├── requirements.txt         # Dependências Python
├── .github/workflows/
│   └── deploy.yml           # CI/CD para EC2
├── data/
│   ├── docs/                # Documentos para upload local
│   └── markdown_docs/       # Markdowns gerados localmente
```

## Governance

Esta Constituição estabelece as regras fundamentais do projeto Radiante v2.
Toda feature spec, plano de implementação e conjunto de tarefas DEVE passar
pela verificação de conformidade ("Constitution Check") antes de ser aprovado.

### Processo de Emenda

1. **Proposta**: Documentar a alteração desejada com justificativa clara.
2. **Análise de Impacto**: Identificar templates e artefatos afetados.
3. **Aprovação**: Consentimento explícito dos stakeholders do projeto.
4. **Registro**: Atualizar este documento com versão semântica incrementada.

### Versionamento

- **MAJOR**: Princípio removido ou redefinido de forma incompatível.
- **MINOR**: Novo princípio ou seção adicionada.
- **PATCH**: Clarificações, correções ou refinamentos não-semânticos.

### Compliance Review

Toda implementação DEVE ser verificada contra os 5 princípios fundamentais
antes de ser considerada completa. Complexidade adicional não prevista nesta
Constituição DEVE ser justificada na seção "Complexity Tracking" do plano.

**Version**: 1.0.0 | **Ratified**: 2026-06-28 | **Last Amended**: 2026-06-28
