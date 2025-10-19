<?php
/**
 * 🎨 FORCE FIX - Add <style> tags to CSS
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎨 FORCE FIXING CSS DISPLAY\n\n";

$page = get_page_by_path('teste-html');

if (!$page) {
    echo "❌ Page not found\n";
    exit(1);
}

$content = $page->post_content;

echo "Before fix:\n";
echo substr($content, 0, 200) . "...\n\n";

// Check if CSS is at the start without <style> tags
if (strpos($content, '.products-grid {') === 0) {
    echo "🔧 CSS found at start without <style> tags\n";
    echo "🔧 Adding <style> tags...\n\n";
    
    // Find where HTML starts (first < that's not in CSS)
    $lines = explode("\n", $content);
    $css_lines = [];
    $html_lines = [];
    $in_html = false;
    
    foreach ($lines as $line) {
        $trimmed = trim($line);
        
        // Check if this line is HTML (starts with < and is not CSS)
        if (!$in_html && $trimmed && $trimmed[0] === '<') {
            $in_html = true;
        }
        
        if ($in_html) {
            $html_lines[] = $line;
        } else {
            $css_lines[] = $line;
        }
    }
    
    // Rebuild content with <style> tags
    $css_part = implode("\n", $css_lines);
    $html_part = implode("\n", $html_lines);
    
    $new_content = "<style>\n" . $css_part . "\n</style>\n\n" . $html_part;
    
    // Remove lazy loading
    $new_content = str_replace('loading="lazy"', 'loading="eager"', $new_content);
    $new_content = str_replace('class="lazy"', '', $new_content);
    
    // Update page
    $result = wp_update_post([
        'ID' => $page->ID,
        'post_content' => $new_content
    ]);
    
    if ($result) {
        echo "✅ Page updated!\n\n";
        echo "After fix:\n";
        echo substr($new_content, 0, 200) . "...\n\n";
        
        // Clear cache
        wp_cache_flush();
        clean_post_cache($page->ID);
        
        echo "✅ CSS is now inside <style> tags\n";
        echo "✅ Images will load immediately with loading=\"eager\"\n\n";
        echo "🌐 Test: http://localhost:8080/teste-html\n";
    } else {
        echo "❌ Failed to update\n";
    }
} else {
    echo "ℹ️  CSS already seems to be wrapped or not at start\n";
    echo "First chars: " . substr($content, 0, 50) . "\n";
}

?>
