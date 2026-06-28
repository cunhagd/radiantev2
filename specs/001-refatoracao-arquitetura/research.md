# Research: Refatoracao da Arquitetura - Modularizacao do Backend

## 1. Analise do Monolito (app.py - 1973 linhas)

### Responsabilidades Identificadas no Codigo Atual

| Responsabilidade | Linhas (aprox.) | Funcoes | Depende de |
|---|---|---|---|
| Configuracao (.env, credenciais) | 1-98 | escopo global | dotenv |
| Extracao de documentos | 99-208 | extract_pdf_text, extract_docx_text, get_document_text | fitz, boto3(textract) |
| Geracao de PDF | 211-450 | generate_pdf | reportlab |
| Cliente Bedrock/LLM | 451-600 | run_llm_stage_streaming, create_bedrock_client | boto3, openai |
| Metricas e precos | 601-700 | funcoes de calculo de custo | (nenhuma) |
| Pipeline de 4 etapas | 893-975 | run_single_pipeline | bedrock_client, prompts, metrics |
| Salvamento S3 | 976-1057 | save_stage_files | s3_client |
| Modo 1x | 1058-1148 | run_once | pipeline, s3_client, pdf_generator |
| Auditoria | 1149-1250 | save_audit_log, save_audit_log_once | s3_client |
| Modo 10x | 1251-1437 | run_ten_times, aggregate_results, standardize_cifra_name, calculate_probability_label | pipeline, ThreadPoolExecutor |
| Contexto S3 | 1438-1721 | get_s3_combined_context | s3_client, extract |
| Servidor HTTP | 1722-1973 | DashboardHTTPHandler, async_analysis_worker, start_web_server | http.server, threading |

### Dependencias Circulares Potenciais

Nenhuma dependencia circular identificada. O grafo de dependencias e
estritamente aciclico: config -> s3_client -> extract -> pipeline -> app

## 2. Decisoes Tecnicas

### 2.1. Interface dos Modulos

Cada modulo exportara apenas as funcoes necessarias via __init__.py ou
imports explicitos. Nenhum modulo importara app.py.

### 2.2. Config Centralizada (config.py)

- Leitura unica do .env no momento da importacao
- Validacao de campos obrigatorios com erro claro
- NamedTuple ou dataclass para acesso type-safe
- Propriedades congeladas (nao reatribuiveis apos inicializacao)

### 2.3. Cliente Bedrock com Fallback (bedrock_client.py)

Implementar a estrategia de 6 combinacoes do test_fallback.py:

1. Opus 4.6 em us-west-2
2. Opus 4.6 em us-east-1
3. Opus 4.6 em eu-central-1
4. Sonnet 4.6 em us-west-2
5. Sonnet 4.6 em us-east-1
6. Sonnet 4.6 em eu-central-1

Usar retry com backoff exponencial (2s, 4s, 8s) antes de rotacionar.

### 2.4. Extracao de Documentos (extract.py)

Manter a logica existente:
- PDF: PyMuPDF -> se < 100 chars/pagina, OCR via Textract
- DOCX: zipfile + ElementTree
- JSON: json.loads()
- TXT/outros: decode utf-8

## 3. Riscos e Mitigacoes

| Risco | Probabilidade | Mitigacao |
|---|---|---|
| Quebra de compatibilidade de API | Baixa | Testar manualmente cada endpoint apos cada modulo |
| Vazamento de credencial | Baixa | Validar config.py que limpa os.environ corretamente |
| Dependencia circular nao detectada | Baixa | Grafo de dependencias mapeado e verificado |
| Regressao em regras de negocio | Media | prompts.py nao e alterado |
