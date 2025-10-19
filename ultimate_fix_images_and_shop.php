<?php
/**
 * 🎯 ULTIMATE FIX - Images & Shop Page
 * Fixes opacity 0 images and empty shop page
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎯 ULTIMATE FIX - IMAGES & SHOP PAGE\n\n";
echo str_repeat("=", 80) . "\n\n";

// ============================================================================
// 1. FIX OPACITY 0 IMAGES - Force all images visible
// ============================================================================

echo "1️⃣ FIXING OPACITY 0 IMAGES...\n\n";

$opacity_fix_css = "
/* === FORCE IMAGES VISIBLE === */

/* Remove opacity 0 from all product images */
.product img,
.product-small img,
.box-image img,
.ux_products img,
.woocommerce-loop-product__link img {
    opacity: 1 !important;
}

/* Remove lazy load opacity effects */
img.lazy,
img.lazy-load,
img[loading='lazy'] {
    opacity: 1 !important;
}

/* Flatsome image fade effect - force visible */
.image-fade_in_back img,
.image-fade_in img {
    opacity: 1 !important;
}

/* Box image wrapper */
.box-image {
    overflow: hidden;
    position: relative;
    background: transparent;
}

.box-image img {
    display: block !important;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Product hover - keep images visible */
.product:hover img,
.product-small:hover img {
    opacity: 1 !important;
}

/* Disable any fade transitions that cause opacity issues */
.product img {
    transition: transform 0.3s ease !important;
}

/* Force display for hidden images */
img[style*='display: none'] {
    display: block !important;
}

/* Ensure images are always visible on load */
.woocommerce-product-gallery__image img {
    opacity: 1 !important;
}
";

// Get current custom CSS
$current_css = wp_get_custom_css();

// Remove old opacity fixes if exist
$current_css = preg_replace('/\/\* === FORCE IMAGES VISIBLE === \*\/.*?(?=\/\*|$)/s', '', $current_css);

// Add new fix
$updated_css = $current_css . "\n\n" . $opacity_fix_css;
wp_update_custom_css_post($updated_css);

echo "   ✅ CSS fix applied - All images forced to opacity: 1\n\n";

// ============================================================================
// 2. FIX SHOP PAGE - Completely recreate
// ============================================================================

echo "2️⃣ FIXING SHOP PAGE...\n\n";

// Get shop page ID
$shop_page_id = wc_get_page_id('shop');

if ($shop_page_id > 0) {
    echo "   Current shop page ID: $shop_page_id\n";
    
    // Get current page
    $shop_page = get_post($shop_page_id);
    
    echo "   Current content length: " . strlen($shop_page->post_content) . " chars\n";
    
    // COMPLETELY EMPTY the page
    $result = wp_update_post([
        'ID' => $shop_page_id,
        'post_content' => '', // MUST be empty for WooCommerce
        'post_title' => 'Shop',
        'post_name' => 'shop',
        'post_status' => 'publish',
        'post_type' => 'page'
    ]);
    
    if ($result) {
        echo "   ✅ Shop page emptied successfully\n";
    } else {
        echo "   ❌ Failed to update shop page\n";
    }
    
    // Delete ALL meta that might interfere
    delete_post_meta($shop_page_id, '_ux_builder_enabled');
    delete_post_meta($shop_page_id, '_ux_builder_version');
    delete_post_meta($shop_page_id, '_ux_builder_shortcode_content');
    delete_post_meta($shop_page_id, '_elementor_edit_mode');
    delete_post_meta($shop_page_id, '_wp_page_template');
    
    echo "   ✅ Removed all page builder meta\n";
    
    // Force default template
    update_post_meta($shop_page_id, '_wp_page_template', 'default');
    
} else {
    echo "   ⚠️  Shop page not found, creating new one...\n";
    
    // Create new shop page
    $new_shop_id = wp_insert_post([
        'post_title' => 'Shop',
        'post_name' => 'shop',
        'post_content' => '',
        'post_status' => 'publish',
        'post_type' => 'page'
    ]);
    
    if ($new_shop_id) {
        update_option('woocommerce_shop_page_id', $new_shop_id);
        echo "   ✅ Created new shop page: ID $new_shop_id\n";
    }
}

echo "\n";

// ============================================================================
// 3. DISABLE FLATSOME CATALOG MODE (might be hiding products)
// ============================================================================

echo "3️⃣ CHECKING FLATSOME SETTINGS...\n\n";

// Disable catalog mode if enabled
$catalog_mode = get_theme_mod('catalog_mode');
if ($catalog_mode) {
    set_theme_mod('catalog_mode', false);
    echo "   ✅ Disabled catalog mode\n";
}

// Enable product display
set_theme_mod('product_display', 'default');
set_theme_mod('category_display', 'default');

echo "   ✅ Product display settings reset\n\n";

// ============================================================================
// 4. CLEAR ALL CACHES AGGRESSIVELY
// ============================================================================

echo "4️⃣ CLEARING ALL CACHES...\n\n";

// WordPress
wp_cache_flush();

// WooCommerce
wc_delete_product_transients();
delete_transient('wc_products_onsale');
delete_transient('wc_featured_products');

// Flatsome
delete_transient('flatsome_settings');
delete_transient('flatsome_customize_preview');
delete_transient('ux_builder_css');

// Database transients
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_transient_%'");
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_site_transient_%'");

// Object cache
if (function_exists('wp_cache_delete_group')) {
    wp_cache_delete_group('themes');
    wp_cache_delete_group('woocommerce');
}

echo "   ✅ All caches cleared\n\n";

// ============================================================================
// 5. FLUSH REWRITE RULES
// ============================================================================

echo "5️⃣ FLUSHING REWRITE RULES...\n\n";

flush_rewrite_rules(true);

echo "   ✅ Rewrite rules flushed\n\n";

// ============================================================================
// 6. VERIFY PRODUCT VISIBILITY
// ============================================================================

echo "6️⃣ VERIFYING PRODUCT VISIBILITY...\n\n";

// Test query
$test_query = new WP_Query([
    'post_type' => 'product',
    'posts_per_page' => 12,
    'post_status' => 'publish'
]);

echo "   Products found: {$test_query->found_posts}\n";
echo "   Posts per page: {$test_query->post_count}\n\n";

// Sample products
if ($test_query->have_posts()) {
    echo "   📦 Sample products:\n";
    $count = 0;
    while ($test_query->have_posts() && $count < 5) {
        $test_query->the_post();
        $product = wc_get_product(get_the_ID());
        $image_id = get_post_thumbnail_id();
        $image_url = wp_get_attachment_url($image_id);
        
        echo "      • " . get_the_title() . "\n";
        echo "        Price: " . $product->get_price_html() . "\n";
        echo "        Image: " . ($image_url ? "✅" : "❌") . "\n";
        $count++;
    }
    wp_reset_postdata();
    echo "\n";
}

// ============================================================================
// 7. ADD FAILSAFE CSS FOR SHOP
// ============================================================================

echo "7️⃣ ADDING FAILSAFE CSS...\n\n";

$failsafe_css = "
/* === SHOP PAGE FAILSAFE === */

/* Force products to display on shop page */
.woocommerce .products,
.woocommerce-page .products,
body.woocommerce-shop .products {
    display: grid !important;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)) !important;
    gap: 30px !important;
}

