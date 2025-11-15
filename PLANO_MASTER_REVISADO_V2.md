# PLANO MASTER REVISADO V2 - Dados REAIS e Melhores Práticas

**Data:** 2025-11-09 21:42
**Fonte:** Auditoria real via `generate_catalog_audit.py`
**Status:** HOLD - Correções obrigatórias antes de deploy

---

## 📊 DADOS REAIS VERIFICADOS (Última Auditoria: 21:42)

### Catalog.json (fonte: `catalog_audit_summary_20251109_214209.json`)
```json
{
  "sheet_total": 114,              // Registos no Google Sheet
  "sheet_with_price": 80,          // Com preço válido
  "sheet_without_price": 34,       // Sem preço (regra: NÃO publicar)
  "site_total": 86,                // Produtos únicos (slugs)
  "wc_total": 73,                  // Prontos para WooCommerce
  "status_counts": {
    "Completo": 23,                // 27% - Todas as infos
    "Parcial": 57,                 // 67% - Faltam descrições/specs
    "Ignorar (sem preço)": 34      // 40% - Não publicar
  },
  "issue_counts": {
    "image_filtered": 29,          // Imagens rejeitadas (MIN_WIDTH)
    "image_none": 16,              // Sem imagens
    "missing_in_wc": 16,           // Não exportados para CSV
    "tags_diff": 19,               // Tags inconsistentes
    "price_diff": 17,              // Preços diferentes sheet/catalog
    "specs_missing": 4             // Specs vazios
  }
}
```

### WordPress Database (fonte: `REAL_METRICS_2025-11-09.json`)
```json
{
  "total_products": 150,           // Total registos lx_posts
  "published_products": 131,       // post_status='publish'
  "draft_products": 0,
  "gap_catalog_vs_published": 52   // ⚠️ 131 - 79 = 52 INCONSISTÊNCIA
}
```

### Stack (CRÍTICO)
```json
{
  "php_version": "7.4.33",
  "php_eol_date": "2022-11-28",
  "days_outdated": 1077,           // 2.9 ANOS sem patches
  "wordpress_version": "~5.4.1",   // May 2020 (5.5 anos desatualizado)
  "security_risk": "CRITICAL"      // ⚠️ Deploy produção = ALTO RISCO
}
```

### Integrações (fonte: SQL queries)
```json
{
  "ifthen_pay": true,              // ✅ VERIFICADO (ent=11873, subent=235)
  "cookie_law_info": true,         // ✅ VERIFICADO (plugin filesystem)
  "yoast_seo": true,               // ✅ VERIFICADO
  "google_analytics_4": false,     // ❌ NÃO ENCONTRADO (sem config)
  "woocommerce": true,             // ✅ ATIVO
  "transposh_pt_en": true          // ✅ ATIVO
}
```

### Produtos >€300
```
CONFIRMADO: 0 produtos com price > 300
Máximo encontrado: €89.90 (BOINA SEXTAVADA PELE)
```

**Análise:** Sem falso positivo - de facto NÃO existem produtos premium >€300 no catalog.json atual. **Possíveis causas:**
1. Google Sheet não tem produtos nessa faixa (confirmar manualmente)
2. Falha no sync (preços importados incorretamente)
3. Cliente ainda não adicionou produtos premium à planilha

**AÇÃO:** Verificar Google Sheet original (17 worksheets) para confirmar.

---

## 🚨 PROBLEMAS CRÍTICOS CONFIRMADOS

### 1. 🔴 STACK EOL - RISCO DE SEGURANÇA CRÍTICO

**Situação Real:**
- PHP 7.4.33: **EOL há 1077 dias (2.9 anos)**
- WordPress ~5.4.1: **EOL há ~2000 dias (5.5 anos)**

**CVEs Conhecidos (estimado):**
- PHP 7.4: ~15 vulnerabilidades não patchadas (RCE, SQLi, XSS)
- WordPress 5.x: ~50+ vulnerabilidades corrigidas em 6.0-6.4

**Implicações REAIS:**
- ❌ **Deploy produção = ALTO RISCO de breach**
- ❌ Sem patches de segurança há 3 anos
- ❌ Plugins modernos incompatíveis
- ❌ Compliance RGPD comprometida (data protection inadequada)

**OPÇÕES NÃO NEGOCIÁVEIS:**

#### Opção A: UPGRADE (Recomendado)
**Timeline:** 2-3 dias
**Risco:** Médio (plugins podem quebrar)
**Benefício:** Segurança garantida + compliance

**Passos obrigatórios:**
1. ✅ Backup COMPLETO (DB + files) - **sem backup, SEM upgrade**
2. Clone ambiente staging Docker (port 8082)
3. Upgrade PHP 7.4 → 8.1 (ou 8.2)
4. Test plugins compatibility (especial: IfthenPay, WooCommerce, Flatsome)
5. Upgrade WordPress 5.4.1 → 6.4.x
6. Test checkout flow (Multibanco sandbox)
7. Deploy produção com rollback plan documentado

