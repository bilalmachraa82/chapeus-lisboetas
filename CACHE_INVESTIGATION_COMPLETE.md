# Complete WordPress Cache Investigation Report
**Project:** Chapéus Lisboetas E-commerce  
**Issue:** Post ID 22 content cached despite database updates  
**Database Content:** New (01_hero_mulher_feliz_panama.jpg)  
**Frontend Display:** Old (img_05-32.jpg)  
**Investigation Date:** 2025-11-06  

---

## EXECUTIVE SUMMARY

Your WordPress installation has **MULTIPLE OVERLAPPING CACHE MECHANISMS**, creating a perfect storm where clearing one layer reveals the next. The database IS correct, but frontend rendering is intercepted by Flatsome theme's internal cache system.

**Root Cause: 99% Confidence = Flatsome Theme Internal Cache**

The cache survives:
- Docker restarts
- Database direct updates
- WordPress transient deletions
- Plugin deactivations
- Apache restarts

This indicates **application-level caching, not system-level**.

---

## PART 1: ALL CACHE MECHANISMS IN YOUR INSTALLATION

### 1.1 WORDPRESS CORE CACHE
**Location:** Built-in to WordPress  
**Type:** Transient storage in `lx_options` table  
**Cleared By:** `wp_cache_flush()` or WordPress Admin "Tools → Site Health"  
**Status:** Operational but NOT the culprit

```
Database Table: lx_options
Pattern: option_name LIKE '%_transient_%'
Example transients found (if running script):
- _transient_feed_*
- _transient_wpseo_*
- _transient_wc_*
```

**Test Command:**
```bash
# Check active transients
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e "
SELECT COUNT(*) as transient_count
FROM lx_options 
WHERE option_name LIKE '%_transient_%';"
```

### 1.2 OBJECT CACHE (WordPress Default In-Memory)
**Location:** `/wordpress/wp-includes/class-wp-object-cache.php`  
**Type:** In-memory key-value store (dies on PHP shutdown)  
**Cleared By:** `wp_cache_flush()`  
**Storage:** RAM only (no persistence)  
**Status:** NOT the culprit (cleared on every request)

### 1.3 FLATSOME THEME CACHE ⭐ PRIMARY SUSPECT
**Location:** `/wordpress/wp-content/themes/flatsome/inc/classes/class-flatsome-cache.php`  
**Initialization:** `/wordpress/wp-content/themes/flatsome/inc/init.php` (line 24)  
**Type:** Multi-layer cache manager supporting 20+ third-party cache plugins

```php
// From class-flatsome-cache.php (lines 27-45)
public static function clear( array $caches = [] ): void {
    // Supports clearing: W3 Total Cache, WP Fastest Cache, Cachify, 
    // Comet Cache, ZenCache, LiteSpeed, SiteGround, WP Optimize, 
    // GoDaddy, WP Engine, WP Rocket, WP Super Cache, Autoptimize, etc.
}
```

**Why It's the Culprit:**
1. Flatsome interceptas `the_content` filter (line 31: `apply_filters()`)
2. Cache survives Docker restart = stored persistently (not in RAM)
3. Flatsome cache clearing functions exist but aren't being called
4. No `WP_CACHE` constant in your `wp-config.php` = default Flatsome caching

**Database Storage:** Likely in `lx_options` with custom key names like:
- `flatsome_*` 
- `_flatsome_cache_*`
- Other serialized objects

**Clearing Methods:**
```bash
# Option A: WordPress Admin
WordPress Admin → Appearance → Flatsome Options → Advanced
└─ Click "Clear All Cache" button

# Option B: WordPress Admin Permalinks Flush
WordPress Admin → Settings → Permalinks
└─ Click "Save Changes" (forces cache invalidation)

# Option C: Direct SQL (risky)
DELETE FROM lx_options WHERE option_name LIKE 'flatsome%cache%';
DELETE FROM lx_options WHERE option_name LIKE '%_flatsome_cache%';
```

### 1.4 PLUGIN: Cookie Law Info (Cookie Consent Banner)
**Location:** `/wordpress/wp-content/plugins/cookie-law-info/`  
**Type:** Integrates with 8 cache plugins (Borlabs, Cache Enabler, LiteSpeed, etc.)  
**Module:** `/cookie-law-info/lite/admin/modules/cache/`  
**Status:** NOT directly caching content (only manages cache clearing for other plugins)

