#!/usr/bin/env python3
"""
Import AI Photos for 9 Test Products
Follows the validated workflow from SUCCESS_FIRST_AI_PHOTO.md
"""

import os
import subprocess
import json
from pathlib import Path

# Test products to import (from SUCCESS_FIRST_AI_PHOTO.md)
TEST_PRODUCTS = [
    {
        "folder": "tags-fabricado-na-italia-la-pura",
        "search_term": "jornaleiro",
        "name": "BOINA JORNALEIRO"
    },
    {
        "folder": "chapeu-art-970-pack-12",
        "search_term": "970",
        "name": "CHAPÉU FEMININO RÁFIA"
    },
    {
        "folder": "chapeu-impermeavel-art-181056",
        "search_term": "181056",
        "name": "CHAPÉU IMPERMEÁVEL"
    },
    {
        "folder": "chapeu-impermeavel-art-181054",
        "search_term": "181054",
        "name": "CHAPÉU DOBRÁVEL"
    },
    {
        "folder": "bone-15125",
        "search_term": "15125",
        "name": "BONÉ COWBOY"
    },
    {
        "folder": "palha-941216-couro",
        "search_term": "941216",
        "name": "CHAPÉU PALHA"
    },
    {
        "folder": "gants-17119",
        "search_term": "17119",
        "name": "LUVAS MASCULINAS"
    },
    {
        "folder": "gants-17120",
        "search_term": "17120",
        "name": "LUVAS FEMININAS"
    },
    {
        "folder": "bone-18438mc-18502mi",
        "search_term": "18438",
        "name": "BOINA HARRIS TWEED"
    }
]

BASE_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)")
PRODUCTS_PATH = BASE_PATH / "wordpress/wp-content/uploads/products"

# Container paths (for WP-CLI inside Docker)
CONTAINER_BASE = "/var/www/html"

def host_to_container_path(host_path):
    """Convert host path to container path"""
    host_str = str(host_path)
    # Remove base path and add container base
    rel_path = host_str.replace(str(BASE_PATH / "wordpress"), "")
    return f"{CONTAINER_BASE}{rel_path}"

def run_wp_cli(command):
    """Run WP-CLI command in Docker container"""
    full_cmd = f"docker exec chapeus_wordpress wp {command} --allow-root"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def find_product_id(search_term):
    """Find WooCommerce product ID by search term"""
    cmd = f"post list --post_type=product --s='{search_term}' --fields=ID,post_title --format=json"
    stdout, stderr, code = run_wp_cli(cmd)

    if code != 0:
        print(f"  ❌ Error searching product: {stderr}")
        return None

    try:
        products = json.loads(stdout)
        if not products:
            return None

        # Return first match
        product = products[0]
        print(f"  ✓ Found product: {product['post_title']} (ID: {product['ID']})")
        return product['ID']
    except:
        return None

def find_test_photos(folder_name):
    """Find test photos in product folder"""
    folder_path = PRODUCTS_PATH / folder_name

    if not folder_path.exists():
        # Try to find folder with partial match
        for category_folder in PRODUCTS_PATH.iterdir():
            if not category_folder.is_dir():
                continue
            for product_folder in category_folder.iterdir():
                if folder_name.lower() in product_folder.name.lower():
                    folder_path = product_folder
                    break
            if folder_path.exists() and folder_path != PRODUCTS_PATH / folder_name:
                break

    if not folder_path.exists():
        print(f"  ⚠️  Folder not found: {folder_name}")
        return None

    photos = {
        "editorial": None,
        "angle": None,
        "lifestyle": []
    }

    for photo_file in folder_path.glob("*_test.jpg"):
        filename = photo_file.name.lower()

        if "editorial" in filename:
            photos["editorial"] = str(photo_file)
        elif "angle" in filename:
            photos["angle"] = str(photo_file)
        elif "lifestyle" in filename:
            photos["lifestyle"].append(str(photo_file))

    if not photos["editorial"]:
        print(f"  ⚠️  No editorial photo found in {folder_path}")
        return None

    print(f"  ✓ Found photos: Editorial={'✓' if photos['editorial'] else '✗'}, Angle={'✓' if photos['angle'] else '✗'}, Lifestyle={len(photos['lifestyle'])}")
    return photos

def import_photo_to_wordpress(photo_path, product_id, product_name, photo_type):
    """Import photo to WordPress Media Library"""
    # Generate title based on product name and photo type
    title = f"AI - {product_name} - {photo_type}"

    # Convert host path to container path
    container_path = host_to_container_path(photo_path)

    # Import with WP-CLI
    cmd = f'media import "{container_path}" --post_id={product_id} --title="{title}" --porcelain'
    stdout, stderr, code = run_wp_cli(cmd)

    if code != 0:
        print(f"    ❌ Import failed: {stderr}")
        return None

    try:
        attachment_id = int(stdout.strip())
        print(f"    ✓ Imported {photo_type} (ID: {attachment_id})")
        return attachment_id
    except:
        print(f"    ❌ Could not parse attachment ID: {stdout}")
        return None

