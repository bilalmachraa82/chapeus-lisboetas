#!/usr/bin/env python3
"""
Register AI-Enhanced Images to WordPress Media Library
Scans for *_pro.jpg files and registers them in WordPress.

Usage:
    python3 scripts/register_enhanced_images.py
    python3 scripts/register_enhanced_images.py --dry-run
    python3 scripts/register_enhanced_images.py --limit=10

Author: Claude Code (Opus 4.1)
Date: 2025-11-13
"""

import argparse
import csv
import hashlib
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
BASE_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)")
PRODUCTS_PATH = BASE_PATH / "wordpress/wp-content/uploads/products"
DOCKER_CONTAINER = "chapeus_wordpress"
TRACKING_CSV = BASE_PATH / "relatorios/ai_enhanced_images_registered.csv"

# Stats
stats = {
    'found': 0,
    'registered': 0,
    'skipped': 0,
    'failed': 0,
    'errors': []
}


def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def is_already_registered(file_path: Path) -> bool:
    """Check if file already registered in tracking CSV."""
    if not TRACKING_CSV.exists():
        return False

    file_hash = get_file_hash(file_path)

    with open(TRACKING_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('file_hash') == file_hash:
                return True

    return False


def register_image_in_wordpress(
    file_path: Path,
    dry_run: bool = False
) -> Optional[int]:
    """
    Register image in WordPress Media Library using WP-CLI.

    Args:
        file_path: Path to image file
        dry_run: If True, only simulate

    Returns:
        WordPress attachment ID or None if failed
    """
    if dry_run:
        print(f"      [DRY RUN] Would register: {file_path.name}")
        return 99999

    try:
        # Get relative path from wp-content/uploads
        relative_path = file_path.relative_to(BASE_PATH / "wordpress/wp-content/uploads")

        # Build WP-CLI command
        # wp media import /var/www/html/wp-content/uploads/products/...
        cmd = [
            "docker", "exec", DOCKER_CONTAINER,
            "wp", "media", "import",
            f"/var/www/html/wp-content/uploads/{relative_path}",
            "--porcelain",  # Output only attachment ID
            "--allow-root"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            attachment_id = int(result.stdout.strip())
            return attachment_id
        else:
            error_msg = result.stderr.strip()
            print(f"      ❌ WP-CLI error: {error_msg}")
            stats['errors'].append({
                'file': str(file_path),
                'error': error_msg
            })
            return None

    except subprocess.TimeoutExpired:
        print(f"      ❌ Timeout registering image")
        stats['errors'].append({
            'file': str(file_path),
            'error': 'Timeout after 30s'
        })
        return None

    except Exception as e:
        print(f"      ❌ Error: {e}")
        stats['errors'].append({
            'file': str(file_path),
            'error': str(e)
        })
        return None


def save_to_tracking_csv(records: List[Dict]) -> None:
    """Save registered images to tracking CSV."""
    if not records:
        return

    # Create directory if needed
    TRACKING_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Check if file exists to determine if we need headers
    file_exists = TRACKING_CSV.exists()

    with open(TRACKING_CSV, 'a', encoding='utf-8', newline='') as f:
        fieldnames = [
            'timestamp',
            'file_path',
            'file_hash',
            'wordpress_id',
            'sku',
            'product_name',
            'file_size_kb',
            'status'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for record in records:
            writer.writerow(record)


def extract_sku_from_path(file_path: Path) -> str:
    """Extract SKU from file path (parent directory name)."""
    return file_path.parent.name


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Register AI-enhanced images in WordPress Media Library'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview only, do not register'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of images to register'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-register even if already in tracking CSV'
    )

    args = parser.parse_args()

    # Print header
    print("=" * 80)
    print("REGISTER AI-ENHANCED IMAGES TO WORDPRESS")
    print("=" * 80)
    print(f"\nMode: {'DRY RUN' if args.dry_run else 'PRODUCTION'}")
    print(f"Source: {PRODUCTS_PATH}")
    print(f"Tracking: {TRACKING_CSV}")
    print("\n" + "-" * 80 + "\n")

    # Find all *_pro.* files
    enhanced_images = sorted(PRODUCTS_PATH.rglob("*_pro.*"))
    stats['found'] = len(enhanced_images)

    print(f"📊 Found {stats['found']} enhanced images\n")

    if not enhanced_images:
        print("❌ No enhanced images found. Has AI processing completed?")
        sys.exit(1)

    # Apply limit if specified
    if args.limit:
        enhanced_images = enhanced_images[:args.limit]
        print(f"📊 Limited to {len(enhanced_images)} images\n")

    print("-" * 80 + "\n")

    # Track records for CSV
    registered_records = []

    # Process each image
    for i, img_path in enumerate(enhanced_images, 1):
        sku = extract_sku_from_path(img_path)
        file_size_kb = img_path.stat().st_size // 1024

        print(f"[{i}/{len(enhanced_images)}] 🖼️  {img_path.name} ({sku})")

        # Check if already registered (unless --force)
        if not args.force and is_already_registered(img_path):
            print(f"      ⏭️  Already registered (skipping)")
            stats['skipped'] += 1
            continue

        # Register in WordPress
        wp_id = register_image_in_wordpress(img_path, args.dry_run)

        if wp_id:
            print(f"      ✅ Registered as attachment #{wp_id}")
            stats['registered'] += 1

            # Add to tracking
            registered_records.append({
                'timestamp': datetime.now().isoformat(),
                'file_path': str(img_path.relative_to(BASE_PATH)),
                'file_hash': get_file_hash(img_path),
                'wordpress_id': wp_id,
                'sku': sku,
                'product_name': '',  # Will be filled by association script
                'file_size_kb': file_size_kb,
                'status': 'registered'
            })
        else:
            print(f"      ❌ Failed to register")
            stats['failed'] += 1

    # Save tracking records
    if registered_records and not args.dry_run:
        save_to_tracking_csv(registered_records)
        print(f"\n✅ Tracking saved to: {TRACKING_CSV}")

    # Print summary
    print("\n" + "=" * 80)
    print("REGISTRATION SUMMARY")
    print("=" * 80)
    print(f"\nFound:       {stats['found']}")
    print(f"Registered:  {stats['registered']}")
    print(f"Skipped:     {stats['skipped']}")
    print(f"Failed:      {stats['failed']}")

    if stats['errors']:
        print(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
        print("\nFirst 5 errors:")
        for error in stats['errors'][:5]:
            print(f"  • {Path(error['file']).name}: {error['error']}")

    print("\n" + "=" * 80)

    if not args.dry_run:
        print(f"\n✅ Tracking CSV: {TRACKING_CSV}")
        print(f"📊 Next step: Run associate_enhanced_images.py to link to products\n")


if __name__ == '__main__':
    main()
