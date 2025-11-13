#!/usr/bin/env python3
"""
Gemini 2.5 Flash Image - Professional E-commerce Photo Generator
Transforms existing product images into professional e-commerce photos using Gemini AI.

Usage:
    python3 scripts/gemini_image_pro.py --test                    # Test with 1 product
    python3 scripts/gemini_image_pro.py --limit=5                 # Process 5 products
    python3 scripts/gemini_image_pro.py                           # Full run (918 images)
    python3 scripts/gemini_image_pro.py --dry-run                 # Preview only

Author: Claude Code (Sonnet 4.5) + Gemini Nano Banana v2
Date: 2025-11-11
"""

import asyncio
import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import new Gemini SDK
try:
    from google import genai
    from google.api_core import exceptions
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install google-genai google-api-core")
    sys.exit(1)

from PIL import Image

# Configuration
GEMINI_API_KEYS = [
    "AIzaSyDWCanKI3CtqyIWTOpaPVPVtmGOW6A7OaE",
    "AIzaSyBXEsObFgYVwqzDH3fvYXP45FWi8UGiLRo"
]
GEMINI_MODEL = "gemini-2.5-flash-image"
IMAGE_BASE_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/uploads/products")
CSV_FILE = Path("output_catalogo/woocommerce_import.csv")
COST_PER_IMAGE = 0.039  # USD

# API key rotation
current_key_index = 0
client = None

# Stats tracking
stats = {
    'total_images': 0,
    'processed': 0,
    'failed': 0,
    'skipped': 0,
    'cost_usd': 0.0,
    'errors': []
}


def rotate_api_key():
    """Rotate to next API key when quota exhausted."""
    global current_key_index, client
    current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
    api_key = GEMINI_API_KEYS[current_key_index]
    client = genai.Client(api_key=api_key)
    print(f"🔄 Rotated to API key #{current_key_index + 1}")


def init_client():
    """Initialize Gemini client with first API key."""
    global client
    api_key = GEMINI_API_KEYS[current_key_index]
    client = genai.Client(api_key=api_key)
    print(f"✓ Initialized Gemini client (key #{current_key_index + 1})")


def get_image_type(filename: str) -> str:
    """
    Determine image type based on filename patterns.

    Returns:
        'isolated': Product on plain background
        'lifestyle': Person wearing product
        'detail': Close-up texture shot
    """
    filename_lower = filename.lower()

    # Lifestyle indicators
    if any(word in filename_lower for word in ['lifestyle', 'worn', 'person', 'model']):
        return 'lifestyle'

    # Detail indicators
    if any(word in filename_lower for word in ['detail', 'texture', 'close', 'macro']):
        return 'detail'

    # Default to isolated product shot
    return 'isolated'


def get_prompt_for_type(image_type: str, product_name: str) -> str:
    """
    Generate optimized prompt based on image type.

    Uses narrative descriptions (not keyword lists) as per best practices.
    """
    if image_type == 'isolated':
        return f"""Create a professional e-commerce product photograph of this {product_name}.
        The image should feature the hat centered on a pure white background with no shadows or distractions.
        Use soft, even studio lighting that brings out the texture and color of the material without harsh shadows.
        The hat should be photographed straight-on at eye level, showing its full form and shape clearly.
        Ensure the colors are accurate and vibrant, the details are sharp and well-defined,
        and the overall composition is clean and professional suitable for an online store."""

    elif image_type == 'lifestyle':
        return f"""Transform this photograph into an editorial-style lifestyle shot of someone wearing this {product_name}.
        The person's face and the hat should both be clearly visible and well-composed in the center of the frame.
        Use a softly blurred neutral background that doesn't compete with the subject.
        Apply natural, flattering lighting that highlights both the person and the hat's details.
        The overall aesthetic should feel like a fashion magazine editorial - sophisticated,
        professional, and aspirational while maintaining authenticity."""

    else:  # detail
        return f"""Create an intimate close-up detail photograph of this {product_name}'s material and craftsmanship.
        Focus on capturing the texture, weave pattern, stitching quality, or unique material characteristics
        that make this hat special. Use macro photography techniques with shallow depth of field to create
        visual interest, with the main textural elements in sharp focus while the background softly fades.
        The lighting should be directional to emphasize the three-dimensional quality of the material,
        creating subtle shadows that reveal depth and texture."""


