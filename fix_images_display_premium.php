<?php
/**
 * 🖼️ FIX IMAGES DISPLAY - Imagens maiores e melhor visualização
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🖼️ CORRIGINDO VISUALIZAÇÃO DE IMAGENS...\n\n";
echo str_repeat("=", 70) . "\n\n";

// ============================================================================
// 1. CONFIGURAR TAMANHOS DE IMAGEM WOOCOMMERCE
// ============================================================================

echo "1️⃣ CONFIGURANDO TAMANHOS DE IMAGEM...\n\n";

// Tamanhos maiores para melhor visualização
update_option('woocommerce_thumbnail_image_width', 500);
update_option('woocommerce_thumbnail_image_height', 500);
update_option('woocommerce_thumbnail_cropping', '1:1');

update_option('woocommerce_single_image_width', 800);
update_option('woocommerce_gallery_thumbnail_size', 200);

// Flatsome product image settings
set_theme_mod('product_image_width', 500);
set_theme_mod('product_image_hover', 'fade');
set_theme_mod('product_box_style', 'default');

echo "   ✅ Thumbnails: 500x500px\n";
echo "   ✅ Single product: 800px\n";
echo "   ✅ Gallery thumbnails: 200px\n\n";

// ============================================================================
// 2. REGENERAR THUMBNAILS (para aplicar novos tamanhos)
// ============================================================================

echo "2️⃣ REGENERANDO THUMBNAILS...\n\n";

$products_with_images = get_posts(array(
    'post_type' => 'product',
    'posts_per_page' => 50, // Primeiros 50 para não demorar muito
    'meta_query' => array(
        array(
            'key' => '_thumbnail_id',
            'compare' => 'EXISTS'
        )
    )
));

$regenerated = 0;
foreach ($products_with_images as $product) {
    $thumb_id = get_post_thumbnail_id($product->ID);
    if ($thumb_id) {
        require_once(ABSPATH . 'wp-admin/includes/image.php');
        $file = get_attached_file($thumb_id);
        if ($file) {
            $metadata = wp_generate_attachment_metadata($thumb_id, $file);
            wp_update_attachment_metadata($thumb_id, $metadata);
            $regenerated++;
        }
    }
}

echo "   ✅ $regenerated thumbnails regenerados\n\n";

// ============================================================================
// 3. CSS PARA IMAGENS MAIORES E MELHOR VISUALIZAÇÃO
// ============================================================================

echo "3️⃣ APLICANDO CSS PREMIUM PARA IMAGENS...\n\n";

$image_css = "
/* === IMAGENS PREMIUM === */

/* Produtos - Imagens maiores */
.product .box-image {
    position: relative;
    overflow: hidden;
    background: #f8f8f8;
}

.product .box-image img {
    width: 100% !important;
    height: auto !important;
    min-height: 400px;
    object-fit: cover;
    object-position: center;
    transition: transform 0.5s ease;
}

.product:hover .box-image img {
    transform: scale(1.12);
}

/* Grid products - aspect ratio consistente */
.products .product {
    margin-bottom: 40px;
}

