<?php
/**
 * Register an existing image inside wp-content/uploads/ as an attachment
 * without generating additional intermediate sizes.
 *
 * Usage (via WP-CLI):
 *   wp eval-file scripts/register_ai_attachment.php <absolute_path> <relative_path>
 *
 * Arguments:
 *   $argv[1] Absolute filesystem path (inside container) to the image.
 *   $argv[2] Uploads-relative path (e.g., products/boinas inverno/bone-22195/img_01_pro.jpg).
 */

if (php_sapi_name() !== 'cli') {
    fwrite(STDERR, "This script must run via CLI.\n");
    exit(1);
}

// WP-CLI passes arguments through $_SERVER['argv']
$args = isset($_SERVER['argv']) ? $_SERVER['argv'] : [];
if (count($args) < 4) {
    fwrite(STDERR, "Usage: wp eval-file register_ai_attachment.php <abs_path> <relative_path>\n");
    exit(1);
}

// argv: [0] => wp, [1] => eval-file, [2] => script.php, [3] => abs_path, [4] => relative_path
$abs_path = $args[3];
$relative_path = $args[4] ?? '';

if (!file_exists($abs_path)) {
    fwrite(STDERR, "File not found: {$abs_path}\n");
    exit(1);
}

if (!function_exists('wp_insert_attachment')) {
    require_once ABSPATH . 'wp-admin/includes/image.php';
}

$filetype = wp_check_filetype($abs_path);
$mime = $filetype['type'] ?? 'image/jpeg';

$attachment = [
    'post_mime_type' => $mime,
    'post_title'     => basename($abs_path),
    'post_content'   => '',
    'post_status'    => 'inherit',
];

$attach_id = wp_insert_attachment($attachment, $abs_path);
if (is_wp_error($attach_id)) {
    fwrite(STDERR, $attach_id->get_error_message() . PHP_EOL);
    exit(1);
}

// Store uploads-relative path (e.g., products/...)
update_post_meta($attach_id, '_wp_attached_file', $relative_path);

// Basic metadata (avoid heavy wp_generate_attachment_metadata)
$size = getimagesize($abs_path);
$metadata = [
    'width'  => $size[0] ?? 0,
    'height' => $size[1] ?? 0,
    'file'   => $relative_path,
    'sizes'  => [],
    'image_meta' => [
        'aperture' => '0',
        'credit'   => '',
        'camera'   => '',
        'caption'  => '',
        'created_timestamp' => '0',
        'copyright' => '',
        'focal_length' => '0',
        'iso' => '0',
        'shutter_speed' => '0',
        'title' => '',
        'orientation' => 0,
        'keywords' => [],
    ],
];
wp_update_attachment_metadata($attach_id, $metadata);

echo $attach_id;
exit(0);
