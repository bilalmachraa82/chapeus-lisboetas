# 🔴 MASTER BUG LIST - Chapéus Lisboetas

**Generated:** 2025-10-30 01:48
**Status:** CONSOLIDATION COMPLETE
**Total Issues Found:** 22
**Critical:** 9 | **High:** 10 | **Medium:** 3

---

## 📊 EXECUTIVE SUMMARY

### By Category
| Category | Critical | High | Medium | Total |
|----------|----------|------|--------|-------|
| **Visual** | 4 | 5 | 3 | 12 |
| **Functional** | 1 | 0 | 0 | 1 |
| **WooCommerce** | 1 | 5 | 0 | 6 |
| **Security/Performance** | 3 | 0 | 0 | 3 |
| **TOTAL** | **9** | **10** | **3** | **22** |

### By Urgency
- 🔥 **Fix AGORA (hoje):** 9 issues
- ⚡ **Fix esta semana:** 10 issues
- ✅ **Melhorias futuras:** 3 issues

---

## 🔴 CRITICAL ISSUES (9) - FIX IMEDIATO

### Visual Issues

#### ISSUE-001: Cookie Banner - Blue CTAs
- **Category:** Visual / RGPD
- **Impact:** 100% of site visitors (cookie banner obrigatório)
- **Problem:** 30+ instances of `#1863DC` (bright blue) instead of `#E07A31` (terracotta)
- **Location:** Cookie Law Info plugin
- **Agent:** Visual Consistency Auditor
- **Fix Time:** 5 min
- **Fix:**
```css
/* Add to style.css */
.cli-plugin-button,
.cli-plugin-main-button {
    background-color: #E07A31 !important;
    color: #FFFFFF !important;
}
```
- **Testing:** Incognito mode → Homepage → See cookie banner
- **Priority:** 🔥 AGORA

---

#### ISSUE-002: WordPress Admin Bar Blue
- **Category:** Visual
- **Impact:** Logged-in users
- **Problem:** `#007cba` (WP default blue) instead of `#E07A31`
- **Location:** Admin bar (top of site when logged in)
- **Agent:** Visual Consistency Auditor
- **Fix Time:** 2 min
- **Fix:**
```css
#wpadminbar {
    background: #E07A31 !important;
}
#wpadminbar .ab-item:hover {
    background: #C8682A !important;
}
```
- **Testing:** Log in → See admin bar → Verify terracotta color
- **Priority:** 🔥 AGORA

---

#### ISSUE-003: Slate Blue Navigation Links (SITE-WIDE)
- **Category:** Visual
- **Impact:** ALL pages, ALL users
- **Problem:** CSS variable `--chap-contrast-light: #5B7B8F` (slate blue) used site-wide
- **Location:** style.css line 248
- **Agent:** Visual Consistency Auditor
- **Fix Time:** 2 min
- **Fix:**
```css
/* Replace line 248 in style.css */
--chap-contrast-light: #8B4513; /* Brand brown instead of slate blue */
```
- **Testing:** Navigate site → Check ALL link colors
- **Priority:** 🔥 AGORA

---

#### ISSUE-004: WooCommerce Notices Blue
- **Category:** Visual / E-commerce
- **Impact:** Checkout flow, cart updates
- **Problem:** `#0693e3` (cyan blue) for "Added to cart" messages
- **Location:** WooCommerce color presets
- **Agent:** Visual Consistency Auditor
- **Fix Time:** 3 min
- **Fix:**
```css
.woocommerce-message,
.woocommerce-info,
.woocommerce-notices-wrapper .woocommerce-message {
    border-top-color: #E07A31 !important;
    background-color: #FAF7F2 !important;
}
.woocommerce-message::before {
    color: #E07A31 !important;
}
```
- **Testing:** Add product to cart → Verify message color
- **Priority:** 🔥 AGORA

---

### Functional Issues

#### ISSUE-005: Menu Dropdown Z-Index Bug
- **Category:** Functional / UX
- **Impact:** ALL users trying to access submenu items
- **Problem:** Dropdown appears BEHIND hero images (z-index: 9 too low)
- **Location:** Header navigation hover states
- **Agent:** Functional Bug Hunter
- **Fix Time:** 2 min
- **Fix:**
```css
.header-nav .nav-dropdown,
.nav-dropdown {
    z-index: 10000 !important;
}
```
- **Testing:** Hover "Loja" menu → Verify dropdown visible
- **Priority:** 🔥 AGORA

