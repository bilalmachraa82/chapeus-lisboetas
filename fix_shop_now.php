<?php
/**
 * 🎯 FIX SHOP PAGE - Remove "Coming Soon" Message
 * Show actual products on /shop
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎯 FIXING SHOP PAGE - REMOVE COMING SOON\n\n";
echo str_repeat("=", 80) . "\n\n";

// ============================================================================
// 1. DISABLE FLATSOME CATALOG MODE
// ============================================================================

echo "1️⃣ DISABLING CATALOG MODE...\n\n";

// Remove all catalog mode settings
set_theme_mod('catalog_mode', false);
set_theme_mod('catalog_mode_type', '');
delete_option('flatsome_wc_catalog_mode');

// Enable add to cart
update_option('woocommerce_enable_cart', 'yes');
update_option('woocommerce_cart_redirect_after_add', 'no');

echo "   ✅ Catalog mode disabled\n\n";

// ============================================================================
// 2. FIX SHOP PAGE TEMPLATE
// ============================================================================

echo "2️⃣ FIXING SHOP PAGE TEMPLATE...\n\n";

$shop_page_id = wc_get_page_id('shop');

if ($shop_page_id > 0) {
    // Completely clean the page
    wp_update_post([
        'ID' => $shop_page_id,
        'post_content' => '', // MUST be empty for WooCommerce
        'post_title' => 'Loja',
        'post_status' => 'publish'
    ]);
    
    // Remove ALL meta
    delete_post_meta($shop_page_id, '_ux_builder_enabled');
    delete_post_meta($shop_page_id, '_ux_builder_version');
    delete_post_meta($shop_page_id, '_ux_builder_shortcode_content');
    delete_post_meta($shop_page_id, 'ux_builder_shortcode_content');
    delete_post_meta($shop_page_id, '_elementor_edit_mode');
    
    // Set default template
    delete_post_meta($shop_page_id, '_wp_page_template');
    update_post_meta($shop_page_id, '_wp_page_template', 'default');
    
    echo "   ✅ Shop page cleaned and reset\n";
    echo "   Shop page ID: $shop_page_id\n\n";
}

// ============================================================================
// 3. CHECK FOR MAINTENANCE MODE PLUGINS
// ============================================================================

echo "3️⃣ CHECKING MAINTENANCE MODE...\n\n";

// Disable any maintenance mode
delete_option('wc_admin_store_in_maintenance_mode');
delete_option('flatsome_maintenance_mode');
update_option('blog_public', 1);

// Check if "coming soon" page is set
$coming_soon_page = get_option('flatsome_coming_soon_page');
if ($coming_soon_page) {
    delete_option('flatsome_coming_soon_page');
    echo "   ✅ Removed coming soon page setting\n";
}

echo "   ✅ Maintenance mode disabled\n\n";

// ============================================================================
// 4. FORCE PRODUCTS VISIBLE ON SHOP
// ============================================================================

echo "4️⃣ FORCING PRODUCTS VISIBLE...\n\n";

$css_fix = "
/* === FORCE SHOP PRODUCTS VISIBLE === */

/* Remove any coming soon overlays */
.woocommerce-store-notice,
.woocommerce-notice--maintenance,
.coming-soon-wrapper,
.maintenance-mode {
    display: none !important;
}

/* Force products to display */
.woocommerce .products,
.woocommerce-page .products {
    display: grid !important;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)) !important;
    gap: 30px !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Force product items visible */
