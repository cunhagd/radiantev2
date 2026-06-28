# Quickstart: Radiante v2

## Pre-requisitos

- Python 3.11+
- AWS Account com acesso a Bedrock, S3 e Textract
- Git

## Setup

1.  Clone o repositorio
2.  Crie o ambiente virtual:
    python -m venv .venv
    .venv/Scripts/Activate  # Windows
    source .venv/bin/activate  # Linux

3.  Instale as dependencias:
    pip install -r requirements.txt

4.  Configure o .env:
    Copie .env.example para .env e preencha as credenciais AWS

5.  Execute o servidor:
    python backend/app.py --mode web

6.  Acesse: http://localhost:8000

## Uso

1. Faca upload de documentos (PDF, DOCX, JSON)
2. Clique em "Analisar 1x" ou "Analisar 10x"
3. Aguarde o processamento (polling automatico a cada 3s)
4. Visualize os resultados, faca download do PDF