---

### WooCommerce Issues

#### ISSUE-006: Duplicate SKU "180" (151 PRODUTOS!)
- **Category:** WooCommerce / Data Integrity
- **Impact:** CRITICAL - All inventory tracking, orders, payments broken
- **Problem:** 151 products share the SAME SKU "180"
- **Location:** lx_postmeta table
- **Agent:** WooCommerce Validator
- **Fix Time:** 5 min (SQL execution)
- **Fix:**
```sql
-- Generate unique SKUs: CL-000248, CL-000585, etc.
UPDATE lx_postmeta pm
JOIN lx_posts p ON pm.post_id = p.ID
SET pm.meta_value = CONCAT('CL-', LPAD(p.ID, 6, '0'))
WHERE pm.meta_key = '_sku'
  AND pm.meta_value = '180'
  AND p.post_type = 'product';
```
- **Testing:** WP Admin → Products → Check SKUs unique
- **Priority:** 🔥 AGORA

---

### Security/Performance Issues

#### ISSUE-007: Missing Security Headers
- **Category:** Security
- **Impact:** Site vulnerable to XSS, clickjacking, etc.
- **Problem:** No X-Content-Type-Options, HSTS, CSP, X-Frame-Options
- **Location:** Server configuration
- **Agent:** Performance & Security Auditor
- **Fix Time:** 15 min
- **Fix:** Install "Really Simple SSL" plugin OR add to .htaccess:
```apache
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
    Header set Strict-Transport-Security "max-age=31536000" env=HTTPS
</IfModule>
```
- **Testing:** `curl -I http://localhost:8080/ | grep X-`
- **Priority:** 🔥 AGORA (antes de deploy)

---

#### ISSUE-008: Hardcoded http:// URLs (124 instances)
- **Category:** Security / SEO
- **Impact:** Mixed content warnings, SSL issues, SEO penalties
- **Problem:** 124 posts/pages with http://localhost:8080 or http://chapeuslisboeta URLs
- **Location:** lx_posts.post_content, lx_options
- **Agent:** Performance & Security Auditor
- **Fix Time:** 10 min
- **Fix:**
```sql
-- Run AFTER production domain configured
UPDATE lx_posts
SET post_content = REPLACE(post_content, 'http://localhost:8080', 'https://chapeuslisboeta.pt');

UPDATE lx_options
SET option_value = REPLACE(option_value, 'http://localhost:8080', 'https://chapeuslisboeta.pt')
WHERE option_value LIKE '%http://localhost:8080%';

-- Or use Better Search Replace plugin
```
- **Testing:** Search site for http:// links
- **Priority:** 🔥 AGORA (durante deploy)

---

#### ISSUE-009: Missing "Livro de Reclamações" Link
- **Category:** Legal Compliance (Portugal)
- **Impact:** NON-COMPLIANT with Decreto-Lei n.º 156/2005
- **Problem:** No link to official complaint book
- **Location:** Footer or contact page
- **Agent:** Performance & Security Auditor
- **Fix Time:** 5 min
- **Fix:**
```html
<!-- Add to footer.php or contact page -->
<a href="https://www.livroreclamacoes.pt/" target="_blank" rel="noopener">
    <img src="/wp-content/uploads/livro-reclamacoes.png" alt="Livro de Reclamações" />
</a>
```
- **Testing:** Check footer → Verify link works
- **Priority:** 🔥 AGORA (legal requirement)

---

## 🟡 HIGH PRIORITY ISSUES (10) - FIX ESTA SEMANA

### Visual Issues

#### ISSUE-010: Form Input Focus States Blue
- **Category:** Visual
- **Impact:** All forms (contact, search, checkout)
- **Problem:** Focus border `#007bff` (blue) instead of terracotta
- **Fix:** See Agent 1 report CSS section
- **Priority:** ⚡ Esta semana

#### ISSUE-011: Blue Section Backgrounds
- **Category:** Visual
- **Impact:** Homepage sections
- **Problem:** Navy blue backgrounds not aligned with brand
- **Fix:** Review homepage sections, adjust to cream/terracotta palette
- **Priority:** ⚡ Esta semana

#### ISSUE-012: Social Media Icons Blue
- **Category:** Visual
- **Impact:** Footer social links
- **Problem:** Facebook blue, Twitter blue, etc.
- **Fix:** Convert to monochrome brown/terracotta
- **Priority:** ⚡ Esta semana

