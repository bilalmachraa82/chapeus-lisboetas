#!/usr/bin/env python3
"""
SKU Mapping Diagnostic - Identify mismatch patterns
Compares filesystem folders with WordPress database SKUs
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import mysql.connector

# Configuração
BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = BASE_DIR / 'wordpress' / 'wp-content' / 'uploads' / 'products'

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'lisboetas_web'
}

def get_wordpress_skus() -> Dict[str, Tuple[int, str]]:
    """
    Get all SKUs from WordPress database
    Returns: {sku: (product_id, product_title)}
    """
    db = mysql.connector.connect(**DB_CONFIG, buffered=True)
    cursor = db.cursor()

    cursor.execute("""
        SELECT pm.meta_value as sku, p.ID, p.post_title
        FROM lx_postmeta pm
        INNER JOIN lx_posts p ON pm.post_id = p.ID
        WHERE pm.meta_key = '_sku'
        AND p.post_type = 'product'
        AND p.post_status IN ('publish', 'private')
        ORDER BY pm.meta_value
    """)

    skus = {}
    for row in cursor.fetchall():
        sku, product_id, title = row
        if sku:  # Skip empty SKUs
            skus[sku.upper()] = (product_id, title)

    cursor.close()
    db.close()

    return skus

def extract_all_possible_skus(folder_name: str) -> List[str]:
    """
    Extract all possible SKU candidates from folder name
    Returns list of candidates in priority order
    """
    candidates = []

    # Pattern 1: Pure numeric (18220mi → 18220)
    matches = re.findall(r'\b(\d{4,6})[a-zA-Z]{0,2}\b', folder_name)
    candidates.extend(matches)

    # Pattern 2: After dash (bone-18074 → 18074)
    matches = re.findall(r'-(\d{4,6})[a-zA-Z]{0,2}\b', folder_name)
    candidates.extend(matches)

    # Pattern 3: Longer numbers (181056 → try 18105, 1810, etc.)
    matches = re.findall(r'\b(\d{5,7})\b', folder_name)
    for match in matches:
        # Try truncating from right
        candidates.append(match[:5])  # First 5 digits
        candidates.append(match[:4])  # First 4 digits

    # Remove duplicates while preserving order
    seen = set()
    unique_candidates = []
    for c in candidates:
        c_upper = c.upper()
        if c_upper not in seen:
            seen.add(c_upper)
            unique_candidates.append(c_upper)

    return unique_candidates

def scan_all_folders() -> Dict[str, Tuple[str, List[str]]]:
    """
    Scan all product folders and extract SKU candidates
    Returns: {folder_path: (category, [sku_candidates])}
    """
    folders = {}

    if not PRODUCTS_DIR.exists():
        return folders

    for category_dir in PRODUCTS_DIR.iterdir():
        if not category_dir.is_dir():
            continue

        for sku_dir in category_dir.iterdir():
            if not sku_dir.is_dir():
                continue

            # Count photos (exclude thumbnails)
            photos = []
            for ext in ['*.jpg', '*.png']:
                for p in sku_dir.glob(ext):
                    if not re.search(r'-\d+x\d+\.(jpg|png)$', p.name) and not p.name.startswith('.'):
                        photos.append(p)
            photo_count = len(photos)

            if photo_count == 0:
                continue

            candidates = extract_all_possible_skus(sku_dir.name)
            folders[str(sku_dir)] = (category_dir.name, candidates, photo_count)

    return folders

def find_best_match(candidates: List[str], wp_skus: Dict[str, Tuple[int, str]]) -> Tuple[str, int, str]:
    """
    Find best matching WordPress SKU for candidates
    Returns: (matched_sku, product_id, product_title) or (None, None, None)
    """
    # Try exact match first
    for candidate in candidates:
        if candidate in wp_skus:
            return (candidate, *wp_skus[candidate])

    # Try partial match (SKU starts with candidate)
    for candidate in candidates:
        for wp_sku, (pid, title) in wp_skus.items():
            if wp_sku.startswith(candidate):
                return (wp_sku, pid, title)

    return (None, None, None)

def main():
    print("\n" + "="*80)
    print("SKU MAPPING DIAGNOSTIC")
    print("="*80 + "\n")

    print("📊 Loading WordPress SKUs...")
    wp_skus = get_wordpress_skus()
    print(f"✓ Found {len(wp_skus)} products in WordPress\n")

    print("📁 Scanning product folders...")
    folders = scan_all_folders()
    print(f"✓ Found {len(folders)} folders with photos\n")

    # Analysis
    matched = []
    unmatched = []

    for folder_path, (category, candidates, photo_count) in folders.items():
        folder_name = Path(folder_path).name
        matched_sku, product_id, product_title = find_best_match(candidates, wp_skus)

        if matched_sku:
            matched.append({
                'folder': folder_name,
                'category': category,
                'candidates': candidates,
                'matched_sku': matched_sku,
                'product_id': product_id,
                'product_title': product_title,
                'photo_count': photo_count
            })
        else:
            unmatched.append({
                'folder': folder_name,
                'category': category,
                'candidates': candidates,
                'photo_count': photo_count
            })

    # Report
    print("="*80)
    print(f"✅ MATCHED: {len(matched)} folders")
    print("="*80)
    for m in matched[:10]:  # Show first 10
        print(f"  {m['folder'][:40]:40s} → SKU: {m['matched_sku']:8s} | {m['product_title'][:35]:35s} | {m['photo_count']:3d} fotos")
    if len(matched) > 10:
        print(f"  ... and {len(matched) - 10} more")

    print("\n" + "="*80)
    print(f"❌ UNMATCHED: {len(unmatched)} folders (products not in WordPress)")
    print("="*80)
    for u in unmatched[:15]:  # Show first 15
        print(f"  {u['folder'][:50]:50s} | Candidates: {', '.join(u['candidates'][:3])[:20]:20s} | {u['photo_count']:3d} fotos")
    if len(unmatched) > 15:
        print(f"  ... and {len(unmatched) - 15} more")

    # Save full report
    report_path = BASE_DIR / 'relatorios' / 'sku_mapping_report.txt'
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("SKU MAPPING FULL REPORT\n")
        f.write("="*80 + "\n\n")

        f.write(f"MATCHED ({len(matched)} folders):\n")
        f.write("-"*80 + "\n")
        for m in matched:
            f.write(f"Folder: {m['folder']}\n")
            f.write(f"  Category: {m['category']}\n")
            f.write(f"  Candidates: {', '.join(m['candidates'])}\n")
            f.write(f"  → Matched SKU: {m['matched_sku']} (ID: {m['product_id']})\n")
            f.write(f"  → Product: {m['product_title']}\n")
            f.write(f"  → Photos: {m['photo_count']}\n\n")

        f.write("\n" + "="*80 + "\n")
        f.write(f"UNMATCHED ({len(unmatched)} folders - products not imported yet):\n")
        f.write("-"*80 + "\n")
        for u in unmatched:
            f.write(f"Folder: {u['folder']}\n")
            f.write(f"  Category: {u['category']}\n")
            f.write(f"  Candidates: {', '.join(u['candidates'])}\n")
            f.write(f"  Photos: {u['photo_count']}\n\n")

    print(f"\n✓ Full report saved: {report_path}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"WordPress products: {len(wp_skus)}")
    print(f"Folders with photos: {len(folders)}")
    if len(folders) > 0:
        print(f"Matched folders: {len(matched)} ({len(matched)/len(folders)*100:.1f}%)")
        print(f"Unmatched folders: {len(unmatched)} ({len(unmatched)/len(folders)*100:.1f}%)")
    else:
        print(f"Matched folders: {len(matched)}")
        print(f"Unmatched folders: {len(unmatched)}")
    print(f"\n💡 Recommendation:")
    if len(matched) >= 90:
        print(f"   ✅ Proceed with import for {len(matched)} products")
    else:
        print(f"   ⚠️  Only {len(matched)} products can be imported")
        print(f"   ⚠️  {len(unmatched)} folders are for products not yet in WordPress")
        print(f"   → Consider importing missing products first, or proceed with {len(matched)} available")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
