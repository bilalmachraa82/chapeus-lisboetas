<?php
/**
 * Emergency Cache Flush Script
 *
 * Place in WordPress root and access via browser to clear ALL caches
 */

// Load WordPress
require_once(__DIR__ . '/wp-load.php');

if (!is_user_logged_in() || !current_user_can('manage_options')) {
    die('Access denied. Please login as administrator.');
}

echo "<h1>Emergency Cache Flush</h1>";
echo "<pre>";

// 1. WordPress transients
echo "Clearing WordPress transients...\n";
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '%_transient_%'");
echo "✓ Transients cleared\n\n";

// 2. WordPress object cache
echo "Flushing WordPress object cache...\n";
wp_cache_flush();
echo "✓ Object cache flushed\n\n";

// 3. Rewrite rules
echo "Flushing rewrite rules...\n";
flush_rewrite_rules();
echo "✓ Rewrite rules flushed\n\n";

// 4. Update post to trigger hooks
echo "Updating homepage post...\n";
wp_update_post(array(
    'ID' => 22,
    'post_modified' => current_time('mysql'),
    'post_modified_gmt' => current_time('mysql', 1)
));
echo "✓ Homepage updated\n\n";

// 5. Clear WooCommerce cache if exists
if (function_exists('wc_delete_shop_order_transients')) {
    echo "Clearing WooCommerce transients...\n";
    wc_delete_shop_order_transients();
    echo "✓ WooCommerce transients cleared\n\n";
}

// 6. Yoast SEO cache
if (class_exists('WPSEO_Options')) {
    echo "Clearing Yoast SEO cache...\n";
    delete_transient('wpseo_sitemap_cache_validator');
    echo "✓ Yoast cache cleared\n\n";
}

echo "\n=========================================\n";
echo "ALL CACHES CLEARED!\n";
echo "=========================================\n\n";
echo "Now try accessing homepage: <a href='/'>http://localhost:8080/</a>\n";
echo "</pre>";
?>