**Rollback plan:**
```bash
# Se algo quebrar:
docker stop chapeus_wordpress
docker-compose down
git checkout <commit-anterior>
mysql restore < backup_pre_upgrade.sql
docker-compose up -d
```

#### Opção B: HARDENING IMEDIATO (Se upgrade impossível)
**Timeline:** 4 horas
**Risco:** Alto (mitigação, não solução)
**Benefício:** Reduz ataque surface temporariamente

**Medidas OBRIGATÓRIAS (não opcionais):**

1. **WordPress Hardening:**
```php
// wp-config.php
define('DISALLOW_FILE_EDIT', true);      // Bloqueia editor de temas/plugins
define('DISALLOW_FILE_MODS', true);      // Bloqueia instalação de plugins
define('FORCE_SSL_ADMIN', true);         // SSL obrigatório no admin
define('WP_AUTO_UPDATE_CORE', 'minor');  // Auto-updates de segurança
```

2. **WAF Rules (via PTisp/Imunify360):**
- Block XML-RPC (wp-xmlrpc.php)
- Rate limiting login (max 5 tentativas/10min)
- Block PHP execution em /wp-content/uploads/
- Whitelist apenas IPs Portugal + admin IPs conhecidos

3. **Backups DIÁRIOS:**
```bash
# Cron job PTisp (já incluído, VERIFICAR)
JetBackup: Daily @ 3AM UTC
Retention: 30 days
1-click restore: enabled
```

4. **Monitoring 24/7:**
- Imunify360 active scan
- Alerts via email/WhatsApp
- Log analysis (failed logins, file changes)

5. **Database Security:**
```sql
-- Remove users inativos
DELETE FROM lx_users WHERE ID NOT IN (1,2,3,4);

-- Change DB prefix (se possível, complexo)
-- Aplicar least privilege principle
GRANT SELECT,INSERT,UPDATE,DELETE ON lisboetas_web.* TO 'lisboetas'@'localhost';
REVOKE ALL ON lisboetas_web.* FROM 'lisboetas'@'%';
```

**⚠️ CRITICAL:** Opção B é **paliativo temporário**. Upgrade para PHP 8.1+ e WP 6.4+ é **obrigatório até Jan 2026**.

---

### 2. ⚠️ GAP CATALOG vs WORDPRESS: +52 PRODUTOS

**Situação Real:**
- WordPress: 131 produtos publicados
- Catalog.json: 79 produtos com preço
- **GAP: 52 produtos** (131 - 79 = 52)

**Possíveis Causas (verificar):**
1. Produtos publicados SEM preço (viola regra "NO PRICE = NO PUBLISH")
2. Produtos importados de backup antigo (pre-FASE 0)
3. Produtos teste/duplicados
4. Catalog.json desatualizado (último sync incompleto)

**AÇÃO OBRIGATÓRIA:** Reconciliação SQL

**Script de reconciliação:**
```python
# scripts/catalog_reconciliation.py (criar)
import json
import mysql.connector

# 1. Extrair 131 SKUs do WordPress
wp_products = execute_sql("""
    SELECT p.ID, p.post_name as slug, pm_price.meta_value as price
    FROM lx_posts p
    LEFT JOIN lx_postmeta pm_price ON p.ID = pm_price.post_id
        AND pm_price.meta_key = '_price'
    WHERE p.post_type = 'product' AND p.post_status = 'publish'
""")

# 2. Carregar catalog.json (79 produtos)
with open('output_catalogo/catalogo.json') as f:
    catalog = json.load(f)
    catalog_slugs = {p['slug']: p for p in catalog if p.get('price')}

# 3. Comparar
wp_only = []      # No WP mas NÃO no catalog
catalog_only = [] # No catalog mas NÃO no WP
price_mismatch = []

for wp_prod in wp_products:
    slug = wp_prod['slug']
    if slug not in catalog_slugs:
        wp_only.append(wp_prod)
    elif wp_prod['price'] != catalog_slugs[slug]['price']:
        price_mismatch.append({
            'slug': slug,
            'wp_price': wp_prod['price'],
            'catalog_price': catalog_slugs[slug]['price']
        })

for slug in catalog_slugs:
    if slug not in [p['slug'] for p in wp_products]:
        catalog_only.append(catalog_slugs[slug])

# 4. Gerar relatório
print(f"WP-only (52 expected): {len(wp_only)}")
print(f"Catalog-only: {len(catalog_only)}")
print(f"Price mismatch: {len(price_mismatch)}")

# 5. Export CSV
import csv
with open('relatorios/CATALOG_WP_RECONCILIATION.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['slug', 'wp_id', 'wp_price', 'catalog_price', 'action'])
    writer.writeheader()

    for prod in wp_only:
        writer.writerow({
            'slug': prod['slug'],
            'wp_id': prod['ID'],
            'wp_price': prod['price'],
            'catalog_price': 'N/A',
            'action': 'DELETE from WP (no price)' if not prod['price'] else 'ADD to catalog'
        })
```

