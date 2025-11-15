#!/usr/bin/env python3
"""
Performance Optimization Report for WooCommerce
Analyzes site performance and provides optimization recommendations.

Usage:
    python3 scripts/performance_optimization.py
    python3 scripts/performance_optimization.py --detailed
    python3 scripts/performance_optimization.py --export

Author: Claude Code (Opus 4.1)
Date: 2025-11-13
"""

import argparse
import csv
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
BASE_PATH = Path("/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)")
UPLOADS_PATH = BASE_PATH / "wordpress/wp-content/uploads"
DOCKER_CONTAINER = "chapeus_wordpress"
REPORT_PATH = BASE_PATH / "relatorios/performance_optimization_report.md"


def get_database_size() -> Tuple[float, str]:
    """Get WordPress database size."""
    try:
        cmd = [
            "docker", "exec", DOCKER_CONTAINER,
            "wp", "db", "size",
            "--allow-root"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            size_str = result.stdout.strip()
            # Parse size (format: "50.2M" or "1.5G")
            if 'M' in size_str:
                size_mb = float(size_str.replace('M', ''))
                return size_mb, size_str
            elif 'G' in size_str:
                size_gb = float(size_str.replace('G', ''))
                return size_gb * 1024, size_str

        return 0, "Unknown"

    except Exception:
        return 0, "Unknown"


def analyze_uploads_directory() -> Dict:
    """Analyze wp-content/uploads directory."""
    stats = {
        'total_files': 0,
        'total_size_mb': 0,
        'images': 0,
        'images_size_mb': 0,
        'enhanced_images': 0,
        'enhanced_size_mb': 0,
        'other': 0,
        'other_size_mb': 0,
        'largest_files': []
    }

    if not UPLOADS_PATH.exists():
        return stats

    all_files = list(UPLOADS_PATH.rglob('*'))

    for file_path in all_files:
        if not file_path.is_file():
            continue

        stats['total_files'] += 1
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        stats['total_size_mb'] += file_size_mb

        # Categorize
        if '_pro.' in file_path.name:
            stats['enhanced_images'] += 1
            stats['enhanced_size_mb'] += file_size_mb
        elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            stats['images'] += 1
            stats['images_size_mb'] += file_size_mb
        else:
            stats['other'] += 1
            stats['other_size_mb'] += file_size_mb

        # Track largest files
        stats['largest_files'].append((file_path, file_size_mb))

    # Sort and keep top 10 largest
    stats['largest_files'] = sorted(
        stats['largest_files'],
        key=lambda x: -x[1]
    )[:10]

    return stats


def check_plugins_installed() -> Dict[str, bool]:
    """Check which optimization plugins are installed."""
    plugins = {
        'wp-rocket': False,
        'autoptimize': False,
        'wp-smush': False,
        'imagify': False,
        'wp-super-cache': False,
        'w3-total-cache': False
    }

    try:
        cmd = [
            "docker", "exec", DOCKER_CONTAINER,
            "wp", "plugin", "list",
            "--field=name",
            "--allow-root"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            installed = result.stdout.strip().split('\n')
            for plugin in plugins.keys():
                if plugin in installed:
                    plugins[plugin] = True

    except Exception:
        pass

    return plugins


def generate_recommendations(stats: Dict, plugins: Dict[str, bool]) -> List[str]:
    """Generate optimization recommendations."""
    recommendations = []

    # Database optimization
    db_size_mb, _ = get_database_size()
    if db_size_mb > 100:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Database',
            'issue': f'Database size is {db_size_mb:.1f}MB',
            'recommendation': 'Run database optimization with WP-CLI',
            'command': 'docker exec chapeus_wordpress wp db optimize --allow-root'
        })

    # Image optimization
    if stats['images_size_mb'] > 100:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Images',
            'issue': f'{stats["images"]} images using {stats["images_size_mb"]:.1f}MB',
            'recommendation': 'Install image optimization plugin (WP-Smush or Imagify)',
            'command': 'wp plugin install wp-smushit --activate --allow-root'
        })

    # Enhanced images (high quality)
    if stats['enhanced_size_mb'] > 50:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'AI Images',
            'issue': f'{stats["enhanced_images"]} AI images using {stats["enhanced_size_mb"]:.1f}MB',
            'recommendation': 'Convert PNG to WebP for 30-50% smaller size',
            'command': 'Consider WebP conversion for enhanced images'
        })

    # Caching
    if not any(plugins.values()):
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Caching',
            'issue': 'No caching plugin installed',
            'recommendation': 'Install WP Rocket or WP Super Cache',
            'command': 'wp plugin install wp-super-cache --activate --allow-root'
        })

    # Object cache
    recommendations.append({
        'priority': 'MEDIUM',
        'category': 'Object Cache',
        'issue': 'Object caching not detected',
        'recommendation': 'Consider Redis or Memcached for object caching',
        'command': 'Requires server-level configuration'
    })

    return recommendations


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Analyze and optimize WordPress performance'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Run detailed analysis'
    )
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export report to Markdown'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("WORDPRESS PERFORMANCE OPTIMIZATION ANALYSIS")
    print("=" * 80)
    print()

    # Analyze uploads
    print("📊 Analyzing wp-content/uploads...")
    stats = analyze_uploads_directory()

    print(f"\nFiles: {stats['total_files']}")
    print(f"Total size: {stats['total_size_mb']:.1f}MB")
    print(f"  • Images: {stats['images']} ({stats['images_size_mb']:.1f}MB)")
    print(f"  • AI Enhanced: {stats['enhanced_images']} ({stats['enhanced_size_mb']:.1f}MB)")
    print(f"  • Other: {stats['other']} ({stats['other_size_mb']:.1f}MB)")

    # Check database
    print("\n📊 Checking database...")
    db_size_mb, db_size_str = get_database_size()
    print(f"Database size: {db_size_str}")

    # Check plugins
    print("\n📊 Checking optimization plugins...")
    plugins = check_plugins_installed()
    installed_count = sum(plugins.values())
    print(f"Optimization plugins installed: {installed_count}/6")
    for plugin, installed in plugins.items():
        status = "✅" if installed else "❌"
        print(f"  {status} {plugin}")

    # Generate recommendations
    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)

    recommendations = generate_recommendations(stats, plugins)

    for i, rec in enumerate(recommendations, 1):
        print(f"\n[{rec['priority']}] {rec['category']}")
        print(f"Issue: {rec['issue']}")
        print(f"Recommendation: {rec['recommendation']}")
        if rec['command'] != 'Requires server-level configuration':
            print(f"Command: {rec['command']}")

    # Export report
    if args.export:
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write("# 🚀 WordPress Performance Optimization Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            f.write("## 📊 Current Status\n\n")
            f.write(f"### Uploads Directory\n")
            f.write(f"- Total files: {stats['total_files']}\n")
            f.write(f"- Total size: {stats['total_size_mb']:.1f}MB\n")
            f.write(f"- Images: {stats['images']} ({stats['images_size_mb']:.1f}MB)\n")
            f.write(f"- AI Enhanced: {stats['enhanced_images']} ({stats['enhanced_size_mb']:.1f}MB)\n")
            f.write(f"- Other: {stats['other']} ({stats['other_size_mb']:.1f}MB)\n\n")

            f.write(f"### Database\n")
            f.write(f"- Size: {db_size_str}\n\n")

            f.write(f"### Optimization Plugins\n")
            f.write(f"- Installed: {installed_count}/6\n")
            for plugin, installed in plugins.items():
                status = "✅" if installed else "❌"
                f.write(f"- {status} {plugin}\n")
            f.write("\n")

            f.write("---\n\n")
            f.write("## 🎯 Recommendations\n\n")

            for rec in recommendations:
                f.write(f"### [{rec['priority']}] {rec['category']}\n\n")
                f.write(f"**Issue:** {rec['issue']}\n\n")
                f.write(f"**Recommendation:** {rec['recommendation']}\n\n")
                if rec['command'] != 'Requires server-level configuration':
                    f.write(f"**Command:**\n```bash\n{rec['command']}\n```\n\n")
                else:
                    f.write(f"**Note:** {rec['command']}\n\n")

        print(f"\n✅ Report exported: {REPORT_PATH}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
