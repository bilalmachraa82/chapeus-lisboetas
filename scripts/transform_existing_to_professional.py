#!/usr/bin/env python3
"""
Transform Existing Product Images → Professional E-commerce Shoot
Uses Google Gemini Flash 2.5 to enhance existing product photos from server

Workflow:
1. Read CSV to get list of products with prices (ACTIVE only)
2. For each product's images on server:
   - Detect image type (product isolated vs lifestyle)
   - Apply Gemini enhancement
   - Save as _pro version
3. Register enhanced images in WordPress

Author: Claude Code (Sonnet 4.5)
Date: 2025-11-10
"""

import os
import csv
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import google.generativeai as genai
from PIL import Image

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
CSV_FILE = "output_catalogo/woocommerce_import.csv"
IMAGES_BASE_DIR = "/var/www/html/wp-content/uploads/products"
CONTAINER_NAME = "chapeus_wordpress"

# Gemini Configuration (2 API keys for quota rotation)
GEMINI_API_KEYS = [
    "AIzaSyBXEsObFgYVwqzDH3fvYXP45FWi8UGiLRo",
    "AIzaSyDWCanKI3CtqyIWTOpaPVPVtmGOW6A7OaE"
]
CURRENT_KEY_INDEX = 0
GEMINI_MODEL = "gemini-2.5-flash-image"  # Nano Banana - Image generation model

# Output Configuration
OUTPUT_SUFFIX = "_pro"  # img_01.jpg → img_01_pro.jpg
PRESERVE_ORIGINAL = True

# Stats tracking
stats = {
    'total_products': 0,
    'total_images': 0,
    'enhanced': 0,
    'failed': 0,
    'skipped': 0,
    'errors': []
}


# ============================================================================
# GEMINI PROMPTS (E-commerce Best Practices 2024)
# ============================================================================

PROMPT_DETECT_TYPE = """
Analyze this image and classify it into ONE of these categories:

1. PRODUCT_ISOLATED - Hat/accessory shown alone, no person
2. PRODUCT_LIFESTYLE - Person wearing the hat
3. PRODUCT_DETAIL - Close-up of texture, material, stitching

Response format: Just output the category name (e.g., "PRODUCT_ISOLATED")
"""

PROMPT_ENHANCE_PRODUCT = """
Transform this hat product image into a professional e-commerce photo:

REQUIREMENTS:
- Keep ONLY the hat/product, remove everything else
- Pure white background (#FFFFFF)
- Centered composition (product fills 70-80% of frame)
- Professional studio lighting (soft, even, no harsh shadows)
- Sharp focus on product details
- True-to-life colors and textures
- Slightly elevated angle (10-15 degrees from front)
- Remove any dust, marks, or imperfections

STYLE:
- Premium e-commerce aesthetic (Zara/Massimo Dutti level)
- Minimalist, clean, timeless
- Professional studio quality

OUTPUT: High-resolution product photo ready for online store (1500x1500px minimum)
"""

PROMPT_ENHANCE_LIFESTYLE = """
Transform this lifestyle photo into a professional e-commerce image:

REQUIREMENTS (Person & Product):
- Keep person wearing the hat naturally
- Professional model pose (confident, relaxed)
- Hat properly fitted and positioned
- Natural, genuine expression

REQUIREMENTS (Background & Lighting):
- Soft neutral background (light gray, beige, or subtle outdoor)
- Clean, uncluttered, professional setting
- Natural or studio lighting (soft, flattering)
- Focus remains on the hat as hero product

REQUIREMENTS (Composition):
- Upper body or head-and-shoulders framing
- Hat clearly visible and in focus
- Professional fashion editorial style
- Accurate colors

STYLE:
- Mango/COS lifestyle photography aesthetic
- Aspirational but approachable
- Premium casual Portuguese/European style

OUTPUT: Professional lifestyle photo (1500x1500px minimum)
"""

