#!/usr/bin/env python3
"""
Register AI-generated images to WordPress Media Library.
Associates images with WooCommerce products based on SKU matching.

Usage:
    python3 scripts/register_ai_images_wordpress.py --dry-run  # Preview
    python3 scripts/register_ai_images_wordpress.py            # Execute
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import mysql.connector
from mysql.connector import Error

# WordPress database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'lisboetas_web',
    'user': 'root',
    'password': 'rootpassword'
}

# Paths
IMAGES_BASE = Path('/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/uploads/products')
WP_UPLOADS_PATH = '/wp-content/uploads/products'


class WordPressImageRegistrar:
    """Register images in WordPress and associate with products."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'images_registered': 0,
            'products_updated': 0,
            'errors': []
        }

    def connect_db(self):
        """Connect to WordPress database."""
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            print("✓ Connected to WordPress database")
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

    def extract_sku_from_path(self, image_path: Path) -> Optional[str]:
        """
        Extract SKU from image path.

        Example: products/boinas inverno/bone-18074-bone-18074k/img_01_pro.jpg
        Returns: bone-18074
        """
        parts = image_path.relative_to(IMAGES_BASE).parts
        if len(parts) >= 2:
            # Product folder name contains SKU(s)
            product_folder = parts[1]

            # Extract first SKU (before first dash or space)
            # bone-18074-bone-18074k-bone-18074gc -> bone-18074
            match = re.match(r'^([^-\s]+(?:-[^-\s]+)*?)(?:-|$)', product_folder)
            if match:
                return match.group(1)

        return None

    def find_product_by_sku(self, sku: str) -> Optional[int]:
        """Find WooCommerce product ID by SKU."""
        query = """
            SELECT p.ID
            FROM lx_posts p
            INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
            WHERE p.post_type IN ('product', 'product_variation')
            AND pm.meta_key = '_sku'
            AND pm.meta_value = %s
            LIMIT 1
        """

        self.cursor.execute(query, (sku,))
        result = self.cursor.fetchone()

        return result['ID'] if result else None

    def register_image_to_media_library(
        self,
        image_path: Path,
        product_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Register image in WordPress Media Library.

        Returns: attachment_id or None
        """
        if self.dry_run:
            return 99999  # Fake ID for dry run

        # Generate relative path for WordPress
        relative_path = image_path.relative_to(
            Path('/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/uploads')
        )
        wp_path = f"/wp-content/uploads/{relative_path}"

        # Check if already registered
        check_query = """
            SELECT ID FROM lx_posts
            WHERE post_type = 'attachment'
            AND guid LIKE %s
            LIMIT 1
        """
        self.cursor.execute(check_query, (f'%{wp_path}',))
        existing = self.cursor.fetchone()

        if existing:
            print(f"    ↻ Already registered (ID: {existing['ID']})")
            return existing['ID']

        # Insert attachment post
        insert_post = """
            INSERT INTO lx_posts (
                post_author, post_date, post_date_gmt, post_content,
                post_title, post_excerpt, post_status, comment_status,
                ping_status, post_name, post_modified, post_modified_gmt,
                post_parent, guid, menu_order, post_type, post_mime_type
            ) VALUES (
                1, NOW(), NOW(), '',
                %s, '', 'inherit', 'open',
                'closed', %s, NOW(), NOW(),
                %s, %s, 0, 'attachment', 'image/jpeg'
            )
        """

        post_title = image_path.stem.replace('_', ' ').title()
        post_name = image_path.stem
        parent_id = product_id if product_id else 0
        guid = f"http://localhost:8080{wp_path}"

        self.cursor.execute(insert_post, (post_title, post_name, parent_id, guid))
        attachment_id = self.cursor.lastrowid

        # Add attachment metadata
        file_size = image_path.stat().st_size

        meta_data = [
            ('_wp_attached_file', str(relative_path)),
            ('_wp_attachment_metadata', json.dumps({
                'width': 2048,  # Will be updated by WordPress
                'height': 2048,
                'file': str(relative_path),
                'filesize': file_size
            }))
        ]

        insert_meta = """
            INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
            VALUES (%s, %s, %s)
        """

        for meta_key, meta_value in meta_data:
            self.cursor.execute(insert_meta, (attachment_id, meta_key, meta_value))

        self.conn.commit()
        return attachment_id

    def associate_images_with_product(
        self,
        product_id: int,
        image_ids: List[int]
    ):
        """
        Associate images with WooCommerce product.
        First image = featured, rest = gallery.
        """
        if self.dry_run:
            print(f"    [DRY RUN] Would set {len(image_ids)} images to product {product_id}")
            return

        if not image_ids:
            return

        # Set featured image (first image)
        featured_id = image_ids[0]
        update_featured = """
            INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
            VALUES (%s, '_thumbnail_id', %s)
            ON DUPLICATE KEY UPDATE meta_value = %s
        """
        self.cursor.execute(update_featured, (product_id, featured_id, featured_id))

        # Set gallery (remaining images)
        if len(image_ids) > 1:
            gallery_ids = ','.join(str(id) for id in image_ids[1:])
            update_gallery = """
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_product_image_gallery', %s)
                ON DUPLICATE KEY UPDATE meta_value = %s
            """
            self.cursor.execute(update_gallery, (product_id, gallery_ids, gallery_ids))

        self.conn.commit()

    def process_all_images(self):
        """Main process: register all AI images and associate with products."""

        # Find all *_pro.jpg images
        images = sorted(IMAGES_BASE.rglob('*_pro.jpg'))

        if not images:
            print("❌ No *_pro.jpg images found")
            return False

        print(f"\n{'='*70}")
        print(f"WORDPRESS IMAGE REGISTRATION")
        print(f"{'='*70}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Images found: {len(images)}")
        print(f"{'='*70}\n")

        # Group images by SKU
        by_sku: Dict[str, List[Path]] = {}

        for img in images:
            sku = self.extract_sku_from_path(img)
            if sku:
                if sku not in by_sku:
                    by_sku[sku] = []
                by_sku[sku].append(img)

        print(f"📦 Products detected: {len(by_sku)}\n")

        # Process each product
        for i, (sku, img_list) in enumerate(sorted(by_sku.items()), 1):
            print(f"[{i}/{len(by_sku)}] 🎩 SKU: {sku}")
            print(f"  Images: {len(img_list)}")

            # Find WooCommerce product
            product_id = self.find_product_by_sku(sku)

            if not product_id:
                print(f"  ⚠️  Product not found in WooCommerce (will register images anyway)")
                self.stats['errors'].append(f"SKU {sku}: Product not found")

            # Register each image
            attachment_ids = []
            for img_path in sorted(img_list):
                attachment_id = self.register_image_to_media_library(
                    img_path,
                    product_id
                )
                if attachment_id:
                    attachment_ids.append(attachment_id)
                    self.stats['images_registered'] += 1

            # Associate with product
            if product_id and attachment_ids:
                self.associate_images_with_product(product_id, attachment_ids)
                self.stats['products_updated'] += 1
                print(f"  ✓ Associated {len(attachment_ids)} images with product")

            print()

        return True

    def print_summary(self):
        """Print final summary."""
        print(f"\n{'='*70}")
        print(f"SUMMARY")
        print(f"{'='*70}")
        print(f"✓ Images registered: {self.stats['images_registered']}")
        print(f"✓ Products updated: {self.stats['products_updated']}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\nErrors:")
            for error in self.stats['errors'][:10]:
                print(f"  • {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")

        print(f"{'='*70}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Register AI images to WordPress')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    registrar = WordPressImageRegistrar(dry_run=args.dry_run)

    # Connect to database
    if not registrar.connect_db():
        return 1

    try:
        # Process images
        success = registrar.process_all_images()

        # Print summary
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
