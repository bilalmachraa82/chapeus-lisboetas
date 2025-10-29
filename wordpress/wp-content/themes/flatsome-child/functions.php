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

// Enqueue AOS (Animate On Scroll) library
function chapeus_enqueue_aos() {
    if (is_admin()) {
        return;
    }

    // AOS CSS
    wp_enqueue_style(
        'aos-css',
        'https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css',
        array(),
        '2.3.4'
    );

    // AOS JS
    wp_enqueue_script(
        'aos-js',
        'https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js',
        array('jquery'),
        '2.3.4',
        true
    );
}
add_action('wp_enqueue_scripts', 'chapeus_enqueue_aos', 90);

// Enqueue GLightbox for Instagram gallery - P1.2
function chapeus_enqueue_glightbox() {
    if (is_admin()) {
        return;
    }

    // GLightbox CSS
    wp_enqueue_style(
        'glightbox-css',
        'https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/css/glightbox.min.css',
        array(),
        '3.2.0'
    );

    // GLightbox JS
    wp_enqueue_script(
        'glightbox-js',
        'https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/js/glightbox.min.js',
        array('jquery'),
        '3.2.0',
        true
    );
}
add_action('wp_enqueue_scripts', 'chapeus_enqueue_glightbox', 90);

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