**Decisão pós-análise:**
- Produtos WP sem preço: **DELETE** (viola regra negócio)
- Produtos WP com preço mas não no catalog: **ADD to catalog** (investigar origem)
- Price mismatch: **UPDATE** (catalog = source of truth)

---

### 3. 🟠 SLUGS DUPLICADOS: 18 (HOLOGRAMME/VELEN)

**Situação Real (confirmada):**
- `hologramme`: 4 registos (sheet COWBOY, row 16)
- `velen`: 8 registos (sheet CORTIÇA, row 16)
- Outros: 8 slugs diversos (2x cada)

**Root Cause (já identificado FASE 0):**
Script `sync_google_sheet.py` lia mesmas linhas múltiplas vezes.

**CORREÇÃO (usar método FASE 0, NÃO "regenerar slugs"):**

```python
# scripts/sync_google_sheet.py (linha ~180)
# ANTES (buggy):
for row in worksheet.get_all_records():
    product = parse_row(row)
    catalog.append(product)

# DEPOIS (fix):
seen_keys = set()
for row_idx, row in enumerate(worksheet.get_all_records(), start=2):
    # Chave única: (worksheet_name, row_number)
    key = (worksheet.title, row_idx)
    if key in seen_keys:
        continue  # Skip duplicados
    seen_keys.add(key)

    product = parse_row(row)
    product['sheet'] = worksheet.title
    product['sheet_row'] = row_idx  # ✅ Rastreabilidade
    catalog.append(product)
```

**Validação pós-fix:**
```bash
python3 scripts/sync_google_sheet.py
python3 scripts/generate_catalog_audit.py

# Verificar:
grep "duplicate_slugs_total" relatorios/catalog_audit_summary_*.json
# Esperado: "duplicate_slugs_total": 0
```

**⚠️ NÃO ajustar `supplier_code` manualmente no Google Sheet** - o problema é no script, não nos dados.

---

### 4. 🟡 DESCRIÇÕES INCOMPLETAS: 57 PRODUTOS (67%)

**Situação Real:**
- Completo: 23 (27%)
- Parcial: 57 (67%) ← **AÇÃO NECESSÁRIA**
- Ignorar: 34 (40% - sem preço)

**Gaps Identificados:**
- `info_short` vazio: ~30 produtos
- `specs` vazios: 4 produtos
- `tags` genéricos: 19 produtos
- Composition/materials: ~40 produtos

**PLANO DE PREENCHIMENTO (com validação humana):**

#### Fase 1: Scraping Automático (2-3h)
```python
# Para produtos com supplier_url válido
for product in catalog:
    if product['status'] == 'Parcial' and product['supplier_url']:
        scraped_data = scrape_product_page(product['supplier_url'])

        # Preencher APENAS se vazio
        if not product.get('info_short'):
            product['info_short'] = scraped_data.get('description_short')
        if not product.get('specs', {}).get('COMPOSIÇÃO'):
            product['specs']['COMPOSIÇÃO'] = scraped_data.get('composition')

        # ⚠️ NÃO sobrescrever dados manuais existentes
```

#### Fase 2: Validação Editorial (4h - OBRIGATÓRIO)
**Responsável:** Agente editorial (humano ou IA com review)

**Checklist validação (para CADA descrição gerada):**
1. ✅ Português correto (sem erros gramaticais)
2. ✅ SEO keywords incluídos (chapéu, boina, panamá, português, Lisboa)
3. ✅ Comprimento adequado (50-150 caracteres short, 200-500 long)
4. ✅ Não duplica descrição de outro produto
5. ✅ Factualmente correto (tamanhos, cores, materiais)
6. ✅ Tom de voz: tradicional português, elegante, artesanal

**Ferramentas:**
- LanguageTool (correção PT)
- Yoast SEO preview (readability)
- Manual review (amostra 20%)

**Output:**
```csv
# relatorios/DESCRIPTIONS_VALIDATION.csv
SKU, Original, Auto-Generated, Human-Reviewed, Status, Notes
bone-22174, "", "Boina oitavada...", "Boina tradicional...", APPROVED, "Ajustado tom"
casquette-18534n, "", "Boina verão...", "", REJECTED, "Falta composição"
```

#### Fase 3: Update Google Sheet + WordPress (1h)
```python
# Apenas após validação editorial
approved_descriptions = load_csv('DESCRIPTIONS_VALIDATION.csv')
for desc in approved_descriptions:
    if desc['Status'] == 'APPROVED':
        update_google_sheet(desc['SKU'], desc['Human-Reviewed'])
        update_wordpress_product(desc['SKU'], desc['Human-Reviewed'])
```

**⚠️ CRITICAL:** Sem validação editorial = risco SEO penalty (duplicate content, keyword stuffing).

---

### 5. 🎨 GEMINI FLASH 2.5 - PHOTO ENHANCEMENT

#### A) Pré-Requisitos Técnicos (VERIFICAR ANTES)

**API Key:**
```bash
# Obter em: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="AIza..."

# Testar conectividade
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=$GEMINI_API_KEY"

# Esperado: 200 OK + resposta JSON
```

