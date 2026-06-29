# Checklist — Controle de Estado dos Botoes

## Objetivo
Controlar quais botoes estao disponiveis com base na presenca de dados de rodagem anterior.

## Requisitos
- [ ] Sistema detecta se ha dados de rodagem anterior ou atual renderizados na tela
- [ ] Se houver dados: bloquear todos os botoes, exceto o botao lixeira
- [ ] Se nao houver dados: liberar apenas o botao de upload
- [ ] Botoes 1x e 10x so sao liberados apos upload bem-sucedido
