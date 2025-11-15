# Plano 3.1 – Reinstalação Limpa e Orquestração com Sub‑Agentes (Zero custos de IA)

## Objetivos
- Reinstalar WordPress/WooCommerce de forma limpa e previsível.
- Visual moderno, clean e funcional (menu/dropdowns, hero, galerias, responsividade).
- Publicar apenas produtos completos (preço + fotos), Sheet como fonte de verdade.
- Reaproveitar ativos existentes (918 fotos originais + lotes AI piloto), sem gastar mais em IA.
- Fluxo sustentável com validação contínua, documentação e staging.

## Tema e Abordagem Visual
- Manter Flatsome + Child Theme: maturidade do UX Builder, integração WooCommerce e velocidade de implementação.
- Modernização: tokens de design (cores, tipografia, spacing), SCSS modular, remoção de CSS/JS não usados (Perfmatters) e lazy‑load.
- Futuro opcional: Block Theme/Woo Blocks ou headless; manter caminho aberto sem impactar agora.

## Arquitetura de Sub‑Agentes
- **Orchestrator‑3.1**: agenda, coordena, agrega logs/relatórios (`relatorios/*`, `validation/*`).
- **SheetSync‑Agent**: sincroniza Google Sheet → catálogo local.
- **SheetSanitizer‑Agent**: normaliza dados (nomes, preço, atributos), marca erros.
- **DescriptionBuilder‑Agent**: descrições curtas/longas por templates (rule‑based, sem IA).
- **PriceGate‑Agent**: gates de publicação (preço > 0, imagens ≥ 2) e definição publish/draft.
- **ImageInventory‑Agent**: inventário/normalização de imagens (dedupe, hash mismatch, nomes/pastas por SKU).
- **PhotoTriage‑Agent (novo)**: triagem/import massivo de fotos (originais + AI já existentes) com match por SKU; associação de galerias/featured.
- **GalleryLinker‑Agent**: vincula imagens canónicas aos produtos; garante 2+ fotos antes de publicar.
- **VariationBuilder‑Agent (novo)**: consolida famílias de SKUs em produtos variáveis (atributos cor/tamanho) com fotos por variação.
- **ImportVerifier‑Agent**: valida CSV/REST e executa import controlado (evita duplicados por `_sku`).
- **WooPagesFixer‑Agent**: reatribui páginas Shop/Cart/Checkout e faz `rewrite flush`; valida 200 OK.
- **MenuUXFix‑Agent**: corrige z‑index/stacking do header/dropdowns e centragem de pessoas na home.
- **VisualQA‑Agent (BackstopJS)**: regressão visual automatizada (Home, Shop, PDP, Cart, Checkout) em desktop/mobile + checklist.
- **DataDiff‑Agent**: compara estados (publish/draft), duplica por `_sku`, metas e deltas.
- **Security&SEO‑Agent**: headers, GA4/GTM, CookieYes, sitemap; migração segura de segredos.

## Fluxo de Trabalho
1. **Reinstalação Limpa** → WordPress + WooCommerce + Flatsome + Child Theme.
2. **SheetSync** → **SheetSanitizer** → **DescriptionBuilder** → **PriceGate** (gera `catalogo_clean_ready.csv`).
3. Em paralelo: **ImageInventory** → **PhotoTriage** → **GalleryLinker** (garante canonicidade e 2+ fotos).
4. **VariationBuilder** (famílias de SKUs) → **ImportVerifier** (CSV/REST com gate: `price>0` & `images≥2`).
5. **WooPagesFixer** (404/permalinks) → **MenuUXFix** (z‑index/dropdowns/hero).
6. **VisualQA (BackstopJS)** → **DataDiff** → **Security&SEO**.
7. **Orchestrator** agrega relatórios finais e publica em staging.

## Reaproveitamento de Recursos (Zero custo IA)
- Usar `wp-content/uploads/catalogo2025/` como canónico.
- Resolver 10 hash mismatches, mantendo a melhor qualidade; documentar decisões.
- Priorizar os 72 SKUs com 2+ fotos para publicação.
- Reusar lotes AI piloto (5 SKUs) apenas quando coerentes com a estética; nada de novas chamadas.
- Padronizar nomes: `img_01.jpg…img_09.jpg` (originais) + sufixos editoriais (`img_01_angle.jpg`, `img_01_lifestyle.jpg`) após aprovação.
- Eliminar cruzamentos de pastas (ex.: imagens de um SKU dentro de outro).

