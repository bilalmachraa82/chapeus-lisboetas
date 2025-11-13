#!/usr/bin/env python3
"""
Import AI photos from filesystem using WordPress Media API (WP-CLI).
Scans for *_pro.jpg files and matches to products via SKU extraction.
"""

import sys
import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'lisboetas_web',
    'user': 'root',
    'password': 'rootpassword'
}

# Base path for AI photos inside Docker container
UPLOADS_BASE = "/var/www/html/wp-content/uploads/products"
# Base path for AI photos on host machine
LOCAL_UPLOADS_BASE = "/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/uploads/products"

# Manual mappings for folders that can't be matched by SKU
# Format: folder_name → [product_id, ...]
MANUAL_FOLDER_MAPPINGS = {
    # Dockers Miki products
    'gorro-344974-gorro-de-la-estilo-bretao-miki-docker-com-aba-de-aperto-traseira': [212404, 212594],
    'gorro-miki-22100-gorro-de-la-estilo-bretao-miki-docker-com-aba-de-aperto-traseira': [212686, 212719],

    # Chapéus Impermeáveis
    'chapeu-impermeavel-art-181054-pack-12-tags-fabricado-na-italia-la-esmagavel-impermeavel': [213898, 214424],
    'chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel': [214125, 214141],

    # Other special cases
    'tags-fabricado-na-italia-la-pura': [213782],  # Boina Jornaleiro Pure Wool
    'chapeu-art-970-pack-12': [213379],  # Chapéu Feminino Ráfia
}