PROMPT_ENHANCE_DETAIL = """
Enhance this detail shot of the hat:

REQUIREMENTS:
- Focus on texture, weave, stitching, materials
- Clean white or subtle gray background
- Macro photography style - show craftsmanship
- Perfect focus on material quality
- Professional lighting highlighting texture
- Show what makes this product premium

STYLE:
- Luxury product photography (Brunello Cucinelli level)
- Emphasize artisanal quality

OUTPUT: Professional detail macro shot (1500x1500px minimum)
"""


# ============================================================================
# GEMINI FUNCTIONS
# ============================================================================

def get_current_api_key() -> str:
    """Get current API key with rotation support"""
    global CURRENT_KEY_INDEX
    return GEMINI_API_KEYS[CURRENT_KEY_INDEX % len(GEMINI_API_KEYS)]

def rotate_api_key():
    """Rotate to next API key when quota exceeded"""
    global CURRENT_KEY_INDEX
    CURRENT_KEY_INDEX += 1
    key = get_current_api_key()
    genai.configure(api_key=key)
    print(f"🔄 Rotated to API key #{CURRENT_KEY_INDEX % len(GEMINI_API_KEYS) + 1}")

def initialize_gemini() -> Optional[genai.GenerativeModel]:
    """Initialize Gemini API with first key"""
    try:
        api_key = get_current_api_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        print(f"✅ Gemini API initialized ({GEMINI_MODEL})")
        print(f"💡 Using {len(GEMINI_API_KEYS)} API keys with rotation")
        return model
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return None


def detect_image_type(model: genai.GenerativeModel, image_path: str) -> str:
    """
    Detect image type using Gemini vision.

    Returns: 'PRODUCT_ISOLATED', 'PRODUCT_LIFESTYLE', or 'PRODUCT_DETAIL'
    """
    try:
        img = Image.open(image_path)

        response = model.generate_content([
            PROMPT_DETECT_TYPE,
            img
        ])

        result = response.text.strip().upper()

        # Validate response
        if "ISOLATED" in result:
            return "PRODUCT_ISOLATED"
        elif "LIFESTYLE" in result:
            return "PRODUCT_LIFESTYLE"
        elif "DETAIL" in result:
            return "PRODUCT_DETAIL"
        else:
            # Default to isolated if unclear
            return "PRODUCT_ISOLATED"

    except Exception as e:
        print(f"    ⚠️  Detection error: {e}")
        return "PRODUCT_ISOLATED"  # Safe default


def enhance_image(
    model: genai.GenerativeModel,
    image_path: str,
    image_type: str,
    output_path: str,
    retry_count: int = 0
) -> bool:
    """
    Enhance image using Gemini 2.0 Flash image generation.

    Args:
        model: Gemini model instance
        image_path: Source image path
        image_type: Detected image type
        output_path: Where to save enhanced version
        retry_count: Number of retries attempted

    Returns:
        True if success, False if failed
    """
    # Select prompt based on type
    prompts = {
        "PRODUCT_ISOLATED": PROMPT_ENHANCE_PRODUCT,
        "PRODUCT_LIFESTYLE": PROMPT_ENHANCE_LIFESTYLE,
        "PRODUCT_DETAIL": PROMPT_ENHANCE_DETAIL
    }

    prompt = prompts.get(image_type, PROMPT_ENHANCE_PRODUCT)

    try:
        img = Image.open(image_path)

        # Generate enhanced version with Gemini 2.0 Flash
        response = model.generate_content(
            [prompt, img],
            generation_config={
                "response_mime_type": "image/jpeg"  # Request image output
            }
        )

        # Gemini 2.0 Flash returns generated image in response
        if hasattr(response, '_result') and hasattr(response._result, 'candidates'):
            for candidate in response._result.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        # Check for inline_data with image
                        if hasattr(part, 'inline_data'):
                            if part.inline_data.mime_type.startswith('image/'):
                                with open(output_path, 'wb') as f:
                                    f.write(part.inline_data.data)
                                return True
                        # Check for blob (alternative format)
                        elif hasattr(part, 'blob'):
                            with open(output_path, 'wb') as f:
                                f.write(part.blob)
                            return True

        # If no image generated, return False
        print(f"    ⚠️  No image data in response")
        return False

    except Exception as e:
        error_msg = str(e)

        # Handle quota exceeded - rotate API key
        if "429" in error_msg or "quota" in error_msg.lower():
            if retry_count < len(GEMINI_API_KEYS):
                print(f"    ⚠️  Quota exceeded, rotating API key...")
                rotate_api_key()
                time.sleep(2)
                return enhance_image(model, image_path, image_type, output_path, retry_count + 1)
            else:
                print(f"    ❌ All API keys exhausted")
                return False

        print(f"    ❌ Enhancement error: {error_msg[:100]}")
        return False


