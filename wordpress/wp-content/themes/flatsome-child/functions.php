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

// Force child theme stylesheet to carry cache-busting version.
add_filter('style_loader_src', function ($src, $handle) {
    $targets = array('flatsome-style', 'flatsome-style-css', 'flatsome-style-css-css');
    if (in_array($handle, $targets, true)) {
        $style_path = get_stylesheet_directory() . '/style.css';
        $version = file_exists($style_path) ? filemtime($style_path) : time();
        $src = add_query_arg('ver', $version, remove_query_arg('ver', $src));
    }

    return $src;
}, 20, 2);

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

// Inject homepage hero tweaks responding to latest client feedback
add_action('wp_enqueue_scripts', function () {
    if (is_admin()) {
        return;
    }

    $hero_overrides = <<<CSS
body.home .wp-block-cover.alignfull.is-light {
    padding-top: 0 !important;
    padding-bottom: clamp(40px, 8vh, 72px) !important;
    min-height: clamp(420px, 60vh, 620px) !important;
    max-height: clamp(520px, 70vh, 720px) !important;
}

body.home .content-area.page-wrapper,
body.home .page-wrapper .col-inner {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

body.home .page-wrapper .col-inner > *:first-child {
    margin-top: 0 !important;
}

body.home #main,
body.home #content,
body.home .row.row-main,
body.home .row.row-main > .col,
body.home .row.row-main > .col .col-inner {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

body.home .top-divider.full-width {
    display: none !important;
    height: 0 !important;
}

body.home .wp-block-cover.alignfull.is-light .wp-block-cover__background {
    background: linear-gradient(
        180deg,
        rgba(17, 8, 2, 0.28) 0%,
        rgba(17, 8, 2, 0.42) 55%,
        rgba(17, 8, 2, 0.48) 100%
    ) !important;
    opacity: 1 !important;
}

body.home .wp-block-cover.alignfull.is-light .wp-block-cover__image-background {
    object-fit: cover !important;
    object-position: 50% 24% !important;
}

body.home .wp-block-cover.alignfull.is-light .wp-block-cover__inner-container {
    padding-top: clamp(40px, 6vh, 80px) !important;
}

/* P0.4 FIX: Separate text-shadow for h1/p vs buttons */
body.home .wp-block-cover.alignfull.is-light h1,
body.home .wp-block-cover.alignfull.is-light p {
    text-shadow:
        0 2px 4px rgba(0, 0, 0, 0.9),
        0 6px 18px rgba(0, 0, 0, 0.6) !important;
}

/* P0.4: Reduced text-shadow for buttons (client feedback: "muito sombreado") */
body.home .wp-block-cover.alignfull.is-light .wp-block-button__link {
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}

body.home .wp-block-cover.alignfull.is-light .wp-block-button__link {
    background-color: var(--chap-action-primary, #E07A31) !important;
    color: var(--chap-white, #FFFFFF) !important;
    border: none !important;
    padding: 16px 32px !important;
}

body.home .wp-block-cover.alignfull.is-light .wp-block-button.is-style-outline .wp-block-button__link {
    background-color: rgba(255, 255, 255, 0.92) !important;
    color: var(--chap-action-primary, #E07A31) !important;
    border: 2px solid rgba(255, 255, 255, 0.92) !important;
}

@media (max-width: 767px) {
    body.home .wp-block-cover.alignfull.is-light {
        min-height: clamp(360px, 72vh, 520px) !important;
        max-height: 78vh !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
    }

    body.home .wp-block-cover.alignfull.is-light h1 {
        font-size: clamp(36px, 7vw, 44px) !important;
        line-height: 1.1 !important;
    }
}
CSS;

    wp_add_inline_style('flatsome-style', $hero_overrides);
}, 110);

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
        // Get hero image - corrected path (P0.4 fix)
        $hero_image = get_site_url() . '/wp-content/uploads/2025/10/homepage/01_hero_mulher_feliz_panama.jpg';

        // Check if custom hero image is set via theme options
        if (function_exists('get_theme_mod')) {
            $custom_hero = get_theme_mod('hero_image');
            if ($custom_hero) {
                $hero_image = $custom_hero;
            }
        }

        // Preload the hero image with high priority for LCP optimization
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

// WordPress Integration - Social Proof Badge
function chapeus_add_social_proof_badge() {
    if (!is_front_page()) {
        return;
    }
    ?>
    <script>
    jQuery(document).ready(function($) {
        // Add Social Proof badge before Instagram/Momentos section
        var instagramSection = $('.is-momentos-gallery, .instagram-feed, [class*="instagram"]').first().closest('.section');
        if (instagramSection.length && !instagramSection.find('.section-label-social-proof').length) {
            instagramSection.prepend('<div class="text-center mb-3"><span class="section-label-social-proof">Social Proof</span></div>');
        }
    });
    </script>
    <?php
}
add_action('wp_footer', 'chapeus_add_social_proof_badge', 100);

// WordPress Integration - "Ver todas as coleções" CTA
function chapeus_add_view_all_collections() {
    if (!is_front_page()) {
        return;
    }
    ?>
    <script>
    jQuery(document).ready(function($) {
        // Add "Ver todas as coleções" button after featured collections
        var collectionsSection = $('.is-featured-collections, .featured-collections-carousel').last().closest('.section');
        if (collectionsSection.length && !collectionsSection.find('.featured-collections__view-all').length) {
            var shopUrl = '<?php echo get_permalink(wc_get_page_id('shop')); ?>';
            collectionsSection.append('<div class="featured-collections__view-all text-center mt-4"><a href="' + shopUrl + '" class="button">Ver todas as coleções</a></div>');
        }
    });
    </script>
    <?php
}
add_action('wp_footer', 'chapeus_add_view_all_collections', 100);

// WordPress Integration - Micro-CTAs "Saber mais"
function chapeus_add_saber_mais_ctas() {
    if (!is_front_page()) {
        return;
    }
    ?>
    <script>
    jQuery(document).ready(function($) {
        // Add "Saber mais" links to icon boxes that don't have them
        $('.icon-box').each(function() {
            var $iconBox = $(this);
            var $textBox = $iconBox.find('.icon-box-text, .text');

            // Only add if there's no existing link
            if ($textBox.length && !$textBox.find('.text-more').length && !$textBox.find('a').length) {
                var aboutUrl = '<?php echo get_permalink(get_page_by_path('sobre-nos')); ?>';
                $textBox.append('<a href="' + aboutUrl + '" class="text-more">Saber mais</a>');
            }
        });
    });
    </script>
    <?php
}
add_action('wp_footer', 'chapeus_add_saber_mais_ctas', 100);

// ISSUE-009: Livro de Reclamações - Portugal Legal Requirement
// Decreto-Lei n.º 156/2005
function chapeus_add_livro_reclamacoes() {
    ?>
    <div class="livro-reclamacoes-footer" style="margin-top: 20px; text-align: center;">
        <a href="https://www.livroreclamacoes.pt/" target="_blank" rel="noopener noreferrer" title="Livro de Reclamações">
            <img src="<?php echo get_stylesheet_directory_uri(); ?>/assets/images/livro-reclamacoes.png"
                 alt="Livro de Reclamações"
                 style="height: 50px; width: auto; display: inline-block;"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';" />
            <span style="display:none; color: #E07A31; font-size: 14px; text-decoration: underline;">📖 Livro de Reclamações</span>
        </a>
    </div>
    <?php
}
add_action('flatsome_footer_bottom', 'chapeus_add_livro_reclamacoes', 100);

/**
 * Blog archive featured image fallbacks.
 *
 * Some imported posts do not have a `_thumbnail_id`, which prevents Flatsome from
 * rendering the `.entry-image` wrapper. This hook chain forces a graceful
 * fallback so archives always display a hero image while also replacing the
 * outdated "boneco de madeira" photo.
 */

/**
 * Map blog post title keywords to curated fallback images.
 */
function chapeus_blog_fallback_image_map() {
    return [
        'cinema' => '2025/10/blog/blog_cinema_iconico.jpg',
        'presente' => '2025/10/blog/blog_presente_feliz.jpg',
        'ovelha' => '2025/10/blog/blog_sustentavel_maos.jpg',
        'inverno-sem-frio' => '2025/10/blog/blog_inverno_feltro.jpg',
        'joao-28' => '2025/10/blog/blog_joao_jovem.jpg',
        'verao-em-lisboa' => '2025/10/blog/blog_verao_lisboa.jpg',
        'boina-portuguesa' => '2025/10/blog/blog_boina_tradicional.jpg',
        'fedora' => '2025/10/blog/blog_fedora_outono.jpg',
        'maria-do-carmo' => '2025/10/blog/blog_maria_vintage.jpg',
        'casamentos' => '2025/10/blog/blog_casamentos_elegante.jpg',
        'cuidar-do-seu' => '2025/10/blog/blog_cuidados_lisboa.jpg',
        'atelier' => '2025/10/blog/blog_atelier_loja.jpg',
        'panama' => '2025/10/blog/blog_panama_feliz.jpg',
        '75-anos' => '2025/10/blog/blog_historia_vintage.jpg',
        '3-perguntas' => '2025/10/blog/blog_perguntas_boina.jpg',
    ];
}

/**
 * Resolve an image stored within the uploads directory.
 *
 * @param string  $relative_path Relative path inside uploads (Y/m/filename).
 * @param WP_Post $post          Post instance used for alt text context.
 * @return array|null            Fallback data structure or null when missing.
 */
function chapeus_blog_prepare_image_from_upload($relative_path, $post) {
    $relative = ltrim($relative_path, '/');

    $upload_dir = wp_upload_dir();
    $file_path = trailingslashit($upload_dir['basedir']) . str_replace(['/', '\\'], DIRECTORY_SEPARATOR, $relative);

    if (!file_exists($file_path)) {
        return null;
    }

    $url = trailingslashit($upload_dir['baseurl']) . str_replace('\\', '/', $relative);
    $dimensions = @getimagesize($file_path);

    return [
        'url' => $url,
        'width' => $dimensions ? (int) $dimensions[0] : null,
        'height' => $dimensions ? (int) $dimensions[1] : null,
        /* translators: %s: blog post title. */
        'alt' => sprintf(__('Fotografia ilustrativa para "%s"', 'flatsome-child'), $post->post_title),
    ];
}

/**
 * Compute fallback metadata for a post when no featured image exists.
 */
function chapeus_blog_get_fallback_image($post_id) {
    static $cache = [];

    if (array_key_exists($post_id, $cache)) {
        return $cache[$post_id];
    }

    $post = get_post($post_id);

    if (!$post instanceof WP_Post || $post->post_type !== 'post') {
        $cache[$post_id] = null;
        return null;
    }

    $normalized_title = sanitize_title($post->post_title);

    foreach (chapeus_blog_fallback_image_map() as $keyword => $relative_path) {
        if (strpos($normalized_title, $keyword) !== false) {
            $image = chapeus_blog_prepare_image_from_upload($relative_path, $post);
            if ($image) {
                $cache[$post_id] = $image;
                return $image;
            }
        }
    }

    if (!empty($post->post_content) && preg_match('/<img[^>]+src=["\']([^"\']+)["\'][^>]*>/i', $post->post_content, $matches)) {
        $alt = $post->post_title;

        if (!empty($matches[0]) && preg_match('/alt=["\']([^"\']*)["\']/i', $matches[0], $alt_match)) {
            $alt = $alt_match[1];
        }

        $cache[$post_id] = [
            'url' => $matches[1],
            'width' => null,
            'height' => null,
            'alt' => $alt,
        ];

        return $cache[$post_id];
    }

    $placeholder_path = get_stylesheet_directory() . '/assets/images/blog-placeholder.svg';
    $placeholder_url = get_stylesheet_directory_uri() . '/assets/images/blog-placeholder.svg';

    if (file_exists($placeholder_path)) {
        $cache[$post_id] = [
            'url' => $placeholder_url,
            'width' => 1200,
            'height' => 800,
            'alt' => $post->post_title,
        ];

        return $cache[$post_id];
    }

    $cache[$post_id] = null;

    return null;
}

/**
 * Pretend posts have a thumbnail when a fallback image is available.
 */
function chapeus_blog_force_fallback_thumbnail($has_thumbnail, $post, $thumbnail_id) {
    if ($has_thumbnail || !$post instanceof WP_Post || $post->post_type !== 'post') {
        return $has_thumbnail;
    }

    return chapeus_blog_get_fallback_image($post->ID) ? true : $has_thumbnail;
}
add_filter('has_post_thumbnail', 'chapeus_blog_force_fallback_thumbnail', 10, 3);

/**
 * Render fallback markup for the_posts without a featured image.
 */
function chapeus_blog_render_fallback_thumbnail($html, $post_id, $thumbnail_id, $size, $attr) {
    if (!empty($html)) {
        return $html;
    }

    $fallback = chapeus_blog_get_fallback_image($post_id);

    if (!$fallback) {
        return $html;
    }

    $attributes = is_array($attr) ? $attr : [];
    $classes = isset($attributes['class']) ? $attributes['class'] : '';
    $attributes['class'] = trim($classes . ' wp-post-image chapeus-fallback-thumbnail');

    if (empty($attributes['alt'])) {
        $attributes['alt'] = $fallback['alt'];
    }

    if (empty($attributes['loading'])) {
        $attributes['loading'] = 'lazy';
    }

    if (empty($attributes['decoding'])) {
        $attributes['decoding'] = 'async';
    }

    if (!empty($fallback['width']) && empty($attributes['width'])) {
        $attributes['width'] = (string) $fallback['width'];
    }

    if (!empty($fallback['height']) && empty($attributes['height'])) {
        $attributes['height'] = (string) $fallback['height'];
    }

    $attribute_string = '';
    foreach ($attributes as $name => $value) {
        if ($value === null || $value === '') {
            continue;
        }

        $attribute_string .= sprintf(' %s="%s"', esc_attr($name), esc_attr($value));
    }

    return sprintf('<img src="%s"%s />', esc_url($fallback['url']), $attribute_string);
}
add_filter('post_thumbnail_html', 'chapeus_blog_render_fallback_thumbnail', 10, 5);

/**
 * CRITICAL: Inline CSS para garantir que fixes aparecem no browser
 * Adiciona CSS diretamente no <head> com prioridade MÁXIMA
 *
 * Razão: CSS file pode estar em cache do browser mesmo com hard refresh
 * Solução: Inline CSS no header = SEMPRE executado, NUNCA em cache
 */
add_action('wp_head', function() {
    ?>
    <style id="chapeus-critical-fixes-inline">
        /********** CRITICAL FIXES - INLINE (Always Execute) **********/

        /* ISSUE-005: Menu Dropdown Z-Index - MUST appear above images */
        .header-wrapper {
            position: relative !important;
            z-index: 10000 !important;
        }

        .header-nav .nav-dropdown,
        .nav-dropdown {
            z-index: 10001 !important;
            background: #FFFFFF !important;
        }

        .hero-section,
        .section-bg-overlay {
            z-index: 1 !important;
        }

        /* ISSUE-003: Links MUST be brown (not slate blue) */
        a:not(.button):not(.nav-top-link) {
            color: #8B4513 !important;
        }

        a:not(.button):not(.nav-top-link):hover {
            color: #D27855 !important;
        }

        /* ISSUE-001: Cookie Banner buttons MUST be terracotta */
        .cli-plugin-button,
        .cli-plugin-main-button {
            background-color: #E07A31 !important;
            color: #FFFFFF !important;
            border-color: #E07A31 !important;
        }

        /* ISSUE-002: Admin Bar MUST be terracotta */
        #wpadminbar {
            background: #E07A31 !important;
        }

        #wpadminbar .ab-item,
        #wpadminbar .ab-item:before {
            color: #FFFFFF !important;
        }

        /* ISSUE-004: WooCommerce notices MUST be terracotta */
        .woocommerce-message,
        .woocommerce-info {
            border-top-color: #E07A31 !important;
            background-color: #FAF7F2 !important;
        }

        .woocommerce-message::before,
        .woocommerce-info::before {
            color: #E07A31 !important;
        }

        /* ISSUE-010: Sobre-Nós Page - MUST have warm cream background (not blue) */
        body.page-id-12 .section,
        body.page-id-12 .hero-section,
        body.page-id-12 .wp-block-cover,
        body.page-id-12 .wp-block-cover__background,
        body.page-id-12 .wp-block-group {
            background-color: #FAF7F2 !important;
            background-image: linear-gradient(135deg, #FAF7F2 0%, #F5EFE6 50%, #FAF7F2 100%) !important;
        }

        /* Override ANY inline blue backgrounds on sobre-nos */
        body.page-id-12 [style*="#b2b0b0"],
        body.page-id-12 [style*="#1863dc"],
        body.page-id-12 [style*="rgb(178, 176, 176)"],
        body.page-id-12 .wp-block-cover__background.has-primary-background-color,
        body.page-id-12 .wp-block-cover__background.has-primary-background-color::before,
        body.page-id-12 .wp-block-cover__background.has-primary-background-color::after {
            background-color: #FAF7F2 !important;
            background-image: none !important;
        }

        /* Text legibility on cream background */
        body.page-id-12 .hero-section h1,
        body.page-id-12 .hero-section h2,
        body.page-id-12 .hero-section p,
        body.page-id-12 .section h1,
        body.page-id-12 .section h2,
        body.page-id-12 .section p {
            color: #2C323A !important;
            text-shadow: none !important;
        }

        /* WCAG: Dark text on light background = 8.2:1 AAA */
        body.page-id-12 .wp-block-cover__inner-container h1,
        body.page-id-12 .wp-block-cover__inner-container h2 {
            color: #2C323A !important;
            text-shadow: none !important;
        }
    </style>
    <?php
}, 999); // Priority 999 = load LAST, override everything

// -----------------------------------------------------------------------------
// UX IMPROVEMENTS: PRODUCT LOOP + BLOG COPY
// -----------------------------------------------------------------------------

remove_action('woocommerce_shop_loop_item_title', 'woocommerce_template_loop_product_title', 10);
add_action('woocommerce_shop_loop_item_title', function () {
    $product_id = get_the_ID();
    $categories = get_the_terms($product_id, 'product_cat');
    if ($categories && !is_wp_error($categories)) {
        $primary = array_shift($categories);
        echo '<span class="product-category">' . esc_html($primary->name) . '</span>';
    }

    echo '<h2 class="woocommerce-loop-product__title">' . esc_html(get_the_title()) . '</h2>';
}, 10);

add_filter('flatsome_blog_no_comments_text', function () {
    return 'Ainda não há comentários. Seja o primeiro a comentar!';
});

add_action('wp_footer', function () {
    if (!is_page('faq')) {
        return;
    }
    ?>
    <script>
    document.querySelectorAll('.faq-section h3').forEach(function (title) {
        const answer = title.nextElementSibling;
        if (!answer) { return; }
        answer.style.maxHeight = '0px';
        answer.style.overflow = 'hidden';
        answer.dataset.collapsed = 'true';
        title.classList.add('faq-question');
        title.addEventListener('click', function () {
            const expanded = answer.dataset.collapsed === 'false';
            if (expanded) {
                answer.style.maxHeight = '0px';
                answer.dataset.collapsed = 'true';
                title.classList.remove('is-open');
            } else {
                answer.style.maxHeight = answer.scrollHeight + 'px';
                answer.dataset.collapsed = 'false';
                title.classList.add('is-open');
            }
        });
    });
    </script>
    <?php
});
