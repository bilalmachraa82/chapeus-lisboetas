# 🧠 ULTRA-THINK: COMPLETE ARCHITECTURE WITH VALIDATORS

**Data:** 15 Novembro 2025
**Scope:** Complete orchestrator architecture + validation layers
**Critical Issue:** Prevent localhost/production visual mismatches (client requirement)

---

## 🎯 EXECUTIVE SUMMARY

**Current Status:** 15 agents implemented, but missing critical pieces:
1. ❌ 8 functionality agents missing (payments, shipping, RGPD, etc.)
2. ❌ 0 validation agents (CRITICAL - prevents localhost/production drift)
3. ❌ 3 placeholder agents incomplete
4. ❌ 3 buggy agents need fixes

**Target Architecture:** 30+ specialized agents with 3-layer validation

**Timeline:** 2-3 weeks for complete implementation

---

## 🏗️ COMPLETE AGENT ARCHITECTURE (30+ AGENTS)

### LAYER 1: DATA FOUNDATION (Phase 1) - 6 agents

#### Existing (4 agents):
1. **SheetSync-Agent** ⚠️ Needs adaptation (catalogo.json source)
2. **SheetSanitizer-Agent** ⚠️ Needs relaxed validation
3. **PriceGate-Agent** ✅ Working
4. **DataDiff-Agent** ❌ Placeholder

#### NEW Validators (2 agents):
5. **🆕 GoogleSheetsValidator-Agent** 🔥 CRITICAL
   - **Purpose:** Validate Google Sheets ↔ WordPress sync
   - **Prevents:** Client updates Google Sheet but site doesn't update
   - **Checks:**
     - Products in Sheet exist in WordPress
     - Prices match
     - SKUs aligned
     - Status (draft/publish) correct
   - **Output:** Discrepancy report (JSON + Markdown)
   - **Frequency:** After every SheetSync, before client handoff

6. **🆕 DataIntegrityValidator-Agent** 🔥 CRITICAL
   - **Purpose:** Validate database integrity after Phase 1
   - **Checks:**
     - No orphan meta fields (product deleted but meta remains)
     - No duplicate SKUs
     - All published products have price >0
     - All products have category assignment
   - **Output:** Health check report
   - **Rollback:** Auto-rollback if integrity <95%

---

### LAYER 2: PRODUCT ENRICHMENT (Phase 2) - 7 agents

#### Existing (4 agents):
7. **DescriptionBuilder-Agent** 🔧 Needs fix (templates not applying)
8. **ImageInventory-Agent** ✅ Working
9. **GalleryLinker-Agent** ⚠️ Partial (low SKU match rate)
10. **VariationBuilder-Agent** 🔧 Needs fix (detection broken)

#### NEW Validators (3 agents):
11. **🆕 ProductPhotoValidator-Agent** 🔥 CRITICAL
    - **Purpose:** Validate ALL products have expected photos
    - **Checks:**
      - Featured image exists and accessible
      - Gallery has ≥1 photo
      - Image URLs return 200 (not 404)
      - Images are >1500×1500px (quality check)
      - AI photos correctly linked (editorial, angle, lifestyle)
    - **Output:** Products without photos report
    - **Target:** 100% products with photos

12. **🆕 ProductDataValidator-Agent** 🔥 CRITICAL
    - **Purpose:** Validate product data completeness
    - **Checks:**
      - All products have title, SKU, price
      - Descriptions not empty or placeholder
      - Specs (color, size, composition) populated
      - Tags assigned
      - Categories hierarchical (Chapéus > Boinas > Inverno)
    - **Output:** Data quality score per product
    - **Target:** >95% complete data

13. **🆕 VariationConsistencyValidator-Agent**
    - **Purpose:** Validate product variations are correct
    - **Checks:**
      - Parent products have child variations
      - Variations have unique attributes (color, size)
      - Pricing consistent (parent = min child price)
      - Stock status aligned
    - **Output:** Variation errors report
    - **Auto-fix:** Simple issues (pricing sync)

---

### LAYER 3: UX POLISH (Phase 3) - 6 agents

#### Existing (3 agents):
14. **WooPagesFixer-Agent** ✅ Working (basic check)
15. **MenuUXFix-Agent** ❌ Placeholder
16. **VisualQA-Agent** ❌ Placeholder

