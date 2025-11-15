#!/usr/bin/env python3
"""
Direct Image Import - Bypass GalleryLinker complexity
Imports images directly from products/ directory structure and assigns to products
"""

import sys
import os
import re
import mimetypes
from pathlib import Path
from datetime import datetime
import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'lisboetas',
    'password': 'e$4rU9h8',
    'database': 'lisboetas_web'
}

PRODUCTS_DIR = Path(__file__).resolve().parent.parent / 'wordpress' / 'wp-content' / 'uploads' / 'products'
UPLOADS_DIR = Path(__file__).resolve().parent.parent / 'wordpress' / 'wp-content' / 'uploads'


def connect_db():
    """Connect to database"""
    return mysql.connector.connect(**DB_CONFIG)


def find_images_for_sku(sku):
    """Find images in products directory for a given SKU"""
    if not sku:
        return []

    images = []
    sku_clean = str(sku).strip()

    # Search in all category folders
    for category_folder in PRODUCTS_DIR.iterdir():
        if not category_folder.is_dir():
            continue

        # Search in SKU folders within category
        for sku_folder in category_folder.iterdir():
            if not sku_folder.is_dir():
                continue

            # Check if folder name contains the SKU
            folder_name = sku_folder.name.lower()

            # Match patterns like: "bone-22182", "18220mi", "bone-18106mi-bone-18106k"
            if sku_clean.lower() in folder_name or f"bone-{sku_clean.lower()}" in folder_name or f"-{sku_clean.lower()}" in folder_name:
                # Find main images (img_01.jpg preferred)
                for img_file in sku_folder.iterdir():
                    if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                        # Prefer img_01.jpg or img_01_pro.jpg (full size, not thumbnails)
                        if 'img_01.jpg' in img_file.name or ('img_01' in img_file.name and 'x' not in img_file.name):
                            images.insert(0, img_file)  # Priority
                        elif 'x' not in img_file.name:  # Full size images
                            images.append(img_file)

    return images


def import_image_to_media_library(image_path, product_id, product_title):
    """Import image file to WordPress media library"""
    db = connect_db()
    cursor = db.cursor()

    try:
        # Get relative path from uploads directory
        rel_path = image_path.relative_to(UPLOADS_DIR)

        # Check if image already exists
        cursor.execute("""
            SELECT ID FROM lx_posts
            WHERE post_type = 'attachment'
            AND guid LIKE %s
            LIMIT 1
        """, (f'%{rel_path}%',))

        result = cursor.fetchone()
        if result:
            attachment_id = result[0]
            print(f"  ✓ Image already in media library: {attachment_id}")
            return attachment_id

        # Create attachment post
        mime_type = mimetypes.guess_type(str(image_path))[0] or 'image/jpeg'

        cursor.execute("""
            INSERT INTO lx_posts (
                post_author, post_date, post_date_gmt, post_content, post_title,
                post_excerpt, post_status, post_type, post_mime_type, guid
            ) VALUES (
                1, NOW(), NOW(), '', %s, '', 'inherit', 'attachment', %s, %s
            )
        """, (
            product_title,
            mime_type,
            f'http://localhost:8080/wp-content/uploads/{rel_path}'
        ))

        attachment_id = cursor.lastrowid

        # Add attachment meta
        cursor.execute("""
            INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
            VALUES (%s, '_wp_attached_file', %s)
        """, (attachment_id, str(rel_path)))

        # Link attachment to product
        cursor.execute("""
            UPDATE lx_posts SET post_parent = %s
            WHERE ID = %s
        """, (product_id, attachment_id))

        db.commit()
        print(f"  ✓ Imported image to media library: {attachment_id}")
        return attachment_id

    except Exception as e:
        print(f"  ❌ Error importing image: {e}")
        db.rollback()
        return None
    finally:
        cursor.close()
        db.close()


def assign_featured_image(product_id, attachment_id):
    """Assign featured image to product"""
    db = connect_db()
    cursor = db.cursor()

    try:
        # Check if already has featured image
        cursor.execute("""
            SELECT meta_value FROM lx_postmeta
            WHERE post_id = %s AND meta_key = '_thumbnail_id'
            LIMIT 1
        """, (product_id,))

        if cursor.fetchone():
            # Update existing
            cursor.execute("""
                UPDATE lx_postmeta
                SET meta_value = %s
                WHERE post_id = %s AND meta_key = '_thumbnail_id'
            """, (attachment_id, product_id))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO lx_postmeta (post_id, meta_key, meta_value)
                VALUES (%s, '_thumbnail_id', %s)
            """, (product_id, attachment_id))

        db.commit()
        print(f"  ✓ Assigned featured image: {attachment_id}")
        return True

    except Exception as e:
        print(f"  ❌ Error assigning featured image: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()


def main():
    """Main execution"""
    print("=== DIRECT IMAGE IMPORT ===\n")

    db = connect_db()
    cursor = db.cursor()

    # Get all products
    cursor.execute("""
        SELECT p.ID, p.post_title, pm.meta_value as sku
        FROM lx_posts p
        LEFT JOIN lx_postmeta pm ON p.ID = pm.post_id AND pm.meta_key = '_sku'
        WHERE p.post_type = 'product'
        AND p.post_status = 'publish'
        ORDER BY p.ID
    """)

    products = cursor.fetchall()
    cursor.close()
    db.close()

    print(f"Found {len(products)} products\n")

    success_count = 0
    no_image_count = 0
    error_count = 0

    for product_id, title, sku in products:
        print(f"\n[{product_id}] {title} (SKU: {sku or 'NO_SKU'})")

        if not sku:
            print("  ⚠️  No SKU - skipping")
            no_image_count += 1
            continue

        # Find images
        images = find_images_for_sku(sku)

        if not images:
            print(f"  ⚠️  No images found for SKU {sku}")
            no_image_count += 1
            continue

        print(f"  Found {len(images)} images")

        # Use first image as featured
        main_image = images[0]
        print(f"  Using: {main_image.name}")

        # Import to media library
        attachment_id = import_image_to_media_library(main_image, product_id, title)

        if not attachment_id:
            error_count += 1
            continue

        # Assign as featured image
        if assign_featured_image(product_id, attachment_id):
            success_count += 1
        else:
            error_count += 1

    print(f"\n=== SUMMARY ===")
    print(f"Total products: {len(products)}")
    print(f"✅ Success: {success_count}")
    print(f"⚠️  No images: {no_image_count}")
    print(f"❌ Errors: {error_count}")
    print(f"Coverage: {(success_count / len(products) * 100):.1f}%")


if __name__ == '__main__':
    main()