/* Force product items to show */
.woocommerce ul.products li.product,
.woocommerce-page ul.products li.product {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Ensure shop page content area is visible */
.woocommerce-shop .content-area,
.woocommerce-shop .site-main {
    display: block !important;
    visibility: visible !important;
}

/* Remove any 'coming soon' overlays */
.woocommerce-store-notice,
.woocommerce-notice--maintenance {
    display: none !important;
}
";

$current_css_2 = wp_get_custom_css();
$updated_css_2 = $current_css_2 . "\n\n" . $failsafe_css;
wp_update_custom_css_post($updated_css_2);

echo "   ✅ Failsafe CSS added\n\n";

// ============================================================================
// FINAL REPORT
// ============================================================================

echo str_repeat("=", 80) . "\n";
echo "✅ ULTIMATE FIX COMPLETE!\n";
echo str_repeat("=", 80) . "\n\n";

echo "🔧 FIXES APPLIED:\n";
echo "   1. ✅ Forced all product images to opacity: 1\n";
echo "   2. ✅ Cleared shop page content completely\n";
echo "   3. ✅ Removed all page builder interference\n";
echo "   4. ✅ Disabled Flatsome catalog mode\n";
echo "   5. ✅ Cleared all caches (WordPress + WooCommerce + Flatsome)\n";
echo "   6. ✅ Flushed rewrite rules\n";
echo "   7. ✅ Added failsafe CSS for product display\n\n";

echo "🌐 TEST NOW:\n";
echo "   • Homepage: http://localhost:8080\n";
echo "   • Shop: http://localhost:8080/shop\n\n";

echo "💡 IMPORTANT:\n";
echo "   1. Do HARD REFRESH: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)\n";
echo "   2. Wait 3-5 seconds for page to fully load\n";
echo "   3. All images should be visible immediately (no fade-in)\n";
echo "   4. Shop should show 12 products in grid\n\n";

echo "📸 BEFORE SHOWING TO CLIENT:\n";
echo "   • Check homepage - all 4 featured products visible\n";
echo "   • Check shop - grid of products with images\n";
echo "   • Check categories work\n";
echo "   • Check single product pages\n\n";

?>
