## Objetivos
- Fazer o menu voltar a aparecer e funcionar (desktop/mobile)
- Corrigir bugs visuais da landing page (hero, pessoas centradas, grid)
- Garantir que submenus não ficam atrás da imagem do hero

## Diagnóstico Rápido
- Menu dropdown preso atrás do hero por z‑index/stacking
- CSS global usa `object-fit: cover` e corta rostos nas fotos da home
- Hero tem `isolation: isolate` e overlays que podem criar contextos de empilhamento
- Possível perda de atribuição de menus/páginas após updates/permalinks

## Plano de Correção
### 1) Menu visível e funcional
- Reatribuir menus em Aparência → Menus e verificar `Primary`/`Mobile`
- Elevar z‑index do header e dos submenus: `#masthead`, `.header-wrapper`, `.nav-dropdown` com `position` adequado
- Testar hover/click em sticky header e mobile (hamburger)

### 2) Hero e fotos de pessoas centradas
- Adicionar regra específica para a galeria/home: `object-position` ajustado (ex.: `50% 20%`) apenas nos blocos com pessoas
- Rever `wp-block-cover` do hero: manter overlays mas impedir que criem contexto acima do menu
- Validar proporções das imagens e remover zoom excessivo

### 3) Consistência de layout
- Verificar grid “Novidades” e coleções: alinhamento, espaçamento e responsividade
- Ajustar breakpoints (tablet/mobile) para evitar cortes/empenos

### 4) Verificações finais
- Flush de permalinks (se necessário) e confirmar que páginas chave respondem 200
- Capturas antes/depois (home, menu aberto, submenus, mobile)

## Entregáveis
- CSS corrigido (child theme/custom CSS) para menu e hero
- Checklist de validação com screenshots
- Relatório curto dos ajustes aplicados

## Agenda
- Hoje: aplicar fix de z‑index/position, centrar fotos, validar em 3 tamanhos de ecrã
- Amanhã: revisão fina do layout e anexar evidências com screenshots