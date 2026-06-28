---

description: Task list for refatoracao da arquitetura
---

# Tasks: Refatoracao da Arquitetura - Modularizacao do Backend

**Input**: Design documents from specs/001-refatoracao-arquitetura/

## Path Conventions

- Backend: backend/ (modulos Python)
- Frontend: frontend/index.html (inalterado)

---

## Phase 1: Setup

- [ ] T001 Criar backend/ com __init__.py vazio
- [ ] T002 [P] Copiar requirements.txt do projeto de referencia
- [ ] T003 [P] Copiar .env.example com campos documentados
- [ ] T004 [P] Copiar frontend/index.html (inalterado)
- [ ] T005 [P] Copiar .github/workflows/deploy.yml
- [ ] T006 [P] Criar data/ com docs/ e markdown_docs/

---

## Phase 2: Foundational

- [ ] T007 Criar backend/config.py (dataclass Config + load_config)
- [ ] T008 [P] Criar backend/metrics.py (PipelineMetrics + calculate_costs)
- [ ] T009 [P] Copiar backend/prompts.py do projeto de referencia

---

## Phase 3: US1 - Modulos (P1)

- [ ] T010 [P] [US1] Criar backend/s3_client.py (interface S3 completa)
- [ ] T011 [P] [US1] Criar backend/extract.py (extratores de documento)
- [ ] T012 [P] [US1] Criar backend/pdf_generator.py (generate_pdf)
- [ ] T013 [P] [US1] Criar backend/bedrock_client.py (fallback regional)
- [ ] T014 [US1] Criar backend/pipeline.py (4 etapas + modos once/ten)

---

## Phase 4: US2 - app.py Leve (P1)

- [ ] T015 [US2] Refatorar backend/app.py para < 200 linhas (orquestrador)

---

## Phase 5: US3 - Config (P2)

- [ ] T016 [US3] Validar config na inicializacao do servidor
- [ ] T017 [US3] Criar .env.example documentado

---

## Phase 6: US4 - Metricas (P3)

- [ ] T018 [US4] Integrar PipelineMetrics no pipeline
- [ ] T019 [US4] Adicionar endpoint GET /api/metrics

---

## Phase 7: Validacao

- [ ] T020 Testar todos os endpoints HTTP
- [ ] T021 Testar pipeline completo (upload + analise 1x)
- [ ] T022 Testar modo 10x (paralelo + consolidacao)
- [ ] T023 Testar fallback Bedrock (ThrottlingException simulada)
- [ ] T024 Testar configuracao invalida
- [ ] T025 Cleanup: remover scripts temporarios