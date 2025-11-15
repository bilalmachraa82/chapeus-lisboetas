#!/usr/bin/env python3
"""
Associate Orphan AI Photos to Products
Automatically matches AI Editorial photos with WooCommerce products
"""

import subprocess
import json
import re
from collections import defaultdict

def run_wp_cli(command):
    """Run WP-CLI command in Docker container"""
    full_cmd = f"docker exec chapeus_wordpress wp {command} --allow-root"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def extract_product_name(photo_title):
    """Extract product name from photo title: 'AI - ProductName - Editorial'"""
    match = re.search(r'AI - (.+?) - Editorial', photo_title)
    if match:
        return match.group(1).strip()
    return None

def find_product_by_name(product_name):
    """Find WooCommerce product by name"""
    # Try exact match first
    cmd = f'post list --post_type=product --s="{product_name}" --fields=ID,post_title --format=json'
    stdout, stderr, code = run_wp_cli(cmd)

    if code == 0 and stdout:
        try:
            products = json.loads(stdout)
            if products:
                # Return first match
                return products[0]['ID'], products[0]['post_title']
        except:
            pass

    # Try partial match with first word
    if ' ' in product_name:
        first_word = product_name.split()[0]
        if len(first_word) > 3:  # Only if meaningful
            cmd = f'post list --post_type=product --s="{first_word}" --fields=ID,post_title --format=json'
            stdout, stderr, code = run_wp_cli(cmd)

            if code == 0 and stdout:
                try:
                    products = json.loads(stdout)
                    if products:
                        return products[0]['ID'], products[0]['post_title']
                except:
                    pass

    return None, None

def associate_photo_to_product(product_id, photo_id):
    """Associate photo as featured image for product"""
    cmd = f"post meta update {product_id} _thumbnail_id {photo_id}"
    stdout, stderr, code = run_wp_cli(cmd)
    return code == 0

def regenerate_thumbnails(photo_id):
    """Regenerate thumbnail sizes"""
    cmd = f"media regenerate {photo_id} --yes"
    stdout, stderr, code = run_wp_cli(cmd)
    return code == 0

def main():
    print("🚀 ASSOCIAÇÃO AUTOMÁTICA DE FOTOS AI")
    print("=" * 70)

    # Get all AI Editorial photos
    print("\n📸 Buscando fotos AI Editorial...")
    cmd = 'post list --post_type=attachment --post_title__like="AI -" --post_title__like="Editorial" --fields=ID,post_title --format=json'
    stdout, stderr, code = run_wp_cli(cmd)

    if code != 0 or not stdout:
        print("❌ Erro ao buscar fotos AI")
        return

    photos = json.loads(stdout)
    print(f"✓ Encontradas {len(photos)} fotos AI Editorial")

    # Group photos by product name
    photos_by_product = defaultdict(list)
    for photo in photos:
        product_name = extract_product_name(photo['post_title'])
        if product_name:
            photos_by_product[product_name].append(photo['ID'])

    print(f"✓ Agrupadas em {len(photos_by_product)} produtos únicos")

    # Process each product
    print("\n" + "=" * 70)
    print("🔗 Associando fotos aos produtos...")
    print("=" * 70)

    success = 0
    failed = 0
    skipped = 0

    for idx, (product_name, photo_ids) in enumerate(photos_by_product.items(), 1):
        print(f"\n[{idx}/{len(photos_by_product)}] 📦 {product_name}")
        print(f"  Fotos disponíveis: {len(photo_ids)}")

        # Find product
        product_id, actual_title = find_product_by_name(product_name)

        if not product_id:
            print(f"  ❌ Produto não encontrado")
            failed += len(photo_ids)
            continue

        print(f"  ✓ Produto encontrado: {actual_title} (ID: {product_id})")

        # Check if already has featured image
        cmd = f"post meta get {product_id} _thumbnail_id"
        stdout, stderr, code = run_wp_cli(cmd)
        existing_thumb = stdout.strip()

        if existing_thumb and existing_thumb != "0" and existing_thumb.isdigit():
            print(f"  ⏭️  Já tem featured image (ID: {existing_thumb}) - pulando")
            skipped += 1
            continue

        # Associate first photo as featured image
        photo_id = photo_ids[0]
        if associate_photo_to_product(product_id, photo_id):
            print(f"  ✅ Featured image associada (Foto ID: {photo_id})")

            # Regenerate thumbnails
            regenerate_thumbnails(photo_id)

            success += 1
        else:
            print(f"  ❌ Falha ao associar")
            failed += 1

    # Clear cache
    print("\n" + "=" * 70)
    print("🧹 Limpando cache...")
    run_wp_cli("cache flush")
    print("✓ Cache limpo")

    # Report
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL")
    print("=" * 70)
    print(f"✅ Associações bem-sucedidas: {success}")
    print(f"⏭️  Produtos já com fotos: {skipped}")
    print(f"❌ Falhas: {failed}")
    print(f"📈 Taxa de sucesso: {success}/{len(photos_by_product)} ({success*100//len(photos_by_product) if photos_by_product else 0}%)")

    if success > 0:
        print("\n🎉 Fotos AI agora visíveis no site!")
        print("👉 Ver: http://localhost:8080/loja/")

    print("=" * 70)

if __name__ == "__main__":
    main()
