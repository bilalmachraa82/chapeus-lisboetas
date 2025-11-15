#!/usr/bin/env python3
"""
Link Product Images to WooCommerce Products
Associates images from media library with products based on CSV paths.

Usage:
    python3 scripts/link_images_to_products.py                    # Full linking
    python3 scripts/link_images_to_products.py --limit=5          # Test mode
    python3 scripts/link_images_to_products.py --dry-run          # Dry run

Author: Claude Code (Sonnet 4.5)
Date: 2025-11-10
"""

import csv
import subprocess
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import time

# Configuration
CONTAINER_NAME = "chapeus_wordpress"
CSV_FILE = "output_catalogo/woocommerce_import.csv"
WP_USER = "codex-admin"

# Stats tracking
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'no_images': 0,
    'errors': []
}


def run_wp_cli(args: List[str], capture_output=True) -> subprocess.CompletedProcess:
    """Execute WP-CLI command inside Docker container."""
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


def csv_path_to_relative(path: str) -> str:
    """Convert CSV image path/URL to uploads-relative path."""
    path = path.strip()
    if not path:
        return ""

    # If URL, strip off uploads prefix
    uploads_token = "/wp-content/uploads/"
    if path.startswith("http://") or path.startswith("https://"):
        idx = path.find(uploads_token)
        if idx != -1:
            path = path[idx + len(uploads_token):]

    # Remove known prefixes from CSV
    if path.startswith("catalogo2025/"):
        path = path[len("catalogo2025/"):]
    if path.startswith("images/"):
        path = path[len("images/"):]

    # Decode URL encoding
    path = path.replace('%20', ' ')

    # Ensure it lives inside products/
    if not path.startswith("products/"):
        path = f"products/{path.lstrip('/')}"

    # Normalize duplicate slashes
    while '//' in path:
        path = path.replace('//', '/')

    return path


def find_attachment_id(relative_path: str) -> Optional[int]:
    """Find attachment ID by _wp_attached_file relative path."""
    if not relative_path:
        return None

    result = run_wp_cli([
        "post", "list",
        "--post_type=attachment",
        f"--meta_key=_wp_attached_file",
        f"--meta_value={relative_path}",
        "--field=ID",
        "--format=ids"
    ])

    if result.returncode == 0:
        output = result.stdout.strip()
        if output:
            return int(output.split('\n')[0])
    return None


def get_product_id_by_sku(sku: str) -> Optional[int]:
    """Get product ID by SKU."""
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


def link_images_to_product(product_id: int, image_ids: List[int], dry_run: bool = False) -> bool:
    """
    Link images to product (featured image + gallery).

    Args:
        product_id: WooCommerce product ID
        image_ids: List of attachment IDs
        dry_run: If True, don't actually update

    Returns:
        True if success, False if failed
    """
    if not image_ids:
        return False

    if dry_run:
        print(f"    [DRY RUN] Would link {len(image_ids)} images to product {product_id}")
        print(f"    Featured: {image_ids[0]}, Gallery: {image_ids[1:]}")
        return True

    # Set featured image (first image)
    featured_result = run_wp_cli([
        "post", "meta", "update", str(product_id),
        "_thumbnail_id", str(image_ids[0])
    ])

    if featured_result.returncode != 0:
        print(f"    ❌ Failed to set featured image: {featured_result.stderr[:100]}")
        return False

    # Set gallery images (remaining images)
    if len(image_ids) > 1:
        gallery_ids = ','.join(str(id) for id in image_ids[1:])
        gallery_result = run_wp_cli([
            "post", "meta", "update", str(product_id),
            "_product_image_gallery", gallery_ids
        ])

        if gallery_result.returncode != 0:
            print(f"    ⚠️  Failed to set gallery: {gallery_result.stderr[:100]}")
            # Don't fail completely, featured image is set

    return True


def process_product(row: Dict, dry_run: bool = False) -> bool:
    """
    Process a single product from CSV and link images.

    Args:
        row: CSV row dict
        dry_run: If True, don't actually update

    Returns:
        True if success, False if failed
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

    # Get product ID
    product_id = get_product_id_by_sku(sku)
    if not product_id:
        stats['failed'] += 1
        stats['errors'].append({
            'sku': sku,
            'name': name,
            'error': 'Product not found in WordPress'
        })
        print(f"    ❌ Product not found")
        return False

    # Parse image paths from CSV
    image_paths = [path.strip() for path in images_str.split(',')]

    # Find attachment IDs for each image
    attachment_ids = []
    for img_path in image_paths:
        rel_path = csv_path_to_relative(img_path)
        att_id = find_attachment_id(rel_path)

        if att_id:
            attachment_ids.append(att_id)
        else:
            print(f"    ⚠️  Image not found in media library: {rel_path}")

    if not attachment_ids:
        stats['no_images'] += 1
        stats['errors'].append({
            'sku': sku,
            'name': name,
            'error': 'No images found in media library'
        })
        print(f"    ❌ No images found in media library")
        return False

    # Link images to product
    success = link_images_to_product(product_id, attachment_ids, dry_run)

    if success:
        stats['success'] += 1
        print(f"    ✓ Linked {len(attachment_ids)} images")
        return True
    else:
        stats['failed'] += 1
        stats['errors'].append({
            'sku': sku,
            'name': name,
            'error': 'Failed to link images'
        })
        print(f"    ✗ Failed to link images")
        return False


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Link product images from media library')
    parser.add_argument('--limit', type=int, help='Limit number of products')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual update)')
    parser.add_argument('--csv', default=CSV_FILE, help='CSV file to process')

    args = parser.parse_args()

    # Check CSV exists
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)

    # Print header
    print("=" * 80)
    print("LINK PRODUCT IMAGES TO WOOCOMMERCE PRODUCTS")
    print("=" * 80)
    print(f"\nCSV: {csv_path}")
    print(f"Container: {CONTAINER_NAME}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'PRODUCTION'}")

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

        # Small delay to avoid overwhelming the server
        if not args.dry_run:
            time.sleep(0.1)

    # Print summary
    print("\n" + "=" * 80)
    print("LINKING SUMMARY")
    print("=" * 80)
    print(f"Total products in CSV: {stats['total']}")
    print(f"Processed: {len(rows)}")
    print(f"Success: {stats['success']} ✓")
    print(f"Failed: {stats['failed']} ✗")
    print(f"No images: {stats['no_images']} ⏭")

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
