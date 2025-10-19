<?php
/**
 * 🖼️ VERIFY IMAGES ARE SHOWING - Deep check
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🖼️ VERIFYING IMAGES STATUS\n\n";
echo str_repeat("=", 80) . "\n\n";

// ============================================================================
// 1. CHECK PRODUCTS WITH IMAGES
// ============================================================================

echo "1️⃣ PRODUCTS WITH IMAGES:\n\n";

$products_with_images = get_posts([
    'post_type' => 'product',
    'posts_per_page' => 10,
    'meta_query' => [
        [
            'key' => '_thumbnail_id',
            'compare' => 'EXISTS'
        ]
    ],
    'orderby' => 'rand'
]);

echo "   📊 Sample of 10 products with images:\n\n";

foreach ($products_with_images as $prod) {
    $thumb_id = get_post_thumbnail_id($prod->ID);
    $thumb_url = wp_get_attachment_url($thumb_id);
    $thumb_path = get_attached_file($thumb_id);
    $file_exists = file_exists($thumb_path);
    
    echo "   • {$prod->post_title}\n";
    echo "     Image ID: $thumb_id\n";
    echo "     URL: $thumb_url\n";
    echo "     File exists: " . ($file_exists ? "✅ YES" : "❌ NO") . "\n";
    
    if ($file_exists) {
        $size = filesize($thumb_path);
        echo "     Size: " . round($size / 1024, 1) . " KB\n";
        
        // Check if image is valid
        $image_info = @getimagesize($thumb_path);
        if ($image_info) {
            echo "     Dimensions: {$image_info[0]}x{$image_info[1]}px\n";
            echo "     Type: {$image_info['mime']}\n";
        }
    }
    echo "\n";
}

// ============================================================================
// 2. CHECK IMAGE SIZES AVAILABLE
// ============================================================================

echo "2️⃣ CHECKING AVAILABLE IMAGE SIZES:\n\n";

$sizes = wp_get_registered_image_subsizes();
foreach ($sizes as $size => $data) {
    if (strpos($size, 'woocommerce') !== false || strpos($size, 'shop') !== false) {
        echo "   • $size: {$data['width']}x{$data['height']} (crop: " . 
             ($data['crop'] ? 'yes' : 'no') . ")\n";
    }
}

echo "\n";

// ============================================================================
// 3. CHECK WOOCOMMERCE IMAGE SETTINGS
// ============================================================================

echo "3️⃣ WOOCOMMERCE IMAGE SETTINGS:\n\n";

$thumb_width = get_option('woocommerce_thumbnail_image_width');
$single_width = get_option('woocommerce_single_image_width');
$thumb_cropping = get_option('woocommerce_thumbnail_cropping');

echo "   Thumbnail width: {$thumb_width}px\n";
echo "   Single image width: {$single_width}px\n";
echo "   Thumbnail cropping: $thumb_cropping\n\n";

// ============================================================================
// 4. TEST IMAGE OUTPUT IN DIFFERENT CONTEXTS
// ============================================================================

echo "4️⃣ TESTING IMAGE OUTPUT:\n\n";

if (!empty($products_with_images)) {
    $test_product = wc_get_product($products_with_images[0]->ID);
    
    echo "   Test product: {$test_product->get_name()}\n\n";
    
    // Test thumbnail
    $thumb_html = $test_product->get_image('woocommerce_thumbnail');
    echo "   Thumbnail HTML length: " . strlen($thumb_html) . " chars\n";
    
    // Check if has img tag
    if (preg_match('/<img[^>]+src="([^"]+)"/', $thumb_html, $matches)) {
        echo "   ✅ Has valid <img> tag\n";
        echo "   Image SRC: {$matches[1]}\n";
        
        // Test if URL is accessible
        $headers = @get_headers($matches[1]);
        if ($headers && strpos($headers[0], '200')) {
            echo "   ✅ Image URL is accessible\n";
        } else {
            echo "   ❌ Image URL not accessible!\n";
        }
    } else {
        echo "   ❌ No <img> tag found in output!\n";
    }
}

echo "\n";

// ============================================================================
// 5. CHECK UPLOADS DIRECTORY
// ============================================================================

echo "5️⃣ UPLOADS DIRECTORY CHECK:\n\n";

$upload_dir = wp_upload_dir();

echo "   Base dir: {$upload_dir['basedir']}\n";
echo "   Base URL: {$upload_dir['baseurl']}\n";
echo "   Writable: " . (is_writable($upload_dir['basedir']) ? "✅ YES" : "❌ NO") . "\n\n";

// Count files in uploads
$uploads_path = $upload_dir['basedir'];
if (is_dir($uploads_path)) {
    $file_count = count(glob($uploads_path . '/*/*.{jpg,jpeg,png,gif,webp}', GLOB_BRACE));
    echo "   Total image files: $file_count\n\n";
}