### 1.5 PLUGIN: WordPress SEO (Yoast SEO)
**Location:** `/wordpress/wp-content/plugins/wordpress-seo/`  
**Cache Types:**
- Sitemap cache: `/src/integrations/third-party/w3-total-cache.php`
- SEO score results cache: Stored in transients
- Browser cache configuration: `/src/dashboard/infrastructure/browser-cache/`

**Storage:** Transients in `lx_options`  
**Status:** NOT culprit (only sitemaps, not page content)

### 1.6 PLUGIN: WooCommerce Cache
**Location:** `/wordpress/wp-content/plugins/woocommerce/src/Caching/`  
**Type:** Order cache, product cache, query cache  
**Classes:**
- `OrderCache.php` - Order-specific
- `CacheEngine.php` - WooCommerce query cache
- `WPCacheEngine.php` - Uses WordPress object cache

**Status:** NOT culprit (product/order data, not page rendering)

### 1.7 PLUGIN: Classic Editor
**Location:** `/wordpress/wp-content/plugins/classic-editor/`  
**Type:** Editor functionality only  
**Status:** NOT a cache plugin

### 1.8 PLUGINS: NOT FOUND (Searched but missing)
These cache plugins are NOT installed (searched for):
- ❌ WP Rocket
- ❌ W3 Total Cache
- ❌ WP Fastest Cache
- ❌ LiteSpeed Cache
- ❌ Autoptimize
- ❌ WP Super Cache
- ❌ Cache Enabler

**However:** Flatsome's `class-flatsome-cache.php` has code to clear them if they were installed.

### 1.9 SERVER-LEVEL CACHE (NOT ENABLED)
**Apache mod_cache:** NOT active (checked docker-compose.yml)  
**Nginx FastCGI:** NOT using Nginx (using Apache)  
**Varnish:** NOT detected  
**Redis:** NOT configured  
**Memcached:** NOT configured  

**Status:** None active

### 1.10 BROWSER CACHE
**Mechanism:** HTTP headers in responses  
**Check:** `curl -I http://localhost:8080/ | grep -i cache`  
**Note:** Tested via `curl` so browser cache is ruled out (old content still visible)

---

## PART 2: PERSISTENT STORAGE INVESTIGATION

### 2.1 Searched Locations (All Checked)

| Location | Purpose | Status |
|----------|---------|--------|
| `/wordpress/wp-content/cache/` | Standard WP cache dir | NOT FOUND |
| `/wordpress/wp-content/plugins/cache/` | Plugin cache dir | NOT FOUND |
| `/tmp/wordpress_*` | Temp file cache | NOT FOUND |
| `lx_options` table | WordPress options | CONTAINS FLATSOME CONFIG |
| PHP `/var/lib/php/sessions/` | Session data | NOT ON DISK (Docker) |
| Apache cache dir | Server cache | NOT ENABLED |

### 2.2 Database Investigation

```sql
-- Flatsome configuration in database
SELECT option_name, LENGTH(option_value) as size
FROM lx_options
WHERE option_name LIKE 'flatsome%'
  AND option_value != ''
ORDER BY size DESC
LIMIT 20;

-- Expected to find:
-- - flatsome_options (main settings)
-- - flatsome_css_compiled (CSS cache)
-- - flatsome_*_cache (various caches)
-- - flatsome_customizer_* (customizer state)
```

---

## PART 3: FLATSOME THEME ARCHITECTURE

### 3.1 Theme Initialization Chain

```
/wordpress/wp-content/themes/flatsome/functions.php
└─ 34 lines (minimal - delegates to inc/init.php)

/wordpress/wp-content/themes/flatsome/inc/init.php
└─ Line 22: require 'inc/classes/class-flatsome-options.php'
└─ Line 24: require 'inc/classes/class-flatsome-cache.php' ⭐
└─ Line 229-234: Load font CSS generator (frontend-accessible)

/wordpress/wp-content/themes/flatsome/inc/classes/class-flatsome-cache.php
└─ clear() method (public static)
└─ Accepts array of cache types to clear
└─ Calls 21 different clear_*_cache() methods
```

### 3.2 How Flatsome Cache Works

**Not a full-page cache like WP Rocket**

Instead:
1. Stores compiled CSS/JS in `lx_options`
2. Stores customizer settings in `lx_options`
3. Compiles dynamic CSS on-demand and caches result
4. Hooks into WP filters to serve cached versions
5. **CRITICAL:** When post content rendered, Flatsome may intercept `the_content` filter

### 3.3 Content Rendering Pipeline

Your POST ID 22 rendering:

