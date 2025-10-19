<?php
/**
 * 🔍 DEEP DIAGNOSTIC & FIX - Root Cause Analysis
 * Comprehensive check of why products don't show on frontend
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🔍 DEEP DIAGNOSTIC - FINDING ROOT CAUSE\n\n";
echo str_repeat("=", 80) . "\n\n";

$issues_found = [];
$fixes_applied = [];

// ============================================================================
// 1. CHECK WOOCOMMERCE CATALOG VISIBILITY
// ============================================================================

echo "1️⃣ CHECKING PRODUCT CATALOG VISIBILITY...\n\n";

$all_products = get_posts([
    'post_type' => 'product',
    'posts_per_page' => -1,
    'post_status' => 'any'
]);

$visibility_stats = [
    'visible' => 0,
    'catalog' => 0,
    'search' => 0,
    'hidden' => 0,
    'draft' => 0,
    'publish' => 0
];

foreach ($all_products as $product_post) {
    $product = wc_get_product($product_post->ID);
    if (!$product) continue;
    
    $visibility = $product->get_catalog_visibility();
    $status = $product_post->post_status;
    
    if (isset($visibility_stats[$visibility])) {
        $visibility_stats[$visibility]++;
    }
    
    if ($status == 'publish') {
        $visibility_stats['publish']++;
    } else {
        $visibility_stats['draft']++;
    }
}

echo "   📊 Visibility Stats:\n";
foreach ($visibility_stats as $type => $count) {
    $icon = $count > 0 ? '✅' : '❌';
    echo "      $icon $type: $count\n";
}

if ($visibility_stats['hidden'] > 0) {
    $issues_found[] = "Hidden products: {$visibility_stats['hidden']}";
    echo "\n   🚨 ISSUE: {$visibility_stats['hidden']} products are HIDDEN!\n";
}

if ($visibility_stats['draft'] > 0) {
    $issues_found[] = "Draft products: {$visibility_stats['draft']}";
    echo "\n   🚨 ISSUE: {$visibility_stats['draft']} products in DRAFT status!\n";
}

echo "\n";

// ============================================================================
// 2. CHECK WOOCOMMERCE SHOP PAGE CONFIGURATION
// ============================================================================

echo "2️⃣ CHECKING WOOCOMMERCE SHOP CONFIGURATION...\n\n";

$shop_page_id = wc_get_page_id('shop');
echo "   Shop Page ID: " . ($shop_page_id > 0 ? "✅ $shop_page_id" : "❌ Not set") . "\n";

if ($shop_page_id > 0) {
    $shop_page = get_post($shop_page_id);
    echo "   Shop Page Status: " . $shop_page->post_status . "\n";
    echo "   Shop Page Title: " . $shop_page->post_title . "\n";
    echo "   Shop Page Content Length: " . strlen($shop_page->post_content) . " chars\n";
    
    if (strlen($shop_page->post_content) > 100) {
        $issues_found[] = "Shop page has content (should be empty for WooCommerce)";
        echo "\n   ⚠️  WARNING: Shop page has content! WooCommerce needs empty page.\n";
    }
} else {
    $issues_found[] = "Shop page not configured";
    echo "\n   🚨 CRITICAL: No shop page set!\n";
}

echo "\n";

// ============================================================================
// 3. TEST ACTUAL PRODUCT QUERIES
// ============================================================================

echo "3️⃣ TESTING PRODUCT QUERIES...\n\n";

// Test 1: Standard WP_Query
$query1 = new WP_Query([
    'post_type' => 'product',
    'posts_per_page' => 12,
    'post_status' => 'publish'
]);

echo "   Standard WP_Query: " . $query1->found_posts . " products found\n";

// Test 2: WooCommerce query
$query2 = new WC_Product_Query([
    'limit' => 12,
    'status' => 'publish',
    'visibility' => 'catalog'
]);
$products2 = $query2->get_products();

echo "   WC_Product_Query (catalog): " . count($products2) . " products found\n";

// Test 3: wc_get_products
$products3 = wc_get_products([
    'limit' => 12,
    'status' => 'publish',
    'return' => 'ids'
]);

echo "   wc_get_products(): " . count($products3) . " products found\n";

// Test 4: Check if any have catalog_visibility = hidden
global $wpdb;
$hidden_count = $wpdb->get_var("
    SELECT COUNT(DISTINCT p.ID)
    FROM {$wpdb->posts} p
    INNER JOIN {$wpdb->term_relationships} tr ON p.ID = tr.object_id
    INNER JOIN {$wpdb->term_taxonomy} tt ON tr.term_taxonomy_id = tt.term_taxonomy_id
    INNER JOIN {$wpdb->terms} t ON tt.term_id = t.term_id
    WHERE p.post_type = 'product'
    AND p.post_status = 'publish'
    AND tt.taxonomy = 'product_visibility'
    AND t.name = 'exclude-from-catalog'
");

echo "   Products excluded from catalog: $hidden_count\n";

if ($hidden_count > 0) {
    $issues_found[] = "Products excluded from catalog: $hidden_count";
    echo "\n   🚨 CRITICAL: $hidden_count products marked 'exclude-from-catalog'!\n";
}

echo "\n";

// ============================================================================
// 4. CHECK PRODUCT STOCK STATUS
// ============================================================================

echo "4️⃣ CHECKING STOCK STATUS...\n\n";

$stock_stats = [
    'instock' => 0,
    'outofstock' => 0,
    'onbackorder' => 0
];

foreach ($all_products as $product_post) {
    $product = wc_get_product($product_post->ID);
    if (!$product) continue;
    
    $stock = $product->get_stock_status();
    if (isset($stock_stats[$stock])) {
        $stock_stats[$stock]++;
    }
}

echo "   📊 Stock Stats:\n";
foreach ($stock_stats as $status => $count) {
    $icon = $status == 'instock' ? '✅' : '⚠️';
    echo "      $icon $status: $count\n";
}

if ($stock_stats['outofstock'] > 50) {
    $issues_found[] = "Many out of stock: {$stock_stats['outofstock']}";
}

echo "\n";

// ============================================================================
// 5. CHECK WOOCOMMERCE SETTINGS
// ============================================================================

echo "5️⃣ CHECKING WOOCOMMERCE SETTINGS...\n\n";

$hide_out_of_stock = get_option('woocommerce_hide_out_of_stock_items');
echo "   Hide out of stock: " . ($hide_out_of_stock == 'yes' ? "⚠️  YES" : "✅ NO") . "\n";

if ($hide_out_of_stock == 'yes') {
    $issues_found[] = "WooCommerce hiding out-of-stock items";
}

$catalog_visibility = get_option('woocommerce_catalog_visibility');
echo "   Catalog visibility: " . ($catalog_visibility ? $catalog_visibility : "✅ Default") . "\n";

echo "\n";

// ============================================================================
// 6. CHECK PERMALINKS
// ============================================================================

echo "6️⃣ CHECKING PERMALINKS...\n\n";

$permalink_structure = get_option('permalink_structure');
echo "   Permalink structure: " . ($permalink_structure ? "✅ $permalink_structure" : "❌ Plain") . "\n";

$product_base = get_option('woocommerce_permalinks');
if ($product_base) {
    echo "   Product base: " . ($product_base['product_base'] ?? 'product') . "\n";
}

echo "\n";

// ============================================================================
// 7. CHECK THEME COMPATIBILITY
// ============================================================================

echo "7️⃣ CHECKING THEME COMPATIBILITY...\n\n";

$theme = wp_get_theme();
echo "   Theme: {$theme->get('Name')} v{$theme->get('Version')}\n";

if ($theme->get('Name') == 'Flatsome') {
    echo "   ✅ Flatsome theme detected\n";
    
    // Check if Flatsome is using UX Builder on shop page
    if ($shop_page_id > 0) {
        $ux_builder = get_post_meta($shop_page_id, '_ux_builder_enabled', true);
        echo "   UX Builder on shop: " . ($ux_builder ? "⚠️  Enabled" : "✅ Disabled") . "\n";
        
        if ($ux_builder) {
            $issues_found[] = "UX Builder enabled on shop page (can interfere)";
        }
    }
}

echo "\n";

// ============================================================================
// FIX SECTION - APPLY FIXES FOR FOUND ISSUES
// ============================================================================

echo str_repeat("=", 80) . "\n";
echo "🔧 APPLYING FIXES...\n";
echo str_repeat("=", 80) . "\n\n";

// FIX 1: Remove all catalog visibility exclusions
echo "FIX 1: Removing catalog visibility exclusions...\n";

global $wpdb;
$term = get_term_by('name', 'exclude-from-catalog', 'product_visibility');
if ($term) {
    $removed = $wpdb->delete(
        $wpdb->term_relationships,
        ['term_taxonomy_id' => $term->term_taxonomy_id],
        ['%d']
    );
    echo "   ✅ Removed $removed 'exclude-from-catalog' assignments\n";
    $fixes_applied[] = "Removed catalog exclusions: $removed";
}

$term2 = get_term_by('name', 'exclude-from-search', 'product_visibility');
if ($term2) {
    $removed2 = $wpdb->delete(
        $wpdb->term_relationships,
        ['term_taxonomy_id' => $term2->term_taxonomy_id],
        ['%d']
    );
    echo "   ✅ Removed $removed2 'exclude-from-search' assignments\n";
    $fixes_applied[] = "Removed search exclusions: $removed2";
}

// FIX 2: Force all products to be visible and in stock
echo "\nFIX 2: Forcing all products visible and in stock...\n";

$fixed = 0;
foreach ($all_products as $product_post) {
    $product = wc_get_product($product_post->ID);
    if (!$product) continue;
    
    // Set visible
    $product->set_catalog_visibility('visible');
    
    // Set in stock
    $product->set_stock_status('instock');
    $product->set_manage_stock(false);
    
    // Set published
    if ($product_post->post_status != 'publish') {
        wp_update_post([
            'ID' => $product_post->ID,
            'post_status' => 'publish'
        ]);
    }
    
    $product->save();
    $fixed++;
}

echo "   ✅ Fixed $fixed products (visibility + stock + status)\n";
$fixes_applied[] = "Fixed $fixed products";

// FIX 3: Ensure shop page is properly configured
echo "\nFIX 3: Configuring shop page...\n";

if ($shop_page_id <= 0) {
    // Create shop page if doesn't exist
    $new_shop_id = wp_insert_post([
        'post_title' => 'Loja',
        'post_name' => 'shop',
        'post_status' => 'publish',
        'post_type' => 'page',
        'post_content' => ''
    ]);
    
    update_option('woocommerce_shop_page_id', $new_shop_id);
    echo "   ✅ Created new shop page: ID $new_shop_id\n";
    $fixes_applied[] = "Created shop page";
} else {
    // Clear shop page content (WooCommerce needs empty page)
    wp_update_post([
        'ID' => $shop_page_id,
        'post_content' => '',
        'post_status' => 'publish'
    ]);
    
    // Disable UX Builder on shop
    delete_post_meta($shop_page_id, '_ux_builder_enabled');
    
    echo "   ✅ Cleared shop page content and disabled UX Builder\n";
    $fixes_applied[] = "Cleared shop page";
}

// FIX 4: WooCommerce settings
echo "\nFIX 4: Optimizing WooCommerce settings...\n";

update_option('woocommerce_hide_out_of_stock_items', 'no');
echo "   ✅ Don't hide out-of-stock items\n";
$fixes_applied[] = "Show out-of-stock items";

// FIX 5: Flush rewrite rules
echo "\nFIX 5: Flushing rewrite rules...\n";

flush_rewrite_rules(true);
echo "   ✅ Rewrite rules flushed\n";
$fixes_applied[] = "Flushed permalinks";

// FIX 6: Clear all caches
echo "\nFIX 6: Clearing all caches...\n";

wp_cache_flush();
wc_delete_product_transients();
delete_transient('wc_products_onsale');
delete_transient('wc_featured_products');
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_transient_%'");

echo "   ✅ All caches cleared\n";
$fixes_applied[] = "Cleared caches";

// FIX 7: Regenerate WooCommerce lookup tables
echo "\nFIX 7: Regenerating WooCommerce lookup tables...\n";

if (class_exists('WC_Product_Data_Store_CPT')) {
    $data_store = new WC_Product_Data_Store_CPT();
    if (method_exists($data_store, 'regenerate_lookup_tables')) {
        // Queue regeneration
        as_enqueue_async_action('wc_update_product_lookup_tables');
        echo "   ✅ Queued lookup table regeneration\n";
        $fixes_applied[] = "Regenerated lookup tables";
    }
}

// ============================================================================
// FINAL REPORT
// ============================================================================

echo "\n";
echo str_repeat("=", 80) . "\n";
echo "📊 DIAGNOSTIC REPORT\n";
echo str_repeat("=", 80) . "\n\n";

echo "🚨 ISSUES FOUND:\n";
if (count($issues_found) == 0) {
    echo "   ✅ No issues found!\n";
} else {
    foreach ($issues_found as $i => $issue) {
        echo "   " . ($i + 1) . ". $issue\n";
    }
}

echo "\n🔧 FIXES APPLIED:\n";
foreach ($fixes_applied as $i => $fix) {
    echo "   " . ($i + 1) . ". $fix\n";
}

echo "\n📈 FINAL STATS:\n";
echo "   Total products: " . count($all_products) . "\n";
echo "   Published: {$visibility_stats['publish']}\n";
echo "   In stock: {$stock_stats['instock']}\n";
echo "   With images: " . count(get_posts([
    'post_type' => 'product',
    'posts_per_page' => -1,
    'meta_query' => [['key' => '_thumbnail_id', 'compare' => 'EXISTS']]
])) . "\n";

echo "\n🌐 TEST NOW:\n";
echo "   http://localhost:8080/shop\n";
echo "   http://localhost:8080/product-category/boinas\n\n";

echo "💡 IMPORTANT:\n";
echo "   • Do HARD REFRESH: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)\n";
echo "   • Clear browser cache if needed\n";
echo "   • Wait 5-10 seconds for page to load\n\n";

echo "✅ DIAGNOSTIC COMPLETE!\n\n";
?>
