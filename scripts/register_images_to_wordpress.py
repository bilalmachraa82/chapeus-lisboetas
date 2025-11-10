#!/usr/bin/env python3
"""
Register uploaded images to WordPress media library via WP-CLI.

This script finds all images in /wp-content/uploads/products/ and registers
them in WordPress media library so they can be used by WooCommerce products.

Usage:
    python3 scripts/register_images_to_wordpress.py
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict

# Configuration
WORDPRESS_CONTAINER = "chapeus_wordpress"
IMAGES_PATH = "/var/www/html/wp-content/uploads/products"
WP_USER = "lisboetas"

def run_docker_command(cmd: List[str]) -> str:
    """Run command in WordPress Docker container."""
    full_cmd = ["docker", "exec", WORDPRESS_CONTAINER] + cmd
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return ""
    return result.stdout.strip()

def find_all_images() -> List[str]:
    """Find all image files in products directory."""
    cmd = [
        "find", IMAGES_PATH,
        "-type", "f",
        "(",
        "-iname", "*.jpg",
        "-o", "-iname", "*.jpeg",
        "-o", "-iname", "*.png",
        "-o", "-iname", "*.webp",
        "-o", "-iname", "*.gif",
        ")"
    ]
    output = run_docker_command(cmd)
    if not output:
        return []
    return output.split('\n')

def is_image_registered(filepath: str) -> bool:
    """Check if image is already in media library."""
    # Extract filename for checking
    filename = Path(filepath).name
    cmd = [
        "wp", "post", "list",
        "--post_type=attachment",
        f"--s={filename}",
        "--format=count",
        "--allow-root"
    ]
    count = run_docker_command(cmd)
    return int(count) > 0 if count.isdigit() else False

def register_image(filepath: str) -> Dict:
    """Register image in WordPress media library."""
    cmd = [
        "wp", "media", "import", filepath,
        "--porcelain",
        "--allow-root"
    ]
    attachment_id = run_docker_command(cmd)

    if attachment_id.isdigit():
        return {
            'success': True,
            'id': int(attachment_id),
            'path': filepath
        }
    else:
        return {
            'success': False,
            'error': attachment_id,
            'path': filepath
        }

def main():
    """Main execution."""
    print("=" * 80)
    print("WORDPRESS MEDIA LIBRARY REGISTRATION")
    print("=" * 80)
    print(f"\nContainer: {WORDPRESS_CONTAINER}")
    print(f"Images path: {IMAGES_PATH}")
    print(f"WordPress user: {WP_USER}\n")

    # Find all images
    print("Finding images...")
    images = find_all_images()
    if not images:
        print("❌ No images found")
        return

    print(f"✓ Found {len(images)} image files\n")

    # Process images
    stats = {
        'total': len(images),
        'registered': 0,
        'skipped': 0,
        'failed': 0
    }

    for i, img_path in enumerate(images, 1):
        filename = Path(img_path).name

        # Check if already registered
        if is_image_registered(img_path):
            stats['skipped'] += 1
            print(f"[{i}/{len(images)}] ⏭  {filename} (already in library)")
            continue

        # Register image
        print(f"[{i}/{len(images)}] 📤 Registering {filename}...", end=' ')
        result = register_image(img_path)

        if result['success']:
            stats['registered'] += 1
            print(f"✓ ID: {result['id']}")
        else:
            stats['failed'] += 1
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")

    # Summary
    print("\n" + "=" * 80)
    print("REGISTRATION SUMMARY")
    print("=" * 80)
    print(f"Total images: {stats['total']}")
    print(f"Registered: {stats['registered']} ✓")
    print(f"Skipped (already in library): {stats['skipped']}")
    print(f"Failed: {stats['failed']}")
    print(f"\nSuccess rate: {(stats['registered']/(stats['total']-stats['skipped'])*100):.1f}%")

    if stats['registered'] > 0:
        print("\n✅ Images registered successfully!")
        print("\nNext steps:")
        print("1. Go to WordPress admin: http://localhost:8080/wp-admin")
        print("2. Check Media Library to verify images")
        print("3. Import products CSV via WooCommerce → Products → Import")
        print("4. WooCommerce will automatically link images to products")

    if stats['failed'] > 0:
        print("\n⚠️  Some images failed to register. Check WordPress logs:")
        print("docker logs chapeus_wordpress | tail -50")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