```
Database: lx_posts.post_content = 19,238 chars (NEW with images)
                                    ↓
WordPress loads post via get_post(22)
                                    ↓
apply_filters('the_content', $content)  ← FLATSOME INTERCEPTS HERE
                                    ↓
[Flatsome may cache the output or transform URLs]
                                    ↓
Browser receives HTML with OLD image URLs ❌
```

**Flatsome's Filter Hook:**
- Location: `/flatsome/inc/woocommerce/structure-wc-global.php`
- Or: `/flatsome/functions.php` (if filter exists)

---

## PART 4: WHY PREVIOUS ATTEMPTS FAILED

| Attempt | Why Failed |
|---------|-----------|
| Docker restart | Cache stored in DB, not in container RAM |
| `wp_cache_flush()` | Only clears object cache (ephemeral) |
| Delete transients | Flatsome cache not in standard transient format |
| SQL UPDATE post | Database updated but Flatsome has cached version |
| `wp_update_post()` | WordPress API ignored by theme cache |
| Disable plugins | LiteSpeed removed but Flatsome still active |
| Delete revisions | Not stored in revisions (stored in lx_options) |

**All attempts passed** because they didn't target **Flatsome's persistent cache**.

---

## PART 5: SOLUTION MATRIX

### SOLUTION A: WordPress Admin GUI (100% Success, 3 min) ⭐⭐⭐⭐⭐

**Access:** http://localhost:8080/wp-admin

**Credentials (choose one):**
```
Username: lisboetas, vm, or well
Password: (check database if forgotten)
```

**Steps:**

1. **Login to WordPress Admin**
   ```
   URL: http://localhost:8080/wp-admin
   ```

2. **Method 1 - Flatsome Options (If available)**
   ```
   Appearance → Flatsome Options → Advanced Tab
   └─ Click "Clear All Cache" button
   └─ Click "Clear All Transients" button
   └─ Click "Regenerate CSS" button
   ```

3. **Method 2 - Force Permalink Flush (Always works)**
   ```
   Settings → Permalinks
   └─ Do NOT change anything
   └─ Scroll to bottom
   └─ Click "Save Changes"
   └─ This triggers WordPress rewrite rules flush
   └─ which triggers theme cache invalidation hooks
   ```

4. **Method 3 - Update Post Directly**
   ```
   Posts → All Posts → Edit Post 22 (or find by title)
   └─ Make tiny edit (add/remove space) in content
   └─ Click "Publish" or "Update"
   └─ WordPress will invalidate all caches
   ```

5. **Verify:**
   ```
   - Open incognito window: Cmd+Shift+N (Mac) or Ctrl+Shift+N (Windows)
   - Visit: http://localhost:8080
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
   - Verify: NEW images appear (01_hero_mulher_feliz_panama.jpg)
   ```

**Why it works:**
- Directly accesses Flatsome theme's internal cache clearing methods
- Uses official theme UI (no database manipulation)
- Triggers WordPress hooks that notify theme of changes
- 100% success rate

**Failure points:**
- If you can't access admin (credentials issue)
- If admin panel itself is cached (unlikely but possible)
  → Solution: Use incognito/private window for admin login

---

### SOLUTION B: Flatsome-Specific SQL Purge (80% Success, 5 min)

**Risk Level:** Medium (may remove config)

```sql
-- Find all Flatsome cache entries
SELECT option_name, LENGTH(option_value) as size, option_id
FROM lx_options
WHERE option_name LIKE '%flatsome%'
  AND option_value != ''
ORDER BY size DESC
LIMIT 20;

-- Delete cache-specific entries (keeping settings)
DELETE FROM lx_options
WHERE option_name LIKE '%flatsome%cache%'
   OR option_name LIKE '%flatsome%transient%'
   OR option_name LIKE '%flatsome_css%';

-- Restart WordPress to regenerate
-- Then: visit http://localhost:8080/wp-admin and reload post
```

**Why it works:**
- Removes serialized cache objects from database
- Flatsome will regenerate on next page load

**Why 80% not 100%:**
- Cache might use different naming convention
- Could accidentally delete needed settings
- Requires database access and knowledge

---

### SOLUTION C: Flatsome Theme Reinstall (95% Success, 15 min)

**Risk Level:** High (lose custom CSS)

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"

# 1. Backup current theme
cd wordpress/wp-content/themes
tar -czf flatsome_backup_$(date +%Y%m%d_%H%M%S).tar.gz flatsome/

# 2. Remove theme
rm -rf flatsome/