#### NEW Validators (3 agents):
17. **🆕 LocalhostProductionValidator-Agent** 🔥 🔥 🔥 CRITICAL
    - **Purpose:** THE BIG ONE - Prevent localhost/production visual drift
    - **Uses:** Chrome DevTools MCP for visual comparison
    - **Checks:**
      - Homepage products match (localhost vs production)
      - Shop page product count identical
      - Individual product pages render correctly
      - Photos visible (not broken images)
      - Cart/Checkout functional
      - Menus/dropdowns working
    - **Method:**
      ```javascript
      // Chrome DevTools MCP integration
      1. Navigate to localhost:8080
      2. Take screenshot + DOM snapshot
      3. Navigate to chapeuslisboeta.pt (production)
      4. Take screenshot + DOM snapshot
      5. Compare:
         - Product count per page
         - Image src URLs (relative vs absolute)
         - CSS rendering (z-index, dropdowns)
         - Missing products/photos
      6. Generate visual diff report
      ```
    - **Output:**
      - Side-by-side screenshots
      - Diff highlights (red = missing, green = extra)
      - JSON diff of products
    - **Frequency:** After every deployment, before going live
    - **Rollback trigger:** >5% visual diff

18. **🆕 ResponsivenessValidator-Agent**
    - **Purpose:** Validate mobile/tablet responsiveness
    - **Uses:** Chrome DevTools MCP device emulation
    - **Checks:**
      - Desktop (1920×1080)
      - Tablet (768×1024)
      - Mobile (375×667, 414×896)
    - **Validates:**
      - No horizontal scroll
      - Images scale correctly
      - Menus collapse to hamburger
      - Checkout usable on mobile
    - **Output:** Responsive test report with screenshots

19. **🆕 AccessibilityValidator-Agent**
    - **Purpose:** WCAG 2.1 AA compliance
    - **Uses:** Chrome DevTools Lighthouse
    - **Checks:**
      - Alt text on all images
      - Color contrast ≥4.5:1
      - Keyboard navigation
      - Screen reader labels
      - Form input labels
    - **Output:** Accessibility score + violations
    - **Target:** ≥90/100

---

### LAYER 4: PAYMENT & SHIPPING (Phase 4) - 4 agents

#### NEW Critical Agents (4 agents):
20. **🆕 IfthenPay-Agent** 🔥 BLOCKER
    - **Purpose:** Configure Portuguese payment gateway
    - **Integrations:**
      - MB Way (instant mobile payments)
      - Multibanco (bank references)
    - **Config:**
      - API keys from IfthenPay account
      - Webhook URLs for payment confirmation
      - Email templates (Portuguese)
    - **Test:** Create test order, verify payment flow
    - **Validator:** Payment callback working

21. **🆕 CTT-Agent** 🔥 BLOCKER
    - **Purpose:** Configure CTT Expresso shipping
    - **Features:**
      - Automatic shipping label generation
      - Tracking number integration
      - Shipping cost calculator (weight-based)
    - **Config:**
      - CTT API credentials
      - Shipping zones (Portugal, EU, International)
      - Pickup location (Chiado store)
    - **Test:** Create test shipment
    - **Validator:** Label PDF generated correctly

22. **🆕 PaymentShippingValidator-Agent** 🔥 CRITICAL
    - **Purpose:** Validate payment + shipping flow end-to-end
    - **Uses:** Chrome DevTools MCP for checkout simulation
    - **Test Flow:**
      ```
      1. Add product to cart
      2. Proceed to checkout
      3. Fill shipping details (CTT address validation)
      4. Select MB Way payment
      5. Verify payment screen loads
      6. Check webhook received (mock payment)
      7. Verify order status = processing
      8. Check shipping label generated
      ```
    - **Output:** Checkout flow report (pass/fail per step)
    - **Frequency:** After every payment/shipping config change
    - **Rollback trigger:** Checkout failure

23. **🆕 OrderValidator-Agent**
    - **Purpose:** Validate orders are correctly recorded
    - **Checks:**
      - Order meta complete (billing, shipping, payment)
      - Products linked to order
      - Stock decremented
      - Email sent to customer + admin
      - Order notes timestamped
    - **Output:** Order integrity report
    - **Auto-fix:** Regenerate missing emails

---

### LAYER 5: PERFORMANCE & SECURITY (Phase 5) - 5 agents

#### Existing (1 agent):
24. **Security&SEO-Agent** ⚠️ Partial (checks only, no config)

#### NEW Agents (4 agents):
25. **🆕 CookieYes-Agent** 🔥 BLOCKER (RGPD legal requirement)
    - **Purpose:** RGPD compliance (mandatory by EU law)
    - **Config:**
      - CookieYes banner widget
      - Privacy policy page
      - Cookie consent tracking
      - Analytics opt-in/opt-out
    - **Checks:**
      - Banner visible on first visit
      - "Aceitar cookies" button functional
      - Google Analytics respects consent
    - **Validator:** Lighthouse privacy audit
    - **Legal risk if missing:** €20M fine or 4% global revenue

