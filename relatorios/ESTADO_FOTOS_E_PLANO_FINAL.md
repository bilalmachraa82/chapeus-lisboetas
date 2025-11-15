# ESTADO FOTOS + PLANO EXECUÇÃO FINAL

**Data:** 2025-11-09 23:25
**Branch:** ux-improvements-fase1-p0

---

## 📊 ESTADO ATUAL - FOTOS E DESCRIÇÕES

### ✅ DESCRIÇÕES: 100% COMPLETAS
- **Total:** 86/86 produtos (100%)
- **Gerado:** 61 descrições profissionais em português
- **Status:** ✅ Commit + push completos (commit 6d833a30)

### ⚠️  FOTOS: 32% COMPLETAS

**Análise Detalhada Executada:** `scripts/analyze_product_images.py`

#### Resumo Fotográfico:
- **Com fotos:** 28/86 produtos (32%)
- **Sem fotos:** 58/86 produtos (68%)
- **Com 2+ fotos:** 23 produtos
- **Com 1 foto:** 5 produtos
- **Máximo fotos/produto:** 19 fotos
- **Média:** 1.4 fotos/produto

#### Tipo de Fotos Disponíveis:
- **Fotos URLs:** 28 produtos (todas as fotos são URLs externas - Google Photos/Fornecedor)
- **Fotos Locais:** 0 produtos (ficheiros locais NÃO existem)

#### Problemas Identificados:
1. **58 produtos SEM fotos** (68% do catálogo)
2. **Preços inválidos:** ~8 produtos com "Etiqueta:" ou "Tags:" no campo preço
3. **URLs fornecedor:** Muitos retornam 404 (hologrammeparis.com)
4. **Ficheiros locais:** Paths existem no JSON mas ficheiros físicos NÃO

---

## 🎯 DECISÃO: PRODUTOS SEM FOTOS

**Regra implementada:** "Se não consegues encontrar as fotos através dos links do Google Sheet, não é para importar"

### Produtos a NÃO Importar (58 produtos):

Todos os produtos na secção "❌ PRODUTOS SEM FOTOS" do relatório `relatorios/product_images_summary.md`

### Produtos a Importar (28 produtos):

Todos os produtos na secção "✅ PRODUTOS COM FOTOS" do relatório `relatorios/product_images_summary.md`

**IMPORTANTE:** Antes de importar, verificar e corrigir preços inválidos:
- `gorro-miki-12601-gorro-640182503`: "Tags: Fabricado na China" → preço real?
- `algodao-4974`: "Etiqueta: Fabricado em Portugal" → preço real?
- `bone-12463`, `bone-12625`: "Etiqueta: Fabricado na China" → preços reais?

---

## 📸 PLANO FOTOSHOOT GEMINI (Opcional)

### Objetivo:
Transformar fotos existentes (Instagram, loja, caseiras) em imagens profissionais de e-commerce usando Google Gemini Flash 2.5

### Tecnologia:
- **Modelo:** Gemini Flash 2.5 (google-generativeai)
- **Custo:** €0.00 - €0.88 (free tier até 1,500 requests/dia)
- **Tempo:** ~4s por imagem gerada

### Processo:

#### 1. Identificar Fonte de Fotos
```bash
# Instagram @chapeuslisboetas
# - 372 posts disponíveis
# - Fotos caseiras de produtos na loja
# - Podem ter fundo desordenado, iluminação irregular
```

#### 2. Download Fotos Instagram
```bash
# Script já existe: instagram-to-professional-images.py
python3 instagram-to-professional-images.py --username chapeuslisboetas --limit 50
```

#### 3. Gemini Transformation Pipeline

**Prompt Premium para Gemini (Aligned com site/produto/indústria):**

```
You are a professional product photography AI for a premium Portuguese hat retailer "Chapéus Lisboetas" based in Chiado, Lisbon.

Transform this casual photo into 4 professional e-commerce images:

1. FRONT VIEW (main product image):
   - Pure white background (RGB 255,255,255)
   - Product centered, facing camera
   - Sharp focus on product details
   - Soft, even lighting (studio quality)
   - Resolution: 1500x1500px minimum
   - Style: Clean, elegant, minimalist

2. 3/4 ANGLE VIEW (secondary):
   - Same white background
   - Product rotated 45 degrees
   - Shows depth and shape
   - Highlights material texture
   - Professional lighting
   - Resolution: 1500x1500px

3. DETAIL CLOSE-UP (texture/quality):
   - Extreme close-up of material/stitching/label
   - Shows craftsmanship quality
   - White or soft neutral background
   - Macro-level sharpness
   - Resolution: 1200x1200px minimum

4. LIFESTYLE IMAGE (on mannequin):
   - Elegant mannequin head (neutral, no face)
   - Product worn naturally
   - Soft gray or cream background
   - Shows scale and fit
   - Professional studio lighting
   - Resolution: 1500x1500px

IMPORTANT:
- Remove any background clutter
- Enhance color accuracy
- Maintain product authenticity (don't alter shape/color)
- Portuguese premium quality aesthetic
- Suitable for luxury e-commerce (Rothys.com style)

Product Category: {PRODUCT_TYPE} (boina/chapéu/boné/panamá)
Material: {MATERIAL} (lã/algodão/palha/pele)
Color: {COLOR}
```

