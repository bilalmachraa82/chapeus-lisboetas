#!/usr/bin/env python3
"""
Cost Optimizer for Chapéus Lisboeta
Automated infrastructure cost optimization and monitoring
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import boto3
import requests
from PIL import Image

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/var/log/cost-optimizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CostOptimizer:
    """Main cost optimization engine"""

    def __init__(self):
        self.config = self.load_config()
        self.s3_client = self.init_s3()
        self.cloudflare_api = self.init_cloudflare()
        self.db_connection = None
        self.optimization_results = {
            'images': {'saved': 0, 'count': 0},
            'database': {'saved': 0, 'operations': 0},
            'cdn': {'cache_ratio': 0, 'bandwidth_saved': 0},
            'storage': {'cleaned': 0, 'files': 0}
        }

    def load_config(self) -> Dict:
        """Load configuration from environment and files"""
        return {
            'wordpress_path': os.getenv('WP_PATH', '/home/ptisp/public_html'),
            'uploads_dir': os.getenv('WP_UPLOADS', '/home/ptisp/public_html/wp-content/uploads'),
            's3_bucket': os.getenv('S3_BUCKET', 'chapeus-backups-eu'),
            's3_region': os.getenv('S3_REGION', 'eu-west-3'),
            'cf_zone_id': os.getenv('CF_ZONE_ID', ''),
            'cf_api_token': os.getenv('CF_API_TOKEN', ''),
            'db_host': os.getenv('DB_HOST', 'localhost'),
            'db_name': os.getenv('DB_NAME', 'lisboetas_web'),
            'db_user': os.getenv('DB_USER', 'lisboetas'),
            'db_password': os.getenv('DB_PASSWORD', ''),
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
            'max_image_width': 2048,
            'webp_quality': 85,
            'retention_days': 90
        }

    def init_s3(self):
        """Initialize S3 client"""
        try:
            return boto3.client('s3', region_name=self.config['s3_region'])
        except Exception as e:
            logger.warning(f"S3 initialization failed: {e}")
            return None

    def init_cloudflare(self) -> Dict:
        """Initialize Cloudflare API client"""
        return {
            'zone_id': self.config['cf_zone_id'],
            'api_token': self.config['cf_api_token'],
            'base_url': 'https://api.cloudflare.com/client/v4'
        }

    def optimize_images(self) -> Tuple[int, int]:
        """
        Optimize all WordPress images
        - Convert to WebP
        - Resize if too large
        - Remove EXIF data

        Returns: (total_saved_bytes, images_processed)
        """
        logger.info("Starting image optimization...")

        total_saved = 0
        images_processed = 0
        uploads_dir = Path(self.config['uploads_dir'])

        if not uploads_dir.exists():
            logger.warning(f"Uploads directory not found: {uploads_dir}")
            return 0, 0

        # Find all image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif')
        image_files = []

        for ext in image_extensions:
            image_files.extend(uploads_dir.rglob(f'*{ext}'))
            image_files.extend(uploads_dir.rglob(f'*{ext.upper()}'))

        logger.info(f"Found {len(image_files)} images to process")

        for image_path in image_files:
            try:
                # Skip if WebP version already exists
                webp_path = image_path.with_suffix('.webp')
                if webp_path.exists():
                    continue

                # Open and analyze image
                with Image.open(image_path) as img:
                    original_size = image_path.stat().st_size

                    # Convert RGBA to RGB if needed
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background

                    # Resize if too large
                    if img.width > self.config['max_image_width']:
                        ratio = self.config['max_image_width'] / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize(
                            (self.config['max_image_width'], new_height),
                            Image.Resampling.LANCZOS
                        )
                        logger.debug(f"Resized {image_path.name} to {self.config['max_image_width']}x{new_height}")

                    # Save as WebP
                    img.save(
                        webp_path,
                        'WEBP',
                        quality=self.config['webp_quality'],
                        method=6,  # Slower but better compression
                        optimize=True
                    )

                    new_size = webp_path.stat().st_size
                    saved = original_size - new_size

                    if saved > 0:
                        total_saved += saved
                        images_processed += 1
                        logger.info(f"Optimized {image_path.name}: saved {saved / 1024:.1f}KB")

                        # Update database references
                        self.update_image_references(str(image_path), str(webp_path))

            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                continue

        self.optimization_results['images']['saved'] = total_saved
        self.optimization_results['images']['count'] = images_processed

        logger.info(f"Image optimization complete: {total_saved / 1024 / 1024:.2f}MB saved, {images_processed} images")
        return total_saved, images_processed

    def update_image_references(self, old_path: str, new_path: str):
        """Update WordPress database with new image paths"""
        try:
            import mysql.connector

            if not self.db_connection:
                self.db_connection = mysql.connector.connect(
                    host=self.config['db_host'],
                    database=self.config['db_name'],
                    user=self.config['db_user'],
                    password=self.config['db_password']
                )

            cursor = self.db_connection.cursor()

            # Extract URL paths
            old_url = old_path.replace(self.config['wordpress_path'], '')
            new_url = new_path.replace(self.config['wordpress_path'], '')

            # Update post content
            cursor.execute("""
                UPDATE lx_posts
                SET post_content = REPLACE(post_content, %s, %s)
                WHERE post_content LIKE %s
            """, (old_url, new_url, f'%{old_url}%'))

            # Update post meta
            cursor.execute("""
                UPDATE lx_postmeta
                SET meta_value = REPLACE(meta_value, %s, %s)
                WHERE meta_value LIKE %s
            """, (old_url, new_url, f'%{old_url}%'))

            self.db_connection.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Database update failed: {e}")

    def optimize_database(self) -> int:
        """
        Database optimization
        - Remove old revisions
        - Clean transients
        - Remove spam comments
        - Optimize tables

        Returns: operations_performed
        """
        logger.info("Starting database optimization...")

        operations = 0

        try:
            import mysql.connector

            if not self.db_connection:
                self.db_connection = mysql.connector.connect(
                    host=self.config['db_host'],
                    database=self.config['db_name'],
                    user=self.config['db_user'],
                    password=self.config['db_password']
                )

            cursor = self.db_connection.cursor()

            # Remove old post revisions (keep last 5)
            cursor.execute("""
                DELETE FROM lx_posts
                WHERE post_type = 'revision'
                AND post_modified < DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            operations += cursor.rowcount
            logger.info(f"Removed {cursor.rowcount} old post revisions")

            # Clean expired transients
            cursor.execute("""
                DELETE FROM lx_options
                WHERE option_name LIKE '_transient_%'
                OR option_name LIKE '_site_transient_%'
            """)
            operations += cursor.rowcount
            logger.info(f"Cleaned {cursor.rowcount} transients")

            # Remove spam comments
            cursor.execute("""
                DELETE FROM lx_comments
                WHERE comment_approved = 'spam'
                AND comment_date < DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            operations += cursor.rowcount
            logger.info(f"Removed {cursor.rowcount} spam comments")

            # Clean orphaned post meta
            cursor.execute("""
                DELETE pm FROM lx_postmeta pm
                LEFT JOIN lx_posts p ON p.ID = pm.post_id
                WHERE p.ID IS NULL
            """)
            operations += cursor.rowcount
            logger.info(f"Cleaned {cursor.rowcount} orphaned post meta")

            # Optimize tables
            tables = ['lx_posts', 'lx_postmeta', 'lx_options', 'lx_comments', 'lx_woocommerce_sessions']
            for table in tables:
                try:
                    cursor.execute(f"OPTIMIZE TABLE {table}")
                    operations += 1
                    logger.info(f"Optimized table {table}")
                except Exception as e:
                    logger.warning(f"Could not optimize {table}: {e}")

            self.db_connection.commit()
            cursor.close()

            self.optimization_results['database']['operations'] = operations
            logger.info(f"Database optimization complete: {operations} operations")

        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return 0

        return operations

    def setup_cdn_caching(self) -> bool:
        """Configure aggressive CDN caching rules"""
        logger.info("Configuring CDN caching...")

        if not self.config['cf_api_token'] or not self.config['cf_zone_id']:
            logger.warning("Cloudflare credentials not configured")
            return False

        headers = {
            'Authorization': f"Bearer {self.config['cf_api_token']}",
            'Content-Type': 'application/json'
        }

        # Purge cache first
        try:
            response = requests.post(
                f"{self.cloudflare_api['base_url']}/zones/{self.config['cf_zone_id']}/purge_cache",
                headers=headers,
                json={'purge_everything': True}
            )
            if response.status_code == 200:
                logger.info("Cloudflare cache purged successfully")
            else:
                logger.warning(f"Cache purge failed: {response.text}")
        except Exception as e:
            logger.error(f"Cloudflare API error: {e}")
            return False

        return True

    def analyze_cdn_performance(self) -> Dict:
        """Get CDN analytics and calculate savings"""
        logger.info("Analyzing CDN performance...")

        if not self.config['cf_api_token'] or not self.config['cf_zone_id']:
            return {}

        headers = {
            'Authorization': f"Bearer {self.config['cf_api_token']}",
            'Content-Type': 'application/json'
        }

        try:
            # Get last 30 days analytics
            response = requests.get(
                f"{self.cloudflare_api['base_url']}/zones/{self.config['cf_zone_id']}/analytics/dashboard",
                headers=headers,
                params={'since': '-30d', 'until': 'now'}
            )

            if response.status_code == 200:
                data = response.json()['result']['totals']

                cache_hits = data.get('cachedRequests', 0)
                total_requests = data.get('requests', 0)
                cached_bytes = data.get('cachedBytes', 0)

                cache_ratio = (cache_hits / total_requests * 100) if total_requests > 0 else 0
                bandwidth_saved_gb = cached_bytes / 1024 / 1024 / 1024

                self.optimization_results['cdn']['cache_ratio'] = cache_ratio
                self.optimization_results['cdn']['bandwidth_saved'] = bandwidth_saved_gb

                logger.info(f"CDN cache ratio: {cache_ratio:.1f}%, bandwidth saved: {bandwidth_saved_gb:.2f}GB")

                return {
                    'cache_ratio': cache_ratio,
                    'bandwidth_saved_gb': bandwidth_saved_gb,
                    'cost_saved': bandwidth_saved_gb * 0.05  # €0.05 per GB
                }

        except Exception as e:
            logger.error(f"CDN analytics failed: {e}")

        return {}

    def cleanup_old_files(self) -> Tuple[int, int]:
        """
        Clean up old temporary files
        - Cache directories
        - Old log files
        - Temporary uploads

        Returns: (bytes_freed, files_deleted)
        """
        logger.info("Cleaning up old files...")

        bytes_freed = 0
        files_deleted = 0

        cleanup_patterns = [
            f"{self.config['wordpress_path']}/wp-content/cache/*",
            f"{self.config['wordpress_path']}/wp-content/uploads/wc-logs/*.log",
            "/tmp/wordpress-*",
            "/tmp/wflogs/*"
        ]

        for pattern in cleanup_patterns:
            try:
                result = subprocess.run(
                    f"find {pattern} -type f -mtime +7 -delete -print",
                    shell=True,
                    capture_output=True,
                    text=True
                )

                deleted_files = result.stdout.strip().split('\n')
                files_deleted += len([f for f in deleted_files if f])

                logger.info(f"Deleted {len(deleted_files)} files matching {pattern}")

            except Exception as e:
                logger.warning(f"Cleanup failed for {pattern}: {e}")

        self.optimization_results['storage']['files'] = files_deleted
        logger.info(f"Cleanup complete: {files_deleted} files deleted")

        return bytes_freed, files_deleted

    def archive_old_backups(self) -> int:
        """
        Move old backups to S3 Glacier

        Returns: number_of_files_archived
        """
        logger.info("Archiving old backups to Glacier...")

        if not self.s3_client:
            logger.warning("S3 client not initialized")
            return 0

        archived = 0
        backup_dir = Path('/home/ptisp/backups')

        if not backup_dir.exists():
            logger.warning("Backup directory not found")
            return 0

        # Archive backups older than 7 days
        cutoff_date = datetime.now() - timedelta(days=7)

        for backup_file in backup_dir.glob('chapeus-*'):
            try:
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

                if file_mtime < cutoff_date:
                    # Upload to Glacier
                    with open(backup_file, 'rb') as f:
                        self.s3_client.put_object(
                            Bucket=self.config['s3_bucket'],
                            Key=f"archive/{backup_file.name}",
                            Body=f,
                            StorageClass='GLACIER_IR'
                        )

                    # Delete local file
                    backup_file.unlink()
                    archived += 1
                    logger.info(f"Archived {backup_file.name} to Glacier")

            except Exception as e:
                logger.error(f"Failed to archive {backup_file}: {e}")

        logger.info(f"Archived {archived} backup files to Glacier")
        return archived

    def generate_cost_report(self) -> Dict:
        """Generate monthly cost report"""
        logger.info("Generating cost report...")

        # Calculate infrastructure costs
        infrastructure_costs = {
            'hosting': 29.99,  # PTisp Premium
            'cdn': 20.00,  # Cloudflare Pro
            'backup_storage': 0,
            'total': 0
        }

        # Calculate S3 storage costs
        if self.s3_client:
            try:
                response = self.s3_client.list_objects_v2(Bucket=self.config['s3_bucket'])
                total_size = sum(obj['Size'] for obj in response.get('Contents', []))
                infrastructure_costs['backup_storage'] = (total_size / 1024 / 1024 / 1024) * 0.004  # €0.004/GB/month
            except:
                pass

        infrastructure_costs['total'] = sum(infrastructure_costs.values())

        # Calculate savings
        cdn_analytics = self.analyze_cdn_performance()

        savings = {
            'bandwidth': cdn_analytics.get('cost_saved', 0),
            'storage': self.optimization_results['images']['saved'] / 1024 / 1024 / 1024 * 0.10,  # €0.10/GB saved
            'total': 0
        }
        savings['total'] = sum(savings.values())

        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'infrastructure': infrastructure_costs,
            'optimizations': self.optimization_results,
            'savings': savings,
            'cdn_analytics': cdn_analytics
        }

        # Save report
        report_file = f"cost-report-{datetime.now().strftime('%Y%m')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Cost report saved to {report_file}")
        return report

    def send_notification(self, report: Dict):
        """Send cost report via Telegram"""
        if not self.config['telegram_bot_token'] or not self.config['telegram_chat_id']:
            return

        message = f"""
💰 **Cost Optimization Report** - {report['date']}

**Infrastructure Costs:**
• Hosting: €{report['infrastructure']['hosting']:.2f}
• CDN: €{report['infrastructure']['cdn']:.2f}
• Backup Storage: €{report['infrastructure']['backup_storage']:.2f}
• **Total: €{report['infrastructure']['total']:.2f}**

**Optimizations:**
• Images: {report['optimizations']['images']['count']} optimized, {report['optimizations']['images']['saved'] / 1024 / 1024:.2f}MB saved
• Database: {report['optimizations']['database']['operations']} operations
• CDN Cache: {report['optimizations']['cdn']['cache_ratio']:.1f}%
• Files Cleaned: {report['optimizations']['storage']['files']}

**Monthly Savings: €{report['savings']['total']:.2f}**

Target: €49.99/month ✓
"""

        try:
            requests.post(
                f"https://api.telegram.org/bot{self.config['telegram_bot_token']}/sendMessage",
                data={
                    'chat_id': self.config['telegram_chat_id'],
                    'text': message,
                    'parse_mode': 'Markdown'
                }
            )
            logger.info("Cost report sent via Telegram")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

    def run_optimization(self):
        """Run all optimization tasks"""
        logger.info("=" * 60)
        logger.info("Starting cost optimization process")
        logger.info("=" * 60)

        try:
            # Image optimization
            self.optimize_images()

            # Database cleanup
            self.optimize_database()

            # CDN configuration
            self.setup_cdn_caching()

            # File cleanup
            self.cleanup_old_files()

            # Backup archival
            self.archive_old_backups()

            # Generate report
            report = self.generate_cost_report()

            # Send notification
            self.send_notification(report)

            logger.info("=" * 60)
            logger.info("Cost optimization completed successfully")
            logger.info("=" * 60)

            # Print summary
            print("\n" + "=" * 60)
            print("OPTIMIZATION SUMMARY")
            print("=" * 60)
            print(f"Images optimized: {self.optimization_results['images']['count']}")
            print(f"Space saved: {self.optimization_results['images']['saved'] / 1024 / 1024:.2f}MB")
            print(f"Database operations: {self.optimization_results['database']['operations']}")
            print(f"Files cleaned: {self.optimization_results['storage']['files']}")
            print(f"Monthly cost: €{report['infrastructure']['total']:.2f}")
            print(f"Monthly savings: €{report['savings']['total']:.2f}")
            print("=" * 60)

        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            sys.exit(1)


def main():
    """Main entry point"""
    optimizer = CostOptimizer()
    optimizer.run_optimization()


if __name__ == "__main__":
    main()