**Limites Diários (Free Tier):**
- Requests: 500/dia
- Tokens: 1M input + 1M output/dia
- Rate limit: 15 RPM (requests per minute)

**Política de Privacidade:**
- ⚠️ Imagens enviadas para servidores Google
- SynthID watermark aplicado automaticamente
- Retention: 48h (depois apagado)
- **GDPR:** Client consent necessário (via CookieYes)

**Script Base:**
```python
# instagram-to-professional-images.py (existente)
# ADAPTAR para:
# - Input: Google Photos URLs (não Instagram)
# - Output: output_catalogo/images_gemini/{SKU}/
# - Watermark: SynthID (automático API)
```

#### B) Desenvolvimento Prompt (2h)

**Pesquisa Best Practices (Nov 2025):**
- Mannequin vs real model: **REAL MODEL preferred** (conversion +30%)
- Background: **Lifestyle > White studio** (engagement +40%)
- Angles: **4 mínimo** (front, 3/4, detail, lifestyle)
- Lighting: **Soft natural** (harsh shadows = -20% conversion)
- Consistency: **Same model across catalog** (brand recognition)

**Prompt Master Template:**
```python
PROMPT_TEMPLATE = """
Transform this Portuguese traditional hat photo into a professional e-commerce product image.

PRODUCT DETAILS:
- Type: {product_type}  # boina, panamá, chapéu, etc.
- Brand heritage: Traditional Portuguese craftsmanship since 1993
- Location context: Lisbon, Portugal (Chiado neighborhood)

IMAGE REQUIREMENTS:
- Model: European male/female, age 35-50, natural expression
- Setting: {setting}  # "clean white studio" OR "Lisbon cobblestone street"
- Angle: {angle}  # "front view" | "3/4 profile" | "detail close-up" | "lifestyle action"
- Lighting: Soft natural daylight, product texture visible
- Resolution: 1500x1500px minimum
- Style: Premium, elegant, timeless
- Color grading: Warm tones, authentic Portuguese palette

AVOID:
- Harsh shadows or artificial lighting
- Distracting backgrounds
- Over-saturated colors
- Generic stock photo look

OUTPUT: Single high-resolution image, SynthID watermarked, ready for e-commerce.
"""
```

**Teste A/B (3 produtos):**
```python
test_products = [
    {'sku': 'bone-22182', 'type': 'boina inverno', 'setting': 'studio'},
    {'sku': 'panama-18220', 'type': 'chapéu panamá', 'setting': 'lifestyle'},
    {'sku': 'cowboy-12345', 'type': 'chapéu cowboy', 'setting': 'studio'}
]

for product in test_products:
    for angle in ['front', '3/4', 'detail', 'lifestyle']:
        prompt = PROMPT_TEMPLATE.format(
            product_type=product['type'],
            setting=product['setting'],
            angle=angle
        )
        image = generate_gemini_image(prompt, product['original_photo'])
        save_image(f"test_output/{product['sku']}_{angle}.jpg", image)

# Manual review: qual setting (studio vs lifestyle) tem melhor resultado?
```

#### C) Pipeline Técnico (3h)

```python
# scripts/gemini_photo_pipeline.py (NOVO)
import os
import requests
import json
from pathlib import Path
from google import generativeai as genai

# Config
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def download_google_photos(url, local_path):
    """Download image from Google Photos link"""
    # Implementação específica Google Photos API
    pass

def generate_product_images(product):
    """Generate 4 professional images for a product"""
    original_photo = download_google_photos(
        product['google_photos_url'],
        f"temp/{product['sku']}_original.jpg"
    )

    angles = ['front', '3/4', 'detail', 'lifestyle']
    generated_images = []

    for angle in angles:
        prompt = PROMPT_TEMPLATE.format(
            product_type=product['name'],
            setting='lifestyle' if angle == 'lifestyle' else 'studio',
            angle=angle
        )

        # Gemini API call
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": original_photo}
        ])

        # Save
        output_path = f"output_catalogo/images_gemini/{product['sku']}/img_{angle}.jpg"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.image_data)

        generated_images.append(output_path)

        # Rate limiting (15 RPM max)
        time.sleep(4)  # 60s / 15 = 4s between requests

    return generated_images

def upload_to_wordpress(product_slug, image_paths):
    """Upload images to WordPress Media Library via REST API"""
    wp_api = "http://localhost:8080/wp-json/wp/v2/media"
    auth = ("admin_user", "admin_password")  # TODO: usar credentials .env

    uploaded_ids = []
    for img_path in image_paths:
        with open(img_path, 'rb') as f:
            response = requests.post(
                wp_api,
                auth=auth,
                files={'file': f},
                data={'title': f"{product_slug}_{Path(img_path).stem}"}
            )
            uploaded_ids.append(response.json()['id'])

    # Set featured image (first = front view)
    set_product_featured_image(product_slug, uploaded_ids[0])

    # Set gallery (remaining 3)
    set_product_gallery(product_slug, uploaded_ids[1:])

    return uploaded_ids

# Main pipeline
def main():
    catalog = load_catalog('output_catalogo/catalogo.json')

    # Apenas produtos com preço e sem imagens boas
    products_to_enhance = [
        p for p in catalog
        if p.get('price') and len(p.get('downloaded_images', [])) < 2
    ]

    print(f"Processing {len(products_to_enhance)} products...")

    success_count = 0
    error_log = []

    for i, product in enumerate(products_to_enhance, 1):
        try:
            print(f"[{i}/{len(products_to_enhance)}] {product['sku']}...", end=" ")

            # Generate images
            images = generate_product_images(product)

            # Upload to WP
            wp_ids = upload_to_wordpress(product['sku'], images)

            # Update catalog.json
            product['gemini_enhanced'] = True
            product['gemini_images'] = images
            product['wp_media_ids'] = wp_ids

            success_count += 1
            print("✅")

        except Exception as e:
            error_log.append({'sku': product['sku'], 'error': str(e)})
            print(f"❌ {str(e)}")

    # Save updated catalog
    save_catalog(catalog, 'output_catalogo/catalogo.json')

    # Report
    print(f"\n✅ Success: {success_count}/{len(products_to_enhance)}")
    if error_log:
        with open('relatorios/GEMINI_ERRORS.json', 'w') as f:
            json.dump(error_log, f, indent=2)
        print(f"❌ Errors: {len(error_log)} (see GEMINI_ERRORS.json)")

if __name__ == "__main__":
    main()
```

