#!/usr/bin/env python3
"""
Analyze catalog for incomplete product descriptions
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
CATALOG_PATH = Path(__file__).parent.parent / "output_catalogo" / "catalogo.json"
OUTPUT_DIR = Path(__file__).parent.parent / "relatorios"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_catalog():
    """Load catalog JSON"""
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_complete_description(product):
    """Check if product has complete description"""
    info_short = product.get('info_short', '') or ''
    specs = product.get('specs') or {}
    tags = product.get('tags') or []

    # Check if scraped data exists
    scraped = product.get('scraped', [])
    has_scraped_desc = False
    if isinstance(scraped, list) and len(scraped) > 0:
        has_scraped_desc = bool(scraped[0].get('description', ''))

    checks = {
        'has_short_desc': bool(info_short.strip()) if isinstance(info_short, str) else False,
        'has_long_desc': has_scraped_desc,
        'has_specs': bool(specs) if isinstance(specs, dict) else False,
        'has_tags': len(tags) > 0 if isinstance(tags, list) else False,
        'has_composition': ('COMPOSIÇÃO' in specs or 'COMPOSICAO' in specs or 'composicao' in specs or 'composition' in specs) if isinstance(specs, dict) else False,
    }
    return checks

def get_price(product):
    """Extract numeric price"""
    price_str = product.get('price', '0')
    if isinstance(price_str, str):
        price_str = price_str.replace('€', '').replace(',', '.').strip()
    try:
        return float(price_str)
    except:
        return 0.0

def categorize_by_priority(product, checks):
    """Determine priority level"""
    price = get_price(product)
    completeness_score = sum(1 for v in checks.values() if v)

    # High priority: expensive products with gaps
    if price > 40 and completeness_score < 4:
        return 'HIGH'
    # Medium priority: mid-range with gaps
    elif price > 20 and completeness_score < 3:
        return 'MEDIUM'
    # Low priority: cheap or mostly complete
    else:
        return 'LOW'

def analyze_catalog():
    """Main analysis function"""
    catalog = load_catalog()

    # Initialize counters
    stats = {
        'total_products': len(catalog),
        'complete': 0,
        'incomplete': 0,
        'missing_long_desc': 0,
        'missing_specs': 0,
        'missing_tags': 0,
        'missing_composition': 0,
        'missing_materials': 0
    }

    # Category breakdown
    by_category = defaultdict(lambda: {
        'total': 0,
        'complete': 0,
        'incomplete': 0,
        'gaps': []
    })

    # Priority lists
    by_priority = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }

    # Detailed analysis
    all_products = []

    for product in catalog:
        sku = product.get('supplier_code', product.get('sku', 'N/A'))
        nome = product.get('name', product.get('nome', 'N/A'))
        categoria = product.get('sheet', product.get('categoria', 'UNCATEGORIZED'))
        price = get_price(product)
        supplier_url = product.get('supplier_url', product.get('url_fornecedor', ''))

        # Check completeness
        checks = is_complete_description(product)
        is_complete = all(checks.values())

        # Update stats
        if is_complete:
            stats['complete'] += 1
        else:
            stats['incomplete'] += 1

        if not checks['has_short_desc']:
            stats['missing_short_desc'] = stats.get('missing_short_desc', 0) + 1
        if not checks['has_long_desc']:
            stats['missing_long_desc'] += 1
        if not checks['has_specs']:
            stats['missing_specs'] += 1
        if not checks['has_tags']:
            stats['missing_tags'] += 1
        if not checks['has_composition']:
            stats['missing_composition'] += 1

        # Category breakdown
        by_category[categoria]['total'] += 1
        if is_complete:
            by_category[categoria]['complete'] += 1
        else:
            by_category[categoria]['incomplete'] += 1
            gaps = [k.replace('has_', '') for k, v in checks.items() if not v]
            by_category[categoria]['gaps'].extend(gaps)

        # Priority categorization
        priority = categorize_by_priority(product, checks)

        # Build product record
        product_record = {
            'sku': sku,
            'nome': nome,
            'categoria': categoria,
            'price': f"€{price:.2f}",
            'priority': priority,
            'has_short_desc': 'YES' if checks['has_short_desc'] else 'NO',
            'has_long_desc': 'YES' if checks['has_long_desc'] else 'NO',
            'has_specs': 'YES' if checks['has_specs'] else 'NO',
            'has_tags': 'YES' if checks['has_tags'] else 'NO',
            'has_composition': 'YES' if checks['has_composition'] else 'NO',
            'completeness_score': f"{sum(1 for v in checks.values() if v)}/5",
            'gaps': ', '.join([k.replace('has_', '') for k, v in checks.items() if not v]),
            'supplier_url': supplier_url,
            'can_auto_scrape': 'YES' if supplier_url and 'hologramme' in supplier_url else 'NO'
        }

        all_products.append(product_record)

        if not is_complete:
            by_priority[priority].append(product_record)

    # Generate summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'overview': stats,
        'by_category': dict(by_category),
        'by_priority_count': {
            'HIGH': len(by_priority['HIGH']),
            'MEDIUM': len(by_priority['MEDIUM']),
            'LOW': len(by_priority['LOW'])
        },
        'recommendations': generate_recommendations(by_priority, stats)
    }

    return summary, by_priority, all_products

def generate_recommendations(by_priority, stats):
    """Generate actionable recommendations"""
    recommendations = []

    # Auto-scrape potential
    auto_scrapable = sum(1 for p in by_priority['HIGH'] + by_priority['MEDIUM']
                         if p['can_auto_scrape'] == 'YES')

    recommendations.append({
        'action': 'Auto-complete from supplier URLs',
        'count': auto_scrapable,
        'estimated_time': f"{auto_scrapable * 2} minutes (automated)",
        'script': 'python3 scripts/catalog_scraper.py'
    })

    # Manual input needed
    manual_needed = len(by_priority['HIGH']) + len(by_priority['MEDIUM']) - auto_scrapable

    recommendations.append({
        'action': 'Manual client input required',
        'count': manual_needed,
        'estimated_time': f"{manual_needed * 5} minutes (client time)",
        'note': 'Products without supplier URLs or unique items'
    })

    # Low priority
    recommendations.append({
        'action': 'Low priority items (defer)',
        'count': len(by_priority['LOW']),
        'estimated_time': 'Phase 2 or post-launch',
        'note': 'Can launch without these being complete'
    })

    return recommendations

def export_reports(summary, by_priority, all_products):
    """Export all report files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 1. JSON analysis
    json_path = OUTPUT_DIR / 'descriptions_analysis.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"✓ Created: {json_path}")

    # 2. CSV for each priority level
    csv_fields = ['sku', 'nome', 'categoria', 'price', 'priority',
                  'has_short_desc', 'has_long_desc', 'has_specs', 'has_tags',
                  'has_composition', 'completeness_score', 'gaps',
                  'supplier_url', 'can_auto_scrape']

    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        csv_path = OUTPUT_DIR / f'descriptions_incomplete_{priority}.csv'
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(by_priority[priority])
        print(f"✓ Created: {csv_path} ({len(by_priority[priority])} products)")

    # 3. Full catalog CSV
    full_csv_path = OUTPUT_DIR / f'descriptions_full_analysis_{timestamp}.csv'
    with open(full_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(all_products)
    print(f"✓ Created: {full_csv_path} ({len(all_products)} products)")

def print_summary(summary, by_priority):
    """Print console summary"""
    print("\n" + "="*80)
    print("CATALOG DESCRIPTIONS ANALYSIS")
    print("="*80)

    print("\n📊 OVERVIEW:")
    print(f"  Total products: {summary['overview']['total_products']}")
    print(f"  Complete: {summary['overview']['complete']} ({summary['overview']['complete']/summary['overview']['total_products']*100:.1f}%)")
    print(f"  Incomplete: {summary['overview']['incomplete']} ({summary['overview']['incomplete']/summary['overview']['total_products']*100:.1f}%)")

    print("\n🔍 GAPS IDENTIFIED:")
    print(f"  Missing short descriptions: {summary['overview'].get('missing_short_desc', 0)}")
    print(f"  Missing long descriptions: {summary['overview']['missing_long_desc']}")
    print(f"  Missing specs: {summary['overview']['missing_specs']}")
    print(f"  Missing tags: {summary['overview']['missing_tags']}")
    print(f"  Missing composition: {summary['overview']['missing_composition']}")

    print("\n📂 BY CATEGORY:")
    for cat, data in sorted(summary['by_category'].items()):
        incomplete_pct = (data['incomplete'] / data['total'] * 100) if data['total'] > 0 else 0
        print(f"  {cat}: {data['total']} total, {data['incomplete']} incomplete ({incomplete_pct:.1f}%)")

    print("\n🎯 PRIORITY BREAKDOWN:")
    print(f"  HIGH priority: {len(by_priority['HIGH'])} products (>€40 with gaps)")
    print(f"  MEDIUM priority: {len(by_priority['MEDIUM'])} products (€20-€40 with gaps)")
    print(f"  LOW priority: {len(by_priority['LOW'])} products (<€20 or mostly complete)")

    print("\n✅ RECOMMENDATIONS:")
    for i, rec in enumerate(summary['recommendations'], 1):
        print(f"  {i}. {rec['action']}: {rec['count']} products")
        print(f"     Estimated time: {rec['estimated_time']}")
        if 'script' in rec:
            print(f"     Run: {rec['script']}")
        if 'note' in rec:
            print(f"     Note: {rec['note']}")

    print("\n📁 FILES CREATED:")
    print(f"  • relatorios/descriptions_analysis.json")
    print(f"  • relatorios/descriptions_incomplete_HIGH.csv")
    print(f"  • relatorios/descriptions_incomplete_MEDIUM.csv")
    print(f"  • relatorios/descriptions_incomplete_LOW.csv")
    print("="*80 + "\n")

if __name__ == '__main__':
    summary, by_priority, all_products = analyze_catalog()
    export_reports(summary, by_priority, all_products)
    print_summary(summary, by_priority)
