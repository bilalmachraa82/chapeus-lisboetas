#!/usr/bin/env python3
"""
WordPress/WooCommerce Import via WP-CLI
Imports products from CSV using WP-CLI commands inside Docker container.

Usage:
    python3 scripts/import_via_wpcli.py                    # Full import
    python3 scripts/import_via_wpcli.py --test --limit=3   # Test mode
    python3 scripts/import_via_wpcli.py --dry-run          # Dry run (no changes)

Author: Claude Code (Sonnet 4.5)
Date: 2025-11-10
"""

import csv
import subprocess
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import time

# Configuration
CONTAINER_NAME = "chapeus_wordpress"
CSV_FILE = "output_catalogo/woocommerce_import.csv"
WP_USER = "codex-admin"
IMAGE_BASE_URL = "http://localhost:8080/wp-content/uploads"

# Stats tracking
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'skipped': 0,
    'errors': []
}

term_cache = []


def run_wp_cli(args: List[str], capture_output=True) -> subprocess.CompletedProcess:
    """
    Execute WP-CLI command inside Docker container.

    Args:
        args: List of WP-CLI arguments
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess object with returncode, stdout, stderr
    """
    cmd = [
        "docker", "exec", CONTAINER_NAME,
        "wp", *args,
        f"--user={WP_USER}",
        "--allow-root"
    ]

    return subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        timeout=60
    )


def product_exists(sku: str) -> Optional[int]:
    """
    Check if product with SKU already exists.

    Returns:
        Product ID if exists, None otherwise
    """
    result = run_wp_cli([
        "post", "list",
        "--post_type=product",
        f"--meta_key=_sku",
        f"--meta_value={sku}",
        "--field=ID",
        "--format=csv"
    ])

    if result.returncode == 0 and result.stdout.strip():
        return int(result.stdout.strip())
    return None


def load_term_cache():
    """Populate term cache with existing product categories."""
    global term_cache
    if term_cache:
        return

    result = run_wp_cli([
        "term", "list", "product_cat",
        "--format=json"
    ])

    if result.returncode == 0 and result.stdout.strip():
        term_cache = json.loads(result.stdout)
    else:
        term_cache = []


def find_term_id(name: str, parent_id: int) -> Optional[int]:
    """Find existing term id by name and parent."""
    load_term_cache()
    for term in term_cache:
        if term.get("name") == name and int(term.get("parent", 0)) == parent_id:
            return int(term["term_id"])
    return None


def add_term_to_cache(term_id: int, name: str, parent_id: int):
    term_cache.append({
        "term_id": term_id,
        "name": name,
        "parent": parent_id
    })


def create_category(category_path: str) -> Optional[int]:
    """
    Create category hierarchy and return leaf category ID.

    Args:
        category_path: "Chapéus > Boinas > Inverno"

    Returns:
        Category ID or None if failed
    """
    if not category_path or category_path == "Uncategorized":
        return None

    categories = [cat.strip() for cat in category_path.split('>')]
    parent_id = 0

    for category in categories:
        existing_id = find_term_id(category, parent_id)

        if existing_id:
            parent_id = existing_id
        else:
            result = run_wp_cli([
                "term", "create", "product_cat", category,
                f"--parent={parent_id}",
                "--porcelain"
            ])

            if result.returncode == 0:
                new_term_id = int(result.stdout.strip())
                add_term_to_cache(new_term_id, category, parent_id)
                parent_id = new_term_id
            else:
                print(f"    ⚠️  Failed to create category: {category}")
                return None

    return parent_id


def prepare_images(images_str: str) -> List[Dict[str, str]]:
    """
    Prepare image URLs from CSV.

    Args:
        images_str: Comma-separated image paths

    Returns:
        List of image dicts with src URLs
    """
    if not images_str:
        return []

    images = []
    for img_path in images_str.split(','):
        img_path = img_path.strip()
        if img_path:
            # Handle different path formats
            if img_path.startswith('http'):
                url = img_path
            else:
                relative = img_path.lstrip('/')
                url = f"{IMAGE_BASE_URL}/{relative}"

            images.append({"src": url})

    return images


