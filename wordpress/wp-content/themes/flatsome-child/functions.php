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

// P2.2 - Add loading priority hints to images
function chapeus_add_image_loading_attributes($attr, $attachment, $size) {
    // Hero images: eager loading (high priority)
    if (is_front_page() && isset($attr['class']) && strpos($attr['class'], 'hero') !== false) {
        $attr['loading'] = 'eager';
        $attr['fetchpriority'] = 'high';
    }
    // Product thumbnails: lazy loading
    else if (isset($attr['class']) && (strpos($attr['class'], 'product') !== false || strpos($attr['class'], 'woocommerce') !== false)) {
        $attr['loading'] = 'lazy';
    }
    // Default: lazy loading for all other images
    else {
        $attr['loading'] = 'lazy';
    }

    return $attr;
}
add_filter('wp_get_attachment_image_attributes', 'chapeus_add_image_loading_attributes', 10, 3);

// P2.2 - Preload critical images
function chapeus_preload_critical_images() {
    if (is_front_page()) {
        // Get hero image (you can customize this path)
        $hero_image = get_template_directory_uri() . '/wp-content/uploads/hero-image.jpg';

        // Check if custom hero image is set via theme options
        if (function_exists('get_theme_mod')) {
            $custom_hero = get_theme_mod('hero_image');
            if ($custom_hero) {
                $hero_image = $custom_hero;
            }
        }

        // Preload the hero image
        echo '<link rel="preload" as="image" href="' . esc_url($hero_image) . '" fetchpriority="high">' . "\n";
    }
}
add_action('wp_head', 'chapeus_preload_critical_images', 5);

// P2.2 - Add width and height attributes to prevent layout shift
function chapeus_add_image_dimensions($image, $attachment_id, $size, $icon) {
    if (!$attachment_id) {
        return $image;
    }

    // Get image metadata
    $meta = wp_get_attachment_metadata($attachment_id);

    if (!empty($meta['width']) && !empty($meta['height'])) {
        // Add width and height attributes if they don't exist
        if (strpos($image, 'width=') === false && strpos($image, 'height=') === false) {
            $width = $meta['width'];
            $height = $meta['height'];

            // For specific sizes, get the correct dimensions
            if (is_array($size) && isset($size[0]) && isset($size[1])) {
                $width = $size[0];
                $height = $size[1];
            } elseif (is_string($size) && isset($meta['sizes'][$size])) {
                $width = $meta['sizes'][$size]['width'];
                $height = $meta['sizes'][$size]['height'];
            }

            $image = str_replace('<img', '<img width="' . esc_attr($width) . '" height="' . esc_attr($height) . '"', $image);
        }
    }

    return $image;
}
add_filter('wp_get_attachment_image', 'chapeus_add_image_dimensions', 10, 4);

// P2.3 - Mobile optimization meta tags
function chapeus_mobile_meta_tags() {
    ?>
    <!-- Mobile Optimization -->
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes">
    <meta name="format-detection" content="telephone=yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="theme-color" content="#D4AF37">

    <!-- Touch icons -->
    <link rel="apple-touch-icon" sizes="180x180" href="<?php echo get_stylesheet_directory_uri(); ?>/assets/icons/apple-touch-icon.png">

    <!-- Optimize for slow networks -->
    <link rel="dns-prefetch" href="//fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
    <?php
}
add_action('wp_head', 'chapeus_mobile_meta_tags', 1);
