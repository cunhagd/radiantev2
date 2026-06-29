# Tasks — Controle de Estado dos Botoes

**Input**: specs/010-controle-botoes/spec.md, specs/010-controle-botoes/plan.md

## 1. [US1] Criar funcao updateButtonsState(hasData) em ui.js
**Arquivo**: `frontend/js/ui.js`
- Criar funcao que aceita booleano `hasData`
- Se `hasData === true`: desabilita btnUpload, btnOnce, btnTen; habilita btnClear
- Se `hasData === false`: habilita btnUpload; desabilita btnOnce, btnTen, btnClear

## 2. [US2] Integrar updateButtonsState no carregamento inicial (DOMContentLoaded)
**Arquivo**: `frontend/index.html` (script inline)
- Apos `API.loadLastResult()`, verificar se retornou dados validos
- Se sim: chamar `updateButtonsState(true)`
- Se nao: chamar `updateButtonsState(false)`

## 3. [US1] Integrar updateButtonsState no clearAllFrontendData()
**Arquivo**: `frontend/js/ui.js`
- Ao final de `clearAllFrontendData()`, chamar `updateButtonsState(false)`

## 4. [US4] Integrar updateButtonsState no renderAll()
**Arquivo**: `frontend/index.html` (script inline)
- Dentro de `renderAll()`, quando dados sao validos, chamar `updateButtonsState(true)`

## 5. [US3] Integrar updateButtonsState apos upload bem-sucedido
**Arquivo**: `frontend/js/ui.js`
- Em `handleFileUpload()`, apos sucesso, chamar `UI.updateButtonsState(false)`
- Nota: `false` porque upload nao cria dados renderizados, apenas prepara para analise
- Apos upload, habilitar botoes 1x e 10x

## 6. [ALL] Testes unitarios
**Arquivo**: `frontend/tests/ui.test.js`
- Testar estados: sem dados, com dados, apos upload, apos limpeza
