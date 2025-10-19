<?php
/**
 * 🔧 Fix Shop Page - Diagnosticar e corrigir produtos não visíveis
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🔧 DIAGNOSTICANDO LOJA...\n\n";

// 1. Verificar produtos
$args = array(
    'post_type' => 'product',
    'posts_per_page' => -1,
    'post_status' => 'publish'
);

$products = get_posts($args);

echo "📦 PRODUTOS:\n";
echo "   • Total: " . count($products) . "\n";

if (count($products) == 0) {
    echo "\n❌ NENHUM PRODUTO ENCONTRADO!\n";
    echo "   Produtos precisam ser reimportados.\n\n";
    exit(1);
}

// 2. Verificar página da loja
$shop_page_id = wc_get_page_id('shop');
if ($shop_page_id > 0) {
    echo "   • Página Shop ID: $shop_page_id\n";
    $shop_page = get_post($shop_page_id);
    echo "   • Status: " . $shop_page->post_status . "\n";
} else {
    echo "   ❌ Página Shop não configurada!\n";
}

// 3. Verificar categorias
$categories = get_terms(array(
    'taxonomy' => 'product_cat',
    'hide_empty' => false
));

echo "\n📁 CATEGORIAS:\n";
echo "   • Total: " . count($categories) . "\n";

// 4. Verificar permalinks
$permalink_structure = get_option('permalink_structure');
echo "\n🔗 PERMALINKS:\n";
echo "   • Estrutura: " . ($permalink_structure ? $permalink_structure : 'Plain (PROBLEMA!)') . "\n";

if (empty($permalink_structure)) {
    echo "\n⚠️  CORRIGINDO PERMALINKS...\n";
    update_option('permalink_structure', '/%postname%/');
    flush_rewrite_rules();
    echo "   ✅ Permalinks atualizados para /%postname%/\n";
}

// 5. Verificar WooCommerce settings
echo "\n⚙️  WOOCOMMERCE SETTINGS:\n";

$options_to_check = array(
    'woocommerce_shop_page_id',
    'woocommerce_cart_page_id',
    'woocommerce_checkout_page_id',
    'woocommerce_myaccount_page_id'
);

foreach ($options_to_check as $option) {
    $value = get_option($option);
    $label = str_replace('woocommerce_', '', str_replace('_page_id', '', $option));
    echo "   • $label: " . ($value ? "ID $value" : "❌ NÃO CONFIGURADO") . "\n";
    
    if (!$value && $option == 'woocommerce_shop_page_id') {
        // Criar página Shop
        $shop_id = wp_insert_post(array(
            'post_title' => 'Shop',
            'post_content' => '',
            'post_status' => 'publish',
            'post_type' => 'page'
        ));
        update_option('woocommerce_shop_page_id', $shop_id);
        echo "   ✅ Página Shop criada (ID: $shop_id)\n";
    }
}

// 6. Flush rewrite rules
echo "\n🔄 ATUALIZANDO REWRITE RULES...\n";
flush_rewrite_rules();
echo "   ✅ Rewrite rules atualizadas\n";

// 7. Verificar visibilidade dos produtos
echo "\n👁️  VISIBILIDADE DOS PRODUTOS:\n";
$visible = 0;
$hidden = 0;

foreach ($products as $product) {
    $terms = wp_get_post_terms($product->ID, 'product_visibility');
    $is_hidden = false;
    
    foreach ($terms as $term) {
        if (in_array($term->slug, array('exclude-from-catalog', 'exclude-from-search'))) {
            $is_hidden = true;
            break;
        }
    }
    
    if ($is_hidden) {
        $hidden++;
        // Remover visibilidade oculta
        wp_remove_object_terms($product->ID, array('exclude-from-catalog', 'exclude-from-search'), 'product_visibility');
    } else {
        $visible++;
    }
}

echo "   • Visíveis: $visible\n";
echo "   • Ocultos (corrigidos): $hidden\n";

// 8. Limpar cache
wp_cache_flush();
echo "\n🗑️  Cache limpo\n";

echo "\n" . str_repeat("=", 70) . "\n";
echo "✅ DIAGNÓSTICO E CORREÇÃO COMPLETOS!\n";
echo str_repeat("=", 70) . "\n";

echo "\n🌐 Testar agora:\n";
echo "   • Shop: http://localhost:8080/shop\n";
echo "   • Produtos: http://localhost:8080/shop (deve mostrar " . count($products) . " produtos)\n\n";
?>
