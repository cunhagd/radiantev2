# Data Model: Limpeza Completa do Sistema

## Entidade: Estado do Sistema (SystemState)

Representa o estado agregado do sistema nos 6 locais de armazenamento.
A limpeza restaura este estado ao "estado inicial".

### Locais de Armazenamento

| ID | Local | Tipo | Mecanismo de Leitura | Mecanismo de Limpeza |
|----|-------|------|---------------------|---------------------|
| LOCAL_FS | `data/` (diretorio local) | Filesystem | `Path.exists()` / `Path.iterdir()` | `shutil.rmtree()` + `Path.unlink()` |
| S3 | Bucket `radiante-final` | Object Storage (S3) | `s3_client.list_files()` | `s3_client.delete_files()` |
| MEMORY | `ANALYSIS_JOBS` (dict) | Memoria (RAM) | Acesso direto ao dict | `dict.update()` para estado inicial |
| PROGRESS | `Progress._data` (dict) | Memoria (Classe singleton) | `Progress.get()` | `Progress.reset()` |
| HISTORY | `_execution_history` (list) | Memoria (Modulo) | `get_execution_history()` | `list.clear()` |
| FRONTEND | DOM (HTML renderizado) | Browser | `document.getElementById()` | `clearAllFrontendData()` |

### Estado Inicial (a ser restaurado)

```python
# ANALYSIS_JOBS
{
    "status": "idle",
    "message": "",
    "error_details": "",
    "last_result": None,
}

# Progress._data
{
    "etapa1":  {"status": "pending", "label": "Aguardando..."},
    "etapa2":  {"status": "pending", "label": "Aguardando..."},
    "etapa3":  [{"status": "pending", "label": "Rodada 1", "resultado": ""}],
    "etapa4":  {"status": "pending", "label": "Aguardando..."},
    "total_runs": 1,
}

# _execution_history
[]

# Frontend
- Meta fields: "—"
- KPI total: "R$ 0,00"
- Cifras list: "<div class='empty-state'>..."
- Observability card: display none
- Audit content: "Carregando..."
```

### Estrutura de Diretorios (apos limpeza)

```text
data/
├── docs/            # Vazio (estrutura mantida)
└── markdown_docs/   # Vazio (estrutura mantida)
```

### Regras de Validacao

- A limpeza DEVE ser idempotente: executar duas vezes seguidas deve produzir o mesmo resultado
- A limpeza NÃO DEVE remover a estrutura de diretorios `data/docs/` e `data/markdown_docs/`
- A limpeza DEVE tolerar falhas parciais (ex: S3 indisponivel) sem interromper os demais locais
- O frontend DEVE ser limpo APENAS apos confirmacao de sucesso do backend