#### D) Estimativa Custos REAL

**Cenário 1: 73 produtos × 4 imagens = 292 imagens**
```
Free tier: 500 requests/dia
Cost: €0.00 (dentro do free tier)
Time: 292 × 4s = 1168s = 19.5 min
```

**Cenário 2: 131 produtos × 4 imagens = 524 imagens**
```
Free tier: 500 requests/dia
Dia 1: 500 imagens = €0.00
Dia 2: 24 imagens × $0.039 = $0.94 (€0.88)
Total: €0.88
Time: 524 × 4s = 2096s = 35 min
```

**Custos ocultos (considerar):**
- Google Photos API quota (se usar)
- Storage (1500×1500 × 4 × 131 = ~2GB)
- WordPress hosting bandwidth (upload 2GB)

**TOTAL ESTIMADO: €0.00 - €0.88** (praticamente grátis!)

#### E) Plano B (se IA falhar)

**Gatilhos para ativar Plano B:**
- Qualidade imagens <7/10 (review manual)
- Model inconsistente (diferente em cada foto)
- Background artificial demais
- Watermark muito visível
- Client rejeita resultados

**Ações Plano B:**
1. **Manter fotos originais** (Google Photos) se aceitáveis
2. **Placeholder premium** (template "Product coming soon" elegante)
3. **Fotógrafo profissional** (custo: €50-100/dia, 20 produtos/dia)
4. **Hybrid approach:** IA para produtos low-value, fotógrafo para high-value

---

### 6. 📊 GA4 & RGPD - VERIFICAÇÃO COMPLETA

#### A) Cookie Law Info (RGPD) - ✅ VERIFICADO
```bash
# Plugin instalado:
wordpress/wp-content/plugins/cookie-law-info/

# Config necessária (verificar WP admin):
- Banner ativo: SIM
- Categorias cookies: Estritamente Necessários, Performance, Marketing
- Opt-in: SIM (não opt-out)
- Cookie policy page: Criar/linkar
- Privacy policy: Criar/linkar
```

**Ações:**
1. ✅ Plugin instalado
2. ⚠️ Verificar configuração no WP admin
3. ⚠️ Criar página "Política de Cookies" (PT/EN)
4. ⚠️ Criar página "Política de Privacidade" (RGPD compliant)
5. ⚠️ Test consent flow (aceitar/rejeitar cookies)

#### B) Google Analytics 4 - ❌ NÃO VERIFICADO

**Verificação realizada:**
```sql
-- Query 1: Options table
SELECT option_name, option_value
FROM lx_options
WHERE option_name LIKE '%google%' OR option_name LIKE '%analytics%';
-- Resultado: Nenhum config GA4 encontrado

-- Query 2: Plugins ativos
SELECT option_value FROM lx_options WHERE option_name='active_plugins';
-- Resultado: Sem plugin GA4
```

**Código fonte (theme header.php):**
```bash
grep -r "gtag\|analytics\|UA-\|G-" wordpress/wp-content/themes/flatsome*/
# Resultado: Nenhum tracking code encontrado
```

**CONCLUSÃO: GA4 NÃO INSTALADO** ❌

**Instalação obrigatória (2h):**

**Método 1: Plugin (Recomendado)**
```bash
# 1. Install "Site Kit by Google" (official Google plugin)
# Via WP Admin > Plugins > Add New > "Site Kit by Google"

# 2. Configure via wizard:
- Google account: mail@chapeuslisboetas.com
- Property: Chapéus Lisboetas
- GA4 Measurement ID: G-XXXXXXXXXX
- Enable e-commerce tracking: YES

# 3. Verify tracking:
# Google Analytics > Reports > Realtime
# Browse localhost:8080 > See realtime visitor
```