#### ISSUE-013: Yoast SEO Admin Colors
- **Category:** Visual (Admin only)
- **Impact:** Admin users
- **Problem:** Yoast green not aligned with brand
- **Fix:** Low priority - admin only
- **Priority:** ⚡ Esta semana

#### ISSUE-014: Navigation Hover States
- **Category:** Visual
- **Impact:** All menu interactions
- **Problem:** Hover color not consistent
- **Fix:** Standardize hover to terracotta
- **Priority:** ⚡ Esta semana

---

### WooCommerce Issues

#### ISSUE-015: 3 Products Missing Images
- **Category:** WooCommerce / Content
- **Impact:** Product pages look unprofessional
- **Products:**
  - Fedora Clássica Lisboa (ID 214461)
  - Boina Tradicional Portuguesa (ID 214462)
  - Chapéu de Palha Alentejano (ID 214463)
- **Fix:** Upload images via WP Admin → Media Library
- **Priority:** ⚡ Esta semana

#### ISSUE-016: 1 Product Without Price
- **Category:** WooCommerce / Data
- **Impact:** Cannot be purchased
- **Product:** Boina Piemonte Bombazine (ID 213525)
- **Fix:**
```sql
INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
VALUES (213525, '_price', '45.00');
```
- **Priority:** ⚡ Esta semana

#### ISSUE-017: ~50 Products Missing SKUs
- **Category:** WooCommerce / Data
- **Impact:** Inventory tracking incomplete
- **Fix:** Generate SKUs similar to ISSUE-006
- **Priority:** ⚡ Esta semana

#### ISSUE-018: 57% Out of Stock (75/131 products)
- **Category:** WooCommerce / Inventory
- **Impact:** Limited product selection for customers
- **Fix:** Update stock levels from physical store inventory
- **Priority:** ⚡ Esta semana

#### ISSUE-019: /loja/ Returns 404
- **Category:** WooCommerce / SEO
- **Impact:** Portuguese users expect /loja/ URL
- **Problem:** Only /shop/ works, /loja/ 404
- **Fix:**
```php
// Add to functions.php
add_action('init', function() {
    add_rewrite_rule('^loja/?$', 'index.php?post_type=product', 'top');
    flush_rewrite_rules();
});
```
- **Priority:** ⚡ Esta semana

---

## 🟢 MEDIUM PRIORITY ISSUES (3) - MELHORIAS FUTURAS

#### ISSUE-020: WordPress Block Editor Blue Presets
- **Category:** Visual (Admin only)
- **Impact:** Block editor UI
- **Fix:** Low priority - editor aesthetics only
- **Priority:** ✅ Futuro

#### ISSUE-021: Loading Spinners Blue
- **Category:** Visual
- **Impact:** Loading states
- **Fix:** Change spinner color to terracotta
- **Priority:** ✅ Futuro

#### ISSUE-022: Theme Customizer UI Colors
- **Category:** Visual (Admin only)
- **Impact:** Admin customizer interface
- **Fix:** Low priority - admin only
- **Priority:** ✅ Futuro

---

## 📈 FIX IMPLEMENTATION PLAN

### Phase 1: CRITICAL FIXES (Hoje - 2h)

**Ordem de execução:**
1. ✅ **ISSUE-006** - Fix duplicate SKUs (SQL - 5 min)
2. ✅ **ISSUE-005** - Menu z-index (CSS - 2 min)
3. ✅ **ISSUE-003** - Site-wide link color (CSS - 2 min)
4. ✅ **ISSUE-001** - Cookie banner colors (CSS - 5 min)
5. ✅ **ISSUE-002** - Admin bar color (CSS - 2 min)
6. ✅ **ISSUE-004** - WooCommerce notices (CSS - 3 min)
7. ✅ **ISSUE-007** - Security headers (Plugin/Apache - 15 min)
8. ✅ **ISSUE-009** - Livro Reclamações (HTML - 5 min)
9. ⏸️ **ISSUE-008** - http:// URLs (WAIT for deploy - 10 min)

**Checkpoint 1:** Git commit + Screenshot + Test

---

### Phase 2: HIGH PRIORITY FIXES (Esta semana - 4h)

**Dia 1: WooCommerce Data**
- ISSUE-015: Upload 3 missing images
- ISSUE-016: Add price to Boina Piemonte
- ISSUE-017: Generate SKUs for 50 products
- ISSUE-018: Update stock levels (requer inventário loja)