.products .box-image {
    aspect-ratio: 1 / 1;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* UX Products shortcode - imagens maiores */
.ux_products .product {
    margin-bottom: 50px;
}

.ux_products .box-image img {
    min-height: 450px !important;
}

/* Single product - galeria maior */
.product-gallery img {
    width: 100% !important;
    height: auto !important;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.product-main .product-images {
    margin-bottom: 30px;
}

/* Lightbox - imagens full size */
.mfp-img {
    max-width: 90vw !important;
    max-height: 90vh !important;
    object-fit: contain;
}

/* Featured images - hero e categorias */
.ux-image-box img {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover;
    object-position: center;
}

/* Lazy load - evitar flash */
img[loading=\"lazy\"] {
    opacity: 0;
    transition: opacity 0.3s;
}

img[loading=\"lazy\"].lazyloaded {
    opacity: 1;
}

/* Zoom effect melhorado */
.image-zoom-hover {
    overflow: hidden;
}

.image-zoom-hover img {
    transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.image-zoom-hover:hover img {
    transform: scale(1.15);
}

/* Responsive - manter qualidade */
@media (max-width: 768px) {
    .product .box-image img {
        min-height: 300px;
    }
    
    .ux_products .box-image img {
        min-height: 350px !important;
    }
}

@media (min-width: 1200px) {
    .product .box-image img {
        min-height: 500px;
    }
    
    .ux_products .box-image img {
        min-height: 550px !important;
    }
}

/* Evitar imagens cortadas/distorcidas */
img {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
}
";

$current_css = wp_get_custom_css();
$updated_css = $current_css . "\n\n/* Premium Image Display */\n" . $image_css;
wp_update_custom_css_post($updated_css);

echo "   ✅ CSS de imagens aplicado\n\n";

// ============================================================================
// 4. CONFIGURAR FLATSOME PRODUCT DISPLAY
// ============================================================================

echo "4️⃣ CONFIGURANDO DISPLAY DE PRODUTOS...\n\n";

// Grid settings
set_theme_mod('category_grid_style', 'default');
set_theme_mod('product_display', 'default');

// Image hover effects
set_theme_mod('product_hover', 'fade');
set_theme_mod('product_hover_style', 'fade');

// Quick view com imagem grande
set_theme_mod('product_quick_view', 1);
set_theme_mod('quick_view_width', 800);

// Lightbox ativo
set_theme_mod('lightbox_products', 1);

// Product box style
set_theme_mod('product_box_style', 'default');
set_theme_mod('category_box_style', 'default');

echo "   ✅ Hover: Fade effect\n";
echo "   ✅ Quick view: 800px\n";
echo "   ✅ Lightbox: Ativo\n\n";

// ============================================================================
// 5. ATUALIZAR SHOP PAGE COM IMAGENS MAIORES
// ============================================================================

echo "5️⃣ ATUALIZANDO LOJA COM GRID OTIMIZADO...\n\n";

// Pegar produtos com imagens
$featured_products = get_posts(array(
    'post_type' => 'product',
    'posts_per_page' => 48,
    'meta_query' => array(
        array(
            'key' => '_thumbnail_id',
            'compare' => 'EXISTS'
        )
    ),
    'orderby' => 'rand'
));

$product_ids = array_map(function($p) { return $p->ID; }, $featured_products);

$optimized_shop = '[section padding="60px"]
[row]
[col span="12" align="center"]
<h1 style="font-family: \'Playfair Display\', serif; font-size: 3.5rem; color: #1B1464; margin-bottom: 15px;">Coleção Completa</h1>
<p style="font-size: 1.25rem; color: #6D4C41; margin-bottom: 50px;">180 chapéus artesanais portugueses • Desde 1950</p>
[/col]
[/row]
[/section]

[section padding="40px"]
[row]

[col span="3" span__sm="12" class="sidebar-shop"]
<div style="background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin-bottom: 25px;">
<h3 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; font-size: 1.25rem; margin-bottom: 20px; border-bottom: 3px solid #FFD700; padding-bottom: 12px;">📁 Categorias</h3>
<ul style="list-style: none; padding: 0; margin: 0;">
<li style="margin: 12px 0;"><a href="/product-category/boinas" style="color: #6D4C41; text-decoration: none; font-size: 1.0625rem; transition: all 0.2s; display: block; padding: 8px 12px; border-radius: 6px;">Boinas <span style="float: right; color: #FFD700; font-weight: 600;">81</span></a></li>
<li style="margin: 12px 0;"><a href="/product-category/bones" style="color: #6D4C41; text-decoration: none; font-size: 1.0625rem; transition: all 0.2s; display: block; padding: 8px 12px; border-radius: 6px;">Bonés <span style="float: right; color: #FFD700; font-weight: 600;">33</span></a></li>
<li style="margin: 12px 0;"><a href="/product-category/bucket-hats" style="color: #6D4C41; text-decoration: none; font-size: 1.0625rem; transition: all 0.2s; display: block; padding: 8px 12px; border-radius: 6px;">Bucket Hats <span style="float: right; color: #FFD700; font-weight: 600;">29</span></a></li>
<li style="margin: 12px 0;"><a href="/product-category/capelines" style="color: #6D4C41; text-decoration: none; font-size: 1.0625rem; transition: all 0.2s; display: block; padding: 8px 12px; border-radius: 6px;">Capelines <span style="float: right; color: #FFD700; font-weight: 600;">12</span></a></li>
<li style="margin: 12px 0;"><a href="/product-category/gorros" style="color: #6D4C41; text-decoration: none; font-size: 1.0625rem; transition: all 0.2s; display: block; padding: 8px 12px; border-radius: 6px;">Gorros <span style="float: right; color: #FFD700; font-weight: 600;">3</span></a></li>
</ul>
</div>

<div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); padding: 30px; border-radius: 16px; text-align: center; color: #1B1464;">
<div style="font-size: 3rem; margin-bottom: 15px;">🚚</div>
<h4 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 8px;">Envio Grátis</h4>
<p style="font-size: 0.9375rem; margin: 0; opacity: 0.9;">Compras acima de €75</p>
</div>
[/col]

[col span="9" span__sm="12"]
<h2 style="font-family: \'Playfair Display\', serif; font-size: 2.25rem; color: #1B1464; margin-bottom: 30px;">✨ Em Destaque</h2>
[ux_products ids="' . implode(',', array_slice($product_ids, 0, 12)) . '" columns="3" show_cat="0" show_quick_view="1" image_height="140%" image_width="100%"]

<h2 style="font-family: \'Playfair Display\', serif; font-size: 2.25rem; color: #1B1464; margin: 60px 0 30px;">🆕 Mais Produtos</h2>
[ux_products ids="' . implode(',', array_slice($product_ids, 12, 36)) . '" columns="3" show_cat="0" show_quick_view="1" image_height="140%" image_width="100%"]
[/col]

[/row]
[/section]';

// Atualizar página teste-html
$test_page = get_page_by_path('teste-html');
if ($test_page) {
    wp_update_post(array(
        'ID' => $test_page->ID,
        'post_content' => $optimized_shop
    ));
    echo "   ✅ Loja atualizada com grid otimizado\n\n";
}

// ============================================================================
// 6. LIMPAR CACHES
// ============================================================================

echo "6️⃣ LIMPANDO CACHES...\n\n";

wp_cache_flush();
delete_transient('flatsome_settings');

echo "   ✅ Caches limpos\n\n";

// ============================================================================
// FINAL
// ============================================================================

echo str_repeat("=", 70) . "\n";
echo "✅ IMAGENS CORRIGIDAS E OTIMIZADAS!\n";
echo str_repeat("=", 70) . "\n\n";

echo "🖼️  CONFIGURAÇÕES APLICADAS:\n";
echo "   • Thumbnails: 500x500px (maiores)\n";
echo "   • Min-height: 400-500px (produtos)\n";
echo "   • Aspect ratio: 1:1 consistente\n";
echo "   • Object-fit: cover (sem distorção)\n";
echo "   • Hover: Scale(1.12) suave\n";
echo "   • Lightbox: Ativo para zoom\n";
echo "   • Quick view: 800px modal\n";
echo "   • Responsive: 300px mobile → 500px desktop\n\n";

echo "🌐 TESTAR:\n";
echo "   http://localhost:8080/teste-html\n\n";

echo "💡 RESULTADO:\n";
echo "   • Imagens muito maiores e visíveis\n";
echo "   • Sem distorção ou corte\n";
echo "   • Hover zoom suave\n";
echo "   • Lightbox para ampliar\n\n";

?>
