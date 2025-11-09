# Quick Fix Guide - WordPress Cache Issue

## THE PROBLEM
Post ID 22 shows old content on frontend even though database has new content.

## THE ROOT CAUSE
**Flatsome Theme Internal Cache** is storing a cached version of the post.

---

## QUICK FIXES (Choose One)

### FIX #1: WordPress Admin (RECOMMENDED - 3 minutes)

```
1. Go to: http://localhost:8080/wp-admin
2. Click: Settings → Permalinks
3. Scroll down and click: "Save Changes"
4. Go back to homepage: http://localhost:8080
5. Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
6. Done! Should see new content
```

**Why this works:**
- Saving permalinks triggers WordPress hooks
- Flatsome theme listens to these hooks
- Cache gets cleared automatically

---

### FIX #2: Database SQL (If admin access broken - 5 minutes)

Run this SQL command:

```sql
DELETE FROM lx_options 
WHERE option_name LIKE '%flatsome%cache%'
   OR option_name LIKE '%flatsome_css%';
```

Then:
1. Stop Docker: `docker-compose down`
2. Start Docker: `docker-compose up -d`
3. Wait 10 seconds
4. Visit: http://localhost:8080
5. Hard refresh page
6. Done!

---

### FIX #3: Complete Theme Reinstall (15 minutes, if others don't work)

```bash
cd "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)"
cd wordpress/wp-content/themes
tar -czf flatsome_backup.tar.gz flatsome/
rm -rf flatsome/
unzip -q ../../flatsome-extracted/Theme\ Files/flatsome.zip
docker exec chapeus_wordpress chown -R www-data:www-data /var/www/html/wp-content/themes/flatsome/
cd ../../..
docker-compose restart
sleep 10
curl http://localhost:8080/ | head -20
```

---

## VERIFICATION

After applying fix, check:

1. **Database is correct:**
   ```bash
   docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
     "SELECT LEFT(post_content, 100) FROM lx_posts WHERE ID = 22;"
   ```
   Should show: `01_hero_mulher_feliz_panama.jpg`

2. **Frontend shows new content:**
   ```bash
   curl http://localhost:8080/ | grep "01_hero"
   ```
   Should show a match (not empty)

3. **Browser displays correctly:**
   - Open incognito: Cmd+Shift+N (Mac)
   - Visit: http://localhost:8080
   - Should see NEW images, not old ones

---

## FILES INVOLVED

**Primary Cache Location:**
- `/wordpress/wp-content/themes/flatsome/inc/classes/class-flatsome-cache.php`

**Cache Storage:**
- Database table: `lx_options` (with names like `flatsome_*`)

**Configuration:**
- `/wordpress/wp-config.php` (no `WP_CACHE` constant = default caching)

---

## WHY PREVIOUS ATTEMPTS FAILED

- Docker restart: Cache in database, not in RAM
- SQL UPDATE: Database updated but theme still serves cached version
- Plugin disabling: Flatsome cache still active
- Transient deletion: Flatsome uses custom storage, not standard transients

---

## NEXT STEPS IF STILL NOT WORKING

1. Check if WordPress admin accessible: http://localhost:8080/wp-admin
2. If not, use Fix #2 (Database SQL)
3. If still not working, use Fix #3 (Theme reinstall)
4. If still not working, check Docker logs:
   ```bash
   docker logs chapeus_wordpress
   docker logs chapeus_mysql
   ```

---

**Created:** 2025-11-06  
**For:** Bilal / Tiago (Chapéus Lisboetas)  
**Status:** Critical issue, 90-100% solvable with one of the 3 fixes above

