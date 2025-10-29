<?php
// Enqueue Swiper.js for Featured Collections Carousel
function chapeus_enqueue_swiper() {
    if (is_admin()) {
        return;
    }

    // Swiper CSS
    wp_enqueue_style(
        'swiper-css',
        'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css',
        array(),
        '11.0.0'
    );

    // Swiper JS
    wp_enqueue_script(
        'swiper-js',
        'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js',
        array('jquery'),
        '11.0.0',
        true
    );
}
add_action('wp_enqueue_scripts', 'chapeus_enqueue_swiper', 90);

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
        array('jquery', 'swiper-js'),
        $version,
        true
    );
}, 100);
