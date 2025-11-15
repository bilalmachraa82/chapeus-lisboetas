#!/usr/bin/env python3
"""
Import AI Test Photos - Version 2
Auto-discovers test products and tries multiple search strategies
"""

import os
import subprocess
import json
import re
from pathlib import Path
from collections import defaultdict

BASE_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)")
PRODUCTS_PATH = BASE_PATH / "wordpress/wp-content/uploads/products"
CONTAINER_BASE = "/var/www/html"

def host_to_container_path(host_path):
    """Convert host path to container path"""
    host_str = str(host_path)
    rel_path = host_str.replace(str(BASE_PATH / "wordpress"), "")
    return f"{CONTAINER_BASE}{rel_path}"

def run_wp_cli(command):
    """Run WP-CLI command in Docker container"""
    full_cmd = f"docker exec chapeus_wordpress wp {command} --allow-root"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def discover_test_products():
    """Scan filesystem for folders containing test photos"""
    test_products = []

    for root, dirs, files in os.walk(str(PRODUCTS_PATH)):
        # Check if this folder has test photos
        test_files = [f for f in files if f.endswith('_test.jpg')]

        if test_files:
            folder_path = Path(root)
            folder_name = folder_path.name

            # Categorize photos by type
            photos = {
                'editorial': None,
                'angle': None,
                'lifestyle': []
            }

            for photo in test_files:
                photo_path = folder_path / photo
                filename_lower = photo.lower()

                if 'editorial' in filename_lower:
                    photos['editorial'] = str(photo_path)
                elif 'angle' in filename_lower:
                    photos['angle'] = str(photo_path)
                elif 'lifestyle' in filename_lower:
                    photos['lifestyle'].append(str(photo_path))

            if photos['editorial']:  # Only include if has editorial
                test_products.append({
                    'folder_name': folder_name,
                    'folder_path': str(folder_path),
                    'photos': photos
                })

    return test_products

def extract_search_terms(folder_name):
    """Extract potential search terms from folder name"""
    terms = []

    # Original folder name
    terms.append(folder_name)

    # Extract SKU patterns (numbers, letters+numbers)
    sku_patterns = re.findall(r'\d+[a-z]*', folder_name, re.IGNORECASE)
    terms.extend(sku_patterns)

    # Extract meaningful words (longer than 3 chars)
    words = re.findall(r'[a-z]{4,}', folder_name, re.IGNORECASE)
    terms.extend(words)

    # Remove common words
    common_words = {'pack', 'tags', 'fabricado', 'italia', 'pura', 'couro', 'art'}
    terms = [t for t in terms if t.lower() not in common_words]

    return list(dict.fromkeys(terms))  # Remove duplicates, preserve order

def find_product_id(folder_name):
    """Try multiple strategies to find matching WooCommerce product"""
    search_terms = extract_search_terms(folder_name)

    print(f"  🔍 Trying search terms: {search_terms}")

    for term in search_terms:
        if len(term) < 3:
            continue

        cmd = f"post list --post_type=product --s='{term}' --fields=ID,post_title --format=json"
        stdout, stderr, code = run_wp_cli(cmd)

        if code == 0 and stdout:
            try:
                products = json.loads(stdout)
                if products:
                    product = products[0]  # Take first match
                    print(f"  ✓ Found via '{term}': {product['post_title']} (ID: {product['ID']})")
                    return product['ID'], product['post_title']
            except:
                continue

    print(f"  ❌ No product found for: {folder_name}")
    return None, None

def import_photo(photo_path, product_id, product_name, photo_type):
    """Import single photo to WordPress"""
    title = f"AI - {product_name} - {photo_type}"
    container_path = host_to_container_path(photo_path)

    cmd = f'media import "{container_path}" --post_id={product_id} --title="{title}" --porcelain'
    stdout, stderr, code = run_wp_cli(cmd)

    if code != 0:
        print(f"    ❌ Import failed: {stderr}")
        return None

    try:
        attachment_id = int(stdout.strip())
        print(f"    ✓ {photo_type} imported (ID: {attachment_id})")
        return attachment_id
    except:
        print(f"    ❌ Invalid attachment ID: {stdout}")
        return None

def set_featured_image(product_id, attachment_id):
    """Set featured image for product"""
    cmd = f"post meta update {product_id} _thumbnail_id {attachment_id}"
    stdout, stderr, code = run_wp_cli(cmd)
    return code == 0

