#!/usr/bin/env python3
"""
Deduplicate catalogo.json based on (sheet, sheet_row) unique key
FASE 0 deduplication method - keep only first occurrence of each (sheet, row)
"""

import json
from pathlib import Path
from datetime import datetime

CATALOG_PATH = Path("output_catalogo/catalogo.json")
BACKUP_PATH = Path(f"output_catalogo/catalogo_before_dedup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

def dedup_catalog():
    print("\n" + "="*80)
    print("FASE 3: DEDUPLICAÇÃO CATALOG.JSON")
    print("="*80 + "\n")

    # Load catalog
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print(f"📊 Produtos antes: {len(catalog)}")

    # Find duplicates by (sheet, sheet_row)
    seen_keys = set()
    unique_products = []
    duplicates = []

    for product in catalog:
        sheet = product.get('sheet')
        sheet_row = product.get('sheet_row')

        # Create unique key
        if sheet and sheet_row:
            key = (sheet, sheet_row)
        else:
            # Fallback: use slug if no sheet/row info
            key = product.get('slug')

        if key in seen_keys:
            duplicates.append({
                'sheet': sheet,
                'sheet_row': sheet_row,
                'slug': product.get('slug'),
                'name': product.get('name')
            })
            print(f"[SKIP] Duplicate: {sheet} row {sheet_row} ({product.get('slug')})")
        else:
            seen_keys.add(key)
            unique_products.append(product)

    print(f"\n📊 Produtos depois: {len(unique_products)}")
    print(f"❌ Duplicados removidos: {len(duplicates)}")

    # Save duplicates report
    if duplicates:
        dup_report_path = Path(f"relatorios/DUPLICATES_REMOVED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(dup_report_path, 'w', encoding='utf-8') as f:
            json.dump(duplicates, f, indent=2, ensure_ascii=False)
        print(f"💾 Relatório duplicados: {dup_report_path}")

    # Backup original
    import shutil
    shutil.copy(CATALOG_PATH, BACKUP_PATH)
    print(f"💾 Backup original: {BACKUP_PATH}")

    # Save deduplicated catalog
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(unique_products, f, indent=2, ensure_ascii=False)

    print(f"✅ Catalog salvo: {CATALOG_PATH}")

    # Verify slugs are unique
    slugs = [p['slug'] for p in unique_products if p.get('slug')]
    unique_slugs = set(slugs)

    print(f"\n🔍 Verificação slugs:")
    print(f"   Total slugs: {len(slugs)}")
    print(f"   Slugs únicos: {len(unique_slugs)}")

    if len(slugs) == len(unique_slugs):
        print(f"   ✅ Todos os slugs são únicos!")
    else:
        print(f"   ⚠️  {len(slugs) - len(unique_slugs)} slugs ainda duplicados")

    print("\n✅ FASE 3 COMPLETA\n")

    return {
        'before': len(catalog),
        'after': len(unique_products),
        'removed': len(duplicates)
    }

if __name__ == "__main__":
    result = dedup_catalog()
    print(f"Resultado: {result}")
