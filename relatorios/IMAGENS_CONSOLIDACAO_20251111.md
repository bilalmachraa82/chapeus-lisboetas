# Consolidação de Imagens – 11/11/2025

## Diretórios
- Legacy: `wordpress/wp-content/uploads/products/`
- Canónico: `wordpress/wp-content/uploads/catalogo2025/`

## Estatísticas
- Ficheiros em legacy: 6 457
- Ficheiros em canónico (antes): 1 097
- Duplicados (mesmo path em ambas pastas): 914
- Ficheiros exclusivos do legacy copiados para canónico: 5 543
- Ficheiros em canónico (depois): 6 640

## Hash mismatches (mesmo path mas conteúdo diferente)
> Necessitam de revisão manual para decidir qual versão manter.

1. `chapéus lã/chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_03.jpg`
2. `chapéus lã/chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_04.jpg`
3. `chapéus lã/chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_05.jpg`
4. `cowboy/bone-15114/img_04.jpg`
5. `cowboy/bone-15114/img_05.jpg`
6. `cowboy/bone-15114/img_07.jpg`
7. `cowboy/bone-15114/img_10.jpg`
8. `cowboy/bone-15114/img_11.jpg`
9. `cowboy/bone-15114/img_12.jpg`
10. `cowboy/bone-15114/img_13.jpg`

Para cada um, o script registou hashes diferentes (ver saída da execução). Até decidir, mantivemos **ambas** as versões (não sobrescreve).

## Próximos passos
1. Atualizar todos os scripts/imports para usarem apenas `catalogo2025`.
2. Rever os 10 ficheiros com hash divergente e normalizar.
3. Após validação, planear remoção da pasta legacy (`products/`) para libertar espaço.
4. Continuar com regeneração de thumbnails (Fase 2) e revisão de galerias (Fase 3).
