# Atualizações 27/10/2025

## Produtos
- Despublicados 13 produtos sem preço definido (IDs: 298, 300, 307, 315, 317, 339, 342, 347, 360, 373, 416, 505, 523).
- Atualizado `wp_wc_product_meta_lookup` para ajustar min/max price a zero nos produtos despublicados e evitar cache de preços.
- Normalizados preços dos SKU ativos relevantes (CHAPÉU COWBOY, bone-15114, algodao-4974, gorro-miki-12601, bone-18110ec) nas tabelas `wp_postmeta` e `wp_wc_product_meta_lookup`.

## Conteúdo
- Criado post de blog "3 Perguntas para Encontrar o Chapéu Perfeito" (ID 722) com destaque para coleções Panamá e Inverno.
- Atribuído o post à categoria "Uncategorized" (default) e imagem destacada ID 600.

## Homepage
- Atualizado hero com imagem de cliente (media ID 600) e CTA para Panamá / Contactos.
- Adicionada secção "Momentos com Chapéus Lisboetas" com slider `[ux_slider]` usando media 601, 600 e 599.

## Menus e Taxonomias
- Criada tag `Panamá` (term_id 230) e associada aos produtos 386, 392, 399. Menu "Loja → Panamá & Cerimónia" aponta para `/product-tag/panama/`.

## Observações
- Base ativa é o prefixo `wp_` (tabelas `lx_` mantêm dados legados). Qualquer script de sync deve apontar para `wp_posts`, `wp_postmeta`, etc.
- Produtos sem preço devem permanecer com `post_status = 'draft'` até definição de valores.
