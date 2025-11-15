# Passo 1 – Auditoria Técnica + Levantamento de Palavras-Chave

_Data_: 2025-10-29  
_Autor_: Codex (Audit Agent)

## 1. Estado Técnico Atual

| Área | Status | Evidência / Observação | Ação Requerida |
| --- | --- | --- | --- |
| Robots & Sitemap | ✅ | `/robots.txt` expõe sitemap gerado pelo Yoast em `http://localhost:8080/sitemap_index.xml`. | Monitorar após deploy para ambiente público; atualizar domínio no sitemap.
| Indexação | ⚠️ | Sitemap aponta para `localhost`, inviável em produção. | Ajustar URL base em Settings → General antes de ir para produção (ou filtrar via `WP_HOME/WP_SITEURL`).
| Canonical | ⚠️ | `<link rel="canonical" href="http://localhost:8080/" />` ainda em `localhost`. | Atualizar domínio definitivo no launch.
| Idioma `html` | ⚠️ | `lang="en-US"` apesar de conteúdo PT. | Definir idioma do site (`Settings → General → Site Language`) para `pt-PT`.
| Meta description | ⚠️ | Yoast não está a injetar `meta name="description"` na home (apenas OG tags). | Configurar meta description manualmente no Yoast para cada página crítica.
| Schema | ✅ | Yoast gera JSON-LD (`yoast-schema-graph`). | Manter; adicionar schema Product/FAQ nas páginas chave.
| Core Web Vitals | ❓ | Não medido neste ambiente (requer Lighthouse/CrUX). | Executar Lighthouse (mobile) e WebPageTest na preparação do deploy.
| Assets | ⚠️ | Child-theme injeta múltiplos scripts externos (Swiper, AOS, GLightbox) em todas as páginas. | Avaliar carregamento condicional para reduzir bloqueios.
| GA4 / Tracking | ❌ | Não existe `gtag.js` na home. | Implementar GA4 + Consent Mode antes de promover o site.
| Segurança | ❓ | Cabeçalhos (HSTS, CSP) não configurados (requere validação no servidor prod). | Preparar configuração Apache/Nginx para produção.

### 1.1 WooCommerce – Produtos

```
SELECT p.ID, p.post_title, pm.meta_value AS price
FROM lx_posts p
JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_price'
WHERE p.post_type='product' AND CAST(pm.meta_value AS DECIMAL(10,2)) > 1000;
```

Resultado: _sem produtos > €1000 na base atual_. Se voltarem a aparecer no frontend, provável cache/variações. Recomendado: criar relatório automático com `wp wc product list --price_min=1000` para auditorias semanais.

### 1.2 Checklist Técnico Imediato

- [ ] Garantir `WP_HOME`/`WP_SITEURL` apontam para domínio final antes do deploy.
- [ ] Definir idioma `pt-PT` e rever traduções.
- [ ] Configurar meta descriptions personalizadas nas páginas core (`Home`, `Loja`, `Sobre Nós`, `Serviços`).
- [ ] Preparar scripts Lighthouse (mobile + desktop) e manter logs.
- [ ] Mapear todos os scripts externos e avaliar atraso (`defer`/`async`).
- [ ] Configurar GA4 + Tag Manager + Consent Mode.

## 2. Levantamento de Palavras-Chave (PT-PT)

_Classificação baseada em intenção + estimativas de procura (dados de mercado PT; priorizar validação via Google Keyword Planner/Ahrefs quando disponível)._ 

| Keyword principal | Volume Est. /mês | Intenção | Conteúdo Sugerido | CTA |
| --- | --- | --- | --- | --- |
| chapéus lisboetas | 150 | Navegacional/Brand | Home otimizada com USP, depoimentos locais | Visitar Loja / Contactar Atelier |
| chapelaria lisboa | 400 | Comercial | Landing para loja física + mapa Google Business | Agendar Visita |
| chapéus artesanais | 250 | Consideração | Artigo “Como são feitos os nossos chapéus artesanais” | Solicitar Personalização |
| chapéu panamá lisboa | 180 | Transacional | Página coleção Panamá com FAQ + vídeo | Comprar Agora |
| remodelação de chapéus | 90 | Serviço | Página “Serviços & Atelier” com processo passo a passo | Pedir orçamento |
| feltro fedora portugal | 120 | Long tail | Blog/guia “Fedoras premium feitos em Portugal” | Ver stock inverno |
| boina portuguesa tradicional | 110 | Long tail | Página produto + storytelling “boina Tardia” | Comprar |
| chapéu cerimónia senhora | 160 | Transacional | Coleção cerimónia com lookbook | Reservar prova |
| como escolher tamanho chapéu | 300 | Informacional | Guia evergreen + tabela medidas | Descarregar guia + captar email |
| atelier de chapéus | 200 | Consideração | Página institucional “Sobre Nós” revamp + vídeo bastidores | Marcar visita |

Cluster secundário (conteúdo blog): `história chapelaria lisboa`, `como cuidar chapéu feltro`, `chapéus inverno homem`, `chapéus verão senhora`, `tendências chapéus 2026`, `chapéus personalizados empresas`.

### 2.1 Mapeamento Página ↔ Keyword Primária

| Página / URL alvo | Keyword foco | Elementos a otimizar |
| --- | --- | --- |
| `/` | chapéus lisboetas | Title, meta description, H1, copy hero com CTA, dados estruturados Organization, proof social |
| `/loja/` + categorias | chapelaria lisboa | H1 único, intro comercial, breadcrumbs, filtros, FAQ schema |
| `/servicos-atelier/` (ou equivalente) | remodelação de chapéus | Estrutura em etapas, “Antes/Depois”, formulário dedicado |
| `/sobre-nos/` | atelier de chapéus | Storytelling, linha do tempo, CTA visita, vídeo |
| `/blog/` + posts | como escolher tamanho chapéu / chapéus artesanais | Conteúdo 1500+ palavras, interlinking, CTA newsletter |
| Coleção Panamá | chapéu panamá lisboa | Fotos HD, alt text, FAQ “Autenticidade Panamá”, snippet local |
|

## 3. Próximas Ações (Sequência Prioritária)

1. **Corrigir Base Técnica** (1-2 dias)
   - Atualizar idioma, metas, preparar domínio real.
   - Instalar e configurar GA4 + Tag Manager + Search Console.
   - Executar testes Lighthouse e registar baseline.
2. **Reescrever Conteúdo Crítico** (2-3 dias)
   - Home, Loja, Sobre Nós com keywords mapeadas e copy orientada a conversão.
   - Adicionar FAQ schema e CTA claros.
3. **Preparar Calendário Editorial** (1-2 dias)
   - 6 a 8 peças “10x” para Q4 (guias, bastidores, lifestyle). 
   - Incluir plano de PR local (Turismo Lisboa, Time Out, bloggers).
4. **Setup de Monitorização** (0.5 dia)
   - Dashboards Looker Studio (GA4 + Search Console).
   - Alerts para quedas de ranking e Core Web Vitals.
5. **Checklist de Pré-lançamento**
   - Backup completo, limpeza de caches, revisão UX/CRO.
   - Verificação final de Core Web Vitals e acessibilidade.

> _Nota_: Este relatório cobre o Passo 1. Para Passo 2 (conteúdo/CRO) e Passo 3 (off-page/monitorização) utilizar este documento como base e criar tarefas no gestor de projetos.
