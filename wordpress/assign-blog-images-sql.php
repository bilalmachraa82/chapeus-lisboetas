<?php
/**
 * Assign Blog Images via Direct SQL
 * For posts that aren't showing via WP_Query
 */

require_once(__DIR__ . '/wp-load.php');
global $wpdb;

echo "🔧 ASSIGNING BLOG IMAGES VIA SQL\n";
echo "=================================\n\n";

// Mapping: post ID => blog image filename
$assignments = [
    214473 => 'blog_cinema_iconico.jpg',      // Chapéus de Cinema
    214472 => 'blog_presente_feliz.jpg',      // Presente Único
    214471 => 'blog_sustentavel_maos.jpg',    // Da Ovelha ao Chapéu
    214470 => 'blog_inverno_feltro.jpg',      // Inverno sem Frio
    214469 => 'blog_joao_jovem.jpg',          // João, 28 Anos
    214468 => 'blog_verao_lisboa.jpg',        // Verão em Lisboa
    214467 => 'blog_boina_tradicional.jpg',   // Boina Portuguesa
    214466 => 'blog_fedora_outono.jpg',       // 5 Looks Fedora
    214465 => 'blog_maria_vintage.jpg',       // Maria do Carmo
    214464 => 'blog_casamentos_elegante.jpg', // Casamentos
];

$upload_dir = wp_upload_dir();
$success = 0;
$errors = 0;

foreach ($assignments as $post_id => $image_filename) {
    // Get post title
    $post = get_post($post_id);
    if (!$post) {
        echo "❌ Post $post_id not found\n";
        $errors++;
        continue;
    }

    echo "📝 Processing: {$post->post_title} (ID: $post_id)\n";

    // Check if already has featured image
    $current_thumb = get_post_thumbnail_id($post_id);
    if ($current_thumb) {
        echo "   ℹ️  Already has thumbnail ID: $current_thumb\n";
    }

    // Full path to source image
    $source_path = ABSPATH . 'wp-content/uploads/2025/10/blog/' . $image_filename;

    if (!file_exists($source_path)) {
        echo "   ❌ Image not found: $image_filename\n\n";
        $errors++;
        continue;
    }

    // Check if this image is already in Media Library
    $existing = $wpdb->get_var($wpdb->prepare(
        "SELECT post_id FROM {$wpdb->postmeta}
         WHERE meta_key = '_wp_attached_file'
         AND meta_value LIKE %s
         LIMIT 1",
        '%' . $wpdb->esc_like($image_filename) . '%'
    ));

    $attachment_id = null;

    if ($existing) {
        $attachment_id = $existing;
        echo "   📎 Found existing attachment: $attachment_id\n";
    } else {
        // Import to Media Library
        $new_filename = 'blog-' . str_replace('.jpg', '-' . $post_id . '.jpg', $image_filename);
        $new_path = $upload_dir['path'] . '/' . $new_filename;

        if (!copy($source_path, $new_path)) {
            echo "   ❌ Failed to copy image\n\n";
            $errors++;
            continue;
        }

        // Create attachment
        $attachment = [
            'guid' => $upload_dir['url'] . '/' . $new_filename,
            'post_mime_type' => 'image/jpeg',
            'post_title' => sanitize_file_name(pathinfo($new_filename, PATHINFO_FILENAME)),
            'post_content' => '',
            'post_status' => 'inherit'
        ];

        $attachment_id = wp_insert_attachment($attachment, $new_path, $post_id);

        if (is_wp_error($attachment_id)) {
            echo "   ❌ Failed to create attachment\n\n";
            $errors++;
            continue;
        }

        // Generate thumbnails
        require_once(ABSPATH . 'wp-admin/includes/image.php');
        $metadata = wp_generate_attachment_metadata($attachment_id, $new_path);
        wp_update_attachment_metadata($attachment_id, $metadata);

        echo "   ✨ Created attachment: $attachment_id\n";
    }

    // Set as featured image
    $result = set_post_thumbnail($post_id, $attachment_id);

    if ($result) {
        echo "   ✅ Featured image assigned\n\n";
        $success++;
    } else {
        echo "   ❌ Failed to assign featured image\n\n";
        $errors++;
    }
}

echo "=================================\n";
echo "✅ Success: $success posts\n";
echo "❌ Errors: $errors posts\n\n";
echo "🎉 DONE! Now check http://localhost:8080/blog/\n";
echo "💡 Hard refresh: Cmd+Shift+R or Ctrl+F5\n";
