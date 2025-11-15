#!/usr/bin/env python3
"""
Fix Product Images - GUID-Based Matching
Associates correct images to products using WordPress GUID field.

This script fixes the issue where all products show the same image
by doing precise path-based matching via database GUID field.

Usage:
    python3 scripts/fix_product_images_guid.py                # Full fix
    python3 scripts/fix_product_images_guid.py --limit=5      # Test mode
    python3 scripts/fix_product_images_guid.py --dry-run      # Preview only

Author: Claude Code (Sonnet 4.5) + User Analysis
Date: 2025-11-10
"""

import csv
import subprocess
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import time
import re

# Configuration
CONTAINER_NAME = "chapeus_wordpress"
MYSQL_CONTAINER = "chapeus_mysql"
DB_NAME = "lisboetas_web"
DB_USER = "root"
DB_PASS = "rootpassword"
CSV_FILE = "output_catalogo/woocommerce_import.csv"
IMAGE_BASE_URL = "http://localhost:8080/wp-content/uploads/products"

# Stats tracking
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'no_images': 0,
    'errors': []
}


def execute_sql(query: str) -> str:
    """Execute SQL query in MySQL container."""
    cmd = [
        "docker", "exec", MYSQL_CONTAINER,
        "mysql", "-u", DB_USER, f"-p{DB_PASS}", DB_NAME,
        "-e", query,
        "--batch", "--skip-column-names"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        raise Exception(f"SQL Error: {result.stderr}")

    return result.stdout.strip()


def clean_image_path(csv_path: str) -> str:
    """
    Clean image path from CSV to match WordPress structure.

    Input: "catalogo2025/boinas%20inverno/bone-22182/img_01.jpg"
    Output: "boinas inverno/bone-22182/img_01.jpg"
    """
    # Remove catalogo2025/ prefix
    path = csv_path.replace('catalogo2025/', '')

    # URL decode
    path = path.replace('%20', ' ')

    return path


def find_attachment_by_guid(image_path: str) -> Optional[int]:
    """
    Find attachment ID by GUID (full URL path).

    This is the PRECISE method - GUID contains full path with spaces/accents.

    Args:
        image_path: Cleaned path like "boinas inverno/bone-22182/img_01.jpg"

    Returns:
        Attachment ID or None
    """
    # Build GUID pattern (WordPress stores full URL in guid)
    guid_pattern = f"%/products/{image_path}"

    # Escape SQL special chars
    guid_pattern = guid_pattern.replace("'", "\\'")

    query = f"""
    SELECT ID FROM lx_posts
    WHERE post_type='attachment'
    AND guid LIKE '{guid_pattern}'
    LIMIT 1
    """

    try:
        result = execute_sql(query)
        if result:
            return int(result.strip())
    except Exception as e:
        print(f"    ⚠️  SQL error finding {image_path}: {e}")

    return None


def get_product_id_by_name(product_name: str) -> Optional[int]:
    """
    Get product ID by post_title (product name).

    This is more reliable than SKU since WP-CLI import updates existing products
    and their post_title matches the CSV Name field.
    """
    name_escaped = product_name.replace("'", "\\'")

    query = f"""
    SELECT ID FROM lx_posts
    WHERE post_type='product'
    AND post_title='{name_escaped}'
    LIMIT 1
    """

    try:
        result = execute_sql(query)
        if result:
            return int(result.strip())
    except Exception as e:
        print(f"    ⚠️  SQL error finding product '{product_name[:30]}...': {e}")

    return None


def update_product_images_sql(product_id: int, image_ids: List[int], dry_run: bool = False) -> bool:
    """
    Update product images via direct SQL (FAST).

    Args:
        product_id: Product ID
        image_ids: List of attachment IDs (first = featured, rest = gallery)
        dry_run: If True, don't execute

    Returns:
        True if success
    """
    if not image_ids:
        return False

    featured_id = image_ids[0]
    gallery_ids = ','.join(str(id) for id in image_ids[1:]) if len(image_ids) > 1 else ''

    if dry_run:
        print(f"    [DRY RUN] Would set:")
        print(f"      Featured: {featured_id}")
        print(f"      Gallery: {gallery_ids or '(none)'}")
        return True

    try:
        # Update or insert _thumbnail_id
        query_featured = f"""
        INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
        VALUES ({product_id}, '_thumbnail_id', '{featured_id}')
        ON DUPLICATE KEY UPDATE meta_value='{featured_id}'
        """
        execute_sql(query_featured)

        # Update or insert _product_image_gallery
        if gallery_ids:
            query_gallery = f"""
            INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
            VALUES ({product_id}, '_product_image_gallery', '{gallery_ids}')
            ON DUPLICATE KEY UPDATE meta_value='{gallery_ids}'
            """
            execute_sql(query_gallery)

        return True

    except Exception as e:
        print(f"    ❌ SQL update error: {e}")
        return False


def process_product(row: Dict, dry_run: bool = False) -> bool:
    """
    Process single product and fix images.

    Args:
        row: CSV row dict
        dry_run: Preview mode

    Returns:
        True if success
    """
    sku = row.get('SKU', '').strip()
    name = row.get('Name', '').strip()
    images_str = row.get('Images', '').strip()

    # Clean SKU (remove newlines)
    if '\n' in sku:
        sku = sku.split('\n')[0].strip()

    if not sku or not name:
        stats['no_images'] += 1
        return False

    if not images_str:
        stats['no_images'] += 1
        print(f"    ⏭  No images in CSV")
        return False

    # Get product ID by name (more reliable than SKU)
    product_id = get_product_id_by_name(name)
    if not product_id:
        stats['failed'] += 1
        stats['errors'].append({
            'sku': sku,
            'name': name,
            'error': 'Product not found in database'
        })
        print(f"    ❌ Product not found")
        return False

    # Parse image paths from CSV
    csv_image_paths = [path.strip() for path in images_str.split(',')]

    # Find attachment IDs using GUID matching
    attachment_ids = []
    for csv_path in csv_image_paths:
        cleaned_path = clean_image_path(csv_path)
        att_id = find_attachment_by_guid(cleaned_path)

        if att_id:
            attachment_ids.append(att_id)
        else:
            # Try alternative: search by filename only as fallback
            filename = Path(cleaned_path).name
            print(f"    ⚠️  Image not found by GUID: {filename}")

    if not attachment_ids:
        stats['failed'] += 1
        stats['errors'].append({
            'sku': sku,
            'name': name,
            'error': 'No images found in media library'
        })
        print(f"    ❌ No images found in WordPress")
        return False

    # Update product with correct images via SQL
    success = update_product_images_sql(product_id, attachment_ids, dry_run)

    if success:
        stats['success'] += 1
        print(f"    ✓ Fixed {len(attachment_ids)} images (Featured: {attachment_ids[0]})")
        return True
    else:
        stats['failed'] += 1
        stats['errors'].append({
            'sku': sku,
            'name': name,
            'error': 'Failed to update images in database'
        })
        print(f"    ✗ Failed to update")
        return False


def clear_wordpress_cache():
    """Clear WordPress cache after fixing images."""
    print("\n🧹 Clearing WordPress cache...")

    try:
        subprocess.run([
            "docker", "exec", CONTAINER_NAME,
            "wp", "cache", "flush", "--allow-root"
        ], capture_output=True, timeout=30)
        print("   ✓ Cache cleared")
    except Exception as e:
        print(f"   ⚠️  Cache clear failed: {e}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Fix product images using GUID-based matching'
    )
    parser.add_argument('--limit', type=int, help='Limit number of products')
    parser.add_argument('--dry-run', action='store_true', help='Preview only (no changes)')
    parser.add_argument('--csv', default=CSV_FILE, help='CSV file to process')

    args = parser.parse_args()

    # Check CSV exists
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)

    # Print header
    print("=" * 80)
    print("FIX PRODUCT IMAGES - GUID-BASED MATCHING")
    print("=" * 80)
    print(f"\nCSV: {csv_path}")
    print(f"MySQL: {MYSQL_CONTAINER} / {DB_NAME}")
    print(f"Mode: {'DRY RUN (no changes)' if args.dry_run else 'PRODUCTION (will update database)'}")

    if args.limit:
        print(f"Limit: {args.limit} products")

    print("\n" + "-" * 80)

    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    stats['total'] = len(rows)

    if args.limit:
        rows = rows[:args.limit]
        print(f"\n📋 Processing {len(rows)} products (limited from {stats['total']})\n")
    else:
        print(f"\n📋 Processing {len(rows)} products\n")

    # Process products
    for i, row in enumerate(rows, 1):
        sku = row.get('SKU', '').strip()
        name = row.get('Name', '').strip()

        # Clean SKU
        if '\n' in sku:
            sku = sku.split('\n')[0].strip()

        if not sku or not name:
            print(f"[{i}/{len(rows)}] ⏭  Skipping empty row")
            continue

        print(f"[{i}/{len(rows)}] 🖼️  {name[:50]}", end=' ')

        process_product(row, dry_run=args.dry_run)

    # Clear cache if not dry run
    if not args.dry_run and stats['success'] > 0:
        clear_wordpress_cache()

    # Print summary
    print("\n" + "=" * 80)
    print("FIX SUMMARY")
    print("=" * 80)
    print(f"Total products in CSV: {stats['total']}")
    print(f"Processed: {len(rows)}")
    print(f"Success: {stats['success']} ✓")
    print(f"Failed: {stats['failed']} ✗")
    print(f"No images: {stats['no_images']} ⏭")

    if stats['errors']:
        print(f"\n❌ {len(stats['errors'])} errors occurred:")
        for error in stats['errors'][:10]:
            print(f"  - {error['sku']}: {error['error'][:100]}")

        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")

    print("\n" + "=" * 80)

    if not args.dry_run and stats['success'] > 0:
        print("\n✅ Images fixed! Visit http://localhost:8080/shop to verify")

    # Exit code
    if stats['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
