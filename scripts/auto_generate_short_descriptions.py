#!/usr/bin/env python3
"""
Auto-generate short descriptions for products missing them
Uses intelligent fallback logic based on available data
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
CATALOG_PATH = Path(__file__).parent.parent / "output_catalogo" / "catalogo.json"
BACKUP_PATH = Path(__file__).parent.parent / "output_catalogo" / f"catalogo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def get_first_sentence(text):
    """Extract first sentence from text"""
    if not text:
        return ""
    # Split by common sentence terminators
    for terminator in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
        if terminator in text:
            return text.split(terminator)[0] + '.'
    # If no sentence terminator, truncate at 100 chars
    return text[:100].strip() + ('...' if len(text) > 100 else '')

def truncate_text(text, max_length=150):
    """Truncate text to max length at word boundary"""
    if not text or len(text) <= max_length:
        return text
    # Find last space before max_length
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + '...'

def generate_short_description(product):
    """Generate short description using intelligent fallback logic"""

    # Priority 1: Use existing short description
    if product.get('info_short'):
        return product['info_short']

    # Priority 2: First sentence of scraped description
    scraped = product.get('scraped', [])
    if scraped and isinstance(scraped, list) and len(scraped) > 0:
        desc = scraped[0].get('description', '')
        if desc:
            short = get_first_sentence(desc)
            if short:
                return short

    # Priority 3: Generate from specs
    specs = product.get('specs', {})
    if specs:
        parts = []

        # Add size if available
        tamanho = specs.get('TAMANHO', specs.get('tamanho', ''))
        if tamanho and 'ajustável' in tamanho.lower():
            parts.append('Tamanho ajustável')
        elif tamanho:
            parts.append(tamanho)

        # Add color if available
        cor = specs.get('COR', specs.get('cor', ''))
        if cor and cor.lower() != 'sortido':
            parts.append(f"Cor: {cor}")

        # Add material if available
        composicao = specs.get('COMPOSIÇÃO', specs.get('COMPOSICAO', specs.get('composicao', '')))
        if composicao:
            # Extract main material
            material = composicao.split(',')[0].split('%')[-1].strip()
            if material:
                parts.append(material)

        if parts:
            return ' - '.join(parts)

    # Priority 4: Generate from category and name
    categoria = product.get('sheet', '')
    nome = product.get('name', '')

    if categoria and nome:
        # Clean up category name
        cat_clean = categoria.replace('BOINAS ', '').replace('CHAPÉUS ', '').title()
        return f"{nome.title()} - {cat_clean}"
    elif nome:
        return nome.title()

    # Priority 5: Generic fallback
    return "Produto exclusivo Chapéus Lisboeta - Consulte detalhes na loja"

def auto_generate_short_descriptions(dry_run=False):
    """Main function to auto-generate short descriptions"""

    # Load catalog
    print(f"Loading catalog from: {CATALOG_PATH}")
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print(f"Loaded {len(catalog)} products")

    # Backup original catalog
    if not dry_run:
        print(f"Creating backup: {BACKUP_PATH}")
        with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

    # Stats
    stats = {
        'total': len(catalog),
        'had_short_desc': 0,
        'generated_from_scraped': 0,
        'generated_from_specs': 0,
        'generated_from_name': 0,
        'generated_generic': 0
    }

    updated_products = []

    # Process each product
    for product in catalog:
        sku = product.get('supplier_code', product.get('sku', 'N/A'))
        nome = product.get('name', 'N/A')
        original_short = product.get('info_short', '')

        # Track original state
        if original_short:
            stats['had_short_desc'] += 1

        # Generate short description
        new_short = generate_short_description(product)

        # Categorize generation method
        if original_short:
            method = 'existing'
        elif new_short and product.get('scraped', []) and any(s.get('description') for s in product.get('scraped', [])):
            method = 'scraped'
            stats['generated_from_scraped'] += 1
        elif new_short and product.get('specs', {}):
            method = 'specs'
            stats['generated_from_specs'] += 1
        elif '-' in new_short and product.get('sheet'):
            method = 'name'
            stats['generated_from_name'] += 1
        else:
            method = 'generic'
            stats['generated_generic'] += 1

        # Update product
        if not dry_run and not original_short:
            product['info_short'] = new_short
            updated_products.append({
                'sku': sku,
                'nome': nome,
                'method': method,
                'short_desc': new_short
            })

        # Print progress for products without original short desc
        if not original_short:
            print(f"\n[{method.upper()}] {sku} - {nome}")
            print(f"  Generated: {new_short[:100]}{'...' if len(new_short) > 100 else ''}")

    # Save updated catalog
    if not dry_run:
        print(f"\n\nSaving updated catalog to: {CATALOG_PATH}")
        with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

        # Save update log
        log_path = Path(__file__).parent.parent / "relatorios" / f"short_descriptions_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'stats': stats,
                'updated_products': updated_products
            }, f, indent=2, ensure_ascii=False)
        print(f"Update log saved to: {log_path}")

    # Print summary
    print("\n" + "="*80)
    print("SHORT DESCRIPTION GENERATION SUMMARY")
    print("="*80)
    print(f"\nTotal products: {stats['total']}")
    print(f"Already had short descriptions: {stats['had_short_desc']}")
    print(f"\nGenerated descriptions: {stats['total'] - stats['had_short_desc']}")
    print(f"  - From scraped descriptions: {stats['generated_from_scraped']}")
    print(f"  - From specs: {stats['generated_from_specs']}")
    print(f"  - From name/category: {stats['generated_from_name']}")
    print(f"  - Generic fallback: {stats['generated_generic']}")

    if dry_run:
        print("\n⚠️  DRY RUN - No changes saved")
        print("Run without --dry-run to apply changes")
    else:
        print(f"\n✅ Updated {len(updated_products)} products")
        print(f"✅ Backup saved to: {BACKUP_PATH}")
        print(f"✅ Catalog updated: {CATALOG_PATH}")

    print("="*80 + "\n")

    return stats, updated_products

if __name__ == '__main__':
    import sys
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("🔍 RUNNING IN DRY-RUN MODE (no changes will be saved)\n")

    stats, updated = auto_generate_short_descriptions(dry_run=dry_run)
