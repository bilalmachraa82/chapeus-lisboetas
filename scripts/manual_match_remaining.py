#!/usr/bin/env python3
"""
Manual matching for remaining folders that couldn't be auto-matched by SKU.

Targets:
- Dockers Miki products (gorro-344974, gorro-miki-22100)
- Chapéus Impermeáveis (chapeu-impermeavel-art-181054, chapeu-impermeavel-art-181056)
"""

import sys
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

# Manual mappings: folder → product IDs (use exact folder names from database)
MANUAL_MAPPINGS = {
    # Dockers Miki products (distribute 10 photos across 4 products)
    'gorro-344974-gorro-de-la-estilo-bretao-miki-docker-com-aba-de-aperto-traseira': [212404, 212594],  # 5 photos → 2 products
    'gorro-miki-22100-gorro-de-la-estilo-bretao-miki-docker-com-aba-de-aperto-traseira': [212686, 212719],  # 5 photos → 2 products

    # Chapéus Impermeáveis (distribute 10 photos across 6 products)
    # Need to analyze images visually first - for now just link to main products
    'chapeu-impermeavel-art-181054-pack-12-tags-fabricado-na-italia-la-esmagavel-impermeavel': [213898, 214424],  # Main waterproof hats
    'chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel': [214125, 214141],  # Waterproof beret + bob
}


class ManualMatcher:
    """Match remaining folders manually."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'folders_processed': 0,
            'products_updated': 0,
            'images_linked': 0,
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

    def get_images_by_folder(self, folder_name: str):
        """Get all AI image IDs for a specific folder."""
        query = """
            SELECT p.ID as image_id
            FROM lx_posts p
            INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
            WHERE p.post_type = 'attachment'
            AND p.post_title LIKE 'AI -%'
            AND pm.meta_key = '_ai_product_folder'
            AND pm.meta_value = %s
            ORDER BY p.ID
        """
        self.cursor.execute(query, (folder_name,))
        results = self.cursor.fetchall()
        return [r['image_id'] for r in results]

    def get_product_info(self, product_id: int):
        """Get product title and SKU."""
        query = """
            SELECT p.post_title, pm.meta_value as sku
            FROM lx_posts p
            LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_sku'
            WHERE p.ID = %s
        """
        self.cursor.execute(query, (product_id,))
        return self.cursor.fetchone()

    def link_images_to_product(self, product_id: int, image_ids: list):
        """Link images to product (add to gallery only, don't replace featured)."""
        if self.dry_run:
            return

        if not image_ids:
            return

        # Get existing gallery
        query = """
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s AND meta_key = '_product_image_gallery'
        """
        self.cursor.execute(query, (product_id,))
        existing = self.cursor.fetchone()

        existing_gallery = existing['meta_value'] if existing and existing.get('meta_value') else ''

        # Add images to gallery (don't touch featured image)
        gallery_ids = ','.join(str(id) for id in image_ids)

        if existing_gallery:
            # Append to existing
            gallery_ids = f"{existing_gallery},{gallery_ids}"

        # Update or insert gallery
        if existing:
            update_query = """
                UPDATE lx_postmeta
                SET meta_value = %s
                WHERE post_id = %s AND meta_key = '_product_image_gallery'
            """
            self.cursor.execute(update_query, (gallery_ids, product_id))
        else:
            insert_query = """
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_product_image_gallery', %s)
            """
            self.cursor.execute(insert_query, (product_id, gallery_ids))

        self.conn.commit()

    def process_all(self):
        """Process all manual mappings."""
        print("="*70)
        print("MANUAL MATCHING - REMAINING FOLDERS")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("="*70 + "\n")

        for folder, product_ids in MANUAL_MAPPINGS.items():
            print(f"📁 {folder}")

            # Get images for this folder
            image_ids = self.get_images_by_folder(folder)

            if not image_ids:
                print(f"  ⚠️  No images found for folder")
                print()
                continue

            print(f"  Images found: {len(image_ids)}")

            # Distribute images across products
            images_per_product = len(image_ids) // len(product_ids)
            remainder = len(image_ids) % len(product_ids)

            start_idx = 0
            for i, product_id in enumerate(product_ids):
                # Get product info
                product = self.get_product_info(product_id)
                if not product:
                    print(f"  ⚠️  Product {product_id} not found")
                    continue

                # Calculate images for this product
                num_images = images_per_product + (1 if i < remainder else 0)
                product_images = image_ids[start_idx:start_idx + num_images]
                start_idx += num_images

                print(f"  → {product['post_title']} (ID: {product_id}, SKU: {product.get('sku', 'N/A')})")
                print(f"    Linking {len(product_images)} images")

                try:
                    self.link_images_to_product(product_id, product_images)
                    self.stats['products_updated'] += 1
                    self.stats['images_linked'] += len(product_images)

                    if not self.dry_run:
                        print(f"    ✓ Linked")
                    else:
                        print(f"    [DRY RUN] Would link")

                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    self.stats['errors'].append(f"{folder} → {product_id}: {e}")

            self.stats['folders_processed'] += 1
            print()

        return True

    def print_summary(self):
        """Print summary."""
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Folders processed: {self.stats['folders_processed']}")
        print(f"✓ Products updated: {self.stats['products_updated']}")
        print(f"✓ Images linked: {self.stats['images_linked']}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\nErrors:")
            for error in self.stats['errors']:
                print(f"  • {error}")

        print("="*70 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Manual matching for remaining folders')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    matcher = ManualMatcher(dry_run=args.dry_run)

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
