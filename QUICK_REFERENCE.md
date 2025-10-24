# QUICK REFERENCE - Hero & Product Grid Fixes

## WHAT WAS FIXED

### Hero Section
- ✅ CTAs now display side-by-side (desktop)
- ✅ CTAs stack vertically on mobile
- ✅ No more overlapping buttons
- ✅ Smooth hover effects

### Product Grid
- ✅ All images perfectly square (1:1)
- ✅ Images centered in containers
- ✅ Equal height product cards
- ✅ Responsive 3-column → 2-column → flexible layout

---

## FILES CHANGED

**Primary file:**
```
/wordpress/wp-content/themes/flatsome-child/style.css
```

**Database updates:**
- WooCommerce thumbnail width: 600px
- Image size: 600x600 (square, cropped)

---

## HOW TO TEST

### 1. Hero Section (30 seconds)
```
Visit: http://localhost:8080
Look for: Two buttons side-by-side
Mobile test: Resize browser, buttons should stack
```

### 2. Product Grid (30 seconds)
```
Visit: http://localhost:8080/shop/
Look for: Square product images, equal heights
Hover test: Cards should lift up slightly
```

---

## IF IMAGES STILL LOOK WRONG

Run this command to regenerate all thumbnails:

```bash
docker exec chapeus_wordpress bash -c "cd /var/www/html && wp plugin install regenerate-thumbnails --activate --allow-root && wp media regenerate --yes --allow-root"
```

**Time:** 5-10 minutes for 131 products
**When to run:** Only if images are still cropped incorrectly after clearing cache

---

## CLEAR CACHE

If changes don't appear:

```bash
# Clear WordPress cache
docker exec chapeus_wordpress bash -c "cd /var/www/html && wp cache flush --allow-root"

# Hard refresh browser
# Chrome/Firefox: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
# Safari: Cmd+Option+R
```

---

## ROLLBACK (if needed)

To undo all changes:

```bash
cd /Users/bilal/Programaçao/Tiago\ Andrado/full-chapeus-lisboetas\ \(2\)
git checkout wordpress/wp-content/themes/flatsome-child/style.css
docker exec chapeus_wordpress bash -c "cd /var/www/html && wp cache flush --allow-root"
```

Then refresh: http://localhost:8080

---

## BROWSER TESTING CHECKLIST

- [ ] Chrome desktop (1920px)
- [ ] Chrome mobile emulation (375px)
- [ ] Firefox desktop
- [ ] Safari (Mac/iOS only)

**Tool:** Chrome DevTools → Toggle device toolbar (Ctrl+Shift+M)

---

## KEY URLS

- Homepage: http://localhost:8080
- Shop: http://localhost:8080/shop/
- Admin: http://localhost:8080/wp-admin
- Category example: http://localhost:8080/product-category/boinas/

---

## CSS CHANGES SUMMARY

**Added to `/wordpress/wp-content/themes/flatsome-child/style.css`:**
- Hero section: 94 lines
- Product grid: 73 lines
- Mobile responsive: 53 lines
- **Total:** 220 lines of production-ready CSS

**No JavaScript changes** - Pure CSS solution for better performance

---

## SUPPORT

**Full documentation:**
- `CHAPEUS_FIX_REPORT.md` - Complete technical report
- `TESTING_GUIDE.md` - Detailed testing procedures
- `QUICK_REFERENCE.md` - This file

**Questions?**
Contact: Bilal Machraa / AiParaTi

---

**Last updated:** 2025-10-23
**Project:** Chapéus Lisboetas
**Status:** READY FOR TESTING