26. **🆕 WPRocket-Agent**
    - **Purpose:** Performance optimization
    - **Config:**
      - Page caching (server-side)
      - GZIP compression
      - Lazy loading images
      - Minify CSS/JS
      - Database cleanup
    - **Target:** PageSpeed >85 mobile, >90 desktop
    - **Validator:** Lighthouse performance score

27. **🆕 SecurityHardening-Agent**
    - **Purpose:** WordPress security best practices
    - **Actions:**
      - Disable XML-RPC (brute force vector)
      - Hide WordPress version
      - Restrict wp-admin access (IP whitelist)
      - 2FA for admin users
      - Security headers (.htaccess)
    - **Validator:** Security scan (WPScan or similar)
    - **Output:** Security score + vulnerabilities

28. **🆕 PerformanceValidator-Agent** 🔥 CRITICAL
    - **Purpose:** Validate site performance
    - **Uses:** Chrome DevTools Lighthouse
    - **Metrics:**
      - Largest Contentful Paint (LCP) <2.5s
      - First Input Delay (FID) <100ms
      - Cumulative Layout Shift (CLS) <0.1
      - Time to Interactive (TTI) <3.5s
    - **Tests:**
      - Homepage, Shop, Product page, Cart, Checkout
      - Desktop + Mobile
    - **Output:** Core Web Vitals report
    - **Target:** All green (90+ scores)
    - **Rollback trigger:** Performance regression >10%

---

### LAYER 6: TRANSLATION & SEO (Phase 6) - 4 agents

#### NEW Agents (4 agents):
29. **🆕 WPML-Agent**
    - **Purpose:** PT/EN translation setup
    - **Config:**
      - WPML plugin + String Translation
      - Default language: PT
      - Secondary: EN
      - URL structure: chapeuslisboeta.pt/en/
    - **Translation:**
      - Products (auto-translate via DeepL API)
      - Pages (manual review)
      - Menus, widgets
    - **Validator:** All products have EN version

30. **🆕 Yoast-Agent**
    - **Purpose:** SEO optimization
    - **Config:**
      - Schema.org markup (Organization, LocalBusiness)
      - Product schema (price, availability)
      - Breadcrumbs
      - XML sitemap
      - Meta descriptions (auto-generate if missing)
    - **Validator:** Yoast SEO score >70/100 per page

31. **🆕 SEOValidator-Agent** 🔥 CRITICAL
    - **Purpose:** Validate SEO best practices
    - **Uses:** Chrome DevTools Lighthouse SEO audit
    - **Checks:**
      - All pages have title tag
      - Meta descriptions <160 chars
      - H1 unique per page
      - Images have alt text
      - Internal linking structure
      - robots.txt + sitemap.xml
      - Canonical URLs
      - Mobile-friendly
    - **Output:** SEO audit report
    - **Target:** 100% pages with meta + schema

32. **🆕 FinalDeploymentValidator-Agent** 🔥 🔥 🔥 CRITICAL
    - **Purpose:** FINAL pre-production checklist
    - **The Ultimate Gatekeeper**
    - **Uses:** ALL validator agents in sequence
    - **Checklist (30+ checks):**
      ```
      DATA:
      ✓ Google Sheets ↔ WordPress synced
      ✓ All products have SKU + price
      ✓ No duplicate SKUs
      ✓ Database integrity 100%

      PHOTOS:
      ✓ 100% products have featured image
      ✓ ≥80% products have gallery (3+ photos)
      ✓ All image URLs accessible (no 404s)
      ✓ AI photos correctly linked

      UX:
      ✓ Localhost matches production (visual diff <5%)
      ✓ Homepage loads correctly
      ✓ Shop page shows all products
      ✓ Product pages render
      ✓ Cart functional
      ✓ Checkout complete flow
      ✓ Menus/dropdowns working
      ✓ Mobile responsive

      PAYMENT/SHIPPING:
      ✓ IfthenPay configured
      ✓ MB Way test payment successful
      ✓ CTT shipping labels generated
      ✓ Order emails sent

      LEGAL/COMPLIANCE:
      ✓ RGPD banner visible
      ✓ Privacy policy page
      ✓ Cookie consent working

      PERFORMANCE:
      ✓ PageSpeed >85 mobile
      ✓ Core Web Vitals green
      ✓ LCP <2.5s, FID <100ms, CLS <0.1

      SEO:
      ✓ All pages have meta
      ✓ Schema markup present
      ✓ Sitemap generated
      ✓ Images have alt text

      SECURITY:
      ✓ SSL certificate valid
      ✓ Security headers configured
      ✓ Admin 2FA enabled
      ✓ Backups automated

      TRANSLATION:
      ✓ WPML configured (PT/EN)
      ✓ All products translated
      ```
    - **Output:**
      - GO/NO-GO decision
      - Detailed report per section
      - Blocking issues highlighted
    - **Rollback trigger:** ANY critical check fails
    - **Approval required:** Human review of report before deploy