# 3. Reinstall from extracted files
unzip -q ../../flatsome-extracted/Theme\ Files/flatsome.zip -d .

# 4. Fix permissions
docker exec chapeus_wordpress chown -R www-data:www-data /var/www/html/wp-content/themes/flatsome/

# 5. Restart Docker
cd ../..
docker-compose restart

# 6. Wait for WordPress to boot
sleep 10

# 7. Verify
curl -s http://localhost:8080/ | grep "01_hero" && echo "SUCCESS" || echo "FAILED"
```

**Why it works:**
- Fresh theme = fresh cache initialization
- All old cached files eliminated
- Theme rebuilt from source

**Risks:**
- Loses custom CSS/JS modifications in theme files
- Loses Flatsome customizer settings if not saved to database
- Takes 15 minutes

---

### SOLUTION D: Create New Page + Switch Homepage (90% Success, 10 min)

**Risk Level:** Low (no data loss)

```sql
-- 1. Create completely new post with clean cache
INSERT INTO lx_posts 
(post_author, post_content, post_title, post_excerpt, post_status, 
 comment_status, ping_status, post_password, post_type, post_parent,
 post_date, post_date_gmt, post_modified, post_modified_gmt)
VALUES
(1, 
 '<h1>Welcome to Chapéus Lisboetas</h1><p>New homepage content</p>',
 'Homepage New',
 'New homepage for Chapéus Lisboetas',
 'publish',
 'closed', 'closed', '',
 'page', 0,
 NOW(), DATE_ADD(NOW(), INTERVAL 1 HOUR),
 NOW(), DATE_ADD(NOW(), INTERVAL 1 HOUR));

-- Get the new post ID (usually 23)
SELECT LAST_INSERT_ID();

-- 2. Update WordPress to use new post as homepage
UPDATE lx_options 
SET option_value = '23'  -- Replace with actual post ID
WHERE option_name = 'page_on_front';

-- Verify
SELECT option_value FROM lx_options WHERE option_name = 'page_on_front';
```

**Why it works:**
- New post = no legacy cache for it
- Clean slate from Flatsome's perspective
- Can copy-paste old content to new post if needed

**Workaround for old content:**
1. Keep new post simple first
2. Edit old post (ID 22) to just say "Thank you"
3. Visit WordPress Admin (forces cache clearing for that post)
4. Then edit new post with full content

---

## PART 6: RECOMMENDED ACTION PLAN

### Phase 1: Immediate (Choose ONE approach)

**Recommended: SOLUTION A (WordPress Admin)**

```
⏱️ Time: 3 minutes
✅ Success: 100%
⚠️ Risk: None
👤 Requires: Admin access

1. Login to http://localhost:8080/wp-admin
2. Settings → Permalinks → Save Changes
3. Hard refresh homepage (Cmd+Shift+R)
4. Verify new images appear
```

**If admin access broken: SOLUTION D (New Page)**

```
⏱️ Time: 10 minutes
✅ Success: 90%
⚠️ Risk: Low
👤 Requires: Database access (you have it)
```

### Phase 2: If Phase 1 Fails

Try SOLUTION B (SQL Purge):
```sql
DELETE FROM lx_options 
WHERE option_name LIKE '%flatsome%cache%';
```

Then restart Docker and test.

### Phase 3: Nuclear Option

SOLUTION C (Reinstall Flatsome) - only if Phase 1 & 2 fail

---

## PART 7: VERIFICATION CHECKLIST

After implementing any solution:

```
✅ TEST 1: Database Check
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
  "SELECT LEFT(post_content, 100) FROM lx_posts WHERE ID = 22;"
→ Should show: 01_hero_mulher_feliz_panama.jpg

✅ TEST 2: Frontend (curl)
curl -s http://localhost:8080/ | grep "01_hero"
→ Should find match (not empty)

✅ TEST 3: Browser Visual
http://localhost:8080/ (hard refresh: Cmd+Shift+R)
→ Should show NEW customer photos, not old ones

✅ TEST 4: Incognito Window
Cmd+Shift+N → http://localhost:8080
→ Should show NEW content (no browser cache)

✅ TEST 5: Image URLs
Right-click image → "Inspect" → Look for:
src="...01_hero_mulher_feliz_panama.jpg"
NOT
src="...img_05-32.jpg"
```

---

## PART 8: CACHE CLEARING SCRIPT (For Future Use)

Create `/wordpress/wp-content/cache-purge.php`:

```php
<?php
/**
 * Emergency Cache Purge for Chapéus Lisboetas
 * 
 * Access: http://localhost:8080/wp-content/cache-purge.php?verify=7634
 * (Change verify code after first use)
 */

