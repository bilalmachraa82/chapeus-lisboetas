# WORDPRESS/WOOCOMMERCE IMPORT GUIDE

**Date:** 2025-11-10 09:01
**Branch:** ux-improvements-fase1-p0
**Status:** Ready for import (all prerequisites completed)

---

## PRE-IMPORT STATUS

### Catalog Ready
- **72 products** with complete image galleries (83.7% of catalog)
- **766 images** total (10.6 avg per product)
- **113MB** total image size
- **14 products** without images (pending client decision)

### Files Prepared
- ✅ `output_catalogo/woocommerce_import.csv` (192 lines, 98KB)
- ✅ `output_catalogo/images/` (918 files organized by category/SKU)
- ✅ Database backup: `backup_pre_import.sql` (48MB)
- ✅ Images uploaded to WordPress: `/wp-content/uploads/products/`

### WordPress Environment
- ✅ Docker containers running (WordPress + MySQL + phpMyAdmin)
- ✅ WordPress accessible: http://localhost:8080
- ✅ Admin panel: http://localhost:8080/wp-admin
- ✅ Database: lisboetas_web (130 existing products, 142 with images)
- ✅ Permissions set: www-data:www-data on all images

---

## IMPORT STEPS

### Step 1: Verify Environment

```bash
# Check Docker status
docker ps --filter "name=chapeus"

# Verify images uploaded
docker exec chapeus_wordpress find /var/www/html/wp-content/uploads/products -type f | wc -l
# Should show: 918

# Test WordPress access
curl -s http://localhost:8080 | grep -i "chapéus" && echo "✓ Site accessible"
```

### Step 2: Access WordPress Admin

1. Open browser: http://localhost:8080/wp-admin
2. Login credentials:
   - **User:** lisboetas
   - **Email:** mail@chapeuslisboetas.com
   - **Password:** (check database or use password reset)

Alternative users:
- vm (pb@virtualmente.pt)
- well (wellcardoso.pt@gmail.com)

### Step 3: Import Products via WooCommerce

#### Option A: WooCommerce CSV Importer (Recommended)

1. **Navigate:** WooCommerce → Products → Import
2. **Upload CSV:** Select `output_catalogo/woocommerce_import.csv`
3. **Column Mapping:**
   - ID → ID (for updates)
   - Type → Type (simple/variable)
   - SKU → SKU
   - Name → Name
   - Published → Published
   - Categories → Categories
   - Tags → Tags
   - Short description → Short description
   - Description → Description
   - Images → Images (comma-separated URLs)
   - Regular price → Regular price
   - Sale price → Sale price
   - Stock → Stock quantity
   - Meta: _fabric → Composição
   - Meta: _color → Cor

4. **Update existing products:** Select "Update existing products" if SKU matches
5. **Run Import:** Click "Run the importer"
6. **Wait:** ~72 products @ 5-10 seconds each = 6-12 minutes

#### Option B: WP-CLI (Faster, Advanced)

```bash
# Copy CSV to container
docker cp output_catalogo/woocommerce_import.csv chapeus_wordpress:/tmp/

# Import via WP-CLI
docker exec chapeus_wordpress wp wc product import /tmp/woocommerce_import.csv \
  --user=lisboetas \
  --allow-root

# Check imported products
docker exec chapeus_wordpress wp wc product list --format=count --allow-root
```

### Step 4: Register Images in Media Library

The images are uploaded but not registered in WordPress media library. Two approaches:

#### Option A: Media Library Import Plugin

1. Install plugin: **Media from FTP** or **Add From Server**
2. Scan `/wp-content/uploads/products/`
3. Import all 918 images to media library
4. Images will get proper WordPress IDs

#### Option B: Manual Script (Python + WordPress API)

```bash
# Use provided script to register images
python3 scripts/register_images_to_wordpress.py
```

### Step 5: Verify Import

```bash
# Check product count
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "SELECT COUNT(*) FROM lx_posts WHERE post_type='product' AND post_status='publish';"

# Check products with images
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "SELECT COUNT(*) FROM lx_posts p JOIN lx_postmeta pm ON p.ID=pm.post_id
      WHERE p.post_type='product' AND pm.meta_key='_thumbnail_id';"

# List imported products
docker exec chapeus_wordpress wp wc product list \
  --fields=id,name,sku,price,images \
  --format=table \
  --allow-root | head -20
```

---

## IMAGE URL MAPPING

Images in CSV use relative paths like:
```
images/boinas inverno/bone-22182/img_01.jpg
```

After import, WordPress needs absolute URLs:
```
http://localhost:8080/wp-content/uploads/products/boinas inverno/bone-22182/img_01.jpg
```

