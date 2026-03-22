# lf-openalex-enrichment-mvp: Plataforma de Enrichment B2B (ISSUE-001)

## Visão Geral

Este repositório contém o Mínimo Produto Viável (MVP) do componente de Enrichment B2B, focado na utilização de dados do OpenAlex para enriquecer perfis de leads e empresas. O objetivo principal é transformar dados brutos em inteligência acionável, calculando sinais de valor e métricas de cobertura que apoiam decisões comerciais e estratégicas.

## Contexto e Issue

Desenvolvido sob a **ISSUE-001: MVP de Enrichment B2B com OpenAlex**, este componente é um pilar estratégico para a geração de valor comercial, permitindo uma segmentação mais precisa e uma qualificação de leads mais eficiente.

## Problema Resolvido

No mercado B2B, a falta de dados completos e validados sobre leads e empresas dificulta a prospecção, personalização de ofertas e o cálculo preciso do potencial de valor. Este componente endereça essa lacuna, enriquecendo dados existentes e fornecendo métricas para priorização e análise.

## Objetivo do MVP

O MVP visa estabelecer uma base robusta para o enriquecimento de dados, com foco nas seguintes capacidades:

*   **Cálculo de Cobertura:** Medir a completude dos atributos de leads/empresas em relação a um conjunto de campos requeridos, incluindo cobertura ponderada.
*   **Sinal de Valor:** Classificar e priorizar leads com base em um "sinal de valor" derivado dos dados enriquecidos.
*   **Enriquecimento em Lote:** Processar lotes de leads para enriquecimento, gerando métricas de cobertura e processamento.
*   **Pontuação de Prioridade:** Atribuir uma pontuação que indica a prioridade de um lead para ser enriquecido, considerando dados faltantes e o potencial de valor.

## Objetivo Final em Produção (Visão Estratégica)

Quando em produção, o `lf-openalex-enrichment-mvp` será um serviço escalável e automatizado, capaz de:

*   **Enriquecimento Contínuo:** Processar leads em tempo real e em lote, integrando-se a diversas fontes de dados além do OpenAlex (quando aplicável e validado).
*   **Otimização de Funil:** Alimentar o funil comercial com leads de alta qualidade e com maior probabilidade de conversão, otimizando o CAC (Custo de Aquisição de Cliente).
*   **Personalização de Ofertas:** Fornecer dados ricos que permitem a criação de ofertas de produto/serviço altamente personalizadas.
*   **Inteligência de Mercado:** Gerar insights sobre tendências de mercado, setores e perfis de clientes ideais através da análise agregada dos dados enriquecidos.
*   **Base de Conhecimento:** Construir uma base de conhecimento sobre entidades e atributos que sirva de referência para outros sistemas.

## Funcionalidades Chave Implementadas (MVP)

*   `calculate_attribute_coverage()`: Calcula a taxa de completude de atributos.
*   `calculate_weighted_attribute_coverage()`: Calcula a taxa de completude com pesos por atributo.
*   `get_value_signal()`: Gera um sinal de valor inicial.
*   `get_value_band_classification()`: Classifica leads em bandas de valor.
*   `batch_enrich_leads()`: Processa um lote de leads para enriquecimento.
*   `get_enrichment_priority_score()`: Calcula a prioridade para o enriquecimento de um lead.

## Estratégia e Abordagem

O desenvolvimento segue uma abordagem incremental e orientada a testes, com foco na entrega contínua de funcionalidades que adicionam valor. A qualidade dos dados e a rastreabilidade das métricas são prioritárias, garantindo que o enriquecimento seja confiável e útil para as decisões de negócio.

## Stack Técnica

*   **Linguagem:** Python
*   **Ferramentas:** Git, GitHub Actions (CI/CD)
*   **Dados:** OpenAlex (fonte primária)

## Como Começar

Para configurar e executar o projeto localmente:

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/leandroclf/lf-openalex-enrichment-mvp.git
    cd lf-openalex-enrichment-mvp
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements-dev.txt
    ```

3.  **Execute o servidor HTTP:**
    ```bash
    PYTHONPATH=. python3 backend/src/http_server.py
    # Servidor disponível em http://localhost:8000
    ```

4.  **Execute testes:**
    ```bash
    PYTHONPATH=. python3 tools/smoke_check.py  # smoke tests
    PYTHONPATH=. pytest -v                      # suite completa
    ```

## Exemplos de Uso

### Endpoint de Enriquecimento `/enrich`

Enriqueça um lote de leads via HTTP POST:

```bash
curl -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "leads": [
      {"company": "Acme Corp", "domain": "acme.com", "industry": "Tech"},
      {"company": "Beta Inc", "domain": "", "industry": "Finance"}
    ],
    "config": {
      "fields": ["company", "domain", "industry", "employee_count"]
    }
  }'
```

Resposta esperada:
```json
{
  "enriched": [...],
  "stats": {
    "total": 2,
    "enriched_count": 1,
    "coverage_rate": 0.625,
    "enrichment_rate": 0.5
  },
  "processed_at": "2026-02-28T14:30:00Z"
}
```

## Diretrizes de Contribuição

Este projeto adota um fluxo de trabalho de desenvolvimento que permite **commit direto na branch `main`**. Pull Requests são opcionais e encorajados para revisão colaborativa, mas não são obrigatórios para a integração de código.

## Governança

*   **Proprietário Primário (`ownerPrimary`):** Builder-repo
*   **Categoria Primária (`categoryPrimary`):** Engenharia-Arquitetura
*   **KPI de Valor (`valueKpi`):** +20% cobertura de atributos por lead

---
_Gerado por Stephen (agente) em 2026-02-27. Ref.: ISSUE-001._
