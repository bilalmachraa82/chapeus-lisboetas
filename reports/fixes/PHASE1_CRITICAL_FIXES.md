# PHASE 1: CRITICAL FIXES - EXECUTION LOG

**Started:** 2025-10-30 01:55
**Status:** IN PROGRESS
**Total Issues:** 9

---

## Fix Order

1. ⏳ ISSUE-006: Duplicate SKU "180" (SQL)
2. ⏸️ ISSUE-005: Menu z-index (CSS)
3. ⏸️ ISSUE-003: Site-wide link color (CSS)
4. ⏸️ ISSUE-001: Cookie banner blue (CSS)
5. ⏸️ ISSUE-002: Admin bar blue (CSS)
6. ⏸️ ISSUE-004: WooCommerce notices (CSS)
7. ⏸️ ISSUE-007: Security headers (Apache/Plugin)
8. ⏸️ ISSUE-009: Livro Reclamações (HTML)
9. ⏸️ ISSUE-008: http:// URLs (DEFER to deploy)

---

## Execution Log

### ISSUE-006: Duplicate SKU "180" Fix
**Started:** 2025-10-30 01:55
**Status:** IN PROGRESS

**Problem:** 151 products share SKU "180"
**Impact:** Cannot track inventory, orders may assign wrong products

**SQL Fix:**
```sql
UPDATE lx_postmeta pm
JOIN lx_posts p ON pm.post_id = p.ID
SET pm.meta_value = CONCAT('CL-', LPAD(p.ID, 6, '0'))
WHERE pm.meta_key = '_sku'
  AND pm.meta_value = '180'
  AND p.post_type = 'product';
```

**Execution:**
- Rows affected: [TBD]
- New SKU format: CL-000248, CL-000585, etc.

**Testing:**
- [ ] Query to verify unique SKUs
- [ ] Check product pages show new SKUs
- [ ] Verify no "180" SKUs remain

**Completed:** [TBD]

---