# ============================================================================
# CSV & FILE PROCESSING
# ============================================================================

def read_active_products(csv_path: str) -> List[Dict]:
    """
    Read CSV and return list of products with prices (ACTIVE only).

    Returns:
        List of dicts with 'name', 'sku', 'images'
    """
    products = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Check if product has price (ACTIVE)
            price = row.get('Regular price', '').strip()
            if not price:
                continue

            try:
                if float(price) <= 0:
                    continue
            except ValueError:
                continue

            # Get images
            images_str = row.get('Images', '').strip()
            if not images_str:
                continue

            products.append({
                'name': row.get('Name', '').strip(),
                'sku': row.get('SKU', '').strip(),
                'price': price,
                'images': [img.strip() for img in images_str.split(',')]
            })

    return products


def csv_path_to_server_path(csv_path: str) -> str:
    """
    Convert CSV image path to server file path.

    Input: 'catalogo2025/boinas%20inverno/bone-22182/img_01.jpg'
    Output: '/var/www/html/wp-content/uploads/products/boinas inverno/bone-22182/img_01.jpg'
    """
    # Remove catalogo2025/ prefix
    path = csv_path.replace('catalogo2025/', '')

    # URL decode
    path = path.replace('%20', ' ')

    # Build full path
    full_path = f"{IMAGES_BASE_DIR}/{path}"

    return full_path


def generate_output_path(source_path: str) -> str:
    """
    Generate output path for enhanced version.

    Input: '/path/img_01.jpg'
    Output: '/path/img_01_pro.jpg'
    """
    path = Path(source_path)
    return str(path.parent / f"{path.stem}{OUTPUT_SUFFIX}{path.suffix}")


# ============================================================================
# DOCKER FILE OPERATIONS
# ============================================================================

def docker_file_exists(file_path: str) -> bool:
    """Check if file exists inside Docker container"""
    cmd = [
        "docker", "exec", CONTAINER_NAME,
        "test", "-f", file_path
    ]

    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def docker_read_file(file_path: str, output_local: str):
    """Copy file from Docker container to local"""
    cmd = [
        "docker", "cp",
        f"{CONTAINER_NAME}:{file_path}",
        output_local
    ]

    subprocess.run(cmd, check=True)


