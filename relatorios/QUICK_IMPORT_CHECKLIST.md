# QUICK CSV IMPORT CHECKLIST

**Date:** 2025-11-10
**Status:** Image registration in progress → CSV import next

---

## ✅ STEP 1: IMAGE REGISTRATION (In Progress)

**Command:** `python3 scripts/register_images_to_wordpress.py`

**Expected:**
- Process 918 image files
- Skip images already in library
- Register new images with WordPress attachment IDs
- Duration: 10-15 minutes

**Verification:**
```bash
# Check media library count
docker exec chapeus_wordpress wp post list --post_type=attachment --format=count --allow-root

# Should show: 900+ images
```

---

## 📋 STEP 2: CSV IMPORT VIA WOOCOMMERCE

### Access WordPress Admin

1. Open browser: **http://localhost:8080/wp-admin**
2. Login credentials:
   - Username: `lisboetas`
   - Email: `mail@chapeuslisboetas.com`
   - Password: (check database or reset)

### Import Products

1. **Navigate:** WooCommerce → Products
2. **Click:** "Import" button (top of page)
3. **Upload CSV:**
   - Click "Choose File"
   - Select: `output_catalogo/woocommerce_import.csv`
   - Click "Continue"

4. **Column Mapping:**
   - Most columns auto-map correctly
   - Verify critical mappings:
     - `SKU` → `SKU`
     - `Name` → `Name`
     - `Regular price` → `Regular price`
     - `Images` → `Images`
     - `Categories` → `Categories`

5. **Import Options:**
   - ☑ **Update existing products** (if SKU matches)
   - ☐ Skip existing products
   - Click "Run the importer"

6. **Wait for Completion:**
   - Progress bar will show
   - 72 products @ ~5-10 seconds each
   - Total: **6-12 minutes**

7. **Review Results:**
   - Imported: X products
   - Updated: Y products
   - Skipped: Z products
   - Failed: 0 (ideally)

---

## 🔍 STEP 3: VERIFICATION

### Check Product Count

```bash
# Total products
docker exec chapeus_wordpress wp wc product list --format=count --allow-root
# Expected: ~202 (130 existing + 72 new/updated)

# Products with images
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "SELECT COUNT(*) FROM lx_posts p
      JOIN lx_postmeta pm ON p.ID=pm.post_id
      WHERE p.post_type='product' AND pm.meta_key='_thumbnail_id';"
# Expected: ~202 (all should have featured images)
```

### Manual Checks

1. **Visit shop page:** http://localhost:8080/shop
   - Products display correctly?
   - Images show?
   - Prices visible?

2. **Check individual products:**
   - Click a few products
   - Image gallery works? (avg 10.6 images)
   - Description formatted?
   - Add to cart button visible?

3. **Verify categories:**
   - http://localhost:8080/product-category/chapeus/
   - Categories assigned correctly?
   - Hierarchy: Chapéus > Boinas > Inverno

4. **Check problematic products:**
   - bone-18106mi (should have 29 images)
   - bob-2018121 (should have 16 images)
   - gorro-miki-12601 (should have 38 images)

---

## ⚠️ TROUBLESHOOTING

### Issue: Images not linking to products

**Symptoms:** Products show but no featured image

**Cause:** Image URLs in CSV don't match WordPress media library

**Fix:**
```bash
# Option 1: Update image URLs in CSV to absolute paths
# Change: catalogo2025/... → http://localhost:8080/wp-content/uploads/products/...

# Option 2: Use Media from FTP plugin
docker exec chapeus_wordpress wp plugin install add-from-server --activate --allow-root

# Then import images from /wp-content/uploads/products/
```

### Issue: Duplicate products created

**Symptoms:** Product count higher than expected

**Cause:** SKU matching failed

**Fix:**
```bash
# Find duplicates
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "SELECT meta_value, COUNT(*) FROM lx_postmeta
      WHERE meta_key='_sku' GROUP BY meta_value HAVING COUNT(*) > 1;"

# Delete recent imports and retry
docker exec chapeus_wordpress wp post delete $(docker exec chapeus_wordpress wp post list --post_type=product --post_status=publish --format=ids --allow-root | tail -72) --force --allow-root
```

### Issue: Categories not assigned

**Symptoms:** Products in "Uncategorized"

**Cause:** Category names don't match existing categories

**Fix:**
- Go to Products → Categories
- Check category names match CSV exactly
- Re-import with correct category names

---

## 📊 EXPECTED RESULTS

After successful import:

```
Products: ~202 total
  ├─ 130 existing (from original backup)
  └─ 72 new/updated (from CSV)

Images: 900+ in media library

Categories:
  ├─ Chapéus
  │   ├─ Boinas > Inverno (24 products)
  │   ├─ Boinas > Verão (12 products)
  │   ├─ Panamá (5 products)
  │   └─ Cowboy (10 products)
  ├─ Acessórios
  │   ├─ Gorros (5 products)
  │   └─ Luvas (2 products)
  └─ Other categories...

Avg images per product: 10.6
Products with galleries: 72 (100%)
```

---

## 🚀 NEXT STEPS AFTER IMPORT

1. **Client review:**
   - Show imported products
   - Get feedback on descriptions/images
   - Decision on 14 products without photos

2. **Security upgrades (CRITICAL):**
   - PHP 7.4 → 8.1
   - WordPress 5.4.1 → 6.4
   - Test in staging first
   - Deploy to production

3. **Payment gateway:**
   - Configure IfthenPay
   - Test MB Way + Multibanco
   - Sandbox testing

4. **Shipping integration:**
   - CTT Expresso setup
   - Label generation
   - Tracking emails

5. **RGPD compliance:**
   - CookieYes banner
   - Privacy policy
   - Terms & conditions

6. **SEO configuration:**
   - Yoast meta data
   - XML sitemaps
   - Schema markup
   - Google Analytics 4

7. **Performance:**
   - WP Rocket caching
   - Image compression
   - CDN setup (PTisp)

---

## 🔄 ROLLBACK (If Needed)

```bash
# Stop WordPress
docker stop chapeus_wordpress

# Restore database backup
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < backup_pre_import.sql

# Restart
docker start chapeus_wordpress

# Verify rollback
docker exec chapeus_wordpress wp wc product list --format=count --allow-root
# Should show: 130 (original count)
```

---

**Timeline:**
- Image registration: 10-15 min (in progress)
- CSV import: 6-12 min (next)
- Verification: 15-20 min (final)
- **Total: ~45 minutes**

**Black Friday:** 19 days remaining ✅

**Prepared:** 2025-11-10 09:30