async def generate_enhanced_image(
    source_path: Path,
    image_type: str,
    product_name: str,
    output_path: Path,
    dry_run: bool = False
) -> bool:
    """
    Generate professional version of image using Gemini 2.5 Flash Image.

    Args:
        source_path: Path to original image
        image_type: 'isolated', 'lifestyle', or 'detail'
        product_name: Product name for context
        output_path: Where to save enhanced image
        dry_run: If True, don't actually generate

    Returns:
        True if success, False if failed
    """
    if dry_run:
        print(f"      [DRY RUN] Would enhance {source_path.name} ({image_type})")
        return True

    try:
        # Read image as PIL Image
        img = Image.open(source_path)

        # Get optimized prompt
        prompt = get_prompt_for_type(image_type, product_name)

        # Generate with Gemini (with retry logic)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[prompt, img]
                )

                # Check for safety filter blocks
                if response.candidates[0].finish_reason != "STOP":
                    reason = response.candidates[0].finish_reason
                    print(f"      ⚠️  Generation blocked: {reason}")
                    stats['errors'].append({
                        'file': source_path.name,
                        'error': f'Safety filter: {reason}'
                    })
                    return False

                # Extract and save image
                for part in response.parts:
                    if part.inline_data is not None:
                        # Get image data
                        image_data = part.inline_data.data

                        # Save directly as bytes
                        with open(output_path, 'wb') as f:
                            f.write(image_data)

                        # Update stats
                        stats['processed'] += 1
                        stats['cost_usd'] += COST_PER_IMAGE

                        return True

                # No image in response
                print(f"      ❌ No image in response")
                return False

            except exceptions.ResourceExhausted:
                if attempt < max_retries - 1:
                    print(f"      ⏳ Quota exceeded, rotating API key...")
                    rotate_api_key()
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

            except exceptions.InvalidArgument as e:
                print(f"      ❌ Invalid argument: {e}")
                stats['errors'].append({
                    'file': source_path.name,
                    'error': str(e)
                })
                return False

    except Exception as e:
        print(f"      ❌ Error: {e}")
        stats['errors'].append({
            'file': source_path.name,
            'error': str(e)
        })
        stats['failed'] += 1
        return False


async def process_product_images(
    product_name: str,
    sku: str,
    images_str: str,
    dry_run: bool = False
) -> Tuple[int, int]:
    """
    Process all images for a single product.

    Args:
        product_name: Product name
        sku: Product SKU
        images_str: Comma-separated image paths from CSV
        dry_run: Preview mode

    Returns:
        (success_count, failed_count)
    """
    if not images_str:
        return (0, 0)

    # Parse image paths
    image_paths = [path.strip() for path in images_str.split(',')]

    success = 0
    failed = 0

    for img_path in image_paths:
        # Clean path from CSV format
        img_path = img_path.replace('catalogo2025/', '').replace('%20', ' ')

        # Build full path
        source_path = IMAGE_BASE_PATH / img_path

        if not source_path.exists():
            print(f"      ⚠️  Image not found: {img_path}")
            stats['skipped'] += 1
            continue

        # Determine image type
        image_type = get_image_type(source_path.name)

        # Build output path (add _pro suffix before extension)
        output_path = source_path.parent / f"{source_path.stem}_pro{source_path.suffix}"

        print(f"      🖼️  {source_path.name} ({image_type})", end=' ')

        # Generate enhanced version
        result = await generate_enhanced_image(
            source_path,
            image_type,
            product_name,
            output_path,
            dry_run
        )

        if result:
            print("✓")
            success += 1
        else:
            print("✗")
            failed += 1

        # Small delay to avoid rate limits
        if not dry_run:
            await asyncio.sleep(0.5)

    return (success, failed)


