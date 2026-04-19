# lf-openalex-enrichment-mvp

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)
[![Run in Postman](https://run.pstmn.io/button.svg)](https://www.postman.com/lfsolucoes)

Plataforma de **Enriquecimento B2B** com dados do [OpenAlex](https://openalex.org). Transforma listas brutas de leads em inteligência acionável: calcula cobertura de atributos, classifica contas por banda de valor e prioriza prospects por gap de enriquecimento.

> **URL de Produção:** https://lf-openalex-enrichment-mvp.onrender.com

---

## Sumario

- [Visao Geral](#visao-geral)
- [Endpoints](#endpoints)
- [Fluxo de Enriquecimento](#fluxo-de-enriquecimento)
- [Quick Start Local](#quick-start-local)
- [Exemplos curl](#exemplos-curl)
- [Integracao Sistemica](#integracao-sistemica)
- [Como Importar no Postman](#como-importar-no-postman)
- [Casos de Uso](#casos-de-uso)
- [Stack Tecnica](#stack-tecnica)
- [Contribuindo](#contribuindo)

---

## Visao Geral

O `lf-openalex-enrichment-mvp` e um servico HTTP leve que expoe quatro endpoints REST para enriquecimento B2B:

- **Enriquecimento em lote** de leads com metricas de cobertura de atributos
- **Classificacao por banda de valor** (high / medium / low) baseada em score
- **Priorizacao de leads** por gap de enriquecimento (quem esta mais incompleto vai primeiro)

Todos os endpoints retornam JSON com `Content-Type: application/json; charset=utf-8` e suportam CORS aberto (`Access-Control-Allow-Origin: *`).

---

## Endpoints

| Metodo | Endpoint              | Descricao                                    | Tag                  |
|--------|-----------------------|----------------------------------------------|----------------------|
| GET    | `/health`             | Verificacao de saude do servico              | Health               |
| GET    | `/sample`             | Payload de exemplo com metadados             | Enrichment           |
| POST   | `/enrich`             | Enriquecimento em lote de leads B2B          | Enrichment           |
| POST   | `/v1/value-score`     | Classificacao de conta por banda de valor    | Value Score          |
| POST   | `/v1/leads/prioritize`| Priorizacao de leads por gap de enriquecimento | Lead Prioritization |

A especificacao completa em OpenAPI 3.0 esta em [`docs/openapi.yaml`](docs/openapi.yaml).

---

## Fluxo de Enriquecimento

O pipeline tipico de enriquecimento B2B segue quatro etapas:

```
1. LEADS BRUTOS
   Lista de empresas/contatos com dados parciais do CRM

        |
        v

2. POST /enrich
   Calcula coverage por lead, identifica campos faltantes
   Retorna: enriched[] com _enrichment.coverage (0-1) e stats

        |
        v

3. POST /v1/value-score
   Para cada conta, classifica o potencial de valor
   Retorna: band (high/medium/low) baseado no score

        |
        v

4. POST /v1/leads/prioritize
   Ordena leads por gap de enriquecimento (mais incompletos primeiro)
   Retorna: lista priorizada com _priorityScore

        |
        v

5. ACAO COMERCIAL
   Equipe de SDR trabalha leads priorizados com dados enriquecidos
```

**Logica de bandas de valor:**
- `score >= 80` → **high** (contas de alto valor, foco imediato)
- `score >= 50` → **medium** (contas de valor medio, nutrir)
- `score < 50` → **low** (contas de baixo potencial, baixa prioridade)

---

## Quick Start Local

### Pre-requisitos

- Python 3.11+
- pip

### Instalacao

```bash
# 1. Clone o repositorio
git clone https://github.com/leandroclf/lf-openalex-enrichment-mvp.git
cd lf-openalex-enrichment-mvp

# 2. Instale as dependencias
pip install -r requirements-dev.txt

# 3. Execute o servidor HTTP
PYTHONPATH=. python3 backend/src/http_server.py
# Servidor disponivel em http://localhost:8000
```

### Verificar instalacao

```bash
curl http://localhost:8000/health
# {"status": "ok", "service": "lf-openalex-enrichment-mvp"}
```

### Executar testes

```bash
# Smoke tests rapidos
PYTHONPATH=. python3 tools/smoke_check.py

# Suite completa de testes
PYTHONPATH=. pytest -v --capture=no
```

---

## Exemplos curl

### GET /health

```bash
curl https://lf-openalex-enrichment-mvp.onrender.com/health
```

Resposta:
```json
{"status": "ok", "service": "lf-openalex-enrichment-mvp"}
```

---

### GET /sample

```bash
curl https://lf-openalex-enrichment-mvp.onrender.com/sample
```

Resposta:
```json
{
  "component": "lf-openalex-enrichment-mvp",
  "source": "openalex",
  "status": "ok",
  "generatedAt": "2026-04-18T10:00:00+00:00",
  "transport": "http",
  "generatedAtHttp": "2026-04-18T10:00:00+00:00"
}
```

---

### POST /enrich

```bash
curl -X POST https://lf-openalex-enrichment-mvp.onrender.com/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "leads": [
      {
        "company": "Acme Corp",
        "domain": "acme.com",
        "industry": "Tecnologia",
        "employee_count": 200
      },
      {
        "company": "Beta Inc",
        "domain": "",
        "industry": "Financas"
      }
    ],
    "config": null
  }'
```

Resposta:
```json
{
  "enriched": [
    {
      "company": "Acme Corp",
      "domain": "acme.com",
      "industry": "Tecnologia",
      "employee_count": 200,
      "_enrichment": {
        "coverage": 1.0,
        "processed_at": "2026-04-18T10:00:00+00:00",
        "source": "openalex"
      }
    },
    {
      "company": "Beta Inc",
      "domain": "",
      "industry": "Financas",
      "employee_count": "",
      "_enrichment": {
        "coverage": 0.5,
        "processed_at": "2026-04-18T10:00:00+00:00",
        "source": "openalex"
      }
    }
  ],
  "stats": {
    "total": 2,
    "enriched_count": 1,
    "coverage_rate": 0.75,
    "enrichment_rate": 0.5
  },
  "processed_at": "2026-04-18T10:00:00+00:00"
}
```

> O campo `config` pode ser `null` (usa campos padrao: `company`, `domain`, `industry`, `employee_count`)
> ou um objeto `{"fields": ["campo1", "campo2"]}` para customizar os campos avaliados.

---

### POST /v1/value-score

```bash
curl -X POST https://lf-openalex-enrichment-mvp.onrender.com/v1/value-score \
  -H "Content-Type: application/json" \
  -d '{"accountId": "acme-001", "score": 80}'
```

Resposta:
```json
{
  "accountId": "acme-001",
  "band": "high",
  "score": 80.0,
  "processed_at": "2026-04-18T10:00:00+00:00"
}
```

---

### POST /v1/leads/prioritize

```bash
curl -X POST https://lf-openalex-enrichment-mvp.onrender.com/v1/leads/prioritize \
  -H "Content-Type: application/json" \
  -d '{
    "leads": [
      {"id": "l1", "company": "Acme", "domain": "acme.com", "coverage": 0.4},
      {"id": "l2", "company": "Beta", "coverage": 0.8}
    ],
    "weights": null
  }'
```

Resposta:
```json
{
  "prioritized": [
    {"id": "l2", "company": "Beta", "coverage": 0.8, "_priorityScore": 4},
    {"id": "l1", "company": "Acme", "domain": "acme.com", "coverage": 0.4, "_priorityScore": 2}
  ],
  "total": 2,
  "processed_at": "2026-04-18T10:00:00+00:00"
}
```

---

## Integracao Sistemica

### Python

```python
import requests

BASE_URL = "https://lf-openalex-enrichment-mvp.onrender.com"

# 1. Enriquecer leads
leads = [
    {"company": "Acme Corp", "domain": "acme.com", "industry": "Tecnologia"},
    {"company": "Beta Inc", "domain": "beta.io"},
]

response = requests.post(f"{BASE_URL}/enrich", json={"leads": leads, "config": None})
result = response.json()

print(f"Total: {result['stats']['total']}")
print(f"Coverage rate: {result['stats']['coverage_rate']}")

# 2. Classificar valor de uma conta
score_response = requests.post(
    f"{BASE_URL}/v1/value-score",
    json={"accountId": "acme-001", "score": 85}
)
score_data = score_response.json()
print(f"Band: {score_data['band']}")  # "high"

# 3. Priorizar leads para enriquecimento
priority_response = requests.post(
    f"{BASE_URL}/v1/leads/prioritize",
    json={"leads": leads, "weights": None}
)
prioritized = priority_response.json()["prioritized"]
print(f"Primeiro lead a enriquecer: {prioritized[0]['company']}")
```

---

### JavaScript (fetch)

```javascript
const BASE_URL = "https://lf-openalex-enrichment-mvp.onrender.com";

// Enriquecer leads
async function enrichLeads(leads) {
  const response = await fetch(`${BASE_URL}/enrich`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ leads, config: null }),
  });
  return response.json();
}

// Classificar valor
async function classifyValue(accountId, score) {
  const response = await fetch(`${BASE_URL}/v1/value-score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accountId, score }),
  });
  return response.json();
}

// Priorizar leads
async function prioritizeLeads(leads, weights = null) {
  const response = await fetch(`${BASE_URL}/v1/leads/prioritize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ leads, weights }),
  });
  return response.json();
}

// Exemplo de uso
(async () => {
  const leads = [
    { company: "Acme Corp", domain: "acme.com", industry: "Tech" },
    { company: "Beta Inc" },
  ];

  const enriched = await enrichLeads(leads);
  console.log("Stats:", enriched.stats);

  const valueScore = await classifyValue("acme-001", 80);
  console.log("Band:", valueScore.band); // "high"

  const prioritized = await prioritizeLeads(leads);
  console.log("Prioridade 1:", prioritized.prioritized[0].company);
})();
```

---

### curl (script completo)

```bash
#!/bin/bash
BASE="https://lf-openalex-enrichment-mvp.onrender.com"

echo "=== Health Check ==="
curl -s "$BASE/health" | python3 -m json.tool

echo ""
echo "=== Enriquecimento ==="
curl -s -X POST "$BASE/enrich" \
  -H "Content-Type: application/json" \
  -d '{"leads":[{"company":"Acme Corp","domain":"acme.com","industry":"Tech","employee_count":200}],"config":null}' \
  | python3 -m json.tool

echo ""
echo "=== Value Score ==="
curl -s -X POST "$BASE/v1/value-score" \
  -H "Content-Type: application/json" \
  -d '{"accountId":"acme-001","score":80}' \
  | python3 -m json.tool

echo ""
echo "=== Priorizacao ==="
curl -s -X POST "$BASE/v1/leads/prioritize" \
  -H "Content-Type: application/json" \
  -d '{"leads":[{"id":"l1","company":"Acme","domain":"acme.com"},{"id":"l2","company":"Beta"}],"weights":null}' \
  | python3 -m json.tool
```

---

## Como Importar no Postman

A pasta `docs/` contem a colecao e o environment prontos para importar:

```
docs/
  openapi.yaml               # Especificacao OpenAPI 3.0
  postman_collection.json    # Colecao Postman v2.1
  postman_environment.json   # Environment com base_url e base_url_local
```

### Passo a passo

**1. Abrir o Postman**
   - Abra o Postman Desktop ou acesse app.getpostman.com

**2. Importar o Environment**
   - Clique em "Environments" no painel esquerdo
   - Clique no botao "Import" (icone de seta para cima)
   - Selecione o arquivo `docs/postman_environment.json`
   - O environment "lf-openalex-enrichment-mvp" sera criado com:
     - `base_url` = `https://lf-openalex-enrichment-mvp.onrender.com`
     - `base_url_local` = `http://localhost:8000`
   - Clique no environment para ativa-lo (deve aparecer no seletor no canto superior direito)

**3. Importar a Colecao**
   - Clique em "Collections" no painel esquerdo
   - Clique no botao "Import"
   - Selecione o arquivo `docs/postman_collection.json`
   - A colecao "lf-openalex-enrichment-mvp" sera criada com as pastas:
     - Health
     - Enrichment
     - Value Score
     - Lead Prioritization

**4. Selecionar o Environment ativo**
   - No canto superior direito do Postman, clique no dropdown de environments
   - Selecione "lf-openalex-enrichment-mvp"
   - Agora a variavel `{{base_url}}` apontara para a URL de producao

**5. Testar a primeira requisicao**
   - Expanda a pasta "Health" na colecao
   - Clique em "GET /health"
   - Clique no botao "Send"
   - Voce deve receber: `{"status": "ok", "service": "lf-openalex-enrichment-mvp"}`

**Dica:** Para testar localmente, substitua `{{base_url}}` por `{{base_url_local}}` nas requisicoes,
ou edite o environment para trocar o valor ativo de `base_url` para `http://localhost:8000`.

---

## Casos de Uso

### 1. Qualificacao de Leads B2B

Importe sua lista de leads do CRM para o `/enrich` e use o `_enrichment.coverage` para
identificar quais contas tem dados suficientes para uma abordagem comercial efetiva.
Leads com `coverage >= 0.75` estao prontos para o SDR; leads com `coverage < 0.5`
precisam de pesquisa adicional antes do contato.

```bash
# Fluxo tipico de qualificacao
POST /enrich → filtra leads com coverage > 0.75 → envia para fila de SDR
```

### 2. Priorizacao de Prospeccao

Antes de iniciar uma campanha outbound, use `/v1/leads/prioritize` para identificar
quais leads tem mais lacunas de dados. Preencha esses gaps primeiro para maximizar
a taxa de conversao das abordagens subsequentes.

```bash
# Identificar quem precisa de mais dados
POST /v1/leads/prioritize → trabalha lista em ordem de _priorityScore desc
```

### 3. Enriquecimento de CRM

Integre o endpoint `/enrich` ao seu webhook de CRM para enriquecer automaticamente
novos leads no momento do cadastro. Use o `coverage_rate` do batch para monitorar
a saude dos dados ao longo do tempo.

```bash
# Webhook de novo lead no CRM
webhook → POST /enrich → atualiza CRM com _enrichment.coverage e dados normalizados
```

### 4. Segmentacao por Valor de Conta

Use `/v1/value-score` para classificar sua base de clientes em bandas de valor e
direcionar esforcos de upsell e cross-sell. Contas na banda `high` devem receber
atencao prioritaria do time de expansao.

```bash
# Segmentacao mensal da base
GET contas do CRM → POST /v1/value-score para cada conta → agrupa por band
# high: expansao prioritaria | medium: nutrir | low: monitorar
```

---

## Stack Tecnica

| Componente     | Tecnologia                          |
|----------------|-------------------------------------|
| Linguagem      | Python 3.11+                        |
| Servidor HTTP  | `http.server` (stdlib, zero deps)   |
| Dados          | OpenAlex (fonte primaria)           |
| Deploy         | Render (producao)                   |
| CI/CD          | GitHub Actions                      |
| Testes         | pytest                              |
| Documentacao   | OpenAPI 3.0, Postman Collection v2.1|

---

## Contribuindo

Este projeto adota commit direto na branch `main`. Pull Requests sao opcionais e
encorajados para revisao colaborativa.

Antes de submeter alteracoes:

```bash
# Execute a suite completa de testes
PYTHONPATH=. pytest -v --capture=no

# Execute smoke tests
PYTHONPATH=. python3 tools/smoke_check.py
```

---

## Governanca

- **Proprietario:** Builder-repo
- **Categoria:** Engenharia-Arquitetura
- **KPI de Valor:** +20% cobertura de atributos por lead
- **Issue de referencia:** ISSUE-001

---

_Documentacao atualizada em 2026-04-18._
