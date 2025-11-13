#!/usr/bin/env python3
"""
Set first AI image as featured image for products that have AI images in gallery.
"""

import sys
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'lisboetas_web',
    'user': 'root',
    'password': 'rootpassword'
}


class FeaturedImageFixer:
    """Set AI images as featured."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'products_updated': 0,
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

    def get_products_with_ai_images(self):
        """Get all products that have AI images in their gallery."""
        query = """
            SELECT DISTINCT
                p.ID as product_id,
                p.post_title,
                pm.meta_value as gallery_ids
            FROM lx_posts p
            INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
            WHERE p.post_type = 'product'
            AND pm.meta_key = '_product_image_gallery'
            AND pm.meta_value REGEXP '214[0-9]{3}'
            ORDER BY p.ID
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_first_ai_image_from_gallery(self, gallery_ids: str):
        """Extract first AI image ID from gallery (IDs 214474-214824)."""
        ids = gallery_ids.split(',')
        for img_id in ids:
            img_id = img_id.strip()
            if img_id.isdigit():
                img_id_int = int(img_id)
                if 214474 <= img_id_int <= 214824:
                    return img_id_int
        return None

    def update_featured_image(self, product_id: int, image_id: int):
        """Update product featured image."""
        if self.dry_run:
            return

        # Update existing thumbnail_id
        update_query = """
            UPDATE lx_postmeta
            SET meta_value = %s
            WHERE post_id = %s AND meta_key = '_thumbnail_id'
        """
        self.cursor.execute(update_query, (image_id, product_id))

        # If no rows affected, insert new
        if self.cursor.rowcount == 0:
            insert_query = """
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_thumbnail_id', %s)
            """
            self.cursor.execute(insert_query, (product_id, image_id))

        self.conn.commit()

    def process_all(self):
        print("="*70)
        print("SET AI IMAGES AS FEATURED")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("="*70 + "\n")

        products = self.get_products_with_ai_images()
        print(f"📦 Found {len(products)} products with AI images\n")

        for i, product in enumerate(products, 1):
            print(f"[{i}/{len(products)}] {product['post_title']}")

            # Get first AI image from gallery
            first_ai = self.get_first_ai_image_from_gallery(product['gallery_ids'])

            if not first_ai:
                print(f"  ⚠️  No AI image found in gallery")
                continue

            # Get AI image title
            img_query = "SELECT post_title FROM lx_posts WHERE ID = %s"
            self.cursor.execute(img_query, (first_ai,))
            img = self.cursor.fetchone()
            img_title = img['post_title'] if img else f"ID {first_ai}"

            print(f"  Setting featured: {img_title} (ID: {first_ai})")

            try:
                self.update_featured_image(product['product_id'], first_ai)
                self.stats['products_updated'] += 1

                if not self.dry_run:
                    print(f"  ✓ Updated")
                else:
                    print(f"  [DRY RUN] Would update")

            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.stats['errors'].append(f"{product['post_title']}: {e}")

            print()

        return True

    def print_summary(self):
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Products updated: {self.stats['products_updated']}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\nErrors:")
            for error in self.stats['errors']:
                print(f"  • {error}")

        print("="*70 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Set AI images as featured')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    fixer = FeaturedImageFixer(dry_run=args.dry_run)

    if not fixer.connect_db():
        return 1

    try:
        success = fixer.process_all()
        fixer.print_summary()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        fixer.close_db()


if __name__ == '__main__':
    sys.exit(main())
