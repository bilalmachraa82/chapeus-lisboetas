# TESTING GUIDE - Hero Section & Product Grid Fixes

## QUICK VISUAL TEST (5 minutes)

### 1. HERO SECTION TEST

**Open:** http://localhost:8080

**What to look for:**

Desktop (>768px):
- [ ] Two buttons side-by-side: "Descobrir Coleção" | "Nossa História"
- [ ] ~16px gap between buttons
- [ ] No overlapping text or buttons
- [ ] Clean hover effects (buttons lift up on hover)

Mobile (<768px):
- [ ] Buttons stack vertically (one above the other)
- [ ] Each button full width
- [ ] Clear touch targets (minimum 48px height)

**Expected behavior:**
```
DESKTOP VIEW:
┌─────────────────────────────────────────┐
│                                         │
│        Chapéus Lisboetas                │
│   Elegância à cabeça, tradição...       │
│                                         │
│  [Descobrir Coleção] [Nossa História]  │  ← Side by side
│                                         │
└─────────────────────────────────────────┘

MOBILE VIEW:
┌───────────────────┐
│                   │
│ Chapéus Lisboetas │
│                   │
│ [Descobrir...]    │  ← Stacked
│ [Nossa História]  │  ← Stacked
│                   │
└───────────────────┘
```

---

### 2. PRODUCT GRID TEST

**Open:** http://localhost:8080/shop/

**What to look for:**

Product Images:
- [ ] All images perfectly square (1:1 ratio)
- [ ] Images centered in containers
- [ ] No distortion or stretching
- [ ] Consistent sizing across all products

Product Cards:
- [ ] Equal height boxes
- [ ] Aligned titles
- [ ] Consistent spacing (24px gap)
- [ ] Grid layout (3 cols desktop, 2 tablet, flexible mobile)

Hover Effects:
- [ ] Card lifts up slightly on hover
- [ ] Image zooms in smoothly
- [ ] No layout shift

**Expected layout:**
```
DESKTOP (3 columns):
┌────────┐  ┌────────┐  ┌────────┐
│ [IMG]  │  │ [IMG]  │  │ [IMG]  │  ← Square images
│ Title  │  │ Title  │  │ Title  │  ← Equal heights
│ Price  │  │ Price  │  │ Price  │
└────────┘  └────────┘  └────────┘
```

---

## DETAILED BROWSER TESTING

### Chrome DevTools Test

1. Open http://localhost:8080
2. Press F12 (DevTools)
3. Toggle device toolbar (Ctrl+Shift+M / Cmd+Shift+M)
4. Test breakpoints:
   - 1920px (Desktop large)
   - 1024px (Desktop small)
   - 768px (Tablet)
   - 480px (Mobile large)
   - 375px (iPhone)
   - 360px (Android)

**What to check at each breakpoint:**
- Hero buttons alignment (horizontal vs vertical)
- Product grid columns (3 → 2 → flexible)
- No horizontal scroll
- Readable text sizes

---

### Firefox Test

1. Open http://localhost:8080 in Firefox
2. Press F12 → Responsive Design Mode
3. Test same breakpoints as Chrome
4. Verify aspect-ratio CSS support (Firefox 88+)

---

### Safari Test (Mac only)

1. Open http://localhost:8080 in Safari
2. Develop → Enter Responsive Design Mode
3. Test iOS device presets (iPhone 12, iPad)
4. Verify -webkit prefixes work correctly

---

## SPECIFIC PAGE TESTS

### Homepage
- URL: http://localhost:8080
- Focus: Hero section CTAs

### Shop Archive
- URL: http://localhost:8080/shop/
- Focus: Product grid layout

### Category Pages
- URL: http://localhost:8080/product-category/boinas/
- Focus: Filtered products maintain grid

### Single Product
- URL: Any product page
- Focus: Related products grid at bottom

---

## CSS VALIDATION

### Chrome DevTools Inspector

1. Right-click on hero section → Inspect
2. Check computed styles for `.text-box a.button`:
   ```
   display: inline-flex
   margin: 8px
   min-height: 52px
   padding: 16px 32px
   ```

