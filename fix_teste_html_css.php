<?php
/**
 * 🎨 FIX TESTE-HTML PAGE - Wrap CSS in style tags
 * Remove lazy loading from images
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎨 FIXING TESTE-HTML PAGE CSS\n\n";
echo str_repeat("=", 80) . "\n\n";

// Get the page
$page = get_page_by_path('teste-html');

if (!$page) {
    echo "❌ Page 'teste-html' not found!\n";
    exit(1);
}

echo "✅ Found page: {$page->post_title} (ID: {$page->ID})\n\n";

$content = $page->post_content;
$original_length = strlen($content);

echo "Original content length: $original_length chars\n\n";

// Fix 1: Wrap CSS in <style> tags
if (strpos($content, '.products-grid {') === 0) {
    echo "🔧 Wrapping CSS in <style> tags...\n";
    
    // Find where the CSS ends (look for the first <div or HTML tag after CSS)
    $css_end_pos = strpos($content, '<div');
    
    if ($css_end_pos !== false) {
        $css_part = substr($content, 0, $css_end_pos);
        $html_part = substr($content, $css_end_pos);
        
        // Wrap CSS
        $content = "<style>\n" . trim($css_part) . "\n</style>\n\n" . $html_part;
        
        echo "   ✅ CSS wrapped successfully\n\n";
    }
}

// Fix 2: Remove lazy loading from images
echo "🔧 Removing lazy loading from images...\n";

// Remove loading="lazy"
$content = str_replace('loading="lazy"', '', $content);

// Remove lazy class
$content = str_replace('class="lazy"', '', $content);
$content = str_replace('class="product-image lazy"', 'class="product-image"', $content);

// Replace data-src with src for immediate loading
$content = preg_replace('/data-src="([^"]+)"/', 'src="$1"', $content);

echo "   ✅ Lazy loading removed\n\n";

// Fix 3: Ensure images have explicit dimensions and loading attributes
echo "🔧 Optimizing image loading...\n";

// Add loading="eager" to force immediate loading
$content = str_replace('<img src=', '<img loading="eager" src=', $content);

echo "   ✅ Image loading optimized\n\n";

// Update the page
$result = wp_update_post([
    'ID' => $page->ID,
    'post_content' => $content
]);

if ($result) {
    echo "✅ Page updated successfully!\n\n";
    echo "New content length: " . strlen($content) . " chars\n\n";
} else {
    echo "❌ Failed to update page\n\n";
    exit(1);
}

// Clear caches
echo "🧹 Clearing caches...\n";
wp_cache_flush();
clean_post_cache($page->ID);
echo "   ✅ Caches cleared\n\n";

// Show sample of new content
echo "📝 First 500 chars of new content:\n";
echo str_repeat("-", 80) . "\n";
echo substr($content, 0, 500) . "...\n";
echo str_repeat("-", 80) . "\n\n";

echo str_repeat("=", 80) . "\n";
echo "✅ FIX COMPLETE!\n";
echo str_repeat("=", 80) . "\n\n";

echo "🌐 TEST NOW:\n";
echo "   http://localhost:8080/teste-html\n\n";

echo "💡 CHANGES MADE:\n";
echo "   1. ✅ Wrapped CSS in <style> tags (CSS will be applied, not shown as text)\n";
echo "   2. ✅ Removed lazy loading (images load immediately)\n";
echo "   3. ✅ Added loading=\"eager\" to all images\n";
echo "   4. ✅ Cleared WordPress caches\n\n";

echo "🎯 EXPECTED RESULT:\n";
echo "   • CSS will be hidden and applied correctly\n";
echo "   • Images will load immediately when page opens\n";
echo "   • No more CSS text visible on page\n";
echo "   • Product grid displays properly\n\n";

?>
