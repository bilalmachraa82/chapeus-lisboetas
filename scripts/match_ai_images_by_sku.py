#!/usr/bin/env python3
"""
Match AI images to WooCommerce products by extracting SKU from folder names.

Strategy:
1. Get all AI images with _ai_product_folder metadata
2. Extract SKU numbers from folder names (e.g., bone-18074 → 18074)
3. Match SKU to products via _sku meta field
4. Link images to products (featured + gallery)
"""

import sys
import re
from collections import defaultdict
import mysql.connector
from mysql.connector import Error

# WordPress database
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'lisboetas_web',
    'user': 'root',
    'password': 'rootpassword'
}


class SKUImageMatcher:
    """Match AI images to products by SKU extraction."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'products_matched': 0,
            'products_updated': 0,
            'images_linked': 0,
            'no_sku_extracted': [],
            'no_product_found': [],
            'errors': []
        }

    def connect_db(self):
        """Connect to WordPress database."""
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True, buffered=True)
            print("✓ Connected to WordPress database\n")
            return True
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def close_db(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_ai_images_with_folders(self):
        """Get all AI images with their product folder metadata."""
        query = """
            SELECT
                p.ID as image_id,
                p.post_title,
                pm1.meta_value as file_path,
                pm2.meta_value as product_folder
            FROM lx_posts p
            LEFT JOIN lx_postmeta pm1 ON p.ID = pm1.post_id AND pm1.meta_key = '_wp_attached_file'
            LEFT JOIN lx_postmeta pm2 ON p.ID = pm2.post_id AND pm2.meta_key = '_ai_product_folder'
            WHERE p.post_type = 'attachment'
            AND p.post_title LIKE 'AI -%'
            AND pm2.meta_value IS NOT NULL
            ORDER BY p.ID
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def extract_sku_from_folder(self, folder_name: str) -> list:
        """
        Extract potential SKUs from folder name.

        Examples:
            bone-18074-bone-18074k-bone-18074gc → [18074, 18074k, 18074gc]
            bone-18440ol → [18440, 18440ol]
            18220mi → [18220, 18220mi]
            chapka-6064 → [6064]

        Returns list of potential SKUs, ordered by priority.
        """
        skus = []

        # Pattern 1: Pure numbers (5-6 digits)
        pure_numbers = re.findall(r'\b(\d{4,6})\b', folder_name)
        skus.extend(pure_numbers)

        # Pattern 2: Numbers with letter suffix (18074k, 18440ol)
        number_letter = re.findall(r'\b(\d{4,6}[a-z]{1,3})\b', folder_name, re.I)
        skus.extend(number_letter)

        # Pattern 3: Numbers with multiple letters (18220mi)
        number_letters = re.findall(r'\b(\d{4,6}[a-z]+)\b', folder_name, re.I)
        skus.extend(number_letters)

        # Remove duplicates while preserving order
        seen = set()
        unique_skus = []
        for sku in skus:
            if sku not in seen:
                seen.add(sku)
                unique_skus.append(sku)

        return unique_skus

    def find_product_by_sku(self, sku: str):
        """Find WooCommerce product by SKU (exact or partial match)."""
        # Try exact match first
        query = """
            SELECT p.ID, p.post_title, pm.meta_value as sku
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

        # Try partial match (SKU contains the number)
        query = """
            SELECT p.ID, p.post_title, pm.meta_value as sku
            FROM lx_posts p
            INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
            AND pm.meta_key = '_sku'
            AND pm.meta_value LIKE %s
            LIMIT 1
        """
        # Extract just numbers for partial match
        numbers_only = re.sub(r'\D', '', sku)
        if len(numbers_only) >= 4:
            self.cursor.execute(query, (f'%{numbers_only}%',))
            result = self.cursor.fetchone()
            if result:
                return result

        return None

    def link_images_to_product(self, product_id: int, image_ids: list):
        """Link images to product (featured + gallery)."""
        if self.dry_run:
            return

        if not image_ids:
            return

        # Get existing gallery images to preserve them
        existing_query = """
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s AND meta_key = '_product_image_gallery'
        """
        self.cursor.execute(existing_query, (product_id,))
        existing = self.cursor.fetchone()
        existing_gallery = existing['meta_value'] if existing and existing['meta_value'] else ''

        # Set first AI image as featured (if no featured exists)
        featured_id = image_ids[0]
        check_featured = """
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s AND meta_key = '_thumbnail_id'
        """
        self.cursor.execute(check_featured, (product_id,))
        has_featured = self.cursor.fetchone()

        if not has_featured:
            # Set featured image
            insert_featured = """
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_thumbnail_id', %s)
            """
            self.cursor.execute(insert_featured, (product_id, featured_id))

        # Add all AI images to gallery (append to existing)
        gallery_ids = ','.join(str(id) for id in image_ids)

        if existing_gallery:
            # Append to existing gallery
            gallery_ids = f"{existing_gallery},{gallery_ids}"

        # Update or insert gallery
        update_gallery = """
            INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
            VALUES (%s, '_product_image_gallery', %s)
            ON DUPLICATE KEY UPDATE meta_value = %s
        """
        self.cursor.execute(update_gallery, (product_id, gallery_ids, gallery_ids))

        self.conn.commit()

    def process_all(self):
        """Main process: match all AI images to products."""
        print("="*70)
        print("MATCH AI IMAGES TO PRODUCTS BY SKU")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("="*70 + "\n")

        # Get all AI images with folder metadata
        print("📥 Fetching AI images with folder metadata...")
        ai_images = self.get_ai_images_with_folders()
        print(f"✓ Found {len(ai_images)} AI images\n")

        # Group images by product folder
        images_by_folder = defaultdict(list)

        for img in ai_images:
            folder = img.get('product_folder', '')
            if folder:
                images_by_folder[folder].append(img['image_id'])

        print(f"📦 Detected {len(images_by_folder)} unique product folders\n")

        # Process each folder
        for i, (folder, image_ids) in enumerate(sorted(images_by_folder.items()), 1):
            print(f"[{i}/{len(images_by_folder)}] 🔍 {folder}")
            print(f"  Images: {len(image_ids)}")

            # Extract SKUs from folder name
            skus = self.extract_sku_from_folder(folder)

            if not skus:
                print(f"  ⚠️  Could not extract SKU from folder name")
                self.stats['no_sku_extracted'].append(folder)
                print()
                continue

            print(f"  SKUs extracted: {', '.join(skus)}")

            # Try to find product with any of the SKUs
            product = None
            matched_sku = None

            for sku in skus:
                product = self.find_product_by_sku(sku)
                if product:
                    matched_sku = sku
                    break

            if not product:
                print(f"  ⚠️  No product found for SKUs: {', '.join(skus)}")
                self.stats['no_product_found'].append(f"{folder} → {', '.join(skus)}")
                print()
                continue

            print(f"  ✓ Found: {product['post_title']} (ID: {product['ID']}, SKU: {product['sku']})")
            self.stats['products_matched'] += 1

            # Link images
            try:
                self.link_images_to_product(product['ID'], image_ids)
                self.stats['products_updated'] += 1
                self.stats['images_linked'] += len(image_ids)
                if not self.dry_run:
                    print(f"  ✓ Linked {len(image_ids)} images to product")
                else:
                    print(f"  [DRY RUN] Would link {len(image_ids)} images")
            except Exception as e:
                print(f"  ❌ Error linking images: {e}")
                self.stats['errors'].append(f"{folder}: {e}")

            print()

        return True

    def print_summary(self):
        """Print summary."""
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Products matched: {self.stats['products_matched']}")
        print(f"✓ Products updated: {self.stats['products_updated']}")
        print(f"✓ Images linked: {self.stats['images_linked']}")
        print(f"⚠️  Folders without SKU: {len(self.stats['no_sku_extracted'])}")
        print(f"⚠️  SKUs without product: {len(self.stats['no_product_found'])}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['no_sku_extracted']:
            print(f"\nFolders without SKU (first 5):")
            for folder in self.stats['no_sku_extracted'][:5]:
                print(f"  • {folder}")

        if self.stats['no_product_found']:
            print(f"\nSKUs without product match (first 10):")
            for item in self.stats['no_product_found'][:10]:
                print(f"  • {item}")

        if self.stats['errors']:
            print(f"\nErrors:")
            for error in self.stats['errors'][:5]:
                print(f"  • {error}")

        print("="*70 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Match AI images to products by SKU')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    matcher = SKUImageMatcher(dry_run=args.dry_run)

    if not matcher.connect_db():
        return 1

    try:
        success = matcher.process_all()
        matcher.print_summary()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        matcher.close_db()


if __name__ == '__main__':
    sys.exit(main())