def set_featured_image(product_id, attachment_id):
    """Set product featured image"""
    cmd = f"post meta update {product_id} _thumbnail_id {attachment_id}"
    stdout, stderr, code = run_wp_cli(cmd)

    if code != 0:
        print(f"    ❌ Failed to set featured image: {stderr}")
        return False

    print(f"    ✓ Featured image set")
    return True

def set_product_gallery(product_id, attachment_ids):
    """Set product gallery images"""
    if not attachment_ids:
        return True

    gallery_str = ",".join(map(str, attachment_ids))
    cmd = f'post meta update {product_id} _product_image_gallery "{gallery_str}"'
    stdout, stderr, code = run_wp_cli(cmd)

    if code != 0:
        print(f"    ❌ Failed to set gallery: {stderr}")
        return False

    print(f"    ✓ Gallery updated with {len(attachment_ids)} photos")
    return True

def regenerate_thumbnails(attachment_ids):
    """Regenerate thumbnails for attachments"""
    ids_str = " ".join(map(str, attachment_ids))
    cmd = f"media regenerate {ids_str} --yes"
    stdout, stderr, code = run_wp_cli(cmd)

    if code != 0:
        print(f"    ⚠️  Thumbnail regeneration warning: {stderr}")
        return False

    print(f"    ✓ Thumbnails regenerated")
    return True

def import_product(product_info):
    """Import all photos for a product"""
    print(f"\n{'='*60}")
    print(f"📦 Processing: {product_info['name']}")
    print(f"{'='*60}")

    # 1. Find product ID
    product_id = find_product_id(product_info['search_term'])
    if not product_id:
        print(f"  ❌ Product not found with search term: {product_info['search_term']}")
        return False

    # 2. Find test photos
    photos = find_test_photos(product_info['folder'])
    if not photos:
        return False

    # 3. Import Editorial as featured image
    print("\n  📸 Importing Editorial (Featured Image)...")
    editorial_id = import_photo_to_wordpress(
        photos['editorial'],
        product_id,
        product_info['name'],
        "Editorial"
    )

    if not editorial_id:
        return False

    set_featured_image(product_id, editorial_id)

    # 4. Import Angle and Lifestyle to gallery
    gallery_ids = []

    if photos['angle']:
        print("\n  📸 Importing Angle (Gallery)...")
        angle_id = import_photo_to_wordpress(
            photos['angle'],
            product_id,
            product_info['name'],
            "Angle"
        )
        if angle_id:
            gallery_ids.append(angle_id)

    for i, lifestyle_path in enumerate(photos['lifestyle'], 1):
        # Extract scenario from filename
        scenario = "Lifestyle"
        if "alfama" in lifestyle_path.lower():
            scenario = "Lifestyle Alfama"
        elif "eletrico" in lifestyle_path.lower():
            scenario = "Lifestyle Elétrico"
        elif "miradouro" in lifestyle_path.lower():
            scenario = "Lifestyle Miradouro"
        elif "tejo" in lifestyle_path.lower():
            scenario = "Lifestyle Tejo"
        elif "cafe" in lifestyle_path.lower():
            scenario = "Lifestyle Café"

        print(f"\n  📸 Importing {scenario} (Gallery)...")
        lifestyle_id = import_photo_to_wordpress(
            lifestyle_path,
            product_id,
            product_info['name'],
            scenario
        )
        if lifestyle_id:
            gallery_ids.append(lifestyle_id)

    if gallery_ids:
        set_product_gallery(product_id, gallery_ids)

    # 5. Regenerate thumbnails
    all_ids = [editorial_id] + gallery_ids
    print("\n  🔄 Regenerating thumbnails...")
    regenerate_thumbnails(all_ids)

    print(f"\n  ✅ SUCCESS: {product_info['name']}")
    return True

def main():
    """Import all test products"""
    print("🚀 IMPORTING 9 TEST PRODUCTS")
    print("=" * 60)
    print("Following validated workflow from SUCCESS_FIRST_AI_PHOTO.md")
    print("=" * 60)

    success_count = 0
    failed_count = 0

    for product_info in TEST_PRODUCTS:
        if import_product(product_info):
            success_count += 1
        else:
            failed_count += 1

    # Clear cache
    print("\n" + "=" * 60)
    print("🧹 Clearing WordPress cache...")
    print("=" * 60)
    run_wp_cli("cache flush")
    print("✓ Cache cleared")

    # Final report
    print("\n" + "=" * 60)
    print("📊 FINAL REPORT")
    print("=" * 60)
    print(f"✅ Success: {success_count}/{len(TEST_PRODUCTS)}")
    print(f"❌ Failed: {failed_count}/{len(TEST_PRODUCTS)}")

    if success_count > 0:
        print("\n🎉 AI photos now visible on WordPress site!")
        print("👉 Check: http://localhost:8080/loja/")

    print("=" * 60)

if __name__ == "__main__":
    main()