def set_gallery(product_id, attachment_ids):
    """Set product gallery"""
    if not attachment_ids:
        return True

    gallery_str = ",".join(map(str, attachment_ids))
    cmd = f'post meta update {product_id} _product_image_gallery "{gallery_str}"'
    stdout, stderr, code = run_wp_cli(cmd)
    return code == 0

def regenerate_thumbnails(attachment_ids):
    """Regenerate thumbnails"""
    if not attachment_ids:
        return True

    ids_str = " ".join(map(str, attachment_ids))
    cmd = f"media regenerate {ids_str} --yes"
    stdout, stderr, code = run_wp_cli(cmd)
    return code == 0

def import_product_photos(product_info):
    """Import all photos for a product"""
    folder_name = product_info['folder_name']
    photos = product_info['photos']

    print(f"\n{'='*70}")
    print(f"📦 {folder_name}")
    print(f"{'='*70}")

    # Find WooCommerce product
    product_id, product_name = find_product_id(folder_name)
    if not product_id:
        return False

    # Import editorial as featured
    print("\n  📸 Importing Editorial (Featured)...")
    editorial_id = import_photo(
        photos['editorial'],
        product_id,
        product_name,
        "Editorial"
    )

    if not editorial_id:
        return False

    set_featured_image(product_id, editorial_id)
    print(f"    ✓ Set as featured image")

    # Import gallery photos
    gallery_ids = []

    if photos['angle']:
        print("\n  📸 Importing Angle (Gallery)...")
        angle_id = import_photo(photos['angle'], product_id, product_name, "Angle")
        if angle_id:
            gallery_ids.append(angle_id)

    for lifestyle_path in photos['lifestyle']:
        # Extract scenario from filename
        scenario = "Lifestyle"
        filename = Path(lifestyle_path).name.lower()
        if "alfama" in filename:
            scenario = "Lifestyle Alfama"
        elif "eletrico" in filename:
            scenario = "Lifestyle Elétrico"
        elif "miradouro" in filename:
            scenario = "Lifestyle Miradouro"
        elif "tejo" in filename:
            scenario = "Lifestyle Tejo"
        elif "cafe" in filename:
            scenario = "Lifestyle Café"

        print(f"\n  📸 Importing {scenario} (Gallery)...")
        lifestyle_id = import_photo(lifestyle_path, product_id, product_name, scenario)
        if lifestyle_id:
            gallery_ids.append(lifestyle_id)

    if gallery_ids:
        set_gallery(product_id, gallery_ids)
        print(f"    ✓ Gallery updated ({len(gallery_ids)} photos)")

    # Regenerate thumbnails
    all_ids = [editorial_id] + gallery_ids
    print("\n  🔄 Regenerating thumbnails...")
    if regenerate_thumbnails(all_ids):
        print(f"    ✓ Thumbnails regenerated")

    print(f"\n  ✅ SUCCESS: {product_name}")
    return True

def main():
    """Main import process"""
    print("🚀 AI TEST PHOTOS IMPORT - AUTO-DISCOVERY")
    print("="*70)

    # Discover all test products
    print("\n🔍 Scanning for test products...")
    test_products = discover_test_products()

    print(f"\n✓ Found {len(test_products)} products with test photos:")
    for p in test_products:
        editorial = '✓' if p['photos']['editorial'] else '✗'
        angle = '✓' if p['photos']['angle'] else '✗'
        lifestyle_count = len(p['photos']['lifestyle'])
        print(f"  • {p['folder_name']}")
        print(f"    Editorial={editorial}, Angle={angle}, Lifestyle={lifestyle_count}")

    print("\n" + "="*70)
    print("Starting import...")
    print("="*70)

    # Import each product
    success = 0
    failed = 0

    for product_info in test_products:
        if import_product_photos(product_info):
            success += 1
        else:
            failed += 1

    # Clear cache
    print("\n" + "="*70)
    print("🧹 Clearing cache...")
    print("="*70)
    run_wp_cli("cache flush")
    print("✓ Cache cleared")

    # Report
    print("\n" + "="*70)
    print("📊 IMPORT COMPLETE")
    print("="*70)
    print(f"✅ Success: {success}/{len(test_products)}")
    print(f"❌ Failed: {failed}/{len(test_products)}")

    if success > 0:
        print("\n🎉 AI photos now visible!")
        print("👉 View: http://localhost:8080/loja/")

    print("="*70)

if __name__ == "__main__":
    main()
