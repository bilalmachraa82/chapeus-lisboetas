#!/usr/bin/env python3
"""
Fix duplicate _product_image_gallery entries by keeping only the most complete one.
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


class GalleryFixer:
    """Fix duplicate gallery entries."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'products_fixed': 0,
            'entries_deleted': 0,
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

    def get_duplicate_galleries(self):
        """Get all products with duplicate gallery entries."""
        query = """
            SELECT post_id, COUNT(*) as count
            FROM lx_postmeta
            WHERE meta_key = '_product_image_gallery'
            GROUP BY post_id
            HAVING count > 1
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_all_galleries_for_product(self, post_id: int):
        """Get all gallery entries for a product."""
        query = """
            SELECT meta_id, meta_value
            FROM lx_postmeta
            WHERE post_id = %s AND meta_key = '_product_image_gallery'
            ORDER BY meta_id
        """
        self.cursor.execute(query, (post_id,))
        return self.cursor.fetchall()

    def delete_meta_entry(self, meta_id: int):
        """Delete a specific meta entry."""
        if self.dry_run:
            return

        query = "DELETE FROM lx_postmeta WHERE meta_id = %s"
        self.cursor.execute(query, (meta_id,))
        self.conn.commit()

    def process_all(self):
        print("="*70)
        print("FIX DUPLICATE GALLERY ENTRIES")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("="*70 + "\n")

        # Get products with duplicates
        duplicates = self.get_duplicate_galleries()
        print(f"📦 Found {len(duplicates)} products with duplicate galleries\n")

        for i, dup in enumerate(duplicates, 1):
            post_id = dup['post_id']
            count = dup['count']

            # Get product name
            name_query = "SELECT post_title FROM lx_posts WHERE ID = %s"
            self.cursor.execute(name_query, (post_id,))
            product = self.cursor.fetchone()
            product_name = product['post_title'] if product else f"ID {post_id}"

            print(f"[{i}/{len(duplicates)}] {product_name}")
            print(f"  Duplicate entries: {count}")

            # Get all gallery entries
            galleries = self.get_all_galleries_for_product(post_id)

            # Find the most complete one (most image IDs)
            best = max(galleries, key=lambda g: len(g['meta_value'].split(',')))
            best_count = len(best['meta_value'].split(','))

            print(f"  Best entry: meta_id={best['meta_id']} ({best_count} images)")

            # Delete the others
            to_delete = [g for g in galleries if g['meta_id'] != best['meta_id']]

            for entry in to_delete:
                entry_count = len(entry['meta_value'].split(','))
                print(f"  Deleting: meta_id={entry['meta_id']} ({entry_count} images)")

                try:
                    self.delete_meta_entry(entry['meta_id'])
                    self.stats['entries_deleted'] += 1

                    if not self.dry_run:
                        print(f"    ✓ Deleted")
                    else:
                        print(f"    [DRY RUN] Would delete")

                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    self.stats['errors'].append(f"{product_name}: {e}")

            self.stats['products_fixed'] += 1
            print()

        return True

    def print_summary(self):
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Products fixed: {self.stats['products_fixed']}")
        print(f"✓ Duplicate entries deleted: {self.stats['entries_deleted']}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\nErrors:")
            for error in self.stats['errors']:
                print(f"  • {error}")

        print("="*70 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Fix duplicate gallery entries')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    fixer = GalleryFixer(dry_run=args.dry_run)

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
