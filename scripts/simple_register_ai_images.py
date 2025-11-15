#!/usr/bin/env python3
"""
Simple approach: Register all AI images to WordPress Media Library.
Creates organized attachments that can be manually assigned to products.

Strategy:
1. Register all *_pro.jpg as WordPress attachments
2. Organize by category in Media Library
3. Generate report for manual review
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

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

IMAGES_BASE = Path('wordpress/wp-content/uploads/products')


class SimpleImageRegistrar:
    """Register AI images as WordPress attachments."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'registered': 0,
            'skipped': 0,
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

    def check_if_registered(self, wp_path: str) -> bool:
        """Check if image already registered."""
        query = """
            SELECT ID FROM lx_posts
            WHERE post_type = 'attachment'
            AND guid LIKE %s
            LIMIT 1
        """
        self.cursor.execute(query, (f'%{wp_path}',))
        return self.cursor.fetchone() is not None

    def register_image(self, image_path: Path) -> int:
        """Register single image."""
        # Generate WordPress paths
        rel_path = image_path.relative_to(Path('wordpress/wp-content/uploads'))
        wp_path = f"/wp-content/uploads/{rel_path}"
        guid = f"http://localhost:8080{wp_path}"

        # Check if already exists
        if self.check_if_registered(wp_path):
            self.stats['skipped'] += 1
            return 0

        if self.dry_run:
            self.stats['registered'] += 1
            return 99999

        # Extract metadata from path
        parts = image_path.relative_to(IMAGES_BASE).parts
        category = parts[0] if len(parts) > 0 else "Uncategorized"
        product_folder = parts[1] if len(parts) > 1 else "Unknown"

        post_title = f"AI - {category} - {product_folder} - {image_path.stem}"
        post_name = f"ai-{image_path.stem}"

        # Insert attachment with ALL required fields
        insert_query = """
            INSERT INTO lx_posts (
                post_author, post_date, post_date_gmt, post_content,
                post_title, post_excerpt, post_status, comment_status,
                ping_status, post_password, post_name, to_ping, pinged,
                post_modified, post_modified_gmt, post_content_filtered,
                post_parent, guid, menu_order, post_type, post_mime_type, comment_count
            ) VALUES (
                1, NOW(), NOW(), '',
                %s, '', 'inherit', 'open',
                'closed', '', %s, '', '',
                NOW(), NOW(), '',
                0, %s, 0, 'attachment', 'image/jpeg', 0
            )
        """

        self.cursor.execute(insert_query, (post_title, post_name, guid))
        attachment_id = self.cursor.lastrowid

        # Add metadata
        file_size = image_path.stat().st_size
        meta_query = """
            INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
            VALUES (%s, %s, %s)
        """

        # Basic metadata
        self.cursor.execute(meta_query, (attachment_id, '_wp_attached_file', str(rel_path)))
        self.cursor.execute(meta_query, (attachment_id, '_wp_attachment_image_alt', post_title))

        # Category tag for organization
        self.cursor.execute(meta_query, (attachment_id, '_ai_category', category))
        self.cursor.execute(meta_query, (attachment_id, '_ai_product_folder', product_folder))

        self.conn.commit()
        self.stats['registered'] += 1

        return attachment_id

    def process_all(self):
        """Process all AI images."""
        images = sorted(IMAGES_BASE.rglob('*_pro.jpg'))

        if not images:
            print("❌ No *_pro.jpg images found")
            return False

        print("="*70)
        print("WORDPRESS IMAGE REGISTRATION")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Images to process: {len(images)}")
        print("="*70 + "\n")

        # Group by category for progress tracking
        from collections import defaultdict
        by_category = defaultdict(list)
        for img in images:
            category = img.relative_to(IMAGES_BASE).parts[0]
            by_category[category].append(img)

        # Process each category
        for category, imgs in sorted(by_category.items()):
            print(f"📁 {category.upper()} ({len(imgs)} images)")

            for img in imgs:
                try:
                    self.register_image(img)
                except Exception as e:
                    self.stats['errors'].append(f"{img.name}: {e}")
                    print(f"  ❌ {img.name}: {e}")

            print(f"  ✓ Processed {len(imgs)} images\n")

        return True

    def print_summary(self):
        """Print summary."""
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Registered: {self.stats['registered']}")
        print(f"↻ Skipped (already registered): {self.stats['skipped']}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\nErrors:")
            for error in self.stats['errors'][:5]:
                print(f"  • {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")

        print("="*70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Register AI images to WordPress')
    parser.add_argument('--dry-run', action='store_true', help='Preview without changes')
    args = parser.parse_args()

    registrar = SimpleImageRegistrar(dry_run=args.dry_run)

    if not registrar.connect_db():
        return 1

    try:
        success = registrar.process_all()
        registrar.print_summary()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        registrar.close_db()


if __name__ == '__main__':
    sys.exit(main())