#### 4. Execução Script

```python
# Modificar instagram-to-professional-images.py
# - Update prompt com template acima
# - Gerar 4 imagens por produto
# - Salvar em output_catalogo/images_gemini/{SKU}/
# - Validar resolução mínima 1500x1500px
```

#### 5. QA Process (Sub-Agent Verification)

**Criar:** `scripts/verify_gemini_images.py`

Verificar:
- ✅ Resolução ≥1500x1500px
- ✅ Background branco (RGB >250 nas bordas)
- ✅ Produto centrado (bbox detection)
- ✅ Todas 4 imagens geradas
- ✅ Ficheiro <2MB (otimização)
- ✅ Formato JPG/PNG válido

#### 6. Estimativa Execução

**Para 28 produtos com fotos existentes:**
- Download Instagram: ~5 min
- Gemini processing: 28 produtos × 4 imagens × 4s = 7.5 min
- QA verification: ~3 min
- **Total:** ~15-20 minutos
- **Custo:** €0.00 (dentro free tier)

**Para 58 produtos SEM fotos:**
- **NÃO APLICÁVEL** - Gemini precisa de foto base para transformar
- **Solução:** Cliente fornece fotos OU produtos não são importados

---

## 🚀 PLANO PRÓXIMOS PASSOS

### FASE 1: Preparação Catálogo (AGORA - 1h)

**1.1. Corrigir Preços Inválidos**
```bash
# Criar script: scripts/fix_invalid_prices.py
# - Identificar produtos com preço "Etiqueta:" ou "Tags:"
# - Consultar Google Sheet para preço correto
# - Atualizar catalog.json
```

**1.2. Filtrar Produtos para Import**
```bash
# Criar: scripts/filter_importable_products.py
# - Incluir APENAS os 28 produtos com fotos
# - Excluir os 58 sem fotos
# - Gerar: output_catalogo/catalogo_importable.json
# - Gerar: output_catalogo/catalogo_woocommerce_ready.csv
```

**1.3. Opcional: Fotoshoot Gemini**
```bash
# Decisão: Executar ou skip?
# Se SIM: python3 instagram-to-professional-images.py --limit 30
# Se NÃO: Usar fotos existentes (URLs) diretamente
```

---

### FASE 2: Upgrade Stack (CRÍTICO - 2-3 dias)

**Risco Atual:** PHP 7.4 EOL há 1077 dias (3 anos) = vulnerabilidades não patch

adas

#### Opção A: Upgrade Completo (RECOMENDADO)

**Timeline:** 2-3 dias
**Risco:** Médio (plugins podem quebrar)
**Benefício:** Segurança garantida, compliance, performance

**Passos:**
```bash
# 1. Clone ambiente staging
docker-compose -f docker-compose.staging.yml up -d
# Porta 8082, database separada

# 2. Upgrade PHP 7.4 → 8.1
# Modificar docker-compose.staging.yml:
#   image: wordpress:6.4-php8.1-apache

# 3. Test plugins críticos
# - WooCommerce
# - IfthenPay
# - Flatsome theme
# - Yoast SEO

# 4. Upgrade WordPress 5.4.1 → 6.4.x
# Via WP admin ou WP-CLI

# 5. Test checkout flow completo
# - Add to cart
# - Checkout
# - Payment (Multibanco sandbox)
# - Order confirmation

# 6. Deploy produção
# - Backup completo (já feito: backups/pre-upgrade-20251109/)
# - Apply changes to production docker-compose.yml
# - Monitor logs
# - Rollback plan ready

# 7. Verify produção
# - SSL/HTTPS working
# - Payment gateway
# - Order emails
# - SEO not broken
```

**Guia Detalhado:** Ver `PLANO_MASTER_REVISADO_V2.md` páginas 10-15

#### Opção B: Hardening Temporário (NÃO RECOMENDADO)

