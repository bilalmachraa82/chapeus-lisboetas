#!/usr/bin/env python3
"""
Import AI photos using WordPress Media API (WP-CLI) - THE CORRECT WAY
This ensures WordPress recognizes attachments properly.
"""

import sys
import os
import subprocess
import mysql.connector
from mysql.connector import Error
from pathlib import Path
import json

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'lisboetas_web',
    'user': 'root',
    'password': 'rootpassword'
}


class AIPhotoImporter:
    """Import AI photos using wp media import (WordPress API)."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
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

    def get_products_with_ai_folders(self):
        """Get products and their AI photo folders."""
        # Get from the matching results we created earlier
        query = """
            SELECT DISTINCT
                p.ID as product_id,
                p.post_title,
                p.post_name,
                pm.meta_value as gallery_ids
            FROM lx_posts p
            LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_product_image_gallery'
            WHERE p.post_type = 'product'
            AND p.ID IN (
                SELECT DISTINCT post_id
                FROM lx_postmeta
                WHERE meta_key = '_thumbnail_id'
                AND meta_value BETWEEN 214474 AND 214824
            )
            ORDER BY p.ID
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def find_ai_photos_for_product(self, product_id: int):
        """Find AI photo files for a product."""
        # Get the AI images that were previously linked to this product
        query = """
            SELECT p.ID, p.post_title, pm.meta_value as file_path
            FROM lx_posts p
            INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
            WHERE p.ID BETWEEN 214474 AND 214824
            AND p.post_type = 'attachment'
            AND pm.meta_key = '_wp_attached_file'
            AND p.ID IN (
                -- Featured image
                SELECT meta_value FROM lx_postmeta
                WHERE post_id = %s AND meta_key = '_thumbnail_id'
                UNION
                -- Gallery images
                SELECT SUBSTRING_INDEX(SUBSTRING_INDEX(meta_value, ',', numbers.n), ',', -1) as id
                FROM lx_postmeta
                CROSS JOIN (
                    SELECT 1 n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
                    UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8
                    UNION SELECT 9 UNION SELECT 10
                ) numbers
                WHERE post_id = %s
                AND meta_key = '_product_image_gallery'
                AND CHAR_LENGTH(meta_value) - CHAR_LENGTH(REPLACE(meta_value, ',', '')) >= numbers.n - 1
            )
            ORDER BY p.ID
        """
        self.cursor.execute(query, (product_id, product_id))
        results = self.cursor.fetchall()

        # Convert to full paths
        photos = []
        for result in results:
            file_path = result['file_path']
            full_path = f"/var/www/html/wp-content/uploads/{file_path}"
            photos.append({
                'old_id': result['ID'],
                'title': result['post_title'],
                'file_path': file_path,
                'full_path': full_path
            })

        return photos

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

    def import_image(self, image_path: str, post_id: int, title: str):
        """Import single image using wp media import."""
        # Use --skip-copy since file already exists in uploads
        # Use --porcelain to get the new attachment ID
        cmd = (
            f"wp media import '{image_path}' "
            f"--post_id={post_id} "
            f"--title='{title}' "
            f"--porcelain "
            f"--allow-root"
        )

        result = self.wp_cli_command(cmd)

        if result['success']:
            # Parse attachment ID from output
            output = result['output']
            try:
                # Porcelain format returns just the ID
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

    def delete_old_attachments(self):
        """Delete old manually-inserted attachments."""
        print("="*70)
        print("CLEANUP: Deleting old attachments (214474-214824)")
        print("="*70 + "\n")

        if self.dry_run:
            print("[DRY RUN] Would delete 351 attachments\n")
            return True

        # Use SQL to delete (faster than WP-CLI for bulk)
        try:
            # Delete attachment posts
            self.cursor.execute("""
                DELETE FROM lx_posts
                WHERE ID BETWEEN 214474 AND 214824
            """)
            deleted_posts = self.cursor.rowcount

            # Delete attachment metadata
            self.cursor.execute("""
                DELETE FROM lx_postmeta
                WHERE post_id BETWEEN 214474 AND 214824
            """)
            deleted_meta = self.cursor.rowcount

            self.conn.commit()
            print(f"✓ Deleted {deleted_posts} attachments and {deleted_meta} metadata entries\n")
            return True

        except Exception as e:
            print(f"❌ Error deleting attachments: {e}")
            return False

    def process_all(self):
        print("="*70)
        print("IMPORT AI PHOTOS VIA WORDPRESS MEDIA API")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("="*70 + "\n")

        # Step 1: Delete old attachments
        if not self.delete_old_attachments():
            print("\n❌ Failed to delete old attachments. Aborting.")
            return False

        # Step 2: Get products with AI photos
        products = self.get_products_with_ai_folders()
        print(f"📦 Found {len(products)} products with AI photos\n")

        for i, product in enumerate(products, 1):
            product_id = product['product_id']
            title = product['post_title']

            print(f"\n[{i}/{len(products)}] {title} (ID: {product_id})")

            # Find AI photos for this product
            photos = self.find_ai_photos_for_product(product_id)

            if not photos:
                print(f"  ⚠️  No AI photos found")
                continue

            print(f"  Found {len(photos)} AI photos")

            # Import photos
            new_attachment_ids = []

            for j, photo in enumerate(photos):
                photo_title = f"AI - {title} - {j+1}"

                print(f"    [{j+1}/{len(photos)}] Importing {os.path.basename(photo['file_path'])}...")

                result = self.import_image(
                    photo['full_path'],
                    product_id,
                    photo_title
                )

                if self.dry_run:
                    # In dry-run, simulate success
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
                    self.stats['errors'].append(f"{title} - {photo['file_path']}: {error}")

            if not new_attachment_ids:
                print(f"  ❌ No images imported successfully")
                continue

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
                gallery_ids = new_attachment_ids[1:]  # Skip first (it's featured)
                print(f"  Updating gallery with {len(gallery_ids)} images")

                gallery_result = self.update_gallery(product_id, gallery_ids)

                if gallery_result['success']:
                    print(f"    ✓ Gallery updated")
                    self.stats['galleries_updated'] += 1
                else:
                    print(f"    ❌ Failed to update gallery: {gallery_result.get('error')}")

            self.stats['products_processed'] += 1

        # Flush cache
        print("\n" + "="*70)
        print("Flushing WordPress cache...")
        cache_result = self.wp_cli_command("wp cache flush --allow-root")
        if cache_result['success']:
            print("✓ Cache flushed")

        return True

    def print_summary(self):
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
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
        description='Import AI photos using WordPress Media API (WP-CLI)'
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview without making changes')
    args = parser.parse_args()

    importer = AIPhotoImporter(dry_run=args.dry_run)

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
