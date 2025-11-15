#!/usr/bin/env python3
"""
Optimize AI-generated images for web performance.
Reduces file size by 80-90% while maintaining visual quality.

Target: 1MB → 150-200KB per image
Method: PIL with quality=85 and optimize=True
"""

from pathlib import Path
from PIL import Image
import sys

def optimize_image(image_path: Path, quality: int = 85, max_dimension: int = 2048):
    """
    Optimize a single image for web.

    Args:
        image_path: Path to image
        quality: JPEG quality (default 85)
        max_dimension: Max width/height (default 2048px)

    Returns:
        (original_size_kb, new_size_kb, reduction_pct)
    """
    try:
        # Get original size
        original_size = image_path.stat().st_size

        # Open image
        img = Image.open(image_path)

        # Convert RGBA to RGB if needed (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Resize if too large
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Save optimized
        img.save(
            image_path,
            'JPEG',
            quality=quality,
            optimize=True,
            progressive=True
        )

        # Get new size
        new_size = image_path.stat().st_size

        # Calculate reduction
        reduction = ((original_size - new_size) / original_size) * 100

        return (
            original_size / 1024,  # KB
            new_size / 1024,       # KB
            reduction              # %
        )

    except Exception as e:
        print(f"❌ Error optimizing {image_path.name}: {e}")
        return None


def main():
    """Optimize all *_pro.jpg images."""

    # Find all AI images
    base_path = Path('wordpress/wp-content/uploads/products')
    images = list(base_path.rglob('*_pro.jpg'))

    if not images:
        print("❌ No *_pro.jpg images found")
        return 1

    print(f"🖼️  Found {len(images)} images to optimize")
    print(f"📦 Starting optimization (quality=85)...\n")

    stats = {
        'total': len(images),
        'success': 0,
        'failed': 0,
        'original_size_kb': 0,
        'new_size_kb': 0
    }

    for i, img_path in enumerate(images, 1):
        result = optimize_image(img_path)

        if result:
            orig_kb, new_kb, reduction = result
            stats['success'] += 1
            stats['original_size_kb'] += orig_kb
            stats['new_size_kb'] += new_kb

            # Progress indicator
            if i % 50 == 0 or i == len(images):
                print(f"[{i}/{len(images)}] ✓ {reduction:.1f}% reduction ({orig_kb:.0f}KB → {new_kb:.0f}KB)")
        else:
            stats['failed'] += 1

    # Final report
    print(f"\n{'='*60}")
    print(f"📊 OPTIMIZATION COMPLETE")
    print(f"{'='*60}")
    print(f"✓ Success: {stats['success']} images")
    print(f"✗ Failed: {stats['failed']} images")
    print(f"📉 Size reduction: {stats['original_size_kb']/1024:.1f} MB → {stats['new_size_kb']/1024:.1f} MB")
    print(f"💾 Space saved: {(stats['original_size_kb'] - stats['new_size_kb'])/1024:.1f} MB ({((stats['original_size_kb'] - stats['new_size_kb']) / stats['original_size_kb']) * 100:.1f}%)")
    print(f"{'='*60}\n")

    return 0 if stats['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