3. Right-click on product image → Inspect
4. Check computed styles for `.product-small .box-image img`:
   ```
   aspect-ratio: 1 / 1
   object-fit: cover
   object-position: center
   ```

---

## REGRESSION TESTS (What NOT to break)

- [ ] Navigation menu still works
- [ ] Cart functionality intact
- [ ] Product filtering/sorting operational
- [ ] Mobile menu toggle working
- [ ] Footer layout unchanged
- [ ] Other pages (About, Contact) not affected

---

## PERFORMANCE CHECK

### PageSpeed Insights (optional)
Not applicable for localhost, but on production:
- Target: >85 mobile, >90 desktop
- Watch for: Layout Shift (CLS), Largest Contentful Paint (LCP)

### Lighthouse Audit (Chrome)
1. F12 → Lighthouse tab
2. Generate report (Desktop + Mobile)
3. Check:
   - Performance: Should remain stable
   - Accessibility: Should be 90+
   - Best Practices: Should be 90+

---

## TROUBLESHOOTING

### Issue: Buttons still overlapping

**Check:**
1. Hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)
2. Clear browser cache
3. Verify CSS file was updated:
   ```bash
   cat /Users/bilal/Programaçao/Tiago\ Andrado/full-chapeus-lisboetas\ \(2\)/wordpress/wp-content/themes/flatsome-child/style.css | grep "text-box a.button"
   ```
4. Check WordPress cache:
   ```bash
   docker exec chapeus_wordpress bash -c "cd /var/www/html && wp cache flush --allow-root"
   ```

### Issue: Product images not square

**Solutions:**
1. Regenerate thumbnails (see below)
2. Check if aspect-ratio is supported (requires modern browser)
3. Fallback: Check object-fit in DevTools

**Regenerate command:**
```bash
docker exec chapeus_wordpress bash -c "cd /var/www/html && wp plugin install regenerate-thumbnails --activate --allow-root && wp media regenerate --yes --allow-root"
```

### Issue: Mobile layout broken

**Check:**
1. Viewport meta tag exists:
   ```bash
   curl -s http://localhost:8080 | grep viewport
   ```
   Should return: `<meta name="viewport" content="width=device-width, initial-scale=1">`

2. Media query syntax in CSS file (line 169)

---

## AUTOMATED TEST SCRIPT (Optional)

Create file: `test_layout.js`

```javascript
// Puppeteer test script
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Test desktop
  await page.setViewport({ width: 1920, height: 1080 });
  await page.goto('http://localhost:8080');

  const buttonCount = await page.$$eval('.text-box a.button', buttons => buttons.length);
  console.log(`Desktop: Found ${buttonCount} buttons`);

  // Test mobile
  await page.setViewport({ width: 375, height: 667 });
  await page.reload();

  const buttonsStacked = await page.evaluate(() => {
    const buttons = document.querySelectorAll('.text-box a.button');
    return buttons[0].offsetTop !== buttons[1].offsetTop;
  });

  console.log(`Mobile: Buttons stacked: ${buttonsStacked}`);

  await browser.close();
})();
```

Run: `node test_layout.js`

---

## SIGN-OFF CHECKLIST

Before marking as complete:

- [ ] Hero CTAs horizontally aligned on desktop
- [ ] Hero CTAs stacked on mobile (<768px)
- [ ] All product images are square (1:1)
- [ ] Product images centered in containers
- [ ] Equal height product cards
- [ ] Hover effects working smoothly
- [ ] No layout regressions on other pages
- [ ] Tested in 3+ viewports (desktop, tablet, mobile)
- [ ] Tested in 2+ browsers (Chrome, Firefox/Safari)
- [ ] Client-facing pages working (shop, categories, single product)

---

**Testing environment:**
- Local URL: http://localhost:8080
- Admin: http://localhost:8080/wp-admin
- Database: http://localhost:8081 (phpMyAdmin)

**Support files:**
- Fix report: `CHAPEUS_FIX_REPORT.md`
- Modified CSS: `wordpress/wp-content/themes/flatsome-child/style.css`
