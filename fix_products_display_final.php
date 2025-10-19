<?php
/**
 * 🔧 FIX DEFINITIVO - Produtos aparecerem no frontend
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🔧 FIX DEFINITIVO - PRODUTOS NO FRONTEND\n\n";
echo str_repeat("=", 70) . "\n\n";

// ============================================================================
// 1. DIAGNOSTICAR TEMA E PLUGINS
// ============================================================================

echo "1️⃣ DIAGNÓSTICO DO TEMA...\n\n";

$current_theme = wp_get_theme();
echo "   • Tema atual: {$current_theme->get('Name')} {$current_theme->get('Version')}\n";
echo "   • Template: {$current_theme->get('Template')}\n";

// Verificar se WooCommerce está ativo
$active_plugins = get_option('active_plugins');
$wc_active = in_array('woocommerce/woocommerce.php', $active_plugins);
echo "   • WooCommerce: " . ($wc_active ? "✅ Ativo" : "❌ Inativo") . "\n\n";

// ============================================================================
// 2. RECRIAR SHOP PAGE COM TEMPLATE CORRETO
// ============================================================================

echo "2️⃣ RECONFIGURANDO SHOP PAGE...\n\n";

$shop_page_id = wc_get_page_id('shop');

// Forçar template padrão do WooCommerce
update_post_meta($shop_page_id, '_wp_page_template', 'default');

// Remover qualquer conteúdo customizado que possa interferir
$shop_page = get_post($shop_page_id);
if ($shop_page) {
    // Limpar conteúdo - WooCommerce vai renderizar automaticamente
    wp_update_post(array(
        'ID' => $shop_page_id,
        'post_content' => ''
    ));
    
    echo "   ✅ Shop page limpa (ID: $shop_page_id)\n";
    echo "   ✅ Template: default\n";
    echo "   ✅ Conteúdo removido (WooCommerce vai renderizar)\n\n";
}

// ============================================================================
// 3. CONFIGURAR FLATSOME PARA MOSTRAR PRODUTOS
// ============================================================================

echo "3️⃣ CONFIGURANDO FLATSOME...\n\n";

// Desativar UX Builder na shop page
delete_post_meta($shop_page_id, '_ux_page_content');
delete_post_meta($shop_page_id, '_ux_builder_post_status');

// Flatsome shop settings
set_theme_mod('category_sidebar', 'left-sidebar');
set_theme_mod('shop_products_pr_page', 12);
set_theme_mod('shop_grid_products_columns', 4);
set_theme_mod('shop_grid_products_rows', 3);
set_theme_mod('product_display', 'default');

echo "   ✅ UX Builder desativado na shop\n";
echo "   ✅ Sidebar: Esquerda\n";
echo "   ✅ Grid: 4 colunas x 3 linhas\n";
echo "   ✅ Display: Default\n\n";

// ============================================================================
// 4. GARANTIR TODOS PRODUTOS SÃO CONSULTÁVEIS
// ============================================================================

echo "4️⃣ GARANTINDO PRODUTOS VISÍVEIS...\n\n";

global $wpdb;

// Query direta SQL para garantir
$count = $wpdb->query("
    UPDATE {$wpdb->posts} 
    SET post_status = 'publish' 
    WHERE post_type = 'product' 
    AND post_status != 'publish'
");

echo "   ✅ $count produtos atualizados (se necessário)\n";

// Remover todos termos de visibilidade negativos
$product_ids = $wpdb->get_col("
    SELECT ID FROM {$wpdb->posts} 
    WHERE post_type = 'product' 
    AND post_status = 'publish'
");

$fixed = 0;
foreach ($product_ids as $pid) {
    wp_remove_object_terms($pid, array(
        'exclude-from-catalog',
        'exclude-from-search',
        'outofstock'
    ), 'product_visibility');
    
    wp_set_object_terms($pid, 'visible', 'product_visibility', false);
    $fixed++;
}

echo "   ✅ $fixed produtos marcados visíveis\n\n";

// ============================================================================
// 5. REGENERAR REWRITE RULES COMPLETO
// ============================================================================

echo "5️⃣ REGENERANDO REWRITE RULES...\n\n";

// Delete all transients
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '%_transient_%'");

// Flush
delete_option('rewrite_rules');
flush_rewrite_rules(true);

// Regenerar WooCommerce endpoints
WC()->query->init_query_vars();
WC()->query->add_endpoints();
flush_rewrite_rules(true);

echo "   ✅ Transients limpos\n";
echo "   ✅ Rewrite rules regeneradas\n";
echo "   ✅ WooCommerce endpoints recriados\n\n";

// ============================================================================
// 6. TESTAR QUERY DIRETAMENTE
// ============================================================================

echo "6️⃣ TESTANDO QUERY DE PRODUTOS...\n\n";

$test_query = new WP_Query(array(
    'post_type' => 'product',
    'post_status' => 'publish',
    'posts_per_page' => 4,
    'orderby' => 'date',
    'order' => 'DESC'
));

echo "   • Query encontrou: {$test_query->found_posts} produtos\n";
echo "   • Posts retornados: {$test_query->post_count}\n";

if ($test_query->have_posts()) {
    echo "   • Primeiros produtos:\n";
    $i = 0;
    while ($test_query->have_posts() && $i < 3) {
        $test_query->the_post();
        echo "      - " . get_the_title() . "\n";
        $i++;
    }
    wp_reset_postdata();
    echo "   ✅ Query funciona!\n\n";
} else {
    echo "   ❌ Query não retorna posts!\n\n";
}

// ============================================================================
// 7. CRIAR PÁGINA ALTERNATIVA SHOP
// ============================================================================

echo "7️⃣ CRIANDO PÁGINA SHOP ALTERNATIVA...\n\n";

$alt_shop_content = '[section padding="0"]
[ux_products columns="4" ids="' . implode(',', array_slice($product_ids, 0, 12)) . '"]
[/section]';

$alt_page = get_page_by_path('loja');
if (!$alt_page) {
    $alt_id = wp_insert_post(array(
        'post_title' => 'Loja',
        'post_name' => 'loja',
        'post_content' => $alt_shop_content,
        'post_status' => 'publish',
        'post_type' => 'page'
    ));
    echo "   ✅ Página alternativa criada: /loja (ID: $alt_id)\n\n";
} else {
    echo "   ⚪ Página /loja já existe\n\n";
}

// ============================================================================
// 8. FORÇAR TEMPLATE ARCHIVE-PRODUCT.PHP
// ============================================================================

echo "8️⃣ VERIFICANDO TEMPLATE...\n\n";

$theme_root = get_theme_root();
$template_path = $theme_root . '/flatsome/woocommerce/archive-product.php';

if (file_exists($template_path)) {
    echo "   ✅ Template archive-product.php existe\n";
} else {
    echo "   ⚠️  Template não encontrado\n";
}

// Verificar se WooCommerce template files estão ok
$wc_template_path = WC()->plugin_path() . '/templates/archive-product.php';
if (file_exists($wc_template_path)) {
    echo "   ✅ WooCommerce template existe\n";
} else {
    echo "   ⚠️  WooCommerce template não encontrado\n";
}

echo "\n";

// ============================================================================
// 9. CRIAR TESTE HTML DIRETO
// ============================================================================

echo "9️⃣ CRIANDO TESTE HTML DIRETO...\n\n";

$html_test = '<h2>Teste de Produtos (HTML Direto)</h2>
<div class="products row row-small large-columns-4 medium-columns-3 small-columns-2">';

$direct_products = get_posts(array(
    'post_type' => 'product',
    'posts_per_page' => 8,
    'post_status' => 'publish'
));

foreach ($direct_products as $p) {
    $product = wc_get_product($p->ID);
    $image = get_the_post_thumbnail($p->ID, 'woocommerce_thumbnail');
    $price = $product ? $product->get_price_html() : '';
    
    $html_test .= '<div class="product col">
        <div class="product-inner">
            <div class="product-image">' . ($image ? $image : '<img src="https://via.placeholder.com/300" alt="No image">') . '</div>
            <h3 class="product-title">' . $p->post_title . '</h3>
            <div class="price">' . $price . '</div>
            <a href="' . get_permalink($p->ID) . '" class="button">Ver Produto</a>
        </div>
    </div>';
}

$html_test .= '</div>';

$html_page = get_page_by_path('teste-html');
if (!$html_page) {
    wp_insert_post(array(
        'post_title' => 'Teste HTML',
        'post_name' => 'teste-html',
        'post_content' => $html_test,
        'post_status' => 'publish',
        'post_type' => 'page'
    ));
    echo "   ✅ Página teste HTML criada: /teste-html\n\n";
} else {
    wp_update_post(array(
        'ID' => $html_page->ID,
        'post_content' => $html_test
    ));
    echo "   ✅ Página teste HTML atualizada\n\n";
}

// ============================================================================
// 10. LIMPAR TUDO
// ============================================================================

echo "🔟 LIMPEZA FINAL...\n\n";

wp_cache_flush();
wc_delete_shop_order_transients();
wc_delete_product_transients();

echo "   ✅ Todos caches limpos\n\n";

// ============================================================================
// FINAL
// ============================================================================

echo str_repeat("=", 70) . "\n";
echo "✅ FIX COMPLETO!\n";
echo str_repeat("=", 70) . "\n\n";

echo "🧪 TESTAR AGORA (EM ORDEM):\n\n";

echo "1. TESTE HTML (deve funcionar 100%):\n";
echo "   http://localhost:8080/teste-html\n\n";

echo "2. PÁGINA ALTERNATIVA /loja:\n";
echo "   http://localhost:8080/loja\n\n";

echo "3. SHOP OFICIAL:\n";
echo "   http://localhost:8080/shop\n\n";

echo "4. PRODUTOS SHORTCODE:\n";
echo "   http://localhost:8080/teste-produtos\n\n";

echo "5. CATEGORIA:\n";
echo "   http://localhost:8080/product-category/boinas\n\n";

echo "⚠️  IMPORTANTE:\n";
echo "   • Fazer Cmd+Shift+R (hard refresh)\n";
echo "   • Se nada aparecer, problema é TEMA FLATSOME\n";
echo "   • Considerar mudar para tema Twenty Twenty-Four temporariamente\n\n";

echo "📊 RESUMO:\n";
echo "   • " . count($product_ids) . " produtos no sistema\n";
echo "   • Query funciona: " . ($test_query->have_posts() ? "✅" : "❌") . "\n";
echo "   • Template existe: " . (file_exists($template_path) ? "✅" : "❌") . "\n\n";

?>