**Timeline:** 4h
**Risco:** Alto a longo prazo
**Benefício:** Deploy mais rápido, mas segurança comprometida

**Medidas:**
```php
// wp-config.php
define('DISALLOW_FILE_EDIT', true);
define('DISALLOW_FILE_MODS', true);
define('FORCE_SSL_ADMIN', true);
define('WP_AUTO_UPDATE_CORE', false);
```

- WAF rules (PTisp/Imunify360)
- Backups diários verificados
- Monitoring 24/7
- **Upgrade OBRIGATÓRIO até Jan 2026**

---

### FASE 3: Google Analytics 4 (2h)

**Objetivo:** Tracking e-commerce + RGPD compliance

**Método:**
```bash
# 1. Install plugin "Site Kit by Google"
# Via WP admin: Plugins → Add New → Search "Site Kit"

# 2. Configure via wizard
# - Email: mail@chapeuslisboetas.com
# - Connect Google account
# - Enable Analytics, Search Console

# 3. Enable enhanced e-commerce
# - GA4 events: pageview, add_to_cart, purchase
# - Product impressions
# - Transaction tracking

# 4. Test events
# - Use GA4 DebugView
# - Test transaction
# - Verify events aparecem em GA4

# 5. Integrate com CookieYes
# - Cookie consent management
# - Block GA4 até user consent
# - RGPD compliance
```

**Documentação:** Ver `PLANO_MASTER_REVISADO_V2.md` páginas 20-22

---

### FASE 4: Import WordPress (1 dia)

**4.1. Preparar Imagens**
```bash
# Se usou Gemini:
# - Upload images_gemini/{SKU}/ → WordPress Media Library
# - Associate com produtos via SKU

# Se usa URLs existentes:
# - WooCommerce CSV import suporta external image URLs
# - WordPress fará download automático
```

**4.2. Import Produtos**
```bash
# Via WooCommerce → Products → Import
# - Upload: output_catalogo/catalogo_woocommerce_ready.csv
# - Map columns:
#   - SKU → sku
#   - Nome → name
#   - Preço → regular_price
#   - Descrição curta → short_description
#   - Imagens → images (URLs comma-separated)
# - Run import
# - Verify 28 produtos importados
```

**4.3. Configure IfthenPay**
```bash
# Já configurado no WordPress existente
# Verificar:
# - Entidade: 11873
# - Subentidade: 235
# - Test transaction em sandbox
```

**4.4. Configure Homepage**
```bash
# Flatsome UX Builder:
# - Featured products carousel
# - Category sections
# - Hero banner
# - Newsletter signup
```

---

### FASE 5: Testing & QA (1 dia)

**5.1. Functional Testing**
- [ ] Homepage loads <2s
- [ ] All product pages accessible
- [ ] Add to cart working
- [ ] Checkout flow completo
- [ ] Payment Multibanco functional
- [ ] Order confirmation email
- [ ] Admin order management

**5.2. Performance Testing**
```bash
# Google PageSpeed Insights
# Target: >85 mobile, >90 desktop

# Core Web Vitals:
# - LCP <2.5s
# - FID <100ms
# - CLS <0.1
```

**5.3. SEO Verification**
- [ ] All pages have meta descriptions
- [ ] Image alt text >95%
- [ ] XML sitemap generated
- [ ] Robots.txt correct
- [ ] Schema markup (Organization, Product)

**5.4. Security Check**
```bash
# SSLLabs.com test: Target A+
# Scan: Wordfence/Sucuri
# Headers: HSTS, X-Frame-Options, CSP
```

---

### FASE 6: Deploy Produção (0.5 dia)

**6.1. Pre-Deploy Checklist**
- [ ] Backup completo (já feito)
- [ ] Staging 100% functional
- [ ] Client approval
- [ ] Rollback plan ready
- [ ] DNS/CDN configured

**6.2. Go-Live**
```bash
# 1. Maintenance mode ON
# 2. Final database backup
# 3. Apply production changes
# 4. Import 28 produtos
# 5. Smoke test (5 min)
# 6. Maintenance mode OFF
# 7. Monitor (2h)
```

**6.3. Post-Deploy**
- [ ] GA4 tracking verificado
- [ ] Test transaction LIVE
- [ ] All pages 200 OK
- [ ] SSL certificate valid
- [ ] Email notifications working

---

### FASE 7: Client Training (1h)

**7.1. Backoffice Tour**
- Adicionar produtos
- Manage orders
- View analytics
- Update content