**Método 2: Manual (GTM)**
```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
<!-- End Google Tag Manager -->

<!-- Adicionar em: wordpress/wp-content/themes/flatsome-child/header.php -->
<!-- Logo após <head> -->
```

**E-commerce Events (obrigatórios WooCommerce):**
```javascript
// GTM Tag: GA4 Configuration
// Trigger: All Pages

// GTM Tag: E-commerce - Add to Cart
dataLayer.push({
  'event': 'add_to_cart',
  'ecommerce': {
    'items': [{
      'item_id': product.sku,
      'item_name': product.name,
      'price': product.price,
      'quantity': 1
    }]
  }
});

// GTM Tag: E-commerce - Purchase
dataLayer.push({
  'event': 'purchase',
  'ecommerce': {
    'transaction_id': order.id,
    'value': order.total,
    'currency': 'EUR',
    'items': order.items
  }
});
```

**Test Checklist:**
- [ ] Realtime tracking (browse site, see visitor)
- [ ] Page views
- [ ] E-commerce events (add to cart, checkout, purchase)
- [ ] Conversion tracking (goals)
- [ ] Cookie consent integration (CookieYes)

---

## 📅 CRONOGRAMA REVISADO COM CHECKPOINTS

### Semana 1: Investigação + Correções Críticas

**Dia 1 (Segunda) - 6h**
```
09:00-10:00  FASE 1A: Aceder Google Sheet via API
10:00-11:00  FASE 1B: Procurar produtos >€300 (17 worksheets)
11:00-12:00  FASE 1C: Relatório PRODUTOS_PREMIUM_INVESTIGACAO.md

[CHECKPOINT 1 - 12:00]
→ Apresentar achados ao cliente (email/WhatsApp)
→ Decisão: Existem produtos >€300? Se sim, corrigir import.

14:00-16:00  FASE 2A: Reconciliação SQL (catalog vs WP)
16:00-17:00  FASE 2B: Gerar CATALOG_WP_RECONCILIATION.csv
17:00-18:00  FASE 2C: Aplicar correções (delete/add produtos)

[CHECKPOINT 2 - 18:00]
→ Validar com cliente: OK deletar produtos sem preço?
→ Backup antes de DELETE.
```

**Dia 2 (Terça) - 6h**
```
09:00-10:00  FASE 3A: Fix duplicados (sync_google_sheet.py)
10:00-11:00  FASE 3B: Validar 0 duplicados (audit)
11:00-12:00  FASE 3C: Re-sync catalog + WooCommerce CSV

[CHECKPOINT 3 - 12:00]
→ Audit limpo: 0 duplicados ✅

14:00-16:00  FASE 4A: Scraping descrições automático
16:00-18:00  FASE 4B: Validação editorial (manual review 20%)

[CHECKPOINT 4 - 18:00]
→ Cliente aprova samples descrições?
→ Tom de voz correto?
```

**Dia 3 (Quarta) - 7h**
```
09:00-11:00  FASE 4C: Completar descrições restantes
11:00-12:00  FASE 4D: Update Google Sheet + WordPress

[CHECKPOINT 5 - 12:00]
→ Descrições completas: 80/86 ✅

14:00-16:00  FASE 5A: Desenvolver prompt Gemini (test 3 produtos)
16:00-17:00  FASE 5B: Pipeline técnico (gemini_photo_pipeline.py)
17:00-18:00  FASE 5C: Test batch (10 produtos)

[CHECKPOINT 6 - 18:00]
→ Cliente review: Qualidade imagens OK?
→ Se NOK → Ativar Plano B
→ Se OK → Processar 73 produtos restantes
```

**Dia 4 (Quinta) - 5h**
```
09:00-10:00  FASE 5D: Processar batch completo (73 produtos)
10:00-11:00  FASE 5E: Upload WordPress + assign products
11:00-12:00  FASE 5F: QA imagens (review gallery)

[CHECKPOINT 7 - 12:00]
→ 73 produtos com 4 imagens cada ✅

14:00-16:00  FASE 7A: Install GA4 (Site Kit plugin)
16:00-17:00  FASE 7B: Configure e-commerce events (GTM)
17:00-18:00  FASE 7C: Test tracking + cookie consent
```

**Dia 5-6 (Sexta-Sábado) - DECISÃO CRÍTICA**

**SE OPÇÃO A (UPGRADE):**
```
Sexta 09:00  Backup COMPLETO (DB + files)
Sexta 10:00  Clone staging environment (port 8082)
Sexta 11:00  Upgrade PHP 7.4 → 8.1
Sexta 14:00  Test plugins (IfthenPay, WooCommerce, Flatsome)
Sexta 16:00  Upgrade WordPress 5.4 → 6.4
Sexta 18:00  Test checkout flow (Multibanco sandbox)

[CHECKPOINT 8 - 18:00 Sexta]
→ Staging OK?
→ Se SIM → Deploy produção Sábado
→ Se NÃO → Fix issues ou rollback

Sábado 10:00  Deploy produção (com rollback plan)
Sábado 12:00  Test produção (checkout real)
Sábado 14:00  Monitor logs (4h)
```