def import_product(row: Dict, dry_run: bool = False) -> bool:
    """
    Import a single product via WP-CLI.

    Args:
        row: CSV row dict
        dry_run: If True, don't actually create product

    Returns:
        True if success, False if failed
    """
    sku = row.get('SKU', '').strip()
    # Clean SKU: take only first line if multi-line SKU
    if '\n' in sku:
        sku = sku.split('\n')[0].strip()

    name = row.get('Name', '').strip()

    if not sku or not name:
        stats['skipped'] += 1
        return False

    # Check if product exists
    product_id = product_exists(sku)

    if product_id:
        action = "update"
        cmd_base = ["wc", "product", "update", str(product_id)]
    else:
        action = "create"
        cmd_base = ["wc", "product", "create"]

    # Build WP-CLI command
    cmd = cmd_base + [
        f"--name={name}",
        f"--sku={sku}",
        f"--status={'publish' if row.get('Published') == '1' else 'draft'}"
    ]

    # Add price
    regular_price = row.get('Regular price', '').strip()
    if regular_price:
        cmd.append(f"--regular_price={regular_price}")

    sale_price = row.get('Sale price', '').strip()
    if sale_price:
        cmd.append(f"--sale_price={sale_price}")

    # Add descriptions
    short_desc = row.get('Short description', '').strip()
    if short_desc:
        cmd.append(f"--short_description={short_desc}")

    description = row.get('Description', '').strip()
    if description:
        cmd.append(f"--description={description}")

    # Add categories
    categories_str = row.get('Categories', '').strip()
    if categories_str:
        category_id = create_category(categories_str)
        if category_id:
            categories_json = json.dumps([{"id": category_id}])
            cmd.append(f"--categories={categories_json}")

    # Add images
    images_str = row.get('Images', '').strip()
    if images_str:
        images = prepare_images(images_str)
        if images:
            images_json = json.dumps(images)
            cmd.append(f"--images={images_json}")

    # Add stock
    stock = row.get('Stock', '').strip()
    if stock and stock.isdigit():
        cmd.append(f"--stock_quantity={stock}")
        cmd.append("--manage_stock=true")
        # Note: stock_status is set automatically based on stock_quantity

    # Add tags
    tags = row.get('Tags', '').strip()
    if tags:
        tag_names = [t.strip() for t in tags.split(',')]
        tags_json = json.dumps([{"name": t} for t in tag_names if t])
        cmd.append(f"--tags={tags_json}")

    # Dry run - just print command
    if dry_run:
        print(f"    [DRY RUN] Would {action} product: {name}")
        print(f"    Command: wp {' '.join(cmd)}")
        return True

    # Execute import
    try:
        result = run_wp_cli(cmd)

        if result.returncode == 0:
            stats['success'] += 1
            return True
        else:
            stats['failed'] += 1
            stats['errors'].append({
                'sku': sku,
                'name': name,
                'error': result.stderr
            })
            print(f"    ❌ Error: {result.stderr[:100]}")
            return False

    except subprocess.TimeoutExpired:
        stats['failed'] += 1
        stats['errors'].append({
            'sku': sku,
            'name': name,
            'error': 'Timeout after 60s'
        })
        print(f"    ❌ Timeout")
        return False
    except Exception as e:
        stats['failed'] += 1
        stats['errors'].append({
            'sku': sku,
            'name': name,
            'error': str(e)
        })
        print(f"    ❌ Exception: {e}")
        return False


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Import WooCommerce products via WP-CLI')
    parser.add_argument('--test', action='store_true', help='Test mode')
    parser.add_argument('--limit', type=int, help='Limit number of products')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual import)')
    parser.add_argument('--csv', default=CSV_FILE, help='CSV file to import')

    args = parser.parse_args()

    # Check CSV exists
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)

    # Print header
    print("=" * 80)
    print("WORDPRESS/WOOCOMMERCE IMPORT VIA WP-CLI")
    print("=" * 80)
    print(f"\nCSV: {csv_path}")
    print(f"Container: {CONTAINER_NAME}")
    print(f"Mode: {'TEST' if args.test else 'DRY RUN' if args.dry_run else 'PRODUCTION'}")

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
        print(f"\n📋 Importing {len(rows)} products (limited from {stats['total']})\n")
    else:
        print(f"\n📋 Importing {len(rows)} products\n")

    # Import products
    for i, row in enumerate(rows, 1):
        sku = row.get('SKU', '').strip()
        name = row.get('Name', '').strip()

        if not sku or not name:
            print(f"[{i}/{len(rows)}] ⏭  Skipping empty row")
            continue

        print(f"[{i}/{len(rows)}] 📦 {name[:50]}", end=' ')

        if product_exists(sku):
            print("(update)", end=' ')
        else:
            print("(new)", end=' ')

        success = import_product(row, dry_run=args.dry_run)

        if success:
            print("✓")
        else:
            print("✗")

        # Small delay to avoid overwhelming the server
        if not args.dry_run:
            time.sleep(0.1)

    # Print summary
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"Total products in CSV: {stats['total']}")
    print(f"Processed: {len(rows)}")
    print(f"Success: {stats['success']} ✓")
    print(f"Failed: {stats['failed']} ✗")
    print(f"Skipped: {stats['skipped']} ⏭")

    if stats['errors']:
        print(f"\n❌ {len(stats['errors'])} errors occurred:")
        for error in stats['errors'][:10]:  # Show first 10
            print(f"  - {error['sku']}: {error['error'][:100]}")

        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")

    print("\n" + "=" * 80)

    # Exit code
    if stats['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