// ============================================================================
// 6. GENERATE TEST HTML WITH IMAGES
// ============================================================================

echo "6️⃣ GENERATING TEST PAGE WITH DIRECT IMAGE URLS:\n\n";

$test_html = '<h1 style="text-align: center; font-size: 3rem; color: #1B1464; margin: 40px 0;">Image Test - Direct URLs</h1>';
$test_html .= '<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; padding: 40px; max-width: 1400px; margin: 0 auto;">';

$count = 0;
foreach ($products_with_images as $prod) {
    $product = wc_get_product($prod->ID);
    $image_id = get_post_thumbnail_id($prod->ID);
    
    if ($image_id) {
        // Get multiple sizes
        $thumb_url = wp_get_attachment_image_url($image_id, 'thumbnail');
        $medium_url = wp_get_attachment_image_url($image_id, 'medium');
        $large_url = wp_get_attachment_image_url($image_id, 'large');
        $full_url = wp_get_attachment_image_url($image_id, 'full');
        
        $test_html .= '<div style="background: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">';
        $test_html .= '<img src="' . esc_url($large_url) . '" alt="' . esc_attr($prod->post_title) . '" style="width: 100%; height: 250px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">';
        $test_html .= '<h3 style="font-size: 1rem; color: #1B1464; text-align: center; margin: 10px 0;">' . esc_html($prod->post_title) . '</h3>';
        $test_html .= '<p style="font-size: 1.25rem; color: #FFD700; text-align: center; font-weight: 700; margin: 5px 0;">' . $product->get_price_html() . '</p>';
        
        // Debug info
        $test_html .= '<details style="margin-top: 10px; font-size: 0.75rem; color: #666;">';
        $test_html .= '<summary>Debug Info</summary>';
        $test_html .= '<p style="margin: 5px 0; word-break: break-all;">Thumb: ' . $thumb_url . '</p>';
        $test_html .= '<p style="margin: 5px 0; word-break: break-all;">Medium: ' . $medium_url . '</p>';
        $test_html .= '<p style="margin: 5px 0; word-break: break-all;">Large: ' . $large_url . '</p>';
        $test_html .= '<p style="margin: 5px 0; word-break: break-all;">Full: ' . $full_url . '</p>';
        $test_html .= '</details>';
        
        $test_html .= '</div>';
        $count++;
    }
}

$test_html .= '</div>';

// Create or update test page
$test_page = get_page_by_path('image-test');
if (!$test_page) {
    $test_page_id = wp_insert_post([
        'post_title' => 'Image Test',
        'post_name' => 'image-test',
        'post_content' => $test_html,
        'post_status' => 'publish',
        'post_type' => 'page'
    ]);
    echo "   ✅ Created /image-test page with $count products\n";
} else {
    wp_update_post([
        'ID' => $test_page->ID,
        'post_content' => $test_html
    ]);
    echo "   ✅ Updated /image-test page with $count products\n";
}

echo "\n";

// ============================================================================
// 7. FINAL SUMMARY
// ============================================================================

echo str_repeat("=", 80) . "\n";
echo "✅ VERIFICATION COMPLETE\n";
echo str_repeat("=", 80) . "\n\n";

echo "📊 SUMMARY:\n";
echo "   • Products with images: " . count($products_with_images) . " (sample)\n";
echo "   • Test page created: /image-test\n";
echo "   • Thumbnail size: {$thumb_width}px\n";
echo "   • Single size: {$single_width}px\n\n";

echo "🌐 TEST PAGES:\n";
echo "   • http://localhost:8080/image-test (with debug info)\n";
echo "   • http://localhost:8080/shop (main shop)\n";
echo "   • http://localhost:8080/product-category/boinas (category)\n\n";

echo "💡 WHAT TO CHECK:\n";
echo "   1. Open /image-test in browser\n";
echo "   2. Check if images load (should see 10 products)\n";
echo "   3. Click 'Debug Info' to see all image URLs\n";
echo "   4. If images don't load, check browser console for errors\n\n";

?>
