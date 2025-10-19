<?php
/**
 * 🎨 FINAL CSS FIX - Handle newlines and wrap CSS properly
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎨 FINAL CSS FIX\n\n";

$page = get_page_by_path('teste-html');

if (!$page) {
    echo "❌ Page not found\n";
    exit(1);
}

$content = $page->post_content;

echo "Original length: " . strlen($content) . " chars\n";
echo "First 100 chars: [" . substr($content, 0, 100) . "]\n\n";

// Find position of first HTML tag
$first_html_pos = strpos($content, '<');

if ($first_html_pos !== false && $first_html_pos > 100) {
    echo "🔧 Found CSS section (0 to $first_html_pos)\n";
    echo "🔧 Found HTML section (from $first_html_pos)\n\n";
    
    // Extract CSS and HTML parts
    $css_part = substr($content, 0, $first_html_pos);
    $html_part = substr($content, $first_html_pos);
    
    // Clean CSS (remove leading/trailing whitespace)
    $css_part = trim($css_part);
    
    // Check if already wrapped in <style>
    if (strpos($css_part, '<style>') === false) {
        echo "🔧 Wrapping CSS in <style> tags...\n";
        
        // Rebuild with proper structure
        $new_content = "<style>\n" . $css_part . "\n</style>\n\n" . $html_part;
        
        // Remove lazy loading
        $new_content = str_replace('loading="lazy"', 'loading="eager"', $new_content);
        
        // Update page
        $result = wp_update_post([
            'ID' => $page->ID,
            'post_content' => $new_content
        ]);
        
        if ($result) {
            echo "✅ Page updated successfully!\n\n";
            echo "New length: " . strlen($new_content) . " chars\n";
            echo "First 100 chars: [" . substr($new_content, 0, 100) . "]\n\n";
            
            // Clear cache
            wp_cache_flush();
            clean_post_cache($page->ID);
            
            echo "✅ FIXES APPLIED:\n";
            echo "   • CSS wrapped in <style> tags\n";
            echo "   • Images set to loading=\"eager\"\n";
            echo "   • Cache cleared\n\n";
            
            echo "🌐 TEST: http://localhost:8080/teste-html\n";
            echo "💡 Do hard refresh: Cmd+Shift+R (Mac)\n";
        } else {
            echo "❌ Failed to update page\n";
        }
    } else {
        echo "ℹ️  CSS already wrapped in <style> tags\n";
    }
} else {
    echo "⚠️  Could not find clear CSS/HTML separation\n";
    echo "First HTML at position: $first_html_pos\n";
}

?>
