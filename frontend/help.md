# Manual do Usuário — POC Radiante

**Sistema de Análise Jurídica com Inteligência Artificial**

---

## Índice

1. Apresentação
2. Acessando o Sistema
3. Visão Geral da Tela
4. Fluxo de Uso Recomendado
5. Fazendo Upload de Documentos
6. Iniciando a Análise
   - Análise Única (1x)
   - Análise 10x
7. Tela de Progresso — Acompanhando a Análise
8. Resultados da Análise
   - Dados do Processo
   - Provisão de Cifras
   - Total Estimado
9. Baixando o Relatório em PDF
10. Limpando Todos os Dados
11. Métricas de Uso
12. Comportamento dos Botões
13. Perguntas Frequentes

---

## 1. Apresentação

A **POC Radiante** é uma plataforma inteligente que auxilia  em análise de processos judiciais. O sistema recebe documentos de um processo (petições, anexos, json do Financo) e, por meio de Inteligência Artificial, extrai automaticamente:

- **Dados do processo** — número, autor, reclamada, valor da causa, juízo, etc.
- **Cifras** — valores de cada pedido e calcula a estimativa de probabilidade de êxito
- **Relatório consolidado** — documento PDF com todas as informações organizadas

Tudo isso de forma rápida, automatizada e segura.

---

## 2. Acessando o Sistema

A POC Radiante é acessado diretamente pelo navegador de internet (Google Chrome, Microsoft Edge, Firefox), sem necessidade de instalar nenhum programa.

**URL de acesso**: https://radiante.emaster.info

Ao acessar, você verá a tela principal com todas funcionalidades.

---

## 3. Visão Geral da Tela

A tela principal é dividida em três áreas:

```
┌─────────────────────────────────────────────────────────┐
│  RADIANTE • Análise Jurídica com IA                     │
│  [Upload] [1x] [10x] [🗑️]                              │
│  Status: aguardando documentos...                       │
├─────────────────────────────────────────────────────────┤
│  ┌─ Dados do Processo ──────────────────────────────┐   │
│  │  Processo: 0001234-56.2025.8.01.0001             │   │
│  │  Autor: João Silva                               │   │
│  │  Advogado: Dra. Maria Souza                      │   │
│  │  Reclamada: Empresa ABC Ltda                     │   │
│  │  Juízo: 1ª Vara Cível                            │   │
│  │  Valor da Causa: R$ 50.000,00                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Provisão de Cifras ─────────────────────────────┐   │
│  │  ● Indenização por Danos Morais                  │   │
│  │    Valor: R$ 20.000,00  |  Provável              │   │
│  │                                                  │   │
│  │  ● Reembolso de Desconto                         │   │
│  │    Valor: R$ 549,50     |  Possível              │   │
│  │                                                  │   │
│  │  ─────────────────────────────────────           │   │
│  │  Total Estimado: R$ 23.631,92                    │   │
│  │                                                  │   │
│  │  [ 📥 Baixar Relatório PDF ]                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Métricas de Uso ────────────────────────────────┐   │
│  │  Custo Total       |  Tokons Entrada |  Saída    │   │
│  │    $0,37           |   264.772       |  7.537    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Fluxo de Uso Recomendado

Para uma experiência completa, siga esta ordem:

```
1️⃣ Clicar botão da lixeira se estiver ativado
        ↓
2️⃣ Clicar no botão de "upload" e anexar os documentos do processo
        ↓
3️⃣ Escolher tipo de análise e clicar no botão: 1x ou 10x
        ↓
4️⃣ Aguardar processamento (acompanhe pela tela de progresso)
        ↓
5️⃣ Visualizar resultados (cifras, dados do processo) 
        ↓