**7.2. Documentação**
- Manual PDF (20 páginas)
- Video tutorials (5-10 min cada)
- Emergency contacts

**7.3. Support Handoff**
- 3 months support included
- WhatsApp: +351 918 911 308
- Email: mail@chapeuslisboetas.com

---

## 📅 CRONOGRAMA EXECUÇÃO

**Assumindo Upgrade Completo (Opção A):**

```
Dia 1 (Dom 10 Nov):
  09:00-12:00 → FASE 1: Preparação catálogo
  14:00-18:00 → FASE 2.1: Clone staging + upgrade PHP
  Noite       → Testes automáticos staging

Dia 2 (Seg 11 Nov):
  09:00-13:00 → FASE 2.2: Upgrade WordPress + test plugins
  14:00-17:00 → FASE 3: Install GA4
  17:00-19:00 → FASE 4.1: Preparar imagens

Dia 3 (Ter 12 Nov):
  09:00-12:00 → FASE 4.2-4.4: Import produtos + config
  14:00-18:00 → FASE 5: Testing & QA
  Noite       → Client review staging

Dia 4 (Qua 13 Nov):
  10:00-12:00 → Ajustes finais cliente
  14:00-15:00 → FASE 6: Deploy produção
  15:00-17:00 → Monitoring + fixes
  17:00-18:00 → FASE 7: Client training

Dia 5-7 (Qui-Sáb):
  Buffer: Monitoring, ajustes menores, preparação Black Friday
```

**Go-Live:** 13 Nov 2025
**Black Friday:** 24 Nov 2025
**Margem:** 11 dias ✅ VIÁVEL

---

## 🎯 MÉTRICAS DE SUCESSO

**Técnicas (Launch):**
- PageSpeed Mobile: >85
- PageSpeed Desktop: >90
- Uptime primeiro mês: >99.5%
- Zero security vulnerabilities (high/critical)

**Business (30 dias):**
- Conversion rate: >1%
- Bounce rate: <60%
- Cart abandonment: <70%
- Newsletter sign-ups: >2% visitors

**SEO (30 dias):**
- Google impressions: >1,000/month
- Organic clicks: >50/month
- Top 10 keywords: >5

---

## 🚨 RISCOS E MITIGAÇÕES

### Risco 1: Plugin Incompatibility (Upgrade)
**Prob:** 30% | **Impact:** Alto
**Mitigação:** Staging environment completo, rollback plan

### Risco 2: 58 Produtos Sem Fotos
**Prob:** 100% | **Impact:** Médio
**Mitigação:** Launch com 28 produtos, adicionar outros depois

### Risco 3: Payment Gateway Issues
**Prob:** 10% | **Impact:** Crítico
**Mitigação:** Test extensively em staging, sandbox IfthenPay

### Risco 4: Timeline Delay
**Prob:** 40% | **Impact:** Médio
**Mitigação:** 11 dias buffer até Black Friday

---

## 📞 DECISÕES PENDENTES

### 1. Fotoshoot Gemini (AGORA)
- [ ] SIM - Executar transformação IA (~20 min)
- [ ] NÃO - Usar fotos URLs existentes

### 2. Upgrade Strategy (HOJE)
- [ ] Opção A: Upgrade completo PHP 8.1 + WP 6.4 (2-3 dias, seguro)
- [ ] Opção B: Hardening temporário (4h, rápido mas risco)

### 3. Produtos Sem Fotos (HOJE)
- [ ] Confirmar: NÃO importar os 58 sem fotos
- [ ] Alternativa: Cliente fornece fotos urgente (prazo?)

---

## ✅ PRÓXIMA AÇÃO IMEDIATA

**Aguardando decisão:**

1. **Fotoshoot Gemini:** SIM ou NÃO?
2. **Upgrade:** Opção A (seguro) ou B (rápido)?
3. **58 produtos sem fotos:** Confirmar exclusão?

**Após decisões:**
```bash
# FASE 1.2 - Filtrar produtos importáveis
python3 scripts/filter_importable_products.py

# FASE 2 - Iniciar upgrade (se Opção A)
# OU
# FASE 3 - Skip para GA4 (se Opção B hardening)
```

---

**Relatórios Gerados:**
- `relatorios/product_images_analysis.json` (análise completa)
- `relatorios/product_images_summary.md` (resumo executivo)
- `relatorios/ESTADO_FOTOS_E_PLANO_FINAL.md` (este documento)

**Responsável:** Claude Code (Sonnet 4.5)
**Cliente:** Tiago Andrade - Chapéus Lisboetas
**Black Friday:** 24 Nov 2025 (11 dias)