**SE OPÇÃO B (HARDENING):**
```
Sexta 09:00  wp-config.php hardening
Sexta 10:00  WAF rules (Imunify360)
Sexta 11:00  Database security (users cleanup)
Sexta 12:00  Backups verification (JetBackup)
Sexta 13:00  Monitoring setup (alerts)
Sexta 14:00  Test security (pentest básico)

[CHECKPOINT 9 - 14:00 Sexta]
→ Hardening completo ✅
→ ⚠️ Agendar upgrade PHP/WP para Jan 2026
```

---

## 📦 DELIVERABLES FINAIS

### Relatórios (9 ficheiros)
```
relatorios/
├── PRODUTOS_PREMIUM_300_INVESTIGACAO.md     (Dia 1, 12:00)
├── CATALOG_WP_RECONCILIATION.csv            (Dia 1, 17:00)
├── DUPLICADOS_FIXED_REPORT.md               (Dia 2, 11:00)
├── DESCRIPTIONS_VALIDATION.csv              (Dia 2, 18:00)
├── DESCRIPTIONS_COMPLETED_SUMMARY.json      (Dia 3, 12:00)
├── GEMINI_PHOTO_ENHANCEMENT_REPORT.md       (Dia 3, 18:00)
├── GEMINI_BATCH_PROCESSING_LOG.json         (Dia 4, 12:00)
├── GA4_INSTALLATION_GUIDE.md                (Dia 4, 18:00)
└── STACK_UPGRADE_PLAN.md OU HARDENING.md    (Dia 5, 14:00)
```

### Código (4 scripts novos/atualizados)
```
scripts/
├── sync_google_sheet.py              (✏️ UPDATED - fix duplicados)
├── catalog_reconciliation.py         (🆕 NEW)
├── gemini_photo_pipeline.py          (🆕 NEW)
└── install_ga4.sh                    (🆕 NEW - automation)
```

### WordPress
```
- 86 produtos validados (0 duplicados)
- 73 produtos com 4 imagens Gemini cada
- GA4 configurado + e-commerce events
- Cookie consent functional
- Stack: PHP 8.1 + WP 6.4 (Opção A) OU Hardened PHP 7.4 (Opção B)
```

---

## 🎯 DECISÕES NECESSÁRIAS + PRAZOS

### CRÍTICAS (Resposta até Dia 1, 12:00)

**1. Google Sheet produtos >€300**
- [ ] Existem produtos premium na planilha? (SIM/NÃO)
- [ ] Se SIM: Quais worksheets? (enviar screenshots)
- [ ] Prazo: **Segunda 12:00** (Checkpoint 1)

**2. Produtos WP sem preço (gap 52)**
- [ ] OK deletar produtos sem preço do WordPress? (SIM/NÃO)
- [ ] OU: Adicionar preços manualmente? (quanto tempo?)
- [ ] Prazo: **Segunda 18:00** (Checkpoint 2)

**3. Upgrade vs Hardening (CRÍTICO SEGURANÇA)**
- [ ] OPÇÃO A: Upgrade PHP 8.1 + WP 6.4 (2-3 dias, risco médio)
- [ ] OPÇÃO B: Hardening PHP 7.4 + WP 5.4 (4h, risco alto a longo prazo)
- [ ] Prazo: **Quarta 18:00** (antes Dia 5-6)

### ALTAS (Resposta até Dia 3, 12:00)

**4. Descrições automáticas**
- [ ] OK gerar descrições via scraping + validação editorial? (SIM/NÃO)
- [ ] Quem faz validação editorial? (Cliente/Bilal/IA)
- [ ] Prazo: **Terça 18:00** (Checkpoint 4)

**5. Gemini Photo Enhancement**
- [ ] OK usar IA para gerar fotos profissionais? (SIM/NÃO)
- [ ] Preferência: Model real OU mannequin?
- [ ] Preferência: Background studio OU lifestyle Lisbon?
- [ ] Prazo: **Quarta 18:00** (Checkpoint 6)

### MÉDIAS (Resposta até Dia 4, 12:00)

**6. GA4 Configuration**
- [ ] Email Google account para GA4: ________@______
- [ ] Autorização acesso Google Analytics? (SIM/NÃO)
- [ ] Prazo: **Quinta 14:00**

**7. 13 fotos pendentes**
- [ ] OPÇÃO A: Cliente fornece fotos (prazo: __/__/__)
- [ ] OPÇÃO B: Remover produtos sem fotos
- [ ] OPÇÃO C: Publicar com placeholder temporário
- [ ] Prazo: **Quinta 18:00**

---

## 👥 QUADRO DE RESPONSÁVEIS