## Gestão da Planilha Google
- **Fonte de Verdade**: Sheet como painel principal; sincronização idempotente.
- **Templates de descrição** (sem IA):
  - Curta: `[Tipo] · [Material] · [Origem] · [Variações]`.
  - Longa: parágrafos a partir de `Composição`, `Tamanhos`, `Vendido por`, `Ocasião/Coleção`.
- **Validações**: nome não vazio, preço numérico > 0, imagens ≥ 2, categorias coerentes; erros em aba `errors`.
- **Publicação automática**: só linhas completas; restantes ficam `draft` com `needs_review=true`.
- **Logs**: `relatorios/SYNC_SHEET_3_1.md` com totais, erros, sugestões.

## UX & Correções Frontend
- **Menu/dropdowns**: header acima do hero; dropdowns absolutos ancorados ao item; testes sticky/mobile.
- **Hero**: evitar `isolation` e overlays acima do menu; manter motion leve.
- **Pessoas na home**: `object-position` específico por bloco para reduzir cortes de cabeça.
- **Coleções/Novidades**: grids responsivos, tokens de spacing, lazy‑load para performance.

## Validação Contínua
- **VisualQA (BackstopJS)**: cenários Home/Shop/PDP/Cart/Checkout; desktop 1920 e mobile 375.
- **DataDiff**: metas por estado (publish/draft), duplicados por `_sku`, evolução do catálogo.
- **Baseline de performance**: Lighthouse (LCP, CLS, TTI) e ajustes.

## Segurança e Conformidade
- Migrar segredos para `.env.local`/secrets e remover do repo.
- Headers de segurança e RGPD (CookieYes); GA4/GTM após catálogo/UX estáveis.
- Backups automáticos (DB + uploads) e health checks simples.

## Critérios de Sucesso
- Navegação perfeita (menu/submenus visíveis; hero não bloqueia).
- ≥90 produtos publicados com preço e 2+ fotos.
- Import automatizado via Sheet com validação e relatórios claros.
- Zero custos adicionais de IA (descrições rule‑based; reaproveitamento de imagens existentes).
- Staging ativo, QA e documentação completa.

## Agenda (48h & Semana)
- **0–4h**: PhotoTriage (piloto 10 SKUs), validação frontend.
- **5–12h**: SheetSync/Sanitizer/Descriptions + PriceGate.
- **13–24h**: MenuUXFix + WooPagesFixer + VisualQA baseline.
- **25–48h**: VariationBuilder (piloto 5 famílias) + ImportVerifier; DataDiff.
- **Semana**: ampliar import, ajustes finos, relatórios consolidados, performance.

## Entregáveis
- `RELATORIO_CATALOGO_3_1.md` – estado, metas, gates, pendências.
- `RELATORIO_IMAGENS_3_1.md` – inventário por SKU, mismatches resolvidos, cruzamentos eliminados.
- `QA_VISUAL_3_1.md` – screenshots antes/depois, diffs e checklist UX.
- `SHEET_PIPELINE_3_1.md` – validações e templates de descrição; uso pelo cliente.
- `OPERACIONAL_WOOCOMMERCE_3_1.md` – reatribuições de páginas, flush permalinks, testes 200.

## Riscos & Mitigações
- Duplicados por SKU: gate + verificação `_sku` pré‑import; relatório de duplicados.
- Inconsistência de imagens: ImageInventory + PhotoTriage + GalleryLinker garantem canonicidade por SKU.
- Regressões visuais: BackstopJS com diffs e aprovação antes de publicar.
- Segredos expostos: migração imediata de `.env` para storage seguro.

Aprovando este plano 3.1 atualizado, inicio a reinstalação limpa e a execução com todos os sub‑agentes, mantendo relatórios e validações contínuas até atingir os critérios de sucesso.