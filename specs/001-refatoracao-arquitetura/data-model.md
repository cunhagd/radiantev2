# Data Model: Refatoracao da Arquitetura

## Entidades

### Config
Objeto de configuracao do sistema, carregado do .env na inicializacao.

| Campo | Tipo | Origem | Obrigatorio |
|---|---|---|---|
| aws_access_key_id | str | .env (AWS_ACCESS_KEY_ID) | Sim |
| aws_secret_access_key | str | .env (AWS_SECRET_ACCESS_KEY) | Sim |
| aws_region | str | .env (REGION) | Sim, padrao us-east-1 |
| bedrock_model_id | str | .env (BEDROCK_MODEL_ID) | Sim |
| bearer_token | str | .env (AWS_BEARER_TOKEN_BEDROCK) | Sim |
| bucket_name | str | Constante (radiante-final) | - |
| grok_prices | dict | .env (GROK_PRICE_*) | Nao |
| docs_dir | str | Constante (data/docs/) | - |
| md_dir | str | Constante (data/markdown_docs/) | - |

### Job
Representa uma execucao do pipeline. Estado efemero em memoria.

| Campo | Tipo | Descricao |
|---|---|---|
| status | str | idle, processing, completed, error |
| message | str | Mensagem de progresso ou resultado |
| error_details | str | Detalhes do erro (se houver) |
| lock | threading.Lock | Mutex para acesso concorrente |

### PipelineMetrics
Metricas de uma execucao do pipeline.

| Campo | Tipo | Descricao |
|---|---|---|
| prompt_tokens | int | Total de tokens de entrada |
| completion_tokens | int | Total de tokens de saida |
| cache_tokens | int | Total de tokens em cache |
| cost_input | float | Custo de tokens de entrada |
| cost_output | float | Custo de tokens de saida |
| cost_cache | float | Custo de tokens de cache |
| cost_total | float | Custo total da rodada |

### Document
Documento processado pelo sistema.

| Campo | Tipo | Descricao |
|---|---|---|
| filename | str | Nome do arquivo original |
| extension | str | pdf, docx, json, txt |
| text | str | Texto extraido |
| pages_native | int | Paginas extraidas via texto nativo |
| pages_ocr | int | Paginas processadas via OCR |
| textract_cost | float | Custo do OCR (se aplicavel) |

## Relacionamentos

Config -> (independiente) -> usado por todos os modulos
Job -> (contem) -> PipelineMetrics
Document -> (origina) -> texto para o Pipeline
S3Client -> (armazena) -> Document, PipelineMetrics, Resultados JSON
