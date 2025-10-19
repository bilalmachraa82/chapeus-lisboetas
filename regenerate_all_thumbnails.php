<?php
/**
 * 🔄 REGENERATE ALL THUMBNAILS - Force recreation of all image sizes
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

echo "🔄 REGENERATING ALL IMAGE THUMBNAILS\n\n";
echo str_repeat("=", 80) . "\n\n";

// Get all attachments
$attachments = get_posts([
    'post_type' => 'attachment',
    'post_mime_type' => 'image',
    'posts_per_page' => -1,
    'post_status' => 'inherit'
]);

echo "📊 Found " . count($attachments) . " images to process\n\n";

$success = 0;
$failed = 0;
$total = count($attachments);

foreach ($attachments as $index => $attachment) {
    $file = get_attached_file($attachment->ID);
    
    if (!$file || !file_exists($file)) {
        echo "   ❌ #{$attachment->ID}: File not found\n";
        $failed++;
        continue;
    }
    
    // Delete old metadata
    $old_metadata = wp_get_attachment_metadata($attachment->ID);
    
    // Regenerate
    $metadata = wp_generate_attachment_metadata($attachment->ID, $file);
    
    if ($metadata && !is_wp_error($metadata)) {
        wp_update_attachment_metadata($attachment->ID, $metadata);
        $success++;
        
        // Show progress every 20 images
        if (($index + 1) % 20 == 0) {
            $percent = round((($index + 1) / $total) * 100);
            echo "   ⏳ Progress: " . ($index + 1) . "/$total ($percent%)\n";
        }
    } else {
        echo "   ❌ #{$attachment->ID}: Failed to generate\n";
        $failed++;
    }
}

echo "\n";
echo str_repeat("=", 80) . "\n";
echo "✅ REGENERATION COMPLETE\n";
echo str_repeat("=", 80) . "\n\n";

echo "📊 RESULTS:\n";
echo "   ✅ Success: $success images\n";
echo "   ❌ Failed: $failed images\n";
echo "   📈 Total: $total images\n\n";

// Verify a few thumbnails were created
echo "🔍 VERIFYING SAMPLE THUMBNAILS:\n\n";

$sample = array_slice($attachments, 0, 5);
foreach ($sample as $att) {
    $file = get_attached_file($att->ID);
    $metadata = wp_get_attachment_metadata($att->ID);
    
    echo "   Image ID {$att->ID}:\n";
    echo "     Original: " . basename($file) . "\n";
    
    if (isset($metadata['sizes'])) {
        foreach ($metadata['sizes'] as $size => $info) {
            $thumb_path = dirname($file) . '/' . $info['file'];
            $exists = file_exists($thumb_path);
            echo "     $size: {$info['file']} " . ($exists ? "✅" : "❌") . "\n";
        }
    }
    echo "\n";
}

echo "💡 Now test the pages:\n";
echo "   • http://localhost:8080/shop\n";
echo "   • http://localhost:8080/image-test\n\n";

?>
