#!/usr/bin/env python3
"""
Link AI images to WooCommerce products by matching folder names.

Strategy:
1. Get all AI images from WordPress Media Library
2. Extract product folder name from image path
3. Find WooCommerce product by matching post_name
4. Set first image as featured, rest as gallery
"""

import os
import re
import sys
from collections import defaultdict

import mysql.connector
from mysql.connector import Error

TABLE_PREFIX = os.environ.get('WP_TABLE_PREFIX', 'wp_')
POSTS_TABLE = f"{TABLE_PREFIX}posts"
POSTMETA_TABLE = f"{TABLE_PREFIX}postmeta"

# WordPress database
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'lisboetas_web',
    'user': 'root',
    'password': 'rootpassword'
}


class ImageProductLinker:
    """Link AI images to WooCommerce products."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'products_updated': 0,
            'matched_by_sku': 0,
            'images_linked': 0,
            'products_not_found': [],
            'errors': []
        }

    def connect_db(self):
        """Connect to WordPress database."""
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
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

    def get_all_ai_images(self):
        """Get all registered AI images with metadata."""
        query = f"""
            SELECT
                p.ID,
                p.post_title,
                p.guid,
                pm.meta_value as file_path
            FROM {POSTS_TABLE} p
            LEFT JOIN {POSTMETA_TABLE} pm ON p.ID = pm.post_id AND pm.meta_key = '_wp_attached_file'
            WHERE p.post_type = 'attachment'
            AND p.post_title LIKE 'AI -%'
            ORDER BY p.ID
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def extract_product_slug_from_path(self, file_path: str) -> str:
        """
        Extract product slug from file path.

        Example: products/boinas inverno/bone-18074-bone-18074k/img_01_pro.jpg
        Returns: bone-18074-bone-18074k
        """
        # Split path and get folder name (before last /)
        parts = file_path.split('/')
        if len(parts) >= 3:
            # Get product folder (e.g., "bone-18074-bone-18074k")
            return parts[-2]
        return None

    def find_product_by_slug(self, product_slug: str):
        """Find WooCommerce product by post_name (slug)."""
        # Try exact match first
        query = f"""
            SELECT ID, post_title, post_name
            FROM {POSTS_TABLE}
            WHERE post_type = 'product'
            AND post_status = 'publish'
            AND post_name = %s
            LIMIT 1
        """
        self.cursor.execute(query, (product_slug,))
        result = self.cursor.fetchone()

        if result:
            return result

        # Try partial match (first SKU in folder name)
        # bone-18074-bone-18074k -> try bone-18074
        first_sku = product_slug.split('-')[:2]  # Get first 2 parts (e.g., bone-18074)
        if len(first_sku) == 2:
            partial_slug = '-'.join(first_sku)
            query = f"""
                SELECT ID, post_title, post_name
                FROM {POSTS_TABLE}
                WHERE post_type = 'product'
                AND post_status = 'publish'
                AND post_name LIKE %s
                LIMIT 1
            """
            self.cursor.execute(query, (f'{partial_slug}%',))
            return self.cursor.fetchone()

        return None

    def link_images_to_product(self, product_id: int, image_ids: list):
        """Link images to product (featured + gallery)."""
        if self.dry_run:
            print(f"    [DRY RUN] Would link {len(image_ids)} images to product {product_id}")
            return

        if not image_ids:
            return

        # Set first image as featured
        featured_id = image_ids[0]

        # Check if featured image already exists
        check_query = f"""
            SELECT meta_value FROM {POSTMETA_TABLE}
            WHERE post_id = %s AND meta_key = '_thumbnail_id'
        """
        self.cursor.execute(check_query, (product_id,))
        existing = self.cursor.fetchone()

        if existing:
            # Update existing
            update_query = f"""
                UPDATE {POSTMETA_TABLE}
                SET meta_value = %s
                WHERE post_id = %s AND meta_key = '_thumbnail_id'
            """
            self.cursor.execute(update_query, (featured_id, product_id))
        else:
            # Insert new
            insert_query = f"""
                INSERT INTO {POSTMETA_TABLE} (post_id, meta_key, meta_value)
                VALUES (%s, '_thumbnail_id', %s)
            """
            self.cursor.execute(insert_query, (product_id, featured_id))

        # Set gallery images (remaining images)
        if len(image_ids) > 1:
            gallery_ids = ','.join(str(id) for id in image_ids[1:])

            # Check if gallery exists
            gallery_check = check_query.replace('_thumbnail_id', '_product_image_gallery')
            self.cursor.execute(gallery_check, (product_id,))
            existing_gallery = self.cursor.fetchone()

            if existing_gallery:
                # Append to existing gallery
                existing_ids = existing_gallery['meta_value']
                if existing_ids:
                    gallery_ids = f"{existing_ids},{gallery_ids}"

                update_query = f"""
                    UPDATE {POSTMETA_TABLE}
                    SET meta_value = %s
                    WHERE post_id = %s AND meta_key = '_product_image_gallery'
                """
                self.cursor.execute(update_query, (gallery_ids, product_id))
            else:
                # Insert new gallery
                insert_query = f"""
                    INSERT INTO {POSTMETA_TABLE} (post_id, meta_key, meta_value)
                    VALUES (%s, '_product_image_gallery', %s)
                """
                self.cursor.execute(insert_query, (product_id, gallery_ids))

        self.conn.commit()

    def extract_possible_skus(self, folder_name: str) -> list:
        """
        Extract potential SKU fragments from folder name.
        Returns list ordered by likelihood.
        """
        if not folder_name:
            return []

        patterns = [
            r'\b(\d{4,6})\b',             # pure numbers
            r'\b(\d{4,6}[a-z]{1,3})\b',   # number + short suffix
            r'\b(\d{4,6}[a-z]+)\b'        # number + longer suffix
        ]
        seen = set()
        candidates = []

        for pattern in patterns:
            for match in re.findall(pattern, folder_name, re.IGNORECASE):
                normalized = match.lower()
                if normalized not in seen:
                    seen.add(normalized)
                    candidates.append(match)

        return candidates

    def find_product_by_sku(self, sku_fragment: str):
        """Find WooCommerce product by matching SKU meta, allowing partial matches."""
        if not sku_fragment:
            return None

        # Exact match
        query = f"""
            SELECT p.ID, p.post_title, p.post_name, pm.meta_value as sku
            FROM {POSTS_TABLE} p
            INNER JOIN {POSTMETA_TABLE} pm ON p.ID = pm.post_id
            WHERE p.post_type = 'product'
            AND p.post_status = 'publish'
            AND pm.meta_key = '_sku'
            AND pm.meta_value = %s
            LIMIT 1
        """
        self.cursor.execute(query, (sku_fragment,))
        result = self.cursor.fetchone()
        if result:
            return result

        # Partial match on numeric portion
        digits = re.sub(r'\D', '', sku_fragment)
        if len(digits) >= 4:
            query = f"""
                SELECT p.ID, p.post_title, p.post_name, pm.meta_value as sku
                FROM {POSTS_TABLE} p
                INNER JOIN {POSTMETA_TABLE} pm ON p.ID = pm.post_id
                WHERE p.post_type = 'product'
                AND p.post_status = 'publish'
                AND pm.meta_key = '_sku'
                AND pm.meta_value LIKE %s
                LIMIT 1
            """
            self.cursor.execute(query, (f"%{digits}%",))
            return self.cursor.fetchone()

        return None

    def process_all(self):
        """Main process: link all AI images to products."""
        print("="*70)
        print("LINK AI IMAGES TO WOOCOMMERCE PRODUCTS")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("="*70 + "\n")

        # Get all AI images
        print("📥 Fetching AI images from WordPress...")
        ai_images = self.get_all_ai_images()
        print(f"✓ Found {len(ai_images)} AI images\n")

        # Group images by product slug
        images_by_product = defaultdict(list)

        for img in ai_images:
            file_path = img.get('file_path', '')
            if file_path:
                product_slug = self.extract_product_slug_from_path(file_path)
                if product_slug:
                    images_by_product[product_slug].append(img['ID'])

        print(f"📦 Detected {len(images_by_product)} unique products\n")

        # Process each product
        for i, (product_slug, image_ids) in enumerate(sorted(images_by_product.items()), 1):
            print(f"[{i}/{len(images_by_product)}] 🔗 {product_slug}")
            print(f"  Images: {len(image_ids)}")

            # Find WooCommerce product
            product = self.find_product_by_slug(product_slug)
            # track how we matched
            match_method = 'slug'
            match_value = product_slug

            if not product:
                possible_skus = self.extract_possible_skus(product_slug)
                for sku_candidate in possible_skus:
                    found = self.find_product_by_sku(sku_candidate)
                    if found:
                        product = found
                        match_method = 'sku'
                        match_value = sku_candidate
                        self.stats['matched_by_sku'] += 1
                        break

                if not product:
                    print(f"  ⚠️  Product not found in WooCommerce")
                    if possible_skus:
                        print(f"     Tried SKUs: {', '.join(possible_skus[:5])}")
                    self.stats['products_not_found'].append(product_slug)
                    continue

            if match_method == 'sku':
                print(f"  ✓ Matched by SKU fragment '{match_value}' → {product['post_title']} (ID: {product['ID']})")
            else:
                print(f"  ✓ Found: {product['post_title']} (ID: {product['ID']})")

            # Link images
            try:
                self.link_images_to_product(product['ID'], image_ids)
                self.stats['products_updated'] += 1
                self.stats['images_linked'] += len(image_ids)
                print(f"  ✓ Linked {len(image_ids)} images")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.stats['errors'].append(f"{product_slug}: {e}")

            print()

        return True

    def print_summary(self):
        """Print summary."""
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Products updated: {self.stats['products_updated']}")
        print(f"✓ Images linked: {self.stats['images_linked']}")
        print(f"✓ Matched via SKU fallback: {self.stats['matched_by_sku']}")
        print(f"⚠️  Products not found: {len(self.stats['products_not_found'])}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['products_not_found']:
            print(f"\nProducts not found (first 10):")
            for slug in self.stats['products_not_found'][:10]:
                print(f"  • {slug}")
            if len(self.stats['products_not_found']) > 10:
                print(f"  ... and {len(self.stats['products_not_found']) - 10} more")

        if self.stats['errors']:
            print(f"\nErrors:")
            for error in self.stats['errors'][:5]:
                print(f"  • {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")

        print("="*70 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Link AI images to WooCommerce products')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    linker = ImageProductLinker(dry_run=args.dry_run)

    if not linker.connect_db():
        return 1

    try:
        success = linker.process_all()
        linker.print_summary()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        linker.close_db()


if __name__ == '__main__':
    sys.exit(main())
