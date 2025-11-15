#!/usr/bin/env python3
"""
Add WordPress image metadata to AI images.
Reads actual image dimensions and creates proper WordPress metadata.
"""

import sys
import os
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from PIL import Image
import json

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'lisboetas_web',
    'user': 'root',
    'password': 'rootpassword'
}

WORDPRESS_ROOT = '/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress'


class MetadataAdder:
    """Add WordPress metadata to images."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.conn = None
        self.cursor = None
        self.stats = {
            'images_processed': 0,
            'metadata_added': 0,
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

    def get_ai_images(self):
        """Get all AI images (IDs 214474-214824)."""
        query = """
            SELECT p.ID, p.post_title, pm.meta_value as file_path
            FROM lx_posts p
            INNER JOIN lx_postmeta pm ON p.ID = pm.post_id
            WHERE p.ID BETWEEN 214474 AND 214824
            AND p.post_type = 'attachment'
            AND pm.meta_key = '_wp_attached_file'
            ORDER BY p.ID
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_image_dimensions(self, file_path: str):
        """Read actual image dimensions."""
        full_path = os.path.join(WORDPRESS_ROOT, 'wp-content', 'uploads', file_path)

        if not os.path.exists(full_path):
            return None

        try:
            with Image.open(full_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format.lower() if img.format else 'jpeg'
                }
        except Exception as e:
            print(f"    ⚠️  Error reading image: {e}")
            return None

    def create_metadata(self, file_path: str, dimensions: dict):
        """Create WordPress metadata structure."""
        filename = os.path.basename(file_path)

        # Generate thumbnail sizes (WordPress default + WooCommerce)
        sizes = {
            'thumbnail': self.calculate_thumbnail(dimensions, 150, 150, filename),
            'medium': self.calculate_thumbnail(dimensions, 300, 300, filename),
            'medium_large': self.calculate_thumbnail(dimensions, 768, 0, filename),
            'large': self.calculate_thumbnail(dimensions, 1024, 1024, filename),
            'woocommerce_thumbnail': self.calculate_thumbnail(dimensions, 324, 324, filename),
            'woocommerce_single': self.calculate_thumbnail(dimensions, 600, 600, filename),
            'woocommerce_gallery_thumbnail': self.calculate_thumbnail(dimensions, 100, 100, filename),
            'shop_catalog': self.calculate_thumbnail(dimensions, 324, 324, filename),
            'shop_single': self.calculate_thumbnail(dimensions, 600, 600, filename),
            'shop_thumbnail': self.calculate_thumbnail(dimensions, 100, 100, filename)
        }

        metadata = {
            'width': dimensions['width'],
            'height': dimensions['height'],
            'file': file_path,
            'sizes': sizes,
            'image_meta': {
                'aperture': '0',
                'credit': '',
                'camera': '',
                'caption': '',
                'created_timestamp': '0',
                'copyright': '',
                'focal_length': '0',
                'iso': '0',
                'shutter_speed': '0',
                'title': '',
                'orientation': '0',
                'keywords': []
            }
        }

        return metadata

    def calculate_thumbnail(self, dimensions: dict, max_width: int, max_height: int, base_filename: str):
        """Calculate thumbnail dimensions maintaining aspect ratio."""
        width = dimensions['width']
        height = dimensions['height']

        # Get filename without extension
        name_parts = base_filename.rsplit('.', 1)
        base_name = name_parts[0]
        extension = name_parts[1] if len(name_parts) > 1 else 'jpg'

        if max_height == 0:
            # Width constraint only
            if width > max_width:
                scale = max_width / width
                new_width = max_width
                new_height = int(height * scale)
                return {
                    'width': new_width,
                    'height': new_height,
                    'file': f"{base_name}-{new_width}x{new_height}.{extension}",
                    'mime-type': 'image/jpeg'
                }
        else:
            # Both constraints
            if width > max_width or height > max_height:
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                return {
                    'width': new_width,
                    'height': new_height,
                    'file': f"{base_name}-{new_width}x{new_height}.{extension}",
                    'mime-type': 'image/jpeg'
                }

        # No resize needed
        return {
            'width': width,
            'height': height,
            'file': base_filename,
            'mime-type': 'image/jpeg'
        }

    def add_metadata(self, post_id: int, metadata: dict):
        """Add metadata to image."""
        if self.dry_run:
            return

        serialized = self.serialize_php(metadata)

        # Check if metadata exists
        check_query = """
            SELECT meta_id FROM lx_postmeta
            WHERE post_id = %s AND meta_key = '_wp_attachment_metadata'
        """
        self.cursor.execute(check_query, (post_id,))
        existing = self.cursor.fetchone()

        if existing:
            # Update existing
            update_query = """
                UPDATE lx_postmeta
                SET meta_value = %s
                WHERE post_id = %s AND meta_key = '_wp_attachment_metadata'
            """
            self.cursor.execute(update_query, (serialized, post_id))
        else:
            # Insert new
            insert_query = """
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_wp_attachment_metadata', %s)
            """
            self.cursor.execute(insert_query, (post_id, serialized))

        self.conn.commit()

    def serialize_php(self, data):
        """Serialize Python dict to PHP serialized format."""

        def serialize_value(val):
            if isinstance(val, bool):
                return f"b:{1 if val else 0};"
            elif isinstance(val, int):
                return f"i:{val};"
            elif isinstance(val, str):
                return f's:{len(val)}:"{val}";'
            elif isinstance(val, dict):
                items = ''.join(serialize_value(k) + serialize_value(v) for k, v in val.items())
                return f"a:{len(val)}:{{{items}}}"
            elif isinstance(val, list):
                items = ''.join(serialize_value(i) + serialize_value(v) for i, v in enumerate(val))
                return f"a:{len(val)}:{{{items}}}"
            else:
                return 'N;'

        return serialize_value(data)

    def process_all(self):
        print("="*70)
        print("ADD IMAGE METADATA")
        print("="*70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("="*70 + "\n")

        images = self.get_ai_images()
        print(f"📷 Found {len(images)} AI images to process\n")

        for i, img in enumerate(images, 1):
            post_id = img['ID']
            file_path = img['file_path']
            title = img['post_title']

            if i % 50 == 0:
                print(f"\n[{i}/{len(images)}] Progress checkpoint...\n")

            # Get dimensions
            dimensions = self.get_image_dimensions(file_path)

            if not dimensions:
                print(f"  ⚠️  [{post_id}] {title}: Image file not found")
                self.stats['errors'].append(f"{title}: File not found")
                continue

            # Create metadata
            metadata = self.create_metadata(file_path, dimensions)

            # Add to database
            try:
                self.add_metadata(post_id, metadata)
                self.stats['metadata_added'] += 1

                if i % 10 == 0:
                    print(f"  ✓ [{post_id}] {dimensions['width']}×{dimensions['height']}px")

            except Exception as e:
                print(f"  ❌ [{post_id}] {title}: {e}")
                self.stats['errors'].append(f"{title}: {e}")

            self.stats['images_processed'] += 1

        return True

    def print_summary(self):
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Images processed: {self.stats['images_processed']}")
        print(f"✓ Metadata added: {self.stats['metadata_added']}")
        print(f"✗ Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\nErrors (first 10):")
            for error in self.stats['errors'][:10]:
                print(f"  • {error}")

        print("="*70 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Add WordPress metadata to AI images')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    args = parser.parse_args()

    adder = MetadataAdder(dry_run=args.dry_run)

    if not adder.connect_db():
        return 1

    try:
        success = adder.process_all()
        adder.print_summary()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        adder.close_db()


if __name__ == '__main__':
    sys.exit(main())
