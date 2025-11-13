#!/usr/bin/env python3
"""
Validate AI-Enhanced Images Quality and Completeness
Checks all enhanced images for quality, dimensions, and completeness.

Usage:
    python3 scripts/validate_enhanced_images.py
    python3 scripts/validate_enhanced_images.py --detailed
    python3 scripts/validate_enhanced_images.py --export-report

Author: Claude Code (Opus 4.1)
Date: 2025-11-13
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image

# Configuration
BASE_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)")
PRODUCTS_PATH = BASE_PATH / "wordpress/wp-content/uploads/products"
MIN_WIDTH = 800
MIN_HEIGHT = 800
MAX_FILE_SIZE_MB = 5
REPORT_PATH = BASE_PATH / "relatorios/ai_validation_report.csv"

# Stats
stats = {
    'total_enhanced': 0,
    'valid': 0,
    'warnings': 0,
    'errors': 0,
    'issues': []
}


def validate_image(img_path: Path, detailed: bool = False) -> Dict:
    """
    Validate single image.

    Returns:
        Dict with validation results
    """
    result = {
        'file': img_path.name,
        'sku': img_path.parent.name,
        'path': str(img_path.relative_to(BASE_PATH)),
        'valid': True,
        'issues': []
    }

    try:
        # Check file exists and readable
        if not img_path.exists():
            result['valid'] = False
            result['issues'].append('File not found')
            return result

        # Get file size
        file_size_mb = img_path.stat().st_size / (1024 * 1024)
        result['size_mb'] = round(file_size_mb, 2)

        if file_size_mb > MAX_FILE_SIZE_MB:
            result['issues'].append(f'File too large ({file_size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB)')

        # Open and validate image
        with Image.open(img_path) as img:
            width, height = img.size
            result['width'] = width
            result['height'] = height
            result['format'] = img.format
            result['mode'] = img.mode

            # Check dimensions
            if width < MIN_WIDTH:
                result['issues'].append(f'Width too small ({width}px < {MIN_WIDTH}px)')
            if height < MIN_HEIGHT:
                result['issues'].append(f'Height too small ({height}px < {MIN_HEIGHT}px)')

            # Check format
            if img.format not in ['JPEG', 'JPG', 'PNG']:
                result['issues'].append(f'Invalid format ({img.format})')

            # Check mode (should be RGB or RGBA)
            if img.mode not in ['RGB', 'RGBA']:
                result['issues'].append(f'Invalid color mode ({img.mode})')

            # Detailed checks
            if detailed:
                # Check if image is corrupted
                try:
                    img.verify()
                except Exception as e:
                    result['issues'].append(f'Corrupted image: {e}')

        # Mark as invalid if any issues
        if result['issues']:
            result['valid'] = False

    except Exception as e:
        result['valid'] = False
        result['issues'].append(f'Error: {str(e)}')

    return result


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Validate AI-enhanced images'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Run detailed validation (slower)'
    )
    parser.add_argument(
        '--export-report',
        action='store_true',
        help='Export validation report to CSV'
    )

    args = parser.parse_args()

    # Print header
    print("=" * 80)
    print("VALIDATE AI-ENHANCED IMAGES")
    print("=" * 80)
    print(f"\nMode: {'DETAILED' if args.detailed else 'QUICK'}")
    print(f"Min dimensions: {MIN_WIDTH}×{MIN_HEIGHT}px")
    print(f"Max file size: {MAX_FILE_SIZE_MB}MB")
    print("\n" + "-" * 80 + "\n")

    # Find all enhanced images
    enhanced_images = sorted(PRODUCTS_PATH.rglob("*_pro.*"))
    stats['total_enhanced'] = len(enhanced_images)

    print(f"📊 Found {stats['total_enhanced']} enhanced images\n")

    if not enhanced_images:
        print("❌ No enhanced images found!")
        return

    print("-" * 80 + "\n")

    # Validate each image
    validation_results = []

    for i, img_path in enumerate(enhanced_images, 1):
        result = validate_image(img_path, args.detailed)
        validation_results.append(result)

        # Print progress
        if result['valid']:
            print(f"[{i}/{len(enhanced_images)}] ✅ {result['file']} "
                  f"({result.get('width', '?')}×{result.get('height', '?')}px, "
                  f"{result.get('size_mb', '?')}MB)")
            stats['valid'] += 1
        else:
            print(f"[{i}/{len(enhanced_images)}] ❌ {result['file']}")
            for issue in result['issues']:
                print(f"      • {issue}")

            if len(result['issues']) > 0:
                stats['errors'] += 1
                stats['issues'].extend(result['issues'])

    # Export report if requested
    if args.export_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(REPORT_PATH, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'sku', 'file', 'valid', 'width', 'height',
                'size_mb', 'format', 'mode', 'issues', 'path'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in validation_results:
                row = {
                    'sku': result['sku'],
                    'file': result['file'],
                    'valid': result['valid'],
                    'width': result.get('width', ''),
                    'height': result.get('height', ''),
                    'size_mb': result.get('size_mb', ''),
                    'format': result.get('format', ''),
                    'mode': result.get('mode', ''),
                    'issues': '; '.join(result['issues']),
                    'path': result['path']
                }
                writer.writerow(row)

        print(f"\n✅ Report exported: {REPORT_PATH}")

    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"\nTotal enhanced:  {stats['total_enhanced']}")
    print(f"Valid:           {stats['valid']} ({stats['valid']/stats['total_enhanced']*100:.1f}%)")
    print(f"Errors:          {stats['errors']}")

    if stats['errors'] > 0:
        print(f"\n⚠️  Top issues:")
        # Count issue types
        issue_counts = {}
        for issue in stats['issues']:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"  • {issue}: {count}x")

    print("\n" + "=" * 80)

    if stats['valid'] == stats['total_enhanced']:
        print("\n✅ All images passed validation!\n")
    else:
        print(f"\n⚠️  {stats['errors']} images with issues - review report\n")


if __name__ == '__main__':
    main()
