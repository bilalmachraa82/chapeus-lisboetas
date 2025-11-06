<?php
/**
 * Fix Blog Featured Images
 *
 * This script:
 * 1. Imports blog images from /wp-content/uploads/2025/10/blog/
 * 2. Assigns correct featured images to each blog post
 * 3. Removes incorrect images (boneco de madeira)
 *
 * Usage: Place in WordPress root and run once:
 * php fix-blog-images.php
 */

// Load WordPress
require_once(__DIR__ . '/wp-load.php');

// Enable error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "🔧 FIXING BLOG IMAGES\n";
echo "====================\n\n";

// Mapping: post title keyword => blog image filename
$post_image_map = [
    'Cinema' => 'blog_cinema_iconico.jpg',
    'Presente' => 'blog_presente_feliz.jpg',
    'Ovelha' => 'blog_sustentavel_maos.jpg',
    'Inverno sem Frio' => 'blog_inverno_feltro.jpg',
    'João, 28' => 'blog_joao_jovem.jpg',
    'Verão em Lisboa' => 'blog_verao_lisboa.jpg',
    'Boina Portuguesa' => 'blog_boina_tradicional.jpg',
    'Fedora' => 'blog_fedora_outono.jpg',
    'Maria do Carmo' => 'blog_maria_vintage.jpg',
    'Casamentos' => 'blog_casamentos_elegante.jpg',
    'Cuidar do Seu' => 'blog_cuidados_lisboa.jpg',
    'Atelier' => 'blog_atelier_loja.jpg',
    'Panamá' => 'blog_panama_feliz.jpg',
    '75 Anos' => 'blog_historia_vintage.jpg',
    '3 Perguntas' => 'blog_perguntas_boina.jpg', // Replace boneco image
];

// Get all published posts
$posts = get_posts([
    'post_type' => 'post',
    'post_status' => 'publish',
    'numberposts' => -1,
    'orderby' => 'date',
    'order' => 'DESC'
]);

echo "📊 Found " . count($posts) . " blog posts\n\n";

$success_count = 0;
$error_count = 0;

foreach ($posts as $post) {
    echo "📝 Processing: " . $post->post_title . "\n";

    // Find matching image
    $image_filename = null;
    foreach ($post_image_map as $keyword => $filename) {
        if (stripos($post->post_title, $keyword) !== false) {
            $image_filename = $filename;
            break;
        }
    }

    if (!$image_filename) {
        echo "   ⚠️  No matching image found\n\n";
        $error_count++;
        continue;
    }

    // Full path to image
    $image_path = ABSPATH . 'wp-content/uploads/2025/10/blog/' . $image_filename;

    if (!file_exists($image_path)) {
        echo "   ❌ Image not found: $image_path\n\n";
        $error_count++;
        continue;
    }

    // Check if already has this image
    $current_thumbnail = get_post_thumbnail_id($post->ID);
    if ($current_thumbnail) {
        $current_file = get_attached_file($current_thumbnail);
        if ($current_file && strpos($current_file, $image_filename) !== false) {
            echo "   ✅ Already has correct image\n\n";
            $success_count++;
            continue;
        }
    }

    // Check if image already in Media Library
    $existing_attachment = null;
    $attachments = get_posts([
        'post_type' => 'attachment',
        'post_status' => 'inherit',
        'posts_per_page' => 1,
        'meta_query' => [
            [
                'key' => '_wp_attached_file',
                'value' => $image_filename,
                'compare' => 'LIKE'
            ]
        ]
    ]);

    if (!empty($attachments)) {
        $existing_attachment = $attachments[0]->ID;
        echo "   📎 Found existing attachment ID: $existing_attachment\n";
    } else {
        // Import image to Media Library
        $wp_upload_dir = wp_upload_dir();

        // Copy to uploads directory if not already there
        $new_filename = 'blog-' . $image_filename;
        $new_file_path = $wp_upload_dir['path'] . '/' . $new_filename;

        if (!copy($image_path, $new_file_path)) {
            echo "   ❌ Failed to copy image\n\n";
            $error_count++;
            continue;
        }

        // Create attachment
        $attachment = [
            'guid' => $wp_upload_dir['url'] . '/' . $new_filename,
            'post_mime_type' => 'image/jpeg',
            'post_title' => preg_replace('/\.[^.]+$/', '', $new_filename),
            'post_content' => '',
            'post_status' => 'inherit'
        ];

        $attach_id = wp_insert_attachment($attachment, $new_file_path, $post->ID);

        if (is_wp_error($attach_id)) {
            echo "   ❌ Failed to create attachment: " . $attach_id->get_error_message() . "\n\n";
            $error_count++;
            continue;
        }

        // Generate metadata
        require_once(ABSPATH . 'wp-admin/includes/image.php');
        $attach_data = wp_generate_attachment_metadata($attach_id, $new_file_path);
        wp_update_attachment_metadata($attach_id, $attach_data);

        $existing_attachment = $attach_id;
        echo "   ✨ Created new attachment ID: $existing_attachment\n";
    }

    // Set as featured image
    if (set_post_thumbnail($post->ID, $existing_attachment)) {
        echo "   ✅ Featured image set successfully\n\n";
        $success_count++;
    } else {
        echo "   ❌ Failed to set featured image\n\n";
        $error_count++;
    }
}

echo "\n====================\n";
echo "✅ Success: $success_count posts\n";
echo "❌ Errors: $error_count posts\n";
echo "\n🎉 DONE! Refresh http://localhost:8080/blog/ to see changes\n";
echo "\n💡 Remember to hard refresh: Cmd+Shift+R (Mac) or Ctrl+F5 (Windows)\n";
