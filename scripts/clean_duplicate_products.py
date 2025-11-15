#!/usr/bin/env python3
"""
Clean Duplicate WooCommerce Products
Migrates image metadata from duplicate products (with -2 suffix) to original products
and removes duplicates to fix broken product URLs.

Problem: Products imported twice, creating duplicates with "-2" suffix URLs.
Original URLs show no photos, "-2" URLs have photos but aren't used.

Solution: Migrate _thumbnail_id and _product_image_gallery from new to old, delete new.

Usage:
    python3 scripts/clean_duplicate_products.py --dry-run    # Preview changes
    python3 scripts/clean_duplicate_products.py              # Execute cleanup

Author: Claude Code (Sonnet 4.5)
Date: 2025-11-11
"""

import os
import subprocess
import argparse
import sys
from typing import Dict, List, Tuple

# Configuration
MYSQL_CONTAINER = "chapeus_mysql"
DB_NAME = "lisboetas_web"
DB_USER = "root"
DB_PASS = "rootpassword"

# Table prefix can vary per WordPress install. We'll try to detect it automatically.
TABLE_PREFIX_CANDIDATES = [
    os.environ.get('WP_TABLE_PREFIX'),  # explicit override if provided
    "wp_",
    "lx_"
]
TABLE_PREFIX = ""

# Meta keys to migrate from duplicate (new) product to the original
META_KEYS_TO_MIGRATE = [
    "_thumbnail_id",
    "_product_image_gallery",
    "_price",
    "_regular_price",
    "_sale_price",
    "_manage_stock",
    "_stock",
    "_stock_status",
    "_backorders",
    "_low_stock_amount"
]

# Stats
stats = {
    'duplicates_found': 0,
    'migrated': 0,
    'deleted': 0,
    'errors': []
}


def detect_table_prefix() -> str:
    """Detect which table prefix is being used in the WordPress database."""
    for candidate in TABLE_PREFIX_CANDIDATES:
        if not candidate:
            continue
        query = f"SHOW TABLES LIKE '{candidate}posts'"
        result = execute_sql(query)
        if result.strip():
            return candidate

    raise RuntimeError("Unable to detect WordPress table prefix.")


def get_table_prefix() -> str:
    """Return the detected table prefix (lazy detection)."""
    global TABLE_PREFIX
    if not TABLE_PREFIX:
        TABLE_PREFIX = detect_table_prefix()
    return TABLE_PREFIX


def execute_sql(query: str, fetch: bool = True) -> str:
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

    return result.stdout.strip() if fetch else ""


def find_duplicate_products() -> List[Tuple[int, str, int, str, str]]:
    """
    Find duplicate products by matching post_title.

    Returns:
        List of (old_id, old_slug, new_id, new_slug, title)
    """
    posts_table = f"{get_table_prefix()}posts"
    query = f"""
    SELECT
        old_p.ID as old_id,
        old_p.post_name as old_slug,
        new_p.ID as new_id,
        new_p.post_name as new_slug,
        old_p.post_title as title
    FROM {posts_table} old_p
    JOIN {posts_table} new_p ON new_p.post_name = CONCAT(old_p.post_name, '-2')
    WHERE old_p.post_type = 'product'
        AND new_p.post_type = 'product'
        AND old_p.post_status IN ('publish', 'draft', 'pending')
        AND new_p.post_status IN ('publish', 'draft', 'pending')
        AND old_p.post_name NOT LIKE '%-2'
    ORDER BY old_p.ID
    """

    result = execute_sql(query)

    if not result:
        return []

    duplicates = []
    for line in result.split('\n'):
        if line.strip():
            parts = line.split('\t')
            if len(parts) >= 5:
                old_id, old_slug, new_id, new_slug, title = parts[0], parts[1], parts[2], parts[3], '\t'.join(parts[4:])
                duplicates.append((int(old_id), old_slug, int(new_id), new_slug, title))

    return duplicates


def fetch_product_meta(product_id: int, meta_keys: List[str]) -> Dict[str, str]:
    """Return a dict of meta_key -> meta_value for selected keys."""
    if not meta_keys:
        return {}

    meta_table = f"{get_table_prefix()}postmeta"
    keys_clause = ",".join(f"'{key}'" for key in meta_keys)
    query = f"""
    SELECT meta_key, meta_value
    FROM {meta_table}
    WHERE post_id = {product_id}
        AND meta_key IN ({keys_clause})
    """

    result = execute_sql(query)
    meta: Dict[str, str] = {}

    if not result:
        return meta

    for line in result.split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t', 1)
        key = parts[0]
        value = parts[1] if len(parts) > 1 else ""
        meta[key] = value

    return meta


