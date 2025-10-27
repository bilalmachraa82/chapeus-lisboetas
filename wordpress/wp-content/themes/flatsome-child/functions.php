<?php
// Enqueue custom assets for the child theme.
add_action('wp_enqueue_scripts', function () {
    if (is_admin()) {
        return;
    }

    // Use filemtime for cache busting during development
    $custom_js_path = get_stylesheet_directory() . '/assets/js/custom.js';
    $version = file_exists($custom_js_path) ? filemtime($custom_js_path) : time();

    wp_enqueue_script(
        'flatsome-child-custom',
        get_stylesheet_directory_uri() . '/assets/js/custom.js',
        array('jquery'),
        $version,
        true
    );
}, 100);
