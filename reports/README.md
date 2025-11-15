# Reports Directory Structure

**Created:** 2025-10-30
**Purpose:** Systematic audit and fix tracking for Chapéus Lisboetas site

## Directory Organization

```
reports/
├── baseline/          # Pre-audit snapshots (DB, theme_mods, Git state)
├── audits/            # Agent audit reports (visual, functional, woocommerce, performance)
├── fixes/             # Fix application logs and documentation
└── screenshots/       # Before/After visual evidence
```

## Naming Convention

```
baseline/
  └── 2025-10-30-HHMM-baseline.md
  └── 2025-10-30-HHMM-db-backup.sql
  └── 2025-10-30-HHMM-theme-mods.json

audits/
  └── 2025-10-30-HHMM-visual-consistency.md
  └── 2025-10-30-HHMM-functional-bugs.md
  └── 2025-10-30-HHMM-woocommerce-validation.md
  └── 2025-10-30-HHMM-performance-security.md

fixes/
  └── 2025-10-30-HHMM-ISSUE-001-dropdown-zindex.md
  └── 2025-10-30-HHMM-ISSUE-002-produtos-1000-euros.md

screenshots/
  └── before-after/
      └── ISSUE-001-dropdown-before.png
      └── ISSUE-001-dropdown-after.png
```

## Issue Labeling System

Labels:
- `critical` - Bloqueante para utilizador (menu ilegível, página quebrada)
- `high` - Impacto significativo (cores erradas, produtos visíveis incorretamente)
- `medium` - Problemas menores (spacing, formatting)
- `low` - Melhorias (nice-to-have)

## Workflow

1. **Baseline Snapshot** → `reports/baseline/`
2. **Run 4 Agents** → `reports/audits/`
3. **Consolidate Master Bug List** → `reports/MASTER_BUG_LIST.md`
4. **Apply Fixes** → Document in `reports/fixes/`
5. **Checkpoint** → Git commit + Screenshot
6. **Final Validation** → Agent 4 report

## Checkpoint Protocol

Após cada lote de fixes:
```bash
# 1. Git commit
git add .
git commit -m "fix(ISSUE-XXX): Description"

# 2. Screenshot
# Save to reports/screenshots/ISSUE-XXX-after.png

# 3. Cross-impact test
# Testar menu + shop + homepage

# 4. Document
# Update reports/fixes/ISSUE-XXX.md
```

## Master Bug List Format

```markdown
# MASTER BUG LIST

Generated: 2025-10-30 HHMM
Status: [IN_PROGRESS / COMPLETED]

## 🔴 CRITICAL

- [ ] **ISSUE-001**: Menu dropdown atrás de imagens (z-index)
  - Impact: Menu ilegível
  - Agent: Functional Bug Hunter
  - Fix: `style.css` line XXX
  - Status: PENDING

## 🟡 HIGH

- [ ] **ISSUE-002**: Produtos >€1000 visíveis
  - Impact: Confusão cliente
  - Agent: WooCommerce Validator
  - Fix: Product visibility settings
  - Status: PENDING

## 🟢 MEDIUM

...
```

---

**Maintained by:** Claude Code Audit System
**Last updated:** 2025-10-30
