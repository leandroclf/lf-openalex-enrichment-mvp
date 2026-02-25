# Arquitetura inicial — lf-openalex-enrichment-mvp

## Especialistas responsáveis
- Arquiteto: architect-tech
- Infra/CI-CD: sre-cost-specialist
- Backend: builder-repo
- Frontend/UI: architect-tech

## Componentes
- backend/src/service.py: núcleo de serviço
- frontend/index.html: camada de visualização inicial
- infra/docker-compose.yml: execução local mínima
- .github/workflows/ci.yml: validações básicas de CI

## Próximo incremento
1. Implementar conector de dados principal
2. Expor contrato de saída
3. Medir qualidade/cobertura
