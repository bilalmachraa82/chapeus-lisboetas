# Plano 3.1 – Reinstalação Limpa e Orquestração com Sub‑Agentes (Sem custos adicionais de IA)

## Objetivos
- Reinstalar o site em ambiente limpo e previsível (sem “base torta”).
- Visual moderno, clean e funcional (menu/dropdowns, hero, galerias).
- Publicar apenas produtos completos (preço + fotos) via Google Sheet como fonte de verdade.
- Reaproveitar ao máximo os ativos atuais (918 fotos originais + lotes AI piloto) sem gastos adicionais de IA.
- Garantir manutenção sustentável com validação contínua e documentação clara.

## Decisão de Tema (Flatsome vs Alternativas)
- Manter Flatsome + Child Theme: ainda faz sentido para e‑commerce clássico em WordPress, pela maturidade do UX Builder, integração com WooCommerce e agilidade visual.
- Modernização: usar tokens de design, SCSS modular e remoção de CSS/JS não utilizados (Perfmatters), garantindo aparência atual e performance.
- Opcional futuro: Block Theme + WooCommerce Blocks ou headless (Next.js). Não necessário agora; o Plano 3.1 mantém caminho aberto.

## Arquitetura de Sub‑Agentes
- Orchestrator‑3.1: coordena execução, agendas, logs e relatórios (`relatorios/*`, `validation/*`).
- SheetSync‑Agent: sincroniza Google Sheet → catálogo local (base em `scripts/sync_google_sheet.py`).
- SheetSanitizer‑Agent: normaliza dados (nomes, preço, atributos) e marca erros.
- DescriptionBuilder‑Agent: gera descrições curtas/longas por templates (regras determinísticas; sem IA paga).
- PriceGate‑Agent: valida preço (>0) e define publish/draft conforme regras.
- ImageInventory‑Agent: audita e normaliza imagens (dedupe, hash mismatch, nomes, pastas por SKU).
- GalleryLinker‑Agent: vincula imagens canónicas a produtos (mínimo 2 fotos antes de publicar).
- ImportVerifier‑Agent: valida CSV/REST e executa import controlado (evita duplicados por `_sku`).
- WooPagesFixer‑Agent: reatribui páginas Shop/Cart/Checkout e executa `rewrite flush`; valida 200 OK.
- MenuUXFix‑Agent: corrige z‑index/stacking do header/dropdowns e centragem de pessoas na home.
- VisualQA‑Agent: captura screenshots (home, loja, PDP), diffs visuais e checklist de UX.
- DataDiff‑Agent: compara estados (publish/draft), reporta discrepâncias e metas.
- Security&SEO‑Agent: headers, GA4/GTM, CookieYes, sitemap; migra segredos fora do repo.

## Fluxo de Trabalho entre Sub‑Agentes
1. Reinstalação limpa → WordPress + WooCommerce + Flatsome + Child Theme.
2. SheetSync → SheetSanitizer → DescriptionBuilder → PriceGate (gera `catalogo_clean_ready.csv`).
3. Em paralelo: ImageInventory → GalleryLinker (garante imagens canónicas por SKU).
4. ImportVerifier (CSV/REST) com gate: entra apenas se `price>0` e `images>=2`.
5. WooPagesFixer (404/permalinks) → MenuUXFix (z‑index, dropdowns, hero).
6. VisualQA → DataDiff → Security&SEO.
7. Orchestrator agrega relatórios: `RELATORIO_CATALOGO_3_1.md`, `RELATORIO_IMAGENS_3_1.md`, `QA_VISUAL_3_1.md`.

## Otimização de Recursos Existentes (Sem custo de IA)
- Imagens: usar `wp-content/uploads/catalogo2025/` como canónico; resolver 10 hash mismatches (ver `relatorios/IMAGENS_CONSOLIDACAO_20251111.md:14-27`).
- Cobertura fotográfica: manter 72 SKUs com 2+ fotos (ver `relatorios/product_images_summary.md:8-20`), priorizando publicação.
- Lotes AI piloto: reaproveitar 5 SKUs já gerados (`relatorios/ai_photos_tracking_20251112_182743.csv:2-6`) quando coerentes.
- Padronização de nomes: `img_01.jpg…img_09.jpg` (originais) + sufixos editoriais (`img_01_angle.jpg`, `img_01_lifestyle.jpg`) somente após aprovação.
- Eliminar cruzamentos de pastas (ex.: `bone-22195_*` dentro de `bone-25023/`).

