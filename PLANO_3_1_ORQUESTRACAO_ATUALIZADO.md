# Plano 3.1 – Reinstalação Limpa e Orquestração com Sub‑Agentes (Zero custos de IA)

## Objetivos
- Reinstalar WordPress/WooCommerce de forma limpa e previsível.
- Visual moderno, clean e funcional (menu/dropdowns, hero, galerias, responsividade).
- Publicar apenas produtos completos (preço + fotos), Sheet como fonte de verdade.
- Reaproveitar ativos existentes (918 fotos originais + lotes AI piloto), sem gastar mais em IA.
- Fluxo sustentável com validação contínua, documentação e staging.

## Tema e Abordagem Visual
- Manter Flatsome + Child Theme.
- Modernização: tokens de design, SCSS modular, remoção de CSS/JS não usados e lazy‑load.
- Futuro opcional: Block Theme/Woo Blocks ou headless; manter caminho aberto.

## Sub‑Agentes
- Orchestrator‑3.1, SheetSync, SheetSanitizer, DescriptionBuilder, PriceGate.
- ImageInventory, PhotoTriage, GalleryLinker.
- VariationBuilder, ImportVerifier.
- WooPagesFixer, MenuUXFix.
- VisualQA (BackstopJS), DataDiff, Security&SEO.

## Fluxo
1. Reinstalação limpa → WP + WC + Flatsome + Child.
2. SheetSync → SheetSanitizer → DescriptionBuilder → PriceGate.
3. Em paralelo: ImageInventory → PhotoTriage → GalleryLinker.
4. VariationBuilder → ImportVerifier (gates: `price>0`, `images≥2`).
5. WooPagesFixer → MenuUXFix.
6. VisualQA (BackstopJS) → DataDiff → Security&SEO.
7. Orchestrator publica relatórios e staging.

## Reaproveitamento (Zero custo IA)
- Usar `wp-content/uploads/catalogo2025/` como canónico.
- Resolver 10 hash mismatches; documentar.
- Priorizar 72 SKUs com 2+ fotos.
- Reusar lotes AI piloto (5 SKUs) quando coerentes.
- Padronizar nomes: `img_01.jpg…img_09.jpg` + sufixos editoriais.
- Eliminar cruzamentos de pastas.

## Planilha Google
- Fonte de Verdade; sincronização idempotente.
- Templates de descrição (sem IA):
  - Curta: `[Tipo] · [Material] · [Origem] · [Variações]`.
  - Longa: baseada em `Composição`, `Tamanhos`, `Vendido por`, `Ocasião/Coleção`.
- Validações: nome, preço > 0, imagens ≥ 2, categorias coerentes.
- Publicação automática só para linhas completas; restantes `draft`.
- Logs: `relatorios/SYNC_SHEET_3_1.md`.

## UX & Frontend
- Menu/dropdowns: header acima do hero; dropdown absoluto ancorado.
- Hero: evitar `isolation` acima do menu.
- Pessoas na home: `object-position` por bloco.
- Grids responsivos; tokens de spacing; lazy‑load.

## Validação
- BackstopJS: Home/Shop/PDP/Cart/Checkout, desktop 1920 e mobile 375.
- DataDiff: metas publish/draft, duplicados `_sku`.
- Performance: Lighthouse e ajustes.

## Segurança
- Migrar segredos para storage seguro; remover do repo.
- Headers de segurança; RGPD; GA4/GTM.
- Backups DB + uploads; health checks.

## Critérios
- Navegação perfeita; hero não bloqueia.
- ≥90 produtos com preço e 2+ fotos.
- Import automatizado via Sheet com validação.
- Zero custos adicionais de IA.
- Staging, QA e documentação completos.

## Agenda
- 0–4h: PhotoTriage (piloto 10 SKUs), validação frontend.
- 5–12h: SheetSync/Sanitizer/Descriptions + PriceGate.
- 13–24h: MenuUXFix + WooPagesFixer + VisualQA baseline.
- 25–48h: VariationBuilder (piloto 5 famílias) + ImportVerifier; DataDiff.
- Semana: ampliar import, relatórios consolidados, performance.

## Entregáveis
- `RELATORIO_CATALOGO_3_1.md`, `RELATORIO_IMAGENS_3_1.md`, `QA_VISUAL_3_1.md`, `SHEET_PIPELINE_3_1.md`, `OPERACIONAL_WOOCOMMERCE_3_1.md`.

## Riscos & Mitigações
- Duplicados `_sku`: gate + relatório.
- Inconsistência de imagens: inventário + triagem + vinculação.
- Regressões visuais: BackstopJS com aprovação.
- Segredos expostos: migração imediata.