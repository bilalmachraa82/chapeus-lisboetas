# Testing Checklist - Navigation Dropdown Fix

## Pre-Fix Verification
- [ ] Confirm issue exists: Hover "Loja" menu on homepage
- [ ] Take screenshot of bug (dropdown hidden behind hero)
- [ ] Note which browsers show the issue

## Apply Fix
- [ ] Open `/wordpress/wp-content/themes/flatsome-child/style.css`
- [ ] Add CSS code to end of file (after line 2232)
- [ ] Save file
- [ ] Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- [ ] Hard refresh page

## Post-Fix Testing

### Desktop Tests
- [ ] Hover "Loja" → Dropdown appears ABOVE hero image
- [ ] Hover "Serviços & Atelier" → Dropdown fully visible
- [ ] Click submenu items → Links work correctly
- [ ] Scroll down → Sticky header dropdown still works
- [ ] Test on large screen (1920px+)
- [ ] Test on medium screen (1024px)

### Mobile Tests (if accessible)
- [ ] Open mobile menu (hamburger icon)
- [ ] Tap "Loja" → Submenu expands
- [ ] Tap submenu items → Navigation works
- [ ] No visual glitches or overlap

### Cross-Browser (if available)
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

## Edge Cases
- [ ] Dropdown near viewport edge (doesn't get cut off)
- [ ] Multiple dropdown hovers in sequence
- [ ] Dropdown with long menu items
- [ ] Fast hover in/out (no flickering)

## Performance Check
- [ ] No layout shift when dropdown appears
- [ ] Smooth animation (if any)
- [ ] No console errors in DevTools

## Final Verification
- [ ] Compare before/after screenshots
- [ ] Mark issue as RESOLVED
- [ ] Update bug tracker (if any)
- [ ] Document fix in changelog

---

**Testing completed by:** _____________  
**Date:** _____________  
**Status:** [ ] PASS [ ] FAIL [ ] NEEDS REVISION
