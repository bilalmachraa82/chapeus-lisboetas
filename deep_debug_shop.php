<?php
/**
 * 🔍 Deep Debug - Descobrir porque produtos não aparecem
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🔍 DEEP DEBUG - SHOP PAGE\n\n";

// 1. Query direta de produtos
echo "1️⃣ QUERY WP_Query (Como WooCommerce faz):\n";

$query_args = array(
    'post_type' => 'product',
    'post_status' => 'publish',
    'posts_per_page' => 12,
    'orderby' => 'date',
    'order' => 'DESC'
);

$loop = new WP_Query($query_args);

echo "   • Found: " . $loop->found_posts . " produtos\n";
echo "   • Post count: " . $loop->post_count . "\n";

if ($loop->have_posts()) {
    echo "   • Primeiros 5 produtos:\n";
    $count = 0;
    while ($loop->have_posts() && $count < 5) {
        $loop->the_post();
        global $product;
        
        $prod_id = get_the_ID();
        $title = get_the_title();
        $price = $product ? $product->get_price() : 'N/A';
        $stock = $product ? $product->get_stock_status() : 'N/A';
        
        echo "      [$prod_id] $title - €$price - Stock: $stock\n";
        $count++;
    }
    wp_reset_postdata();
}

// 2. Verificar template da loja
echo "\n2️⃣ TEMPLATE HIERARCHY:\n";
$shop_page_id = wc_get_page_id('shop');
$template = get_page_template_slug($shop_page_id);
echo "   • Shop page ID: $shop_page_id\n";
echo "   • Template: " . ($template ? $template : 'default') . "\n";

// 3. Verificar se tema suporta WooCommerce
echo "\n3️⃣ THEME SUPPORT:\n";
$theme_support = current_theme_supports('woocommerce');
echo "   • WooCommerce support: " . ($theme_support ? 'YES' : 'NO') . "\n";

if (!$theme_support) {
    echo "   ⚠️  Adicionando suporte WooCommerce ao tema...\n";
    add_theme_support('woocommerce');
}

// 4. Verificar shortcode
echo "\n4️⃣ TESTANDO SHORTCODE [products]:\n";
$shortcode_output = do_shortcode('[products limit="4"]');
$has_products = (strpos($shortcode_output, 'product') !== false);
echo "   • Shortcode funciona: " . ($has_products ? 'YES' : 'NO') . "\n";
if ($has_products) {
    echo "   • Output length: " . strlen($shortcode_output) . " chars\n";
}

// 5. Testar conteúdo da página shop
echo "\n5️⃣ CONTEÚDO DA PÁGINA SHOP:\n";
$shop_page = get_post($shop_page_id);
echo "   • Post content length: " . strlen($shop_page->post_content) . " chars\n";
echo "   • Content: " . substr($shop_page->post_content, 0, 100) . "...\n";

// 6. Verificar se página usa UX Builder
$ux_content = get_post_meta($shop_page_id, '_ux_page_content', true);
echo "\n6️⃣ UX BUILDER:\n";
echo "   • UX Builder ativo: " . ($ux_content ? 'YES' : 'NO') . "\n";

// 7. Verificar taxon omias
echo "\n7️⃣ TAXONOMIES:\n";
$taxonomies = get_object_taxonomies('product');
echo "   • Taxonomies: " . implode(', ', $taxonomies) . "\n";

// 8. Sample product check
echo "\n8️⃣ SAMPLE PRODUCT DETAILED:\n";
$sample = get_posts(array('post_type' => 'product', 'posts_per_page' => 1));
if ($sample) {
    $p = $sample[0];
    $product = wc_get_product($p->ID);
    
    echo "   • ID: " . $p->ID . "\n";
    echo "   • Title: " . $p->post_title . "\n";
    echo "   • Status: " . $p->post_status . "\n";
    echo "   • Type: " . ($product ? $product->get_type() : 'unknown') . "\n";
    echo "   • Price: €" . ($product ? $product->get_price() : '0') . "\n";
    echo "   • Catalogable: " . ($product && $product->is_visible() ? 'YES' : 'NO') . "\n";
    echo "   • Permalink: " . get_permalink($p->ID) . "\n";
}

echo "\n" . str_repeat("=", 70) . "\n";
echo "✅ DEBUG COMPLETO!\n";
echo str_repeat("=", 70) . "\n\n";

// Testar URL direta
echo "🧪 TESTAR URLs:\n";
echo "   • Shop: http://localhost:8080/shop\n";
echo "   • Shop (alt): http://localhost:8080/?post_type=product\n";
if ($sample) {
    echo "   • Produto: " . get_permalink($sample[0]->ID) . "\n";
}
echo "\n";
?>