**Dia 2: Visual Polish**
- ISSUE-010: Form focus states
- ISSUE-011: Section backgrounds
- ISSUE-012: Social icons
- ISSUE-014: Navigation hover

**Dia 3: Portuguese SEO**
- ISSUE-019: /loja/ rewrite rule

**Checkpoint 2:** Git commit + Full site test

---

### Phase 3: MEDIUM PRIORITY (Pós-deploy)

- ISSUE-020, 021, 022: Admin UI tweaks

---

## 🧪 TESTING PROTOCOL

### After Each Fix:
1. **Apply fix** (CSS/SQL/PHP)
2. **Hard refresh** browser (Cmd+Shift+R)
3. **Test specific feature**
4. **Screenshot** before/after
5. **Git commit** with message
6. **Document** in `reports/fixes/ISSUE-XXX.md`

### After Phase 1 (Critical):
1. Full homepage test
2. Menu navigation test
3. Add to cart flow test
4. Cookie banner test (incognito)
5. Admin login test

### After Phase 2 (High):
1. Complete e-commerce flow (browse → add → checkout)
2. Test all product pages
3. Test all static pages
4. Mobile responsive test (375px, 414px)
5. Cross-browser test (Chrome, Firefox, Safari)

### Before Deploy:
1. Run all 4 agents again (regression test)
2. Client UAT (User Acceptance Testing)
3. Backup everything
4. Security scan
5. Performance test (PageSpeed)

---

## 📊 PROGRESS TRACKING

| Phase | Issues | Status | ETA |
|-------|--------|--------|-----|
| Phase 1: Critical | 9 | ⏳ IN PROGRESS | Hoje |
| Phase 2: High | 10 | 🔜 PENDING | Esta semana |
| Phase 3: Medium | 3 | 📅 PLANNED | Pós-deploy |

**Total Issues:** 22
**Fixed:** 0
**In Progress:** 9
**Pending:** 13

---

## 🎯 SUCCESS CRITERIA

### Site is Ready for Deploy When:
- [ ] All 9 CRITICAL issues fixed
- [ ] All 10 HIGH issues fixed (or deferred with client approval)
- [ ] Zero blue colors visible to users
- [ ] Menu dropdown visible on hover
- [ ] All products have unique SKUs
- [ ] Security headers configured
- [ ] Livro de Reclamações link present
- [ ] Client approval obtained

---

## 📞 STAKEHOLDER COMMUNICATION

**Email Template for Client:**

```
Assunto: Audit Completo do Site - 22 Issues Encontrados

Olá Tiago,

Completámos um audit exaustivo do site usando 4 agents especializados.

BOAS NOTÍCIAS:
✅ Performance excelente (171-197ms load time)
✅ /sobre-nos/ funciona perfeitamente (false alarm!)
✅ Blog com 5 posts e imagens
✅ RGPD compliant (cookie banner + privacy policy)

PROBLEMAS ENCONTRADOS:
🔴 9 issues CRÍTICOS (fix hoje)
🟡 10 issues HIGH (fix esta semana)
🟢 3 issues MEDIUM (melhorias futuras)

MAIS CRÍTICO:
1. Cores azul aparecendo (cookie banner, links, admin)
2. Menu dropdown encoberto (z-index bug)
3. 151 produtos com SKU duplicado "180" (!!!)
4. Missing security headers
5. Livro de Reclamações missing (legal requirement)

TIMELINE:
- Hoje: Fix 9 critical issues (2h)
- Esta semana: Fix 10 high issues (4h)
- Deploy: Sexta-feira?

Relatórios completos disponíveis em:
/reports/audits/

Podemos agendar call para discutir?

Cumprimentos,
[Nome]
```

---

## 📁 REPORT FILES

All detailed reports saved to:
```
/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/reports/audits/

├── 2025-10-30-0148-visual-consistency.md (18KB, 706 lines)
├── 2025-10-30-0148-functional-bugs.md (9.7KB, 431 lines)
├── 2025-10-30-0148-woocommerce-validation.md (15KB, 1599 lines)
├── 2025-10-30-0148-performance-security.md (15KB, 431 lines)
└── QUICK_SUMMARY.md (overview)
```

---

**Document Created:** 2025-10-30 01:48
**Last Updated:** 2025-10-30 01:52
**Status:** CONSOLIDATION COMPLETE - READY FOR PHASE 1
**Next Action:** Apply CRITICAL fixes (9 issues)

---

**🚀 READY TO START PHASE 1?**