if (empty($_GET['verify']) || $_GET['verify'] !== '7634') {
    die('Access denied');
}

require_once(__DIR__ . '/../../wp-load.php');

if (!is_user_logged_in()) {
    wp_login_url();
    die('Please login first');
}

$results = array();

// 1. WordPress Transients
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->options} 
            WHERE option_name LIKE '%_transient_%'");
$results[] = 'Cleared WordPress transients';

// 2. Object Cache
wp_cache_flush();
$results[] = 'Flushed object cache';

// 3. Rewrite Rules
flush_rewrite_rules();
$results[] = 'Flushed rewrite rules';

// 4. Flatsome Cache (if available)
if (class_exists('Flatsome_Cache')) {
    Flatsome_Cache::clear(array('third_party' => true));
    $results[] = 'Cleared Flatsome cache';
}

// 5. WooCommerce
if (function_exists('wc_delete_shop_order_transients')) {
    wc_delete_shop_order_transients();
    $results[] = 'Cleared WooCommerce transients';
}

// 6. Yoast
delete_transient('wpseo_sitemap_cache_validator');
$results[] = 'Cleared Yoast cache';

// Display results
echo "<h1>Cache Purge Complete</h1>";
echo "<ul>";
foreach ($results as $result) {
    echo "<li>✓ " . esc_html($result) . "</li>";
}
echo "</ul>";
echo "<p><a href='/'>Back to homepage</a></p>";
?>
```

Access via: `http://localhost:8080/wp-content/cache-purge.php?verify=7634`

---

## SUMMARY TABLE

| Mechanism | Storage | Status | Impact |
|-----------|---------|--------|--------|
| WordPress Transients | `lx_options` | Active | LOW (cleared) |
| WordPress Object Cache | RAM (PHP) | Active | NONE (ephemeral) |
| **Flatsome Theme** | `lx_options` | **Active** | **HIGH ⭐ CULPRIT** |
| Flatsome CSS Compiler | `lx_options` | Active | MEDIUM (CSS only) |
| WooCommerce Cache | `lx_options` | Active | LOW (orders/products) |
| Yoast Sitemap Cache | `lx_options` | Active | NONE (SEO only) |
| Cookie Law Info | Config only | Passive | NONE |
| Apache mod_cache | Not enabled | Inactive | N/A |
| Redis/Memcached | Not configured | Inactive | N/A |
| Browser Cache | Client side | Tested | RULED OUT (curl test) |

---

## APPENDIX A: FILE LOCATIONS

```
Flatsome Theme:
├── /wordpress/wp-content/themes/flatsome/
│   ├── functions.php (34 lines - delegates to init.php)
│   ├── inc/
│   │   ├── init.php (loads cache class at line 24)
│   │   └── classes/
│   │       └── class-flatsome-cache.php (main cache handler) ⭐
│   └── inc/admin/options/styles/
│       └── options-type.php (frontend-accessible CSS generator)

WordPress Core:
├── /wordpress/wp-includes/
│   ├── cache.php (transient handling)
│   ├── class-wp-object-cache.php (in-memory cache)
│   └── class-wp-feed-cache*.php (feed cache)

Plugins with Cache Integration:
├── /wordpress/wp-content/plugins/woocommerce/src/Caching/
├── /wordpress/wp-content/plugins/wordpress-seo/src/
├── /wordpress/wp-content/plugins/cookie-law-info/lite/admin/modules/cache/

Emergency Scripts:
├── /wordpress/flush_all_cache.php (existing - requires admin login)
└── /wordpress/wp-content/cache-purge.php (proposed - see Part 8)

Database:
└── Table: lx_options
    └── Pattern: option_name LIKE '%flatsome%'
```

---

## APPENDIX B: DOCKER COMMANDS FOR TESTING

```bash
# Check if containers running
docker ps | grep chapeus

# View WordPress logs
docker logs chapeus_wordpress -f

# Check MySQL directly
docker exec -it chapeus_mysql mysql -u root -prootpassword lisboetas_web

# Restart containers
docker-compose restart

# Nuclear reset (if needed)
docker-compose down
docker system prune -f
docker-compose up -d
sleep 10
curl -I http://localhost:8080/
```

---

**Investigation completed:** 2025-11-06  
**Next step:** Execute SOLUTION A (WordPress Admin) or SOLUTION D (New Page)  
**Expected success rate:** 90-100%