---

## 🔍 VALIDATION STRATEGY (3-LAYER DEFENSE)

### Layer 1: Inline Validation (During Execution)
**Agents:** Every functional agent has built-in validation
```python
class BaseAgent:
    def execute(self):
        # Before
        self.validate_prerequisites()  # E.g., DB accessible, files exist

        # During
        self.run()  # Agent work with self.record_success/failure

        # After
        self.validate_results()  # E.g., product created, meta saved

        if self.metrics.success_rate < self.min_success_rate:
            self.rollback()
```

### Layer 2: Phase Validation (After Phase Completion)
**Agents:** Dedicated validator per phase
- Phase 1 → GoogleSheetsValidator + DataIntegrityValidator
- Phase 2 → ProductPhotoValidator + ProductDataValidator
- Phase 3 → LocalhostProductionValidator + ResponsivenessValidator
- Phase 4 → PaymentShippingValidator + OrderValidator
- Phase 5 → PerformanceValidator + SecurityValidator
- Phase 6 → SEOValidator

**Orchestrator integration:**
```python
def execute_phase(self, phase):
    # 1. Run functional agents
    for agent in phase.agents:
        self.execute_agent(agent)

    # 2. Run validator agents
    for validator in phase.validators:
        result = self.execute_agent(validator)
        if not result.passed:
            self.trigger_rollback(phase)
            return False

    # 3. Check validation gate
    return self.validate_gate(phase.gate)
```

### Layer 3: Final Deployment Validation
**Agent:** FinalDeploymentValidator-Agent
**When:** Before every production deployment
**Purpose:** Comprehensive checklist (30+ checks)
**Output:** GO/NO-GO decision

---

## 🌐 LOCALHOST vs PRODUCTION VALIDATION (Critical Requirement)

### Problem Statement
**User's past experience:** "localhost looked perfect, but production was missing products/photos"