def escape_meta_value(value: str) -> str:
    """Escape characters that would break SQL statements."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def upsert_meta(post_id: int, meta_key: str, meta_value: str):
    """Insert/update a product meta key."""
    meta_table = f"{get_table_prefix()}postmeta"
    escaped = escape_meta_value(meta_value)
    query = f"""
    INSERT INTO {meta_table} (post_id, meta_key, meta_value)
    VALUES ({post_id}, '{meta_key}', '{escaped}')
    ON DUPLICATE KEY UPDATE meta_value='{escaped}'
    """
    execute_sql(query, fetch=False)


def migrate_meta(old_id: int, new_id: int, dry_run: bool = False) -> bool:
    """Migrate selected metadata (images, price, stock) from duplicate to original."""

    meta = fetch_product_meta(new_id, META_KEYS_TO_MIGRATE)

    if '_thumbnail_id' not in meta:
        print(f"      ⚠️  No thumbnail found on duplicate product {new_id}")
        return False

    if dry_run:
        print(f"      [DRY RUN] Would migrate:")
        for key, value in meta.items():
            preview = value
            if len(preview) > 100:
                preview = preview[:97] + "..."
            print(f"        {key}: {preview}")
        return True

    try:
        for key, value in meta.items():
            upsert_meta(old_id, key, value)

        return True

    except Exception as e:
        print(f"      ❌ Migration error: {e}")
        stats['errors'].append({
            'old_id': old_id,
            'new_id': new_id,
            'error': str(e)
        })
        return False


def delete_duplicate_product(product_id: int, dry_run: bool = False) -> bool:
    """
    Delete duplicate product (force delete, bypass trash).

    Args:
        product_id: Product ID to delete
        dry_run: If True, don't execute

    Returns:
        True if success
    """
    if dry_run:
        print(f"      [DRY RUN] Would delete product {product_id}")
        return True

    try:
        # Direct SQL delete (faster than WP-CLI for bulk operations)
        prefix = get_table_prefix()
        posts_table = f"{prefix}posts"
        meta_table = f"{prefix}postmeta"

        query_post = f"DELETE FROM {posts_table} WHERE ID = {product_id}"
        execute_sql(query_post, fetch=False)

        query_meta = f"DELETE FROM {meta_table} WHERE post_id = {product_id}"
        execute_sql(query_meta, fetch=False)

        return True

    except Exception as e:
        print(f"      ❌ Delete error: {e}")
        stats['errors'].append({
            'product_id': product_id,
            'error': str(e)
        })
        return False


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Clean duplicate WooCommerce products'
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without executing')

    args = parser.parse_args()

    # Print header
    print("=" * 80)
    print("CLEAN DUPLICATE WOOCOMMERCE PRODUCTS")
    print("=" * 80)
    print(f"\nDatabase: {MYSQL_CONTAINER} / {DB_NAME}")
    print(f"Mode: {'DRY RUN (no changes)' if args.dry_run else 'PRODUCTION (will modify database)'}")
    print("\n" + "-" * 80 + "\n")

    # Find duplicates
    print("🔍 Searching for duplicate products...")
    duplicates = find_duplicate_products()

    if not duplicates:
        print("✅ No duplicates found! Database is clean.")
        sys.exit(0)

    stats['duplicates_found'] = len(duplicates)
    print(f"📋 Found {len(duplicates)} duplicate pairs\n")
    print("-" * 80 + "\n")

    # Process each duplicate
    for i, (old_id, old_slug, new_id, new_slug, title) in enumerate(duplicates, 1):
        print(f"[{i}/{len(duplicates)}] 🔄 {title[:60]}")
        print(f"    Original: ID {old_id} → /{old_slug}/")
        print(f"    Duplicate: ID {new_id} → /{new_slug}/")

        # Step 1: Migrate metadata
        success = migrate_meta(old_id, new_id, args.dry_run)

        if success:
            stats['migrated'] += 1
            print(f"    ✓ Images migrated")

            # Step 2: Delete duplicate
            deleted = delete_duplicate_product(new_id, args.dry_run)

            if deleted:
                stats['deleted'] += 1
                print(f"    ✓ Duplicate deleted")
            else:
                print(f"    ✗ Delete failed")
        else:
            print(f"    ✗ Migration failed")

        print()

    # Print summary
    print("=" * 80)
    print("CLEANUP SUMMARY")
    print("=" * 80)
    print(f"Duplicate pairs found: {stats['duplicates_found']}")
    print(f"Images migrated: {stats['migrated']} ✓")
    print(f"Duplicates deleted: {stats['deleted']} ✓")

    if stats['errors']:
        print(f"\n❌ {len(stats['errors'])} errors occurred:")
        for error in stats['errors'][:10]:
            print(f"  - {error}")

        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")

    print("\n" + "=" * 80)

    if not args.dry_run and stats['migrated'] > 0:
        print("\n✅ Duplicate cleanup complete!")
        print("\nNext steps:")
        print("1. Verify original URLs now show photos:")
        print("   http://localhost:8080/product/boina-oitava-harris-tweed/")
        print("   http://localhost:8080/product/boina-piemonte-mix-wool/")
        print("2. Clear WordPress cache: docker exec chapeus_wordpress wp cache flush --allow-root")
        print("3. Check shop page for any remaining issues")

    # Exit code
    if stats['errors']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