class AIPhotoImporterV3:
    """Import AI photos from filesystem using WordPress Media API."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'folders_found': 0,
            'folders_matched': 0,
            'products_processed': 0,
            'images_imported': 0,
            'featured_set': 0,
            'galleries_updated': 0,
            'errors': []
        }

    def connect_db(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True, buffered=True)
            print("✓ Connected to WordPress database\n")
            return True
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def close_db(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def scan_filesystem_for_photos(self):
        """Scan filesystem for all *_pro.jpg files grouped by folder."""
        print("📁 Scanning filesystem for AI photos...")

        folders = defaultdict(list)
        local_base = Path(LOCAL_UPLOADS_BASE)

        if not local_base.exists():
            print(f"❌ Base path doesn't exist: {local_base}")
            return {}

        # Find all *_pro.jpg files
        for pro_file in local_base.rglob("*_pro.jpg"):
            folder_path = pro_file.parent
            folder_name = folder_path.name

            # Convert to Docker container path
            relative_path = pro_file.relative_to(local_base)
            docker_path = f"{UPLOADS_BASE}/{relative_path}"

            folders[folder_name].append({
                'local_path': str(pro_file),
                'docker_path': docker_path,
                'filename': pro_file.name,
                'folder': folder_name
            })

        self.stats['folders_found'] = len(folders)
        print(f"  Found {len(folders)} folders with AI photos")
        print(f"  Total images: {sum(len(files) for files in folders.values())}\n")

        return folders

    def extract_sku_from_folder(self, folder_name: str) -> list:
        """Extract potential SKUs from folder name."""
        skus = []

        # Pattern 1: Pure numbers (4-6 digits)
        pure_numbers = re.findall(r'\b(\d{4,6})\b', folder_name)
        skus.extend(pure_numbers)

        # Pattern 2: Numbers with letter suffix (18074k, 18440ol)
        number_letter = re.findall(r'\b(\d{4,6}[a-z]{1,3})\b', folder_name, re.I)
        skus.extend(number_letter)

        # Remove duplicates while preserving order
        seen = set()
        unique_skus = []
        for sku in skus:
            if sku not in seen:
                seen.add(sku)
                unique_skus.append(sku)

        return unique_skus

    def find_product_by_sku(self, skus: list):
        """Find product ID by SKU(s)."""
        if not skus:
            return None

        # Try each SKU variant
        for sku in skus:
            query = """
                SELECT p.ID, p.post_title
                FROM lx_posts p
                INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
                WHERE p.post_type = 'product'
                AND p.post_status = 'publish'
                AND pm.meta_key = '_sku'
                AND pm.meta_value = %s
                LIMIT 1
            """
            self.cursor.execute(query, (sku,))
            result = self.cursor.fetchone()

            if result:
                return result

        return None

    def wp_cli_command(self, cmd: str):
        """Execute WP-CLI command inside Docker container."""
        full_cmd = f"docker exec chapeus_wordpress {cmd}"

        if self.dry_run:
            print(f"  [DRY RUN] Would execute: {cmd}")
            return {'success': True, 'output': 'DRY RUN', 'id': 99999}

        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {'success': True, 'output': result.stdout.strip(), 'id': None}
            else:
                return {'success': False, 'error': result.stderr.strip()}

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def import_image(self, docker_path: str, post_id: int, title: str):
        """Import single image using wp media import."""
        cmd = (
            f"wp media import '{docker_path}' "
            f"--post_id={post_id} "
            f"--title='{title}' "
            f"--porcelain "
            f"--allow-root"
        )

        result = self.wp_cli_command(cmd)

        if result['success']:
            output = result['output']
            try:
                attachment_id = int(output.strip().split('\n')[-1])
                result['id'] = attachment_id
            except (ValueError, IndexError):
                result['id'] = None

        return result

    def set_featured_image(self, post_id: int, attachment_id: int):
        """Set featured image for product."""
        cmd = (
            f"wp post meta update {post_id} "
            f"_thumbnail_id {attachment_id} "
            f"--allow-root"
        )
        return self.wp_cli_command(cmd)

    def update_gallery(self, post_id: int, attachment_ids: list):
        """Update product gallery."""
        if not attachment_ids:
            return {'success': True}

        gallery_string = ','.join(str(id) for id in attachment_ids)
        cmd = (
            f"wp post meta update {post_id} "
            f"_product_image_gallery '{gallery_string}' "
            f"--allow-root"
        )
        return self.wp_cli_command(cmd)

    def process_all(self):
        print("="*70)
        print("IMPORT AI PHOTOS FROM FILESYSTEM VIA WORDPRESS MEDIA API")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("="*70 + "\n")

        # Step 1: Scan filesystem for AI photos
        folders_with_photos = self.scan_filesystem_for_photos()

        if not folders_with_photos:
            print("❌ No AI photos found on filesystem")
            return False

        # Step 2: Match folders to products and import
        print("🔗 Matching folders to products...\n")

        for folder_name, photos in folders_with_photos.items():
            print(f"\n📂 {folder_name} ({len(photos)} images)")

            # Check manual mappings first
            if folder_name in MANUAL_FOLDER_MAPPINGS:
                product_ids = MANUAL_FOLDER_MAPPINGS[folder_name]
                print(f"  ✓ Manual mapping: {len(product_ids)} product(s)")

                # Process each product in the manual mapping
                for product_id in product_ids:
                    # Get product details
                    query = "SELECT ID, post_title FROM lx_posts WHERE ID = %s"
                    self.cursor.execute(query, (product_id,))
                    product = self.cursor.fetchone()

                    if not product:
                        print(f"    ⚠️  Product ID {product_id} not found")
                        continue

                    self.process_product_photos(product, photos)

                continue

            # Try SKU extraction
            skus = self.extract_sku_from_folder(folder_name)
            if not skus:
                print(f"  ⚠️  Could not extract SKU from folder name")
                self.stats['errors'].append(f"{folder_name}: No SKU extracted")
                continue

            print(f"  Extracted SKUs: {', '.join(skus)}")

            # Find product by SKU
            product = self.find_product_by_sku(skus)
            if not product:
                print(f"  ⚠️  No product found with SKU(s): {', '.join(skus)}")
                self.stats['errors'].append(f"{folder_name}: No product match for SKUs {skus}")
                continue

            self.stats['folders_matched'] += 1
            self.process_product_photos(product, photos)

        # Flush cache at the end
        print("\n" + "="*70)
        print("Flushing WordPress cache...")
        cache_result = self.wp_cli_command("wp cache flush --allow-root")
        if cache_result['success']:
            print("✓ Cache flushed")

        return True

    def process_product_photos(self, product, photos):
        """Process photos for a single product."""
        product_id = product['ID']
        product_title = product['post_title']

        print(f"  ✓ Processing: {product_title} (ID: {product_id})")

        # Import photos for this product
        new_attachment_ids = []

        for j, photo in enumerate(sorted(photos, key=lambda x: x['filename']), 1):
            photo_title = f"AI - {product_title} - {j}"

            print(f"    [{j}/{len(photos)}] Importing {photo['filename']}...")

            result = self.import_image(
                photo['docker_path'],
                product_id,
                photo_title
            )

            if self.dry_run:
                new_attachment_ids.append(99999 + j)
                print(f"      [DRY RUN] Would import successfully")
                self.stats['images_imported'] += 1
            elif result['success'] and result.get('id'):
                new_id = result['id']
                new_attachment_ids.append(new_id)
                print(f"      ✓ Imported (new ID: {new_id})")
                self.stats['images_imported'] += 1
            else:
                error = result.get('error', 'Unknown error')
                print(f"      ❌ Failed: {error}")
                self.stats['errors'].append(f"{product_title} - {photo['filename']}: {error}")

        if not new_attachment_ids:
            print(f"  ❌ No images imported successfully")
            return

        # Set first image as featured
        print(f"  Setting featured image: {new_attachment_ids[0]}")
        featured_result = self.set_featured_image(product_id, new_attachment_ids[0])

        if featured_result['success']:
            print(f"    ✓ Featured image set")
            self.stats['featured_set'] += 1
        else:
            print(f"    ❌ Failed to set featured: {featured_result.get('error')}")

        # Update gallery with remaining images
        if len(new_attachment_ids) > 1:
            gallery_ids = new_attachment_ids[1:]
            print(f"  Updating gallery with {len(gallery_ids)} images")

            gallery_result = self.update_gallery(product_id, gallery_ids)

            if gallery_result['success']:
                print(f"    ✓ Gallery updated")
                self.stats['galleries_updated'] += 1
            else:
                print(f"    ❌ Failed to update gallery: {gallery_result.get('error')}")

        self.stats['products_processed'] += 1

    def print_summary(self):
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"📁 Folders found: {self.stats['folders_found']}")
        print(f"✓ Folders matched: {self.stats['folders_matched']}")
        print(f"✓ Products processed: {self.stats['products_processed']}")
        print(f"✓ Images imported: {self.stats['images_imported']}")
        print(f"✓ Featured images set: {self.stats['featured_set']}")
        print(f"✓ Galleries updated: {self.stats['galleries_updated']}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\nErrors (first 10):")
            for error in self.stats['errors'][:10]:
                print(f"  • {error}")

        print("="*70 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Import AI photos from filesystem using WordPress Media API'
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview without making changes')
    args = parser.parse_args()

    importer = AIPhotoImporterV3(dry_run=args.dry_run)

    if not importer.connect_db():
        return 1

    try:
        success = importer.process_all()
        importer.print_summary()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        importer.close_db()


if __name__ == '__main__':
    sys.exit(main())
