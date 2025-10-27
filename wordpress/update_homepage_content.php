<?php
/**
 * Emergency Homepage Update Script
 *
 * Updates homepage content using WordPress APIs (respects hooks/filters)
 */

// Load WordPress
require_once(__DIR__ . '/wp-load.php');

// Security check - allow access without login for emergency
// In production, add authentication

echo "<h1>Homepage Content Update</h1>";
echo "<pre>";

// Read new content
$new_content_file = __DIR__ . '/homepage_photos_updated.html';

if (!file_exists($new_content_file)) {
    die("ERROR: homepage_photos_updated.html not found!\n");
}

$new_content = file_get_contents($new_content_file);

echo "Content loaded: " . strlen($new_content) . " bytes\n\n";

// Update post using WordPress API (triggers hooks)
$post_id = 22;

$result = wp_update_post(array(
    'ID' => $post_id,
    'post_content' => $new_content,
    'post_modified' => current_time('mysql'),
    'post_modified_gmt' => current_time('mysql', 1)
), true);

if (is_wp_error($result)) {
    echo "ERROR: " . $result->get_error_message() . "\n";
} else {
    echo "✓ Post $post_id updated successfully\n\n";

    // Clear all caches
    echo "Clearing caches...\n";

    // WordPress object cache
    wp_cache_flush();
    echo "✓ Object cache flushed\n";

    // Transients
    global $wpdb;
    $wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '%_transient_%'");
    echo "✓ Transients cleared\n";

    // Rewrite rules
    flush_rewrite_rules();
    echo "✓ Rewrite rules flushed\n";

    // WooCommerce cache (if exists)
    if (function_exists('wc_delete_shop_order_transients')) {
        wc_delete_shop_order_transients();
        echo "✓ WooCommerce cache cleared\n";
    }

    echo "\n=========================================\n";
    echo "SUCCESS! Homepage updated.\n";
    echo "=========================================\n\n";
    echo "Check homepage: <a href='/' target='_blank'>http://localhost:8080/</a>\n\n";

    // Show first 200 chars of new content
    echo "New content preview:\n";
    echo htmlspecialchars(substr($new_content, 0, 200)) . "...\n";
}

echo "</pre>";
?>