The WooCommerce importer will automatically:
1. Download images from URLs (if provided as full URLs)
2. OR find images in media library (if already uploaded)
3. Associate with products

**Important:** If images don't appear, you may need to:
- Update CSV to use full URLs: `http://localhost:8080/wp-content/uploads/products/...`
- Or import images to media library first (Step 4)

---

## TROUBLESHOOTING

### Issue: Images not showing after import

**Cause:** Images uploaded but not registered in media library

**Fix:**
```bash
# Option 1: Install Media from FTP plugin
docker exec chapeus_wordpress wp plugin install add-from-server --activate --allow-root

# Option 2: Re-generate thumbnails
docker exec chapeus_wordpress wp media regenerate --yes --allow-root
```

### Issue: Duplicate products created

**Cause:** SKU matching failed, created new products instead of updating

**Fix:**
```bash
# Find duplicates
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "SELECT meta_value as sku, COUNT(*) as count FROM lx_postmeta
      WHERE meta_key='_sku' GROUP BY meta_value HAVING count > 1;"

# Delete test imports
docker exec chapeus_wordpress wp post delete $(docker exec chapeus_wordpress wp post list --post_type=product --format=ids --allow-root) --force --allow-root
```

### Issue: Import timeout/fails

**Cause:** Large CSV or slow server

**Fix:**
```bash
# Increase PHP timeout
docker exec chapeus_wordpress bash -c "echo 'max_execution_time = 600' >> /usr/local/etc/php/conf.d/custom.ini"
docker restart chapeus_wordpress

# Or split CSV into smaller batches
split -l 25 output_catalogo/woocommerce_import.csv batch_
# Import each batch separately
```

### Issue: Permission denied on images

**Cause:** Wrong file ownership

**Fix:**
```bash
docker exec chapeus_wordpress chown -R www-data:www-data /var/www/html/wp-content/uploads/
```

---

## POST-IMPORT VERIFICATION CHECKLIST

- [ ] Product count matches expected (130 existing + 72 new = 202 or 72 updated)
- [ ] All products have featured images
- [ ] Product galleries show multiple images (avg 10.6 per product)
- [ ] Categories assigned correctly (Boinas Inverno, Boinas Verão, etc.)
- [ ] Prices display correctly (EUR format)
- [ ] SKUs unique and match supplier codes
- [ ] Short descriptions present
- [ ] Long descriptions formatted properly
- [ ] Stock status set (in stock/out of stock)
- [ ] Images load without 404 errors
- [ ] Mobile responsive image display
- [ ] No PHP errors in WordPress debug log

---

## NEXT STEPS AFTER IMPORT

### 1. Review 14 Products Without Images

**Medium/High Value (request client photos):**
- bone-22174 (€29.90) - BOINA OITAVADA HARRINGBONE
- casquette-18534n (€37.50) - Boina verão Itália
- chapeu-australiano (€67.50) - CHAPEU AUSTRALIANO ⭐ HIGH VALUE
- chapeu-colonial-pith-helmet (€45.00) - CHAPEU COLONIAL
- chapeu-cloche (€35.00) - CHAPEU CLOCHE
- solid (€19.90) - CHAPÉU UV
- bucket-hat-reversivel (€19.90) - BUCKET HAT

**Low Value/Invalid (recommend removal):**
- palha-12403 (€3.00) - Chapéus palha
- bone-2018016 (INVALID) - Bonés verão
- casquete (€1.00) - Casquete
- chapeu-cerimonia-perolas (€2.00) - Cerimónia perólas
- chapeu-cerimonia-flores (€3.00) - Cerimónia flores
- chapeu-cowboy (€2.00) - Chapéu cowboy
- velen (N/A) - VELEN (404 error)

### 2. Test Product Pages

Visit a few product pages to verify:
- http://localhost:8080/product/boina-bico-de-pato-ajustavel/
- http://localhost:8080/product/bob-bucket-hat/
- Check image galleries, pricing, descriptions

### 3. Category Review

Ensure category hierarchy correct:
- Chapéus > Boinas > Inverno
- Chapéus > Boinas > Verão
- Chapéus > Panamá
- Acessórios > Gorros
- Acessórios > Luvas

### 4. SEO Meta Data

Add via Yoast SEO (if installed):
- Meta titles
- Meta descriptions
- Focus keyphrases
- Schema markup (Product type)

### 5. Enable Cache

After verifying everything works:
```bash
# Install WP Rocket or WP Super Cache
docker exec chapeus_wordpress wp plugin install wp-super-cache --activate --allow-root

# Configure caching rules
```

