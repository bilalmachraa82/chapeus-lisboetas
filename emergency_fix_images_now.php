<?php
/**
 * 🚨 EMERGENCY FIX - Imagens aparecerem AGORA
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🚨 EMERGENCY FIX - FORÇAR IMAGENS APARECEREM\n\n";
echo str_repeat("=", 70) . "\n\n";

// ============================================================================
// 1. VERIFICAR ESTADO ATUAL DAS IMAGENS
// ============================================================================

echo "1️⃣ VERIFICANDO ESTADO DAS IMAGENS...\n\n";

$all_products = get_posts(array(
    'post_type' => 'product',
    'posts_per_page' => 10,
    'orderby' => 'date',
    'order' => 'DESC'
));

echo "   📊 Primeiros 10 produtos:\n";
foreach ($all_products as $product) {
    $has_thumb = has_post_thumbnail($product->ID);
    $thumb_id = get_post_thumbnail_id($product->ID);
    $thumb_url = $thumb_id ? wp_get_attachment_url($thumb_id) : 'nenhuma';
    
    echo "      • " . $product->post_title . "\n";
    echo "        Thumbnail: " . ($has_thumb ? "✅ ID $thumb_id" : "❌ Não") . "\n";
    if ($thumb_url != 'nenhuma') {
        echo "        URL: $thumb_url\n";
    }
}

// ============================================================================
// 2. CRIAR PÁGINA DE TESTE COM HTML DIRETO (SEM SHORTCODES)
// ============================================================================

echo "\n2️⃣ CRIANDO PÁGINA COM HTML DIRETO...\n\n";

$products_html = get_posts(array(
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

$html_content = '<style>
.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
    padding: 40px 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.product-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.product-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px rgba(27, 20, 100, 0.2);
}

.product-image {
    width: 100%;
    height: 400px;
    overflow: hidden;
    background: #f5f5f5;
    position: relative;
}

.product-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
}

.product-info {
    padding: 25px;
    text-align: center;
}

.product-title {
    font-family: "Playfair Display", serif;
    font-size: 1.25rem;
    color: #1B1464;
    margin: 0 0 12px 0;
    font-weight: 600;
}

.product-price {
    font-family: "Montserrat", sans-serif;
    font-size: 1.75rem;
    color: #FFD700;
    font-weight: 700;
    margin: 0 0 20px 0;
}

.product-button {
    display: inline-block;
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    color: #1B1464;
    padding: 12px 30px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9375rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    transition: all 0.3s;
}

.product-button:hover {
    background: linear-gradient(135deg, #1B1464 0%, #2A1F7D 100%);
    color: #FFD700;
    transform: translateY(-2px);
}

@media (max-width: 768px) {
    .products-grid {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 20px;
    }
    
    .product-image {
        height: 300px;
    }
}
</style>

<div style="text-align: center; padding: 60px 20px 40px; background: linear-gradient(135deg, #F5F5DC 0%, #FAFAF8 100%);">
    <h1 style="font-family: \'Playfair Display\', serif; font-size: 3.5rem; color: #1B1464; margin: 0 0 15px;">Coleção Completa</h1>
    <p style="font-size: 1.375rem; color: #6D4C41; margin: 0;">180 Chapéus Artesanais • Tradição Portuguesa desde 1950</p>
</div>

<div class="products-grid">';

$count = 0;
foreach ($products_html as $prod) {
    $product = wc_get_product($prod->ID);
    if (!$product) continue;
    
    $image_id = get_post_thumbnail_id($prod->ID);
    $image_url = wp_get_attachment_image_url($image_id, 'large');
    
    if (!$image_url) continue;
    
    $title = $prod->post_title;
    $price = $product->get_price_html();
    $link = get_permalink($prod->ID);
    
    $html_content .= '<div class="product-card">
        <div class="product-image">
            <img src="' . esc_url($image_url) . '" alt="' . esc_attr($title) . '" loading="lazy">
        </div>
        <div class="product-info">
            <h3 class="product-title">' . esc_html($title) . '</h3>
            <div class="product-price">' . $price . '</div>
            <a href="' . esc_url($link) . '" class="product-button">Ver Produto</a>
        </div>
    </div>';
    
    $count++;
}

$html_content .= '</div>

<div style="text-align: center; padding: 60px 20px; background: #1B1464; color: white;">
    <h2 style="font-family: \'Playfair Display\', serif; font-size: 2.5rem; color: #FFD700; margin: 0 0 20px;">Chapéus Lisboetas</h2>
    <p style="font-size: 1.125rem; opacity: 0.9; max-width: 600px; margin: 0 auto;">Tradição artesanal portuguesa desde 1950. Cada chapéu é uma obra de arte feita à mão.</p>
</div>';

// Atualizar página teste-html
$test_page = get_page_by_path('teste-html');
if ($test_page) {
    wp_update_post(array(
        'ID' => $test_page->ID,
        'post_content' => $html_content
    ));
    echo "   ✅ Página HTML direta criada com $count produtos\n";
    echo "   ✅ Todas imagens com URLs completas\n";
    echo "   ✅ Grid responsivo CSS puro\n\n";
}

// ============================================================================
// 3. VERIFICAR SE IMAGENS EXISTEM NO SERVIDOR
// ============================================================================

echo "3️⃣ VERIFICANDO IMAGENS NO SERVIDOR...\n\n";

$sample_products = array_slice($products_html, 0, 5);
foreach ($sample_products as $prod) {
    $thumb_id = get_post_thumbnail_id($prod->ID);
    if ($thumb_id) {
        $file_path = get_attached_file($thumb_id);
        $file_exists = file_exists($file_path);
        
        echo "   • " . $prod->post_title . "\n";
        echo "     Ficheiro: " . ($file_exists ? "✅ Existe" : "❌ Não encontrado") . "\n";
        if ($file_exists) {
            $size = filesize($file_path);
            echo "     Tamanho: " . round($size / 1024, 1) . " KB\n";
        }
    }
}

echo "\n";

// ============================================================================
// 4. FORÇAR REGENERAÇÃO DE TODAS THUMBNAILS
// ============================================================================

echo "4️⃣ REGENERANDO TODAS THUMBNAILS...\n\n";

$all_attachments = get_posts(array(
    'post_type' => 'attachment',
    'post_mime_type' => 'image',
    'posts_per_page' => 100,
    'orderby' => 'date',
    'order' => 'DESC'
));

echo "   📊 Total imagens: " . count($all_attachments) . "\n";

require_once(ABSPATH . 'wp-admin/includes/image.php');

$regenerated = 0;
foreach ($all_attachments as $attachment) {
    $file = get_attached_file($attachment->ID);
    if ($file && file_exists($file)) {
        $metadata = wp_generate_attachment_metadata($attachment->ID, $file);
        wp_update_attachment_metadata($attachment->ID, $metadata);
        $regenerated++;
        
        if ($regenerated % 20 == 0) {
            echo "   ⏳ $regenerated regenerados...\n";
        }
    }
}

echo "   ✅ $regenerated thumbnails regenerados\n\n";

// ============================================================================
// 5. LIMPAR TODOS CACHES AGRESSIVAMENTE
// ============================================================================

echo "5️⃣ LIMPANDO CACHES AGRESSIVAMENTE...\n\n";

wp_cache_flush();
wc_delete_product_transients();

global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_transient_%'");
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_site_transient_%'");

// Limpar cache do Flatsome
delete_transient('flatsome_settings');
delete_transient('flatsome_customize_preview');

echo "   ✅ WordPress cache\n";
echo "   ✅ WooCommerce transients\n";
echo "   ✅ Database transients\n";
echo "   ✅ Flatsome cache\n\n";

// ============================================================================
// FINAL
// ============================================================================

echo str_repeat("=", 70) . "\n";
echo "✅ EMERGENCY FIX COMPLETO!\n";
echo str_repeat("=", 70) . "\n\n";

echo "🌐 TESTAR AGORA:\n";
echo "   http://localhost:8080/teste-html\n\n";

echo "📊 RESULTADO:\n";
echo "   • $count produtos com imagens DIRETAS\n";
echo "   • Grid CSS puro (sem shortcodes)\n";
echo "   • Imagens 400px altura\n";
echo "   • URLs completas verificadas\n";
echo "   • $regenerated thumbnails regenerados\n\n";

echo "💡 IMPORTANTE:\n";
echo "   • Fazer HARD REFRESH: Cmd+Shift+R\n";
echo "   • Aguardar 5 segundos para carregar\n";
echo "   • Se ainda não aparecer, problema é no browser cache\n\n";

?>