## Gestão da Planilha Google
- Fonte de Verdade: Sheet é o painel principal; sincronização idempotente.
- Templates de Descrição (sem IA):
  - Curta: `[Tipo] · [Material] · [Origem] · [Variações]`.
  - Longa: parágrafos a partir de `Composição`, `Tamanhos`, `Vendido por`, `Ocasião/Coleção`.
- Validações antes da importação: nome não vazio, preço numérico > 0, imagens ≥ 2, categorias/atributos coerentes; erros vão para aba `errors`.
- Publicação automática: apenas linhas “completas”; restantes ficam `draft` com `needs_review=true`.
- Logs: `relatorios/SYNC_SHEET_3_1.md` com totais, erros, sugestões.

## UX & Correções Frontend
- Menu/dropdowns: header sempre acima do hero; dropdowns absolutos ancorados ao item; testes em sticky/mobile.
- Hero: evitar `isolation` e overlays com z‑index acima do menu; manter motion leve.
- Pessoas na home: `object-position` específico por bloco para reduzir cortes de cabeça.
- Coleções e Novidades: grids responsivos, espaçamentos consistentes e lazy‑load.

## Qualidade e Validação Contínua
- VisualQA: screenshots padronizados desktop/tablet/mobile; diffs com tolerância controlada.
- DataDiff: metas por estado (publish/draft), contagem de SKUs, duplicados por `_sku`.
- Revisão semanal: checklist e micro‑ajustes; baseline de performance (Lighthouse).

## Segurança e Conformidade
- Migrar segredos (.env) para `.env.local`/secrets; remover do repo.
- Headers de segurança e RGPD (CookieYes); GA4/GTM após catálogo/UX.
- Backups automáticos (`DB + uploads`) e health checks simples.

## Critérios de Sucesso
- Navegação perfeita (menu/submenus visíveis em todas as páginas; hero não bloqueia).
- ≥90 produtos publicados com preço e 2+ fotos.
- Importação automatizada via Sheet com validação e relatórios claros.
- Zero custos adicionais de IA (descrições rule‑based).
- Manutenção sustentável com staging, QA e documentação.

## Agenda (Fases)
- Fase A (Dia 1): reinstalação limpa + child theme; configurar páginas WooCommerce.
- Fase B (Dia 2): SheetSync/Sanitizer/Descriptions + ImageInventory; plano de correções.
- Fase C (Dia 3): MenuUXFix + WooPagesFixer; VisualQA inicial.
- Fase D (Dia 4): GalleryLinker + ImportVerifier (piloto 20–30 produtos); DataDiff.
- Fase E (Dia 5): Ajustes finos, relatórios consolidados; baseline performance/acessibilidade.

## Entregáveis
- `RELATORIO_CATALOGO_3_1.md` – estado e metas do catálogo.
- `RELATORIO_IMAGENS_3_1.md` – inventário por SKU, mismatches resolvidos.
- `QA_VISUAL_3_1.md` – screenshots antes/depois e checklist UX.
- `SHEET_PIPELINE_3_1.md` – regras de validação e templates de descrição.
- `OPERACIONAL_WOOCOMMERCE_3_1.md` – reatribuições de páginas, flush, testes 200.

## Riscos & Mitigações
- Duplicados por SKU: gate e verificação por `_sku` antes de import; relatório de duplicados.
- Inconsistência de imagens: ImageInventory + GalleryLinker garantem canonicidade por SKU.
- Regressões visuais: VisualQA com diffs e aprovação antes de publicar.
- Segredos expostos: migração imediata de `.env` para storage seguro.

Se aprovar o Plano 3.1, inicio a reinstalação limpa e a orquestração dos sub‑agentes com geração dos relatórios e validações descritas acima.