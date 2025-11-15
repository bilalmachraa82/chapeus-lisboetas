#!/usr/bin/env python3
"""
Update WooCommerce import CSV to use AI-enhanced images instead of originals.

Replaces:
  img_01.jpg -> img_01_pro.jpg
  img_02.jpg -> img_02_pro.jpg
  etc.

Only updates images that exist as *_pro.jpg files.
"""

import csv
import sys
from pathlib import Path
from typing import List

CSV_INPUT = Path('output_catalogo/woocommerce_import_localhost.csv')
CSV_OUTPUT = Path('output_catalogo/woocommerce_import_AI_READY.csv')
IMAGES_BASE = Path('wordpress/wp-content/uploads/products')


def get_available_ai_images() -> set:
    """Get set of all available AI image paths."""
    ai_images = set()

    for img in IMAGES_BASE.rglob('*_pro.jpg'):
        # Convert to WordPress path format
        # wordpress/wp-content/uploads/products/boinas inverno/bone-18074/img_01_pro.jpg
        # -> /wp-content/uploads/products/boinas inverno/bone-18074/img_01_pro.jpg
        rel_path = img.relative_to(Path('wordpress'))
        wp_path = f"/{rel_path}"
        ai_images.add(wp_path)

    return ai_images


def update_image_path(original_path: str, ai_images: set) -> str:
    """
    Update single image path if AI version exists.

    Args:
        original_path: Original image URL
        ai_images: Set of available AI image paths

    Returns:
        Updated path with _pro.jpg if exists, otherwise original
    """
    if not original_path or not original_path.strip():
        return original_path

    # Extract path from URL
    # http://localhost:8080/wp-content/uploads/.../img_01.jpg
    # -> /wp-content/uploads/.../img_01_pro.jpg
    if '/wp-content/' in original_path:
        path_part = original_path.split('localhost:8080')[1] if 'localhost:8080' in original_path else original_path

        # Try to replace with _pro version
        if path_part.endswith('.jpg'):
            pro_path = path_part.replace('.jpg', '_pro.jpg')

            if pro_path in ai_images:
                # Reconstruct full URL
                return f"http://localhost:8080{pro_path}"

    return original_path


def main():
    """Update CSV with AI images."""

    if not CSV_INPUT.exists():
        print(f"❌ CSV not found: {CSV_INPUT}")
        return 1

    print("="*70)
    print("UPDATE CSV WITH AI IMAGES")
    print("="*70)
    print(f"Input:  {CSV_INPUT}")
    print(f"Output: {CSV_OUTPUT}")
    print("="*70 + "\n")

    # Get available AI images
    print("🔍 Scanning for AI images...")
    ai_images = get_available_ai_images()
    print(f"✓ Found {len(ai_images)} AI images\n")

    # Read and update CSV
    print("📝 Updating CSV...")

    stats = {
        'products': 0,
        'images_original': 0,
        'images_updated': 0
    }

    with open(CSV_INPUT, 'r', encoding='utf-8') as infile, \
         open(CSV_OUTPUT, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            stats['products'] += 1

            # Update Images column (comma-separated list)
            if row.get('Images'):
                original_images = [img.strip() for img in row['Images'].split(',')]
                stats['images_original'] += len(original_images)

                updated_images = []
                for img_url in original_images:
                    updated_url = update_image_path(img_url, ai_images)
                    updated_images.append(updated_url)

                    if updated_url != img_url:
                        stats['images_updated'] += 1

                row['Images'] = ', '.join(updated_images)

            writer.writerow(row)

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"✓ Products processed: {stats['products']}")
    print(f"✓ Original images: {stats['images_original']}")
    print(f"✓ Updated to AI: {stats['images_updated']}")
    print(f"✓ Kept original: {stats['images_original'] - stats['images_updated']}")
    print(f"\n💾 Output saved to: {CSV_OUTPUT}")
    print(f"{'='*70}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