6️⃣ Baixar relatório em PDF
```

---

## 5. Fazendo Upload de Documentos

O primeiro passo é enviar os documentos do processo que deseja analisar.

**O que pode ser enviado:**
- Documentos em formato **PDF** (petições, anexos, contratos etc)
- Arquivos em formato **JSON** (dados estruturados do Financo)

**Como fazer:**

1. Clique no botão **Upload**
2. Selecione **um ou mais arquivos** do seu computador
3. Acompanhe o progresso na barra de status ao lado dos botões

**Comportamento:**
- Você pode selecionar vários arquivos de uma vez (segure Ctrl e selecione os arquivos)
- Cada arquivo é enviado individualmente
- Ao final, o sistema informa quantos arquivos foram enviados com sucesso

**Após o upload:**
- Os botões **1x** e **10x** serão liberados quando os documentos forem processados
- O botão **Upload** continua disponível para adicionar mais documentos antes de iniciar a análise, se necessário

---

## 6. Iniciando a Análise

Após enviar os documentos, você pode iniciar a análise de duas formas:

### 6.1 Análise Única (1x)

O sistema executa **uma rodada completa** de análise em todos os documentos enviados.

**Quando usar:**
- Para um resultado rápido
- Para testar o sistema com novos documentos
- Quando o processo tem menor complexidade

**Como usar:**
1. Clique no botão **1x** (ícone de play ▶️)
2. A tela de progresso será exibida
3. Ao finalizar, os resultados aparecem automaticamente

**Tempo estimado**: 1 a 3 minutos (dependendo do volume de documentos)

### 6.2 Análise 10x

O sistema executa **10 rodadas completas** de análise, calculando a probabilidade com maior precisão estatística.

**Quando usar:**
- Para processos complexos com muitos documentos e cifras
- Quando você precisa de maior confiabilidade nas estimativas
- Para análises mais robustas

**Como usar:**
1. Clique no botão **10x** (ícone de estrela ⭐)
2. A tela de progresso será exibida
3. Ao finalizar, os resultados aparecem automaticamente

**Tempo estimado**: 5 a 15 minutos (dependendo do volume de documentos)

> 💡 **Dica**: A análise 10x consome mais recursos computacionais, mas fornece estimativas mais precisas. Para uso cotidiano, a análise 1x já oferece bons resultados. Se for natada acurácia baixa na análise 1x, dar preferência para a análise 10x.

---

## 7. Tela de Progresso

Ao iniciar uma análise, uma tela de progresso é exibida com:

- **Título** — indica se é análise 1x ou 10x
- **Cronômetro** — tempo decorrido desde o início
- **Timeline** — etapas do processamento com status visual

**Etapas da análise:**

| Etapa | Descrição | Status |
|-------|-----------|--------|
| Etapa 1 | Extração de Cabeçalho | ⏳ Aguardando / 🔄 Processando / ✅ Concluído |
| Etapa 2 | Cálculo de Cifras | ⏳ Aguardando / 🔄 Processando / ✅ Concluído |
| Etapa 3 | Cálculo de Probabilidade | ⏳ Aguardando / 🔄 Processando / ✅ Concluído |
| Etapa 4 | Consolidação do Provisionamento | ⏳ Aguardando / 🔄 Processando / ✅ Concluído |

**No modo 10x**, a Etapa 3 exibe detalhadamente cada uma das 10 rodadas com seu status individual (ex: "5/10 concluídas").

**Comportamento:**
- A tela de progresso **não pode ser fechada** durante o processamento
- Todos os botões ficam desabilitados
- Ao finalizar, a tela se fecha automaticamente e os resultados aparecem

---

## 8. Resultados da Análise

Após a conclusão, a tela principal exibe os resultados organizados em seções.

### 8.1 Dados do Processo

O sistema extrai automaticamente as principais informações do processo:

| Campo | Descrição |
|-------|-----------|
| **Processo** | Número completo do processo |
| **Autor** | Nome da parte autora/reclamante |
| **Advogado** | Nome do advogado da parte autora |
| **Reclamada** | Nome da parte ré/reclamada |
| **Tomadora** | Tomadora de serviços (se aplicável) |
| **Juízo** | Vara ou tribunal responsável |
| **Localidade** | Cidade/UF do juízo |
| **Início** | Data de início do processo |
| **Valor da Causa** | Valor total indicado na petição |

### 8.2 Provisão de Cifras

Cada cifra (pedido de valor) identificada é exibida em um cartão individual com:

- **Nome da cifra** — descrição do pedido
- **Valor solicitado** — valor que a parte autora pede
- **Descrição** — resumo do fundamento do pedido
- **Probabilidade** — estimativa de êxito:
  - ✅ **Provável** — alta chance de ser concedido
  - ⚖️ **Possível** — chance moderada
  - ❌ **Improvável** — baixa chance
- **Valor estimado** — valor provável de condenação (calculado com base na probabilidade)

### 8.3 Total Estimado

Na parte inferior da seção de cifras, o sistema exibe o **valor total estimado**, que é a soma de todos os valores estimados de cada cifra.

---

## 9. Baixando o Relatório em PDF

Após a análise, você pode baixar um relatório profissional em PDF contendo todas as informações.

**Como baixar:**

1. Localize o botão **Baixar Relatório PDF** (ícone de download 📥)
2. Clique no botão
3. O PDF será baixado automaticamente para o seu computador

**O que contém o relatório:**
- Dados completos do processo
- Lista detalhada de todas as cifras com valores e probabilidades
- Total estimado consolidado
- Formatação profissional pronta para impressão ou compartilhamento

---

## 10. Limpando Todos os Dados

Para iniciar uma nova análise é **obrigatório** que o usuário clique no botão de limpeza para limpar todos os dados da análise atual, evitando conflitos de dados e erros nas análises.

**Como fazer:**

1. Clique no botão **Lixeira** 🗑️ (canto superior direito)
2. Uma mensagem de confirmação será exibida: *"Limpar todos os dados?"*
3. Clique em **Limpar tudo** para confirmar
4. Ou clique em **Cancelar** para manter os dados

**O que acontece ao limpar:**
- Todos os documentos enviados são removidos
- Todas as análises e resultados são apagados
- O sistema volta ao estado inicial
- Uma tela de progresso mostra as etapas da limpeza

> ⚠️ **Atenção**: A limpeza é **permanente e irreversível**. Baixe o relatório PDF antes de limpar se precisar dos dados.

---

## 11. Métricas de Uso

O sistema exibe métricas de transparência sobre o uso de recursos na análise:

| Métrica | Descrição |
|---------|-----------|
| **Custo Total** | Custo estimado em dólares da análise |
| **Tokens Entrada** | Volume de dados processados (entrada) |
| **Tokens Cache** | Dados reaproveitados entre etapas |
| **Tokens Saída** | Volume de dados gerados (saída) |

**No modo 10x**, uma tabela detalhada mostra o custo e tokens de cada uma das 10 rodadas individualmente.

---

## 12. Comportamento dos Botões

O sistema gerencia automaticamente quais botões estão disponíveis em cada momento:

| Situação | Upload | 1x | 10x | 🗑️ Lixeira |
|----------|--------|----|-----|-------------|
| **Tela inicial (sem dados)** | ✅ Livre | 🔒 Bloqueado | 🔒 Bloqueado | 🔒 Bloqueado |
| **Após upload de documentos** | ✅ Livre | ✅ Livre | ✅ Livre | 🔒 Bloqueado |
| **Análise em andamento** | 🔒 Bloqueado | 🔒 Bloqueado | 🔒 Bloqueado | 🔒 Bloqueado |
| **Resultados na tela** | 🔒 Bloqueado | 🔒 Bloqueado | 🔒 Bloqueado | ✅ Livre |
| **Após limpeza** | ✅ Livre | 🔒 Bloqueado | 🔒 Bloqueado | 🔒 Bloqueado |

Isso significa que:
- Você **não pode** fazer upload enquanto os resultados estão na tela — primeiro limpe os dados
- Você **não pode** iniciar uma análise se outra já estiver em andamento
- A **lixeira** só fica disponível quando há dados para limpar

---

## 13. Perguntas Frequentes

### Quanto tempo leva uma análise?

- **Análise 1x**: 1 a 3 minutos
- **Análise 10x**: 5 a 15 minutos

O tempo varia conforme o tamanho e quantidade dos documentos enviados.

### Quantos documentos posso enviar?

Não há limite definido. Você pode enviar quantos arquivos precisar em um único upload, desde que façam parte do mesmo processo.

### Posso fechar o navegador durante a análise?

**Não recomendado**. A análise é interrompida se a página for fechada. Mantenha a aba aberta até o término.

### O que fazer se aparecer "Erro de conexão"?

1. Verifique sua conexão com a internet
2. Recarregue a página (pressionando Ctrl + F5)
3. Tente novamente o upload e a análise
4. Se o erro persistir, contate o suporte técnico

### Posso compartilhar o relatório PDF?

Sim! O PDF pode ser baixado e compartilhado livremente.

### Preciso instalar algum programa?

Não. A POC Radiante funciona totalmente pelo navegador. Basta acessar o link.

### Os dados são seguros?

Sim. Os documentos enviados são processados em ambiente seguro na nuvem e armazenados com criptografia.

---

## Suporte

Em caso de dúvidas ou problemas técnicos, entre em contato:

**E-mail**: [gustavo.cunha@emaster.info](mailto:gustavo.cunha@emaster.info)

---

*Documento gerado em junho de 2026 • Versão 1.0*