---

## ROLLBACK PROCEDURE (If Needed)

If import fails or causes issues:

```bash
# Stop WordPress
docker stop chapeus_wordpress

# Restore database
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
docker exec -i chapeus_mysql mysql -u root -prootpassword lisboetas_web < backup_pre_import.sql

# Restart WordPress
docker start chapeus_wordpress

# Verify restoration
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "SELECT COUNT(*) FROM lx_posts WHERE post_type='product';"
```

---

## TECHNICAL NOTES

### Database Structure
- **Table prefix:** `lx_` (not standard `wp_`)
- **Products table:** `lx_posts` (post_type='product')
- **Meta data:** `lx_postmeta` (product specs, images, pricing)
- **Product images:** `_thumbnail_id` meta key (featured image)
- **Gallery images:** `_product_image_gallery` meta key (comma-separated IDs)

### Image Organization
```
wp-content/uploads/products/
├── artigos em pele/
├── boinas inverno/
│   ├── bone-22182/
│   │   ├── img_01.jpg
│   │   ├── img_02.jpg
│   │   └── ...
│   ├── bone-25025/
│   └── ...
├── boinas verão/
├── bonés/
├── cerimónia/
└── ...
```

### CSV Format
WooCommerce expects specific column names:
- `ID` - Product ID (for updates)
- `Type` - simple, variable, grouped, external
- `SKU` - Unique product identifier
- `Name` - Product title
- `Published` - 1 (publish), 0 (draft), -1 (private)
- `Images` - Comma-separated URLs or media library IDs
- `Categories` - Pipe-separated category hierarchy: "Chapéus > Boinas > Inverno"
- `Regular price` - Numeric (no currency symbol)
- `Stock` - Quantity or blank for unlimited

---

## BACKUP STRATEGY

**Current Backup:**
- File: `backup_pre_import.sql` (48MB)
- Date: 2025-11-10 08:59
- Products: 130 existing products before import
- Location: Project root

**Post-Import Backup:**
```bash
# Create backup after successful import
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web \
  > backup_post_import_$(date +%Y%m%d).sql
```

**PTisp Hosting Backups:**
- Automatic daily backups for 30 days (JetBackup)
- 1-click restore available
- Contact: PTisp 24/7 support

---

## PERFORMANCE OPTIMIZATION

After import, optimize for speed:

### 1. Image Optimization
```bash
# Install image optimization plugin
docker exec chapeus_wordpress wp plugin install ewww-image-optimizer --activate --allow-root

# Bulk optimize
docker exec chapeus_wordpress wp ewww-image-optimizer optimize all --allow-root
```

### 2. Database Optimization
```bash
# Optimize database tables
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web \
  -e "OPTIMIZE TABLE lx_posts, lx_postmeta, lx_options;"
```

### 3. Enable CDN
- Configure Cloudflare or PTisp CDN
- Point to wp-content/uploads/products/

### 4. Lazy Loading
- Enable native WordPress lazy loading (built-in 5.5+)
- Or use plugin: Lazy Load by WP Rocket

---

## SUCCESS METRICS

**Target KPIs (post-import):**
- Product count: 200+ (130 existing + 72 validated new)
- Products with images: >95%
- Avg images per product: 10.6
- Image load time: <2 seconds
- Page speed: >85 mobile, >90 desktop
- Zero 404 errors
- Product page bounce rate: <60%

**Tracking:**
- Google Analytics 4: E-commerce tracking
- Search Console: Product page indexing
- WooCommerce Analytics: Sales by product

---

## SUPPORT CONTACTS

**Technical Issues:**
- Bilal/AiParaTi: 3 months support included
- WordPress.org forums: https://wordpress.org/support/
- WooCommerce docs: https://woocommerce.com/documentation/

**Hosting Issues:**
- PTisp support: 24/7 phone (check client portal)
- JetBackup restore: 1-click via cPanel

**Emergency Rollback:**
- Database restore: See "ROLLBACK PROCEDURE" above
- Contact Bilal immediately

---

## TIMELINE

**Estimated Duration:**
- CSV import: 6-12 minutes (72 products)
- Image registration: 10-15 minutes (918 files)
- Verification: 15-20 minutes
- Total: ~45 minutes

**Black Friday Deadline:**
- Today: 2025-11-10
- Black Friday: 2025-11-29 (19 days)
- Time buffer: Comfortable ✅

---

**Prepared by:** Claude Code (Sonnet 4.5)
**Executed:** 533px resolution fix + image upload
**Status:** Ready for WooCommerce import
**Next:** Execute import steps above

**Report generated:** 2025-11-10 09:01