async def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Generate professional e-commerce photos with Gemini')
    parser.add_argument('--test', action='store_true', help='Test with 1 product only')
    parser.add_argument('--limit', type=int, help='Limit number of products')
    parser.add_argument('--dry-run', action='store_true', help='Preview only (no generation)')
    parser.add_argument('--csv', default=CSV_FILE, help='CSV file to process')

    args = parser.parse_args()

    # Check CSV exists
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)

    # Initialize Gemini client
    init_client()

    # Print header
    print("=" * 80)
    print("GEMINI 2.5 FLASH IMAGE - PROFESSIONAL PHOTO GENERATOR")
    print("=" * 80)
    print(f"\nModel: {GEMINI_MODEL}")
    print(f"Cost: ${COST_PER_IMAGE} per image")
    print(f"Mode: {'TEST' if args.test else 'DRY RUN' if args.dry_run else 'PRODUCTION'}")
    print(f"CSV: {csv_path}")
    print("\n" + "-" * 80)

    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Filter: only products with prices (active products)
    active_rows = [
        row for row in rows
        if row.get('Regular price', '').strip()
    ]

    print(f"\n📋 Found {len(active_rows)} active products (out of {len(rows)} total)")

    # Count total images
    for row in active_rows:
        images_str = row.get('Images', '').strip()
        if images_str:
            stats['total_images'] += len(images_str.split(','))

    print(f"🖼️  Total images to process: {stats['total_images']}")
    print(f"💰 Estimated cost: ${stats['total_images'] * COST_PER_IMAGE:.2f} USD")

    if args.test:
        active_rows = active_rows[:1]
        print(f"\n🧪 TEST MODE: Processing 1 product only\n")
    elif args.limit:
        active_rows = active_rows[:args.limit]
        print(f"\n📊 LIMITED: Processing {len(active_rows)} products\n")
    else:
        print(f"\n🚀 FULL RUN: Processing all {len(active_rows)} products\n")

    print("-" * 80 + "\n")

    # Process products
    start_time = time.time()

    for i, row in enumerate(active_rows, 1):
        sku = row.get('SKU', '').strip()
        name = row.get('Name', '').strip()
        images_str = row.get('Images', '').strip()

        # Clean SKU
        if '\n' in sku:
            sku = sku.split('\n')[0].strip()

        if not sku or not name:
            continue

        print(f"[{i}/{len(active_rows)}] 🎩 {name[:60]}")

        # Process all images for this product
        success, failed = await process_product_images(name, sku, images_str, args.dry_run)

        print(f"    ✓ {success} enhanced, ✗ {failed} failed\n")

    # Calculate duration
    duration = time.time() - start_time

    # Print summary
    print("\n" + "=" * 80)
    print("GENERATION SUMMARY")
    print("=" * 80)
    print(f"Total images: {stats['total_images']}")
    print(f"Processed: {stats['processed']} ✓")
    print(f"Failed: {stats['failed']} ✗")
    print(f"Skipped: {stats['skipped']} ⏭")
    print(f"Total cost: ${stats['cost_usd']:.2f} USD")
    print(f"Duration: {duration/60:.1f} minutes")

    if stats['errors']:
        print(f"\n❌ {len(stats['errors'])} errors occurred:")
        for error in stats['errors'][:10]:
            print(f"  - {error['file']}: {error['error'][:100]}")

        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")

    print("\n" + "=" * 80)

    if not args.dry_run and stats['processed'] > 0:
        print(f"\n✅ Generated {stats['processed']} professional photos!")
        print(f"   Next step: Register in WordPress with register_enhanced_images.py")

    # Exit code
    if stats['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