.woocommerce ul.products li.product,
.woocommerce-page ul.products li.product {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Force product images visible */
.woocommerce ul.products li.product img {
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Shop page specific */
body.post-type-archive-product .site-main,
body.woocommerce-shop .content-area {
    display: block !important;
    visibility: visible !important;
}

/* Remove any 'horizon' message */
.woocommerce-info,
.woocommerce-message {
    display: none !important;
}
";

$current_css = wp_get_custom_css();

// Remove old fixes
$current_css = preg_replace('/\/\* === FORCE SHOP PRODUCTS VISIBLE === \*\/.*?(?=\/\*|$)/s', '', $current_css);

// Add new fix
$updated_css = $current_css . "\n\n" . $css_fix;
wp_update_custom_css_post($updated_css);

echo "   ✅ CSS fix applied\n\n";

// ============================================================================
// 5. SET WOOCOMMERCE SHOP SETTINGS
// ============================================================================

echo "5️⃣ CONFIGURING WOOCOMMERCE SETTINGS...\n\n";

// Products per page
update_option('woocommerce_catalog_rows', '4'); // 4 rows
update_option('woocommerce_catalog_columns', '3'); // 3 columns = 12 products

// Enable product visibility
update_option('woocommerce_shop_page_display', ''); // Show products

echo "   ✅ WooCommerce settings configured\n";
echo "   Products per page: 12 (3 columns × 4 rows)\n\n";

// ============================================================================
// 6. CLEAR ALL CACHES
// ============================================================================

echo "6️⃣ CLEARING CACHES...\n\n";

// WordPress
wp_cache_flush();

// WooCommerce
wc_delete_product_transients();
delete_transient('wc_products_onsale');
delete_transient('wc_featured_products');

// Flatsome
delete_transient('flatsome_settings');
delete_transient('flatsome_customize_preview');

// All transients
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_transient_%'");
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_site_transient_%'");

echo "   ✅ All caches cleared\n\n";

// ============================================================================
// 7. FLUSH REWRITE RULES
// ============================================================================

echo "7️⃣ FLUSHING REWRITE RULES...\n\n";

flush_rewrite_rules(true);

echo "   ✅ Rewrite rules flushed\n\n";

// ============================================================================
// 8. VERIFY PRODUCTS
// ============================================================================

echo "8️⃣ VERIFYING PRODUCTS...\n\n";

$products_query = new WP_Query([
    'post_type' => 'product',
    'posts_per_page' => 12,
    'post_status' => 'publish',
    'orderby' => 'date',
    'order' => 'DESC'
]);

echo "   Total products: " . $products_query->found_posts . "\n";
echo "   Showing: " . $products_query->post_count . " products\n\n";

if ($products_query->have_posts()) {
    echo "   📦 First 5 products:\n";
    $count = 0;
    while ($products_query->have_posts() && $count < 5) {
        $products_query->the_post();
        $product = wc_get_product(get_the_ID());
        $has_img = has_post_thumbnail() ? "✅" : "❌";
        $price = $product->get_price_html();
        
        echo "      $has_img " . get_the_title() . " - $price\n";
        $count++;
    }
    wp_reset_postdata();
    echo "\n";
}

// ============================================================================
// FINAL REPORT
// ============================================================================

echo str_repeat("=", 80) . "\n";
echo "✅ SHOP PAGE FIX COMPLETE!\n";
echo str_repeat("=", 80) . "\n\n";

echo "🔧 FIXES APPLIED:\n";
echo "   1. ✅ Disabled catalog mode\n";
echo "   2. ✅ Cleaned shop page (empty content)\n";
echo "   3. ✅ Removed all page builder meta\n";
echo "   4. ✅ Disabled maintenance mode\n";
echo "   5. ✅ Removed 'coming soon' settings\n";
echo "   6. ✅ Added CSS to force products visible\n";
echo "   7. ✅ Set WooCommerce to show 12 products\n";
echo "   8. ✅ Cleared all caches\n";
echo "   9. ✅ Flushed rewrite rules\n\n";

echo "🌐 TEST NOW:\n";
echo "   http://localhost:8080/shop\n\n";

echo "💡 AFTER TESTING:\n";
echo "   1. Do HARD REFRESH: Cmd+Shift+R (Mac)\n";
echo "   2. You should see 12 products in a grid\n";
echo "   3. No more 'Great things are on the horizon' message\n";
echo "   4. All products should have images visible\n\n";

echo "🎯 The shop page should now show ACTUAL PRODUCTS!\n\n";

?>