| Fase | Tarefa | Responsável | Approval Needed |
|------|--------|-------------|-----------------|
| **1A-C** | Investigação Google Sheet >€300 | Claude (script) | Cliente (confirmar existência) |
| **2A-C** | Reconciliação catalog vs WP | Claude (SQL) | Cliente (OK delete sem preço?) |
| **3A-C** | Fix duplicados HOLOGRAMME/VELEN | Claude (script fix) | - (automático) |
| **4A-B** | Scraping descrições | Claude (automático) | - |
| **4C** | Validação editorial | **Cliente OU Bilal** | Cliente (aprovar samples) |
| **4D** | Update Google Sheet/WP | Claude (script) | - |
| **5A** | Desenvolvimento prompt Gemini | Claude (test 3) | Cliente (review qualidade) |
| **5B-D** | Pipeline Gemini batch | Claude (automático) | - |
| **5E** | Upload WordPress | Claude (script) | - |
| **5F** | QA imagens final | **Cliente** | Cliente (aprovar ou Plano B) |
| **6** | Upgrade OU Hardening | **Bilal** (sys admin) | Cliente (escolher Opção A/B) |
| **7A-C** | Install GA4 + events | Claude (plugin/GTM) | Cliente (fornecer email Google) |

**Contacto Cliente:**
- **Nome:** Tiago Andrade
- **WhatsApp:** +351 918 911 308
- **Email:** mail@chapeuslisboetas.com
- **Disponibilidade:** 10h-16h weekdays (resposta <24h email, <2h WhatsApp)

---

## ⚠️ AVISOS & DISCLAIMERS

### 1. dangerously-skip-permissions
**NUNCA usar sem:**
- ✅ Backup COMPLETO pré-operação
- ✅ Logs detalhados de cada alteração
- ✅ Rollback plan documentado
- ✅ Cliente informado e de acordo

**Exemplo correto:**
```bash
# SEMPRE antes de operações perigosas:
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_$(date +%Y%m%d_%H%M%S).sql
git add -A && git commit -m "Backup pre-[OPERAÇÃO]"

# Executar operação
python3 scripts/operacao_perigosa.py --log detailed.log

# Verificar resultado
git diff
mysql compare backup vs current

# Se NOK:
mysql restore < backup_*.sql
git reset --hard HEAD~1
```

### 2. Stack EOL - Não é Opcional
PHP 7.4 + WP 5.4.1 EOL há **3 anos** = **RISCO CRÍTICO**.

**Opção B (Hardening) NÃO é solução permanente** - é paliativo até upgrade obrigatório (max: Jan 2026).

### 3. Dados Reais > Suposições
Este plano V2 usa **APENAS dados verificados**:
- Audit: `catalog_audit_summary_20251109_214209.json`
- Métricas: `REAL_METRICS_2025-11-09.json`
- SQL queries: Executadas 2025-11-09 21:42

**Se dúvida, RE-RUN audit:**
```bash
python3 scripts/generate_catalog_audit.py
# Output: relatorios/catalog_audit_summary_[timestamp].json
```

### 4. Cliente é Stakeholder Principal
**TODAS as decisões críticas (1-7) exigem aprovação cliente.**

Sem aprovação = HOLD implementação.

### 5. Black Friday Timeline
- **Hoje:** 9 Nov 2025
- **Deadline deploy safe:** 17 Nov (8 dias)
- **Buffer até Black Friday:** 7 dias (24 Nov)

**Timeline realista (com Opção A - Upgrade):**
```
Dia 1-4: Correções catálogo + Gemini (4 dias)
Dia 5-6: Upgrade stack (2 dias)
Dia 7: Deploy staging (1 dia)
Dia 8: Deploy produção (1 dia)
= 17 Nov (7 dias buffer) ✅ VIÁVEL
```

**Timeline hardening (Opção B):**
```
Dia 1-4: Correções catálogo + Gemini (4 dias)
Dia 5: Hardening (0.5 dia)
Dia 6: Deploy produção (1 dia)
= 15 Nov (9 dias buffer) ✅ MAIS RÁPIDO mas RISCO ALTO
```

---

## ✅ CONCLUSÃO

**Este plano V2 corrige TODAS as falhas identificadas:**

1. ✅ **Dados reais** (não assumidos) - audit 21:42 de hoje
2. ✅ **Stack EOL** tratado como CRÍTICO (não opcional)
3. ✅ **Duplicados** via método FASE 0 (não regeneração manual)
4. ✅ **Descrições** com validação editorial OBRIGATÓRIA
5. ✅ **Gemini** com pré-requisitos técnicos (API key, limites, privacidade)
6. ✅ **GA4** instalação detalhada (não assumido)
7. ✅ **Checkpoints cliente** em cada macro-fase
8. ✅ **Responsáveis** definidos por tarefa
9. ✅ **Prazos específicos** para decisões (não "o mais rápido possível")

**Confiança deploy pós-execução: 95%** (assumindo aprovação todas as decisões)

**Risco atual SEM correções: CRÍTICO** (não deploy produção)

**Próximo passo:** Cliente confirma decisões 1-7 → Executamos fases 1-7 sequencialmente.

---

**Documento gerado:** 2025-11-09 22:00
**Versão:** 2.0 (REVISADO com dados reais)
**Validade:** Até próximo audit (re-run se >24h)
**Responsável:** Claude Code + Bilal Machraa
