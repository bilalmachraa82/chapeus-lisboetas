#!/usr/bin/env python3
"""
Associate AI-Enhanced Images with WooCommerce Products
Links registered enhanced images to their corresponding products.

Usage:
    python3 scripts/associate_enhanced_images.py
    python3 scripts/associate_enhanced_images.py --dry-run
    python3 scripts/associate_enhanced_images.py --featured-only

Author: Claude Code (Opus 4.1)
Date: 2025-11-13
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
BASE_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)")
TRACKING_CSV = BASE_PATH / "relatorios/ai_enhanced_images_registered.csv"
DOCKER_CONTAINER = os.environ.get("WP_CONTAINER", "chapeus_wordpress")
MYSQL_CONTAINER = os.environ.get("MYSQL_CONTAINER", "chapeus_mysql")
MYSQL_DB = os.environ.get("WP_DB_NAME", "lisboetas_web")
MYSQL_USER = os.environ.get("WP_DB_USER", "root")
MYSQL_PASS = os.environ.get("WP_DB_PASS", "rootpassword")
TABLE_PREFIX = os.environ.get("WP_TABLE_PREFIX", "wp_")
POSTS_TABLE = f"{TABLE_PREFIX}posts"
POSTMETA_TABLE = f"{TABLE_PREFIX}postmeta"

# Stats
stats = {
    'products_found': 0,
    'products_updated': 0,
    'images_added': 0,
    'featured_set': 0,
    'skipped': 0,
    'failed': 0,
    'errors': []
}


def run_mysql_query(sql: str) -> Optional[Tuple[int, str]]:
    """Run SQL inside MySQL container and return first row (ID, title)."""
    safe_sql = sql.replace('"', r'\"')
    cmd = [
        "docker", "exec", MYSQL_CONTAINER,
        "mysql",
        f"-u{MYSQL_USER}",
        f"-p{MYSQL_PASS}",
        "-D", MYSQL_DB,
        "-e", safe_sql
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode != 0:
        return None

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    first_data = lines[1]
    parts = first_data.split("\t")
    if not parts:
        return None

    try:
        product_id = int(parts[0])
    except ValueError:
        return None

    title = parts[1] if len(parts) > 1 else ""
    return product_id, title


def generate_sku_candidates(raw_value: str) -> List[str]:
    """Generate possible SKU tokens from folder/sku string."""
    if not raw_value:
        return []

    cleaned = raw_value.replace("–", "-").replace("—", "-").strip()
    candidates = []

    # direct cleaned folder name
    if cleaned:
        candidates.append(cleaned)

    # add tokens by splitting on delimiters
    for token in re.split(r"[\\s_/]+", cleaned):
        token = token.strip("- ")
        if token and token not in candidates:
            candidates.append(token)

    # numeric fragments (e.g., 18074, 18074GC)
    numeric_tokens = re.findall(r"\d{3,6}[a-zA-Z]*", cleaned)
    for token in numeric_tokens:
        if token not in candidates:
            candidates.append(token)

    return candidates


def get_product_by_sku(sku: str) -> Optional[Tuple[int, str]]:
    """
    Find WordPress product ID by SKU using WP-CLI.

    Args:
        sku: Product SKU

    Returns:
        Product ID or None if not found
    """
    candidates = generate_sku_candidates(sku)

    for candidate in candidates:
        # Exact match
        safe_candidate = candidate.replace("'", "''")
        sql = (
            f"SELECT p.ID, p.post_title FROM {POSTS_TABLE} p "
            f"INNER JOIN {POSTMETA_TABLE} pm ON p.ID = pm.post_id "
            f"WHERE p.post_type='product' AND p.post_status='publish' "
            f"AND pm.meta_key='_sku' AND pm.meta_value='{safe_candidate}' LIMIT 1;"
        )
        result = run_mysql_query(sql)
        if result:
            return result

        # Partial numeric match
        digits = re.sub(r"\\D", "", candidate)
        if digits and len(digits) >= 3:
            sql_like = (
                f"SELECT p.ID, p.post_title FROM {POSTS_TABLE} p "
                f"INNER JOIN {POSTMETA_TABLE} pm ON p.ID = pm.post_id "
                f"WHERE p.post_type='product' AND p.post_status='publish' "
                f"AND pm.meta_key='_sku' AND pm.meta_value LIKE '%{digits}%' "
                f"LIMIT 1;"
            )
            result = run_mysql_query(sql_like)
            if result:
                return result

    return None


def get_product_gallery(product_id: int) -> List[int]:
    """
    Get current product gallery image IDs.

    Args:
        product_id: WordPress product ID

    Returns:
        List of attachment IDs
    """
    try:
        cmd = [
            "docker", "exec", DOCKER_CONTAINER,
            "wp", "post", "meta", "get",
            str(product_id),
            "_product_image_gallery",
            "--allow-root"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():
            gallery_str = result.stdout.strip()
            return [int(id) for id in gallery_str.split(',') if id]

        return []

    except Exception:
        return []


def set_product_gallery(
    product_id: int,
    attachment_ids: List[int],
    dry_run: bool = False
) -> bool:
    """
    Update product gallery with image IDs.

    Args:
        product_id: WordPress product ID
        attachment_ids: List of attachment IDs to add
        dry_run: If True, only simulate

    Returns:
        True if successful
    """
    if dry_run:
        print(f"      [DRY RUN] Would add {len(attachment_ids)} images to gallery")
        return True

    try:
        gallery_str = ','.join(str(id) for id in attachment_ids)

        cmd = [
            "docker", "exec", DOCKER_CONTAINER,
            "wp", "post", "meta", "update",
            str(product_id),
            "_product_image_gallery",
            gallery_str,
            "--allow-root"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.returncode == 0

    except Exception as e:
        print(f"      ❌ Error updating gallery: {e}")
        return False


def set_featured_image(
    product_id: int,
    attachment_id: int,
    dry_run: bool = False
) -> bool:
    """
    Set product featured image (thumbnail).

    Args:
        product_id: WordPress product ID
        attachment_id: Attachment ID to set as featured
        dry_run: If True, only simulate

    Returns:
        True if successful
    """
    if dry_run:
        print(f"      [DRY RUN] Would set attachment #{attachment_id} as featured")
        return True

    try:
        cmd = [
            "docker", "exec", DOCKER_CONTAINER,
            "wp", "post", "meta", "update",
            str(product_id),
            "_thumbnail_id",
            str(attachment_id),
            "--allow-root"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        return result.returncode == 0

    except Exception as e:
        print(f"      ❌ Error setting featured image: {e}")
        return False


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Associate enhanced images with WooCommerce products'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview only, do not update'
    )
    parser.add_argument(
        '--featured-only',
        action='store_true',
        help='Only set featured images, skip gallery'
    )
    parser.add_argument(
        '--gallery-only',
        action='store_true',
        help='Only update gallery, skip featured image'
    )

    args = parser.parse_args()

    # Print header
    print("=" * 80)
    print("ASSOCIATE ENHANCED IMAGES WITH PRODUCTS")
    print("=" * 80)
    print(f"\nMode: {'DRY RUN' if args.dry_run else 'PRODUCTION'}")
    print(f"Tracking CSV: {TRACKING_CSV}")
    print("\n" + "-" * 80 + "\n")

    # Load tracking CSV
    if not TRACKING_CSV.exists():
        print(f"❌ Tracking CSV not found: {TRACKING_CSV}")
        print("   Run register_enhanced_images.py first!")
        sys.exit(1)

    with open(TRACKING_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"📊 Found {len(records)} registered images\n")
    print("-" * 80 + "\n")

    # Group images by SKU
    images_by_sku: Dict[str, List[Dict]] = {}
    for record in records:
        sku = record['sku']
        if sku not in images_by_sku:
            images_by_sku[sku] = []
        images_by_sku[sku].append(record)

    stats['products_found'] = len(images_by_sku)
    print(f"📦 Found {stats['products_found']} unique products (SKUs)\n")

    # Process each product
    for i, (sku, image_records) in enumerate(images_by_sku.items(), 1):
        print(f"[{i}/{len(images_by_sku)}] 📦 {sku}")

        # Find WordPress product
        product_info = get_product_by_sku(sku)

        if not product_info:
            print(f"      ⚠️  Product not found in WordPress (skipping)")
            stats['skipped'] += 1
            continue

        product_id, product_title = product_info
        print(f"      ✓ Found product ID {product_id} ({product_title})")

        # Get attachment IDs
        attachment_ids = [
            int(rec['wordpress_id'])
            for rec in image_records
            if rec['wordpress_id'].isdigit()
        ]

        if not attachment_ids:
            print(f"      ⚠️  No valid attachment IDs (skipping)")
            stats['skipped'] += 1
            continue

        print(f"      📸 {len(attachment_ids)} enhanced images to add")

        # Set featured image (first enhanced image)
        if not args.gallery_only:
            featured_id = attachment_ids[0]
            if set_featured_image(product_id, featured_id, args.dry_run):
                print(f"      ✅ Featured image set: #{featured_id}")
                stats['featured_set'] += 1
            else:
                print(f"      ❌ Failed to set featured image")
                stats['failed'] += 1

        # Update gallery (all enhanced images)
        if not args.featured_only:
            # Get existing gallery
            existing_gallery = get_product_gallery(product_id)

            # Merge: keep originals + add enhanced
            updated_gallery = existing_gallery + attachment_ids

            if set_product_gallery(product_id, updated_gallery, args.dry_run):
                print(f"      ✅ Gallery updated: {len(existing_gallery)} → {len(updated_gallery)} images")
                stats['products_updated'] += 1
                stats['images_added'] += len(attachment_ids)
            else:
                print(f"      ❌ Failed to update gallery")
                stats['failed'] += 1

        print()

    # Print summary
    print("=" * 80)
    print("ASSOCIATION SUMMARY")
    print("=" * 80)
    print(f"\nProducts found:    {stats['products_found']}")
    print(f"Products updated:  {stats['products_updated']}")
    print(f"Images added:      {stats['images_added']}")
    print(f"Featured set:      {stats['featured_set']}")
    print(f"Skipped:           {stats['skipped']}")
    print(f"Failed:            {stats['failed']}")

    print("\n" + "=" * 80)

    if not args.dry_run:
        print(f"\n✅ Products updated successfully!")
        print(f"📊 Next step: Regenerate thumbnails with WP-CLI\n")
        print(f"   docker exec {DOCKER_CONTAINER} wp media regenerate --yes --allow-root\n")


if __name__ == '__main__':
    main()
