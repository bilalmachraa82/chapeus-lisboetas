<?php
// Enqueue custom assets for the child theme.
add_action('wp_enqueue_scripts', function () {
    if (is_admin()) {
        return;
    }

    $theme_version = wp_get_theme()->get('Version');

    wp_enqueue_script(
        'flatsome-child-custom',
        get_stylesheet_directory_uri() . '/assets/js/custom.js',
        array(),
        $theme_version,
        true
    );
});