def docker_write_file(local_path: str, docker_path: str):
    """Copy local file to Docker container"""
    cmd = [
        "docker", "cp",
        local_path,
        f"{CONTAINER_NAME}:{docker_path}"
    ]

    subprocess.run(cmd, check=True)


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def process_product_images(
    model: genai.GenerativeModel,
    product: Dict,
    dry_run: bool = False
) -> int:
    """
    Process all images for a single product.

    Returns:
        Number of images successfully enhanced
    """
    print(f"\n📦 {product['name'][:60]}")
    print(f"   SKU: {product['sku']} | Price: €{product['price']}")

    enhanced_count = 0

    for idx, csv_image_path in enumerate(product['images'], 1):
        server_path = csv_path_to_server_path(csv_image_path)

        # Check if file exists
        if not docker_file_exists(server_path):
            print(f"   [{idx}/{len(product['images'])}] ⏭  Not found: {Path(server_path).name}")
            stats['skipped'] += 1
            continue

        output_path = generate_output_path(server_path)

        # Check if already enhanced
        if docker_file_exists(output_path):
            print(f"   [{idx}/{len(product['images'])}] ⏭  Already enhanced: {Path(output_path).name}")
            stats['skipped'] += 1
            continue

        if dry_run:
            print(f"   [{idx}/{len(product['images'])}] [DRY RUN] Would enhance: {Path(server_path).name}")
            continue

        # Copy from Docker to local temp
        temp_local = f"/tmp/gemini_input_{idx}.jpg"
        docker_read_file(server_path, temp_local)

        # Detect image type
        print(f"   [{idx}/{len(product['images'])}] 🔍 Analyzing {Path(server_path).name}...", end=' ')
        image_type = detect_image_type(model, temp_local)
        print(f"({image_type})")

        # Enhance with Gemini
        print(f"      🎨 Enhancing...", end=' ')
        temp_output = f"/tmp/gemini_output_{idx}.jpg"

        success = enhance_image(model, temp_local, image_type, temp_output)

        if success:
            # Copy enhanced version back to Docker
            docker_write_file(temp_output, output_path)
            print(f"✓ Saved as {Path(output_path).name}")
            enhanced_count += 1
            stats['enhanced'] += 1
        else:
            print(f"✗ Failed")
            stats['failed'] += 1
            stats['errors'].append({
                'product': product['name'],
                'image': Path(server_path).name,
                'error': 'Enhancement failed'
            })

        # Cleanup temp files
        for temp_file in [temp_local, temp_output]:
            if Path(temp_file).exists():
                Path(temp_file).unlink()

        # Rate limiting (Gemini API)
        time.sleep(2)

    return enhanced_count


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Transform existing product images to professional e-commerce photos'
    )
    parser.add_argument('--csv', default=CSV_FILE, help='CSV file with products')
    parser.add_argument('--limit', type=int, help='Limit number of products')
    parser.add_argument('--dry-run', action='store_true', help='Preview only (no changes)')
    parser.add_argument('--test', action='store_true', help='Test mode (3 products)')

    args = parser.parse_args()

    # Print header
    print("=" * 80)
    print("TRANSFORM EXISTING IMAGES → PROFESSIONAL E-COMMERCE SHOOT")
    print("=" * 80)
    print(f"\nCSV: {args.csv}")
    print(f"Source: {IMAGES_BASE_DIR}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'PRODUCTION'}")

    if args.test:
        print("Test mode: 3 products")
        args.limit = 3

    print("\n" + "-" * 80)

    # Initialize Gemini
    print("\n🔧 Initializing Gemini API...")
    model = initialize_gemini()

    if not model:
        print("❌ Cannot initialize Gemini. Exiting.")
        return 1

    # Read active products from CSV
    print(f"\n📋 Reading active products from CSV...")
    products = read_active_products(args.csv)

    if not products:
        print("❌ No active products found (products need price > 0)")
        return 1

    stats['total_products'] = len(products)

    if args.limit:
        products = products[:args.limit]
        print(f"✓ Found {len(products)} products (limited from {stats['total_products']})")
    else:
        print(f"✓ Found {len(products)} products with images")

    # Count total images
    stats['total_images'] = sum(len(p['images']) for p in products)
    print(f"✓ Total images to process: {stats['total_images']}")

    # Process each product
    print("\n" + "=" * 80)
    print("PROCESSING IMAGES")
    print("=" * 80)

    for prod_idx, product in enumerate(products, 1):
        print(f"\n[{prod_idx}/{len(products)}]", end=' ')
        process_product_images(model, product, dry_run=args.dry_run)

    # Print summary
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    print(f"Total products: {stats['total_products']}")
    print(f"Processed: {len(products)}")
    print(f"Total images: {stats['total_images']}")
    print(f"Enhanced: {stats['enhanced']} ✓")
    print(f"Skipped: {stats['skipped']} ⏭")
    print(f"Failed: {stats['failed']} ✗")

    if stats['errors']:
        print(f"\n❌ {len(stats['errors'])} errors occurred:")
        for error in stats['errors'][:10]:
            print(f"  - {error['product']} / {error['image']}: {error['error']}")

        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")

    print("\n" + "=" * 80)

    if not args.dry_run and stats['enhanced'] > 0:
        print("\n✅ Enhanced images saved!")
        print("💡 Next step: Register enhanced images in WordPress")

    return 0 if stats['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())