**Root causes:**
1. Image URLs hardcoded to localhost (http://localhost:8080)
2. Products in draft status locally but not synced to production
3. Cache differences (localhost = no cache, production = aggressive cache)
4. Database differences (different wp_options values)
5. File permissions (localhost = permissive, production = restrictive)

### Solution: LocalhostProductionValidator-Agent

**Architecture:**
```javascript
class LocalhostProductionValidator {
  constructor() {
    this.localhost = 'http://localhost:8080';
    this.production = 'https://chapeuslisboeta.pt';
    this.chromeDevTools = new ChromeDevToolsMCP();
  }

  async validate() {
    // 1. Product count comparison
    const localProducts = await this.getProductCount(this.localhost);
    const prodProducts = await this.getProductCount(this.production);

    if (localProducts !== prodProducts) {
      this.errors.push(`Product count mismatch: ${localProducts} local vs ${prodProducts} prod`);
    }

    // 2. Visual comparison (Chrome DevTools MCP)
    const pages = ['/', '/shop/', '/product/boina-bico-pato/', '/cart/', '/checkout/'];

    for (const page of pages) {
      const localSnapshot = await this.takeSnapshot(this.localhost + page);
      const prodSnapshot = await this.takeSnapshot(this.production + page);

      const diff = await this.compareSnapshots(localSnapshot, prodSnapshot);

      if (diff.percentage > 5) {  // >5% difference
        this.errors.push(`Visual diff on ${page}: ${diff.percentage}%`);
        this.saveVisualDiff(page, diff);
      }
    }

    // 3. Image accessibility check
    const localImages = await this.getAllImageUrls(this.localhost);
    const prodImages = await this.getAllImageUrls(this.production);

    for (const img of localImages) {
      const accessible = await this.checkImageAccessible(img);
      if (!accessible) {
        this.errors.push(`Image broken: ${img}`);
      }
    }

    // 4. Database sync check
    const localDB = await this.queryDatabase('localhost');
    const prodDB = await this.queryDatabase('production');

    const skuDiff = this.compareSKUs(localDB.skus, prodDB.skus);
    if (skuDiff.length > 0) {
      this.errors.push(`SKU mismatch: ${skuDiff.join(', ')}`);
    }

    return {
      passed: this.errors.length === 0,
      errors: this.errors,
      warnings: this.warnings,
      report: this.generateReport()
    };
  }

  async takeSnapshot(url) {
    // Use Chrome DevTools MCP
    await this.chromeDevTools.navigate(url);
    await this.chromeDevTools.waitForNetworkIdle();

    return {
      screenshot: await this.chromeDevTools.takeScreenshot(),
      dom: await this.chromeDevTools.getDOMSnapshot(),
      products: await this.chromeDevTools.evaluateScript(`
        Array.from(document.querySelectorAll('.product')).map(p => ({
          title: p.querySelector('.product-title')?.textContent,
          price: p.querySelector('.price')?.textContent,
          image: p.querySelector('img')?.src,
          sku: p.dataset.sku
        }))
      `)
    };
  }

  compareSnapshots(local, prod) {
    // Product-level comparison
    const localProducts = new Set(local.products.map(p => p.sku));
    const prodProducts = new Set(prod.products.map(p => p.sku));

    const missing = [...localProducts].filter(sku => !prodProducts.has(sku));
    const extra = [...prodProducts].filter(sku => !localProducts.has(sku));

    // Visual pixel diff (optional - expensive)
    const pixelDiff = this.compareImages(local.screenshot, prod.screenshot);

    return {
      missingProducts: missing,
      extraProducts: extra,
      pixelDifference: pixelDiff,
      percentage: (missing.length + extra.length) / localProducts.size * 100
    };
  }
}
```

**Chrome DevTools MCP Integration:**
```python
# In LocalhostProductionValidator-Agent
def validate_visual_consistency(self):
    """Use Chrome DevTools MCP for visual validation"""

    # Available MCP tools:
    # - mcp__chrome-devtools__navigate_page
    # - mcp__chrome-devtools__take_screenshot
    # - mcp__chrome-devtools__take_snapshot (DOM)
    # - mcp__chrome-devtools__evaluate_script
    # - mcp__chrome-devtools__list_network_requests

    pages = [
        {'path': '/', 'name': 'Homepage'},
        {'path': '/shop/', 'name': 'Shop'},
        {'path': '/cart/', 'name': 'Cart'},
    ]

    for page in pages:
        # Localhost
        self.navigate_and_snapshot('http://localhost:8080' + page['path'])
        local_screenshot = self.take_screenshot()
        local_products = self.extract_products()

        # Production
        self.navigate_and_snapshot('https://chapeuslisboeta.pt' + page['path'])
        prod_screenshot = self.take_screenshot()
        prod_products = self.extract_products()

        # Compare
        diff = self.compare_product_lists(local_products, prod_products)

        if diff['missing'] or diff['extra']:
            self.add_error(f"{page['name']}: {len(diff['missing'])} missing, {len(diff['extra'])} extra products")
            self.save_comparison_report(page['name'], diff)
```

**Output Report Format:**
```markdown
# Localhost vs Production Validation Report

**Date:** 2025-11-15 02:30:00
**Localhost:** http://localhost:8080
**Production:** https://chapeuslisboeta.pt

## Summary
- ✅ Product count: MATCH (62 products)
- ❌ Visual consistency: FAIL (12% diff)
- ⚠️  Image accessibility: 3 broken images
- ✅ Database sync: MATCH

## Detailed Findings

### Homepage
- **Product count:** 8 local vs 6 production ❌
- **Missing products (production):**
  - SKU 18456 - Boina Harris Tweed
  - SKU 22182 - Boné Bico de Pato
- **Screenshot diff:** 15% (see images/homepage_diff.png)

### Shop Page
- **Product count:** 62 local vs 62 production ✅
- **Visual diff:** 2% (minor CSS differences)

### Product Page (sample: 18456)
- **Image count:** 5 local vs 3 production ⚠️
- **Missing images:**
  - img_03_angle.jpg (404 error)
  - img_04_lifestyle.jpg (404 error)

## Recommendations
1. Sync missing products to production (SheetSync-Agent)
2. Fix broken image URLs (GalleryLinker-Agent)
3. Clear production cache (WPRocket-Agent)

## GO/NO-GO Decision
**Status:** ❌ NO-GO
**Blocking issues:** 2 missing products, 3 broken images
**Action required:** Fix issues and re-validate
```

---

## 📊 GOOGLE SHEETS FUTURE-PROOFING

### Requirement
**User:** "In the future, the client will update Google Sheets and we need the website to sync automatically"

### Solution Architecture

#### Agent: GoogleSheetsSyncMonitor-Agent (NEW)
**Purpose:** Continuous monitoring + auto-sync
**Trigger:** Google Sheets webhook (Apps Script onEdit)

**Workflow:**
```
1. Client edits Google Sheet
   ↓
2. Apps Script onEdit trigger
   ↓
3. POST webhook → chapeuslisboeta.pt/wp-json/custom/v1/sheets-updated
   ↓
4. WordPress receives webhook
   ↓
5. Triggers GoogleSheetsSyncMonitor-Agent
   ↓
6. Agent executes:
   - SheetSync-Agent (pull changes)
   - GoogleSheetsValidator-Agent (verify sync)
   - ProductPhotoValidator-Agent (check photos still ok)
   - LocalhostProductionValidator-Agent (if production)
   ↓
7. Email report to admin + client
```

**Apps Script Code (Google Sheets):**
```javascript
// Add to Google Sheet: Extensions → Apps Script
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  const range = e.range;

  // Only trigger for product data changes
  if (['BOINAS INVERNO', 'BOINAS VERÃO', /* ... */].includes(sheet.getName())) {
    const webhookUrl = 'https://chapeuslisboeta.pt/wp-json/custom/v1/sheets-updated';

    const payload = {
      sheet: sheet.getName(),
      row: range.getRow(),
      column: range.getColumn(),
      oldValue: e.oldValue,
      newValue: e.value,
      user: Session.getActiveUser().getEmail(),
      timestamp: new Date().toISOString()
    };

    UrlFetchApp.fetch(webhookUrl, {
      method: 'POST',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      headers: {
        'X-API-Key': 'secret_key_here'  // WordPress validates
      }
    });
  }
}
```

**WordPress Endpoint:**
```php
// In WordPress functions.php or custom plugin
add_action('rest_api_init', function() {
  register_rest_route('custom/v1', '/sheets-updated', [
    'methods' => 'POST',
    'callback' => 'handle_sheets_webhook',
    'permission_callback' => 'validate_api_key'
  ]);
});

function handle_sheets_webhook($request) {
  $data = $request->get_json_params();

  // Log the change
  error_log("Google Sheet updated: {$data['sheet']} row {$data['row']}");

  // Trigger sync (async via WP-Cron or immediate)
  wp_schedule_single_event(time(), 'run_sheet_sync_agent', [$data]);

  // Or immediate (for testing):
  // exec('python3 /path/to/orchestrator/agents/sheet_sync_agent.py > /dev/null 2>&1 &');

  return new WP_REST_Response(['status' => 'queued'], 200);
}
```

**Agent: GoogleSheetsSyncMonitor-Agent**
```python
class GoogleSheetsSyncMonitorAgent(BaseAgent):
    """Monitor Google Sheets changes and trigger sync"""

    def run(self) -> int:
        # 1. Check for pending changes (from webhook queue)
        changes = self.get_pending_changes()

        if not changes:
            self.logger.info("No pending changes")
            return 0

        # 2. Run SheetSync-Agent
        self.logger.info(f"Processing {len(changes)} changes")
        sync_result = self.execute_sub_agent('SheetSync-Agent')

        if sync_result.status != AgentStatus.COMPLETED:
            self.add_error("SheetSync failed")
            return 1

        # 3. Validate sync
        validator_result = self.execute_sub_agent('GoogleSheetsValidator-Agent')

        if validator_result.status != AgentStatus.COMPLETED:
            self.add_error("Validation failed")
            self.send_alert_email(changes, validator_result)
            return 1

        # 4. Send success notification
        self.send_success_email(changes)

        return 0
```

#### Validation After Client Updates
**Agent:** GoogleSheetsValidator-Agent (already defined above)

**Checks:**
1. Product count matches (Google Sheets vs WordPress)
2. Prices match
3. SKUs aligned
4. New products created (if client added rows)
5. Deleted products set to draft (if client deleted rows)
6. Changed prices updated in WordPress

**Auto-rollback:** If validation fails >10%, rollback WordPress changes

**Email notification:**
```
To: Tiago Andrade <mail@chapeuslisboetas.com>
Cc: Bilal <bilal@aiparati.com>
Subject: ✅ Google Sheet sync complete - 3 products updated

Hi Tiago,

Your Google Sheet changes have been synced to the website:

✅ Updated: 3 products
  - Boina Harris Tweed: Price €45 → €50
  - Chapéu Panama: Added new color variation
  - Boné Trucker: Updated description

✅ Validation: All checks passed
✅ Photos: All products still have images
✅ Website: Live and accessible

View changes: https://chapeuslisboeta.pt/shop/

---
Automated by GoogleSheetsSyncMonitor-Agent
```

---

## 🚀 IMPLEMENTATION PHASES

### PHASE 0: IMMEDIATE FIXES (2 hours) 🔥 NOW
**Goal:** Unblock orchestrator execution with 62 products

1. ✅ Adapt SheetSync-Agent to read catalogo.json
2. ✅ Adapt SheetSanitizer-Agent similarly
3. ▶️ Test Phase 1 agents with 62 products
4. 📊 Generate first validation report

**Deliverable:** Orchestrator can execute Phase 1

---

### PHASE 1: CRITICAL VALIDATORS (1 day)
**Goal:** Prevent localhost/production drift

Implement 3 critical validators:
1. **LocalhostProductionValidator-Agent** (4 hours)
   - Chrome DevTools MCP integration
   - Visual comparison
   - Product count validation
   - Image accessibility checks

2. **ProductPhotoValidator-Agent** (2 hours)
   - Validate all products have photos
   - Check image URLs (200 status)
   - AI photo linking verification

3. **DataIntegrityValidator-Agent** (2 hours)
   - Database health checks
   - Orphan meta cleanup
   - Duplicate SKU detection

**Deliverable:** 3 validators operational

---

### PHASE 2: CRITICAL MISSING AGENTS (1 week)
**Goal:** Complete payment, shipping, RGPD (site can actually sell)

Implement 4 blockers:
1. **IfthenPay-Agent** (2 days)
   - MB Way integration
   - Multibanco references
   - Webhook handling
   - Test payment flow

2. **CTT-Agent** (2 days)
   - API integration
   - Label generation
   - Tracking numbers
   - Zone configuration

3. **CookieYes-Agent** (1 day)
   - RGPD banner
   - Privacy policy
   - Consent tracking
   - Analytics opt-in

4. **PaymentShippingValidator-Agent** (1 day)
   - End-to-end checkout test
   - Payment callback validation
   - Shipping label check

**Deliverable:** Site can accept orders legally

---

### PHASE 3: ADDITIONAL AGENTS (3-5 days)
**Goal:** Complete functionality

Implement 4 nice-to-have:
1. **Flatsome-Agent** (1 day) - Theme configuration
2. **WPRocket-Agent** (1 day) - Performance
3. **WPML-Agent** (1 day) - PT/EN translation
4. **Yoast-Agent** (1 day) - SEO

**Deliverable:** Professional, fast, multilingual site

---

### PHASE 4: PLACEHOLDER COMPLETION (2-3 days)
**Goal:** No more placeholders

Complete 3 agents:
1. **DataDiff-Agent** (1 day) - Full Google Sheets comparison
2. **MenuUXFix-Agent** (1 day) - CSS injection
3. **VisualQA-Agent** (1 day) - BackstopJS integration

**Deliverable:** All 15 original agents functional

---

### PHASE 5: BUG FIXES (1-2 days)
**Goal:** Fix known issues

Fix 3 buggy agents:
1. **DescriptionBuilder-Agent** - Force template application
2. **VariationBuilder-Agent** - Fix detection regex
3. **ImportVerifier-Agent** - Fix metrics calculation

**Deliverable:** 100% agents working correctly

---

### PHASE 6: FINAL VALIDATORS (2 days)
**Goal:** Complete validation layer

Implement final validators:
1. **PerformanceValidator-Agent** (Chrome DevTools Lighthouse)
2. **SEOValidator-Agent** (Meta, schema, sitemap)
3. **FinalDeploymentValidator-Agent** (30+ checklist)

**Deliverable:** Production-ready deployment system

---

### PHASE 7: GOOGLE SHEETS AUTO-SYNC (1 day)
**Goal:** Future-proof for client updates

Implement:
1. Apps Script webhook
2. WordPress endpoint
3. GoogleSheetsSyncMonitor-Agent
4. Email notifications

**Deliverable:** Client can update Google Sheets → auto-sync to website

---

## 📋 COMPLETE AGENT ROSTER (32 AGENTS)

### ✅ Existing Functional (5):
1. PhotoTriage-Agent
2. PriceGate-Agent
3. ImageInventory-Agent
4. WooPagesFixer-Agent
5. Orchestrator-3.1

### ⚠️ Existing Partial (4):
6. SheetSync-Agent → needs catalogo.json adaptation
7. SheetSanitizer-Agent → needs relaxed validation
8. GalleryLinker-Agent → needs improved SKU matching
9. Security&SEO-Agent → needs actual config (not just checks)

### 🔧 Existing Buggy (3):
10. DescriptionBuilder-Agent
11. VariationBuilder-Agent
12. ImportVerifier-Agent

### ❌ Existing Placeholder (3):
13. DataDiff-Agent
14. MenuUXFix-Agent
15. VisualQA-Agent

### 🆕 NEW Critical Validators (7):
16. LocalhostProductionValidator-Agent 🔥🔥🔥
17. ProductPhotoValidator-Agent 🔥
18. DataIntegrityValidator-Agent 🔥
19. GoogleSheetsValidator-Agent 🔥
20. PaymentShippingValidator-Agent 🔥
21. PerformanceValidator-Agent 🔥
22. FinalDeploymentValidator-Agent 🔥🔥🔥

### 🆕 NEW Functionality Agents (8):
23. IfthenPay-Agent 🔥 BLOCKER
24. CTT-Agent 🔥 BLOCKER
25. CookieYes-Agent 🔥 BLOCKER (legal)
26. Flatsome-Agent
27. WPRocket-Agent
28. WPML-Agent
29. Yoast-Agent
30. GoogleSheetsSyncMonitor-Agent

### 🆕 NEW Supporting Validators (2):
31. ProductDataValidator-Agent
32. ResponsivenessValidator-Agent

**Total:** 32 specialized agents
**Critical path:** 15 agents (5 existing + 10 new critical)
**Timeline:** 2-3 weeks for complete system

---

## 🎯 SUCCESS METRICS

### Technical Metrics
- ✅ 100% agents functional (no placeholders)
- ✅ 100% products have photos
- ✅ <5% localhost/production visual diff
- ✅ PageSpeed >85 mobile, >90 desktop
- ✅ Checkout success rate >95%
- ✅ Database integrity 100%
- ✅ Google Sheets sync accuracy >99%

### Business Metrics
- ✅ Site can accept real orders (IfthenPay + CTT)
- ✅ RGPD compliant (CookieYes)
- ✅ Client can update Google Sheets autonomously
- ✅ Zero data loss (validators prevent)
- ✅ Professional appearance (Flatsome)
- ✅ Multilingual (WPML PT/EN)

### Client Autonomy
- ✅ Google Sheet → Website auto-sync
- ✅ Email notifications on sync
- ✅ Validation reports (non-technical)
- ✅ 1-click rollback if needed

---

## 🚨 CRITICAL DECISION POINT

**Question:** Implement immediately or phase gradually?

### Option A: Full Implementation (2-3 weeks)
**Pros:**
- ✅ Complete system
- ✅ No technical debt
- ✅ All validators in place

**Cons:**
- ⏳ Delays launch
- ⏳ More complex testing

### Option B: Phased (Recommended) ⭐
**Week 1:** Immediate fixes + critical validators + payment/shipping
**Week 2:** Additional agents + placeholder completion
**Week 3:** Final validators + Google Sheets auto-sync

**Pros:**
- ✅ Can launch after Week 1 (basic functionality)
- ✅ Incremental validation
- ✅ Lower risk

**Cons:**
- ⚠️ Some features delayed

---

## RECOMMENDATION

**Implement Phase 0-2 immediately (1 week total):**

**TODAY (2 hours):**
- Fix SheetSync + SheetSanitizer (catalogo.json source)
- Run orchestrator with 62 products
- Generate validation report

**THIS WEEK:**
- LocalhostProductionValidator-Agent (CRITICAL)
- ProductPhotoValidator-Agent
- IfthenPay-Agent (can't sell without it!)
- CTT-Agent (can't ship without it!)
- CookieYes-Agent (legal requirement)

**Result after 1 week:**
- ✅ 62 products live
- ✅ Can accept orders
- ✅ RGPD compliant
- ✅ Localhost/production validated
- ✅ Photos verified

**Then gradually add:** Flatsome, WPRocket, WPML, remaining validators over 2 weeks

---

**Next step:** Proceed with Phase 0 (adapt SheetSync)?

---

**Generated by:** Claude Code (Ultra-Think Mode)
**For:** Bilal / AiParaTi
**Cliente:** Chapéus Lisboeta (Tiago Andrade)
**Architecture:** 32-agent orchestrator with 3-layer validation
**Mission:** "Never lose visual consistency between localhost and production again"
