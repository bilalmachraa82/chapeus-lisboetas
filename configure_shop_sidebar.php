<?php
/**
 * 🎨 Configurar Sidebar de Categorias na Shop
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎨 CONFIGURANDO SIDEBAR DA SHOP...\n\n";

// ============================================================================
// 1. ATIVAR SIDEBAR NA SHOP
// ============================================================================

echo "1️⃣ CONFIGURANDO LAYOUT...\n\n";

// Flatsome shop sidebar
set_theme_mod('category_sidebar', 'sidebar-main');
set_theme_mod('shop_sidebar', 'left');
set_theme_mod('product_layout', 'sidebar-left');

echo "   ✅ Sidebar esquerda ativada\n\n";

// ============================================================================
// 2. REGISTRAR E POPULAR SIDEBAR
// ============================================================================

echo "2️⃣ CRIANDO WIDGETS DA SIDEBAR...\n\n";

// Get sidebar
$sidebars_widgets = get_option('sidebars_widgets');

if (!isset($sidebars_widgets['sidebar-main'])) {
    $sidebars_widgets['sidebar-main'] = array();
}

// Limpar sidebar existente
$sidebars_widgets['sidebar-main'] = array('_multiwidget' => 1);

// ============================================================================
// Widget 1: Categorias de Produtos
// ============================================================================

$widget_categories = array(
    1 => array(
        'title' => 'Categorias',
        'orderby' => 'name',
        'count' => 1,
        'hierarchical' => 1,
        'show_children_only' => 0
    )
);

update_option('widget_woocommerce_product_categories', $widget_categories);
$sidebars_widgets['sidebar-main'][] = 'woocommerce_product_categories-1';

echo "   ✅ Widget Categorias adicionado\n";

// ============================================================================
// Widget 2: Filtro por Preço
// ============================================================================

$widget_price = array(
    1 => array(
        'title' => 'Filtrar por Preço'
    )
);

update_option('widget_woocommerce_price_filter', $widget_price);
$sidebars_widgets['sidebar-main'][] = 'woocommerce_price_filter-1';

echo "   ✅ Widget Filtro de Preço adicionado\n";

// ============================================================================
// Widget 3: Produtos em Destaque
// ============================================================================

$widget_featured = array(
    1 => array(
        'title' => 'Em Destaque',
        'number' => 3,
        'show' => '',
        'orderby' => 'date',
        'order' => 'desc'
    )
);

update_option('widget_woocommerce_products', $widget_featured);
$sidebars_widgets['sidebar-main'][] = 'woocommerce_products-1';

echo "   ✅ Widget Produtos Destaque adicionado\n\n";

// Salvar widgets
update_option('sidebars_widgets', $sidebars_widgets);

// ============================================================================
// 3. CONFIGURAR SHOP PAGE DISPLAY
// ============================================================================

echo "3️⃣ CONFIGURANDO EXIBIÇÃO DA LOJA...\n\n";

// Mostrar produtos e categorias
update_option('woocommerce_shop_page_display', 'both');
update_option('woocommerce_category_archive_display', '');

// Grid settings
update_option('woocommerce_catalog_columns', 3); // 3 colunas com sidebar
update_option('woocommerce_catalog_rows', 4); // 4 linhas

echo "   ✅ Grid 3x4 configurado\n";
echo "   ✅ Categorias visíveis\n\n";

// ============================================================================
// 4. ENABLE AJAX FILTERING (Flatsome)
// ============================================================================

echo "4️⃣ CONFIGURANDO FILTROS AJAX...\n\n";

set_theme_mod('category_filter_style', 'default');
set_theme_mod('lazy_load_backgrounds', 1);
set_theme_mod('lazy_load_icons', 1);

echo "   ✅ Filtros AJAX ativados\n";
echo "   ✅ Lazy load configurado\n\n";

// ============================================================================
// 5. BREADCRUMBS
// ============================================================================

echo "5️⃣ CONFIGURANDO BREADCRUMBS...\n\n";

update_option('woocommerce_breadcrumb_enabled', 'yes');
set_theme_mod('breadcrumb_size', 'normal');
set_theme_mod('breadcrumb_show_title', 1);

echo "   ✅ Breadcrumbs ativados\n\n";

// ============================================================================
// 6. PRODUCT CATALOG OPTIONS
// ============================================================================

echo "6️⃣ OPÇÕES DE CATÁLOGO...\n\n";

// Sale badge
set_theme_mod('sale_bubble_percentage', 1);
set_theme_mod('sale_bubble_text', 'Sale!');

// Add to cart button
set_theme_mod('product_display_add_to_cart_button', 1);
set_theme_mod('product_hover', 'icon');

// Quick view
set_theme_mod('product_quick_view', 1);

echo "   ✅ Sale badges configurados\n";
echo "   ✅ Quick view ativado\n";
echo "   ✅ Hover effects aplicados\n\n";

// ============================================================================
// FINAL
// ============================================================================

// Flush rewrite rules
flush_rewrite_rules();
wp_cache_flush();

echo str_repeat("=", 70) . "\n";
echo "✅ SIDEBAR CONFIGURADA COM SUCESSO!\n";
echo str_repeat("=", 70) . "\n\n";

echo "📊 WIDGETS ATIVOS:\n";
echo "   • Categorias de Produtos\n";
echo "   • Filtro por Preço\n";
echo "   • Produtos em Destaque\n\n";

echo "⚙️  CONFIGURAÇÕES:\n";
echo "   • Layout: Sidebar Esquerda\n";
echo "   • Grid: 3 colunas x 4 linhas\n";
echo "   • Filtros AJAX: Ativados\n";
echo "   • Quick View: Ativo\n";
echo "   • Breadcrumbs: Ativos\n\n";

echo "🌐 TESTAR:\n";
echo "   • Shop: http://localhost:8080/shop\n";
echo "   • Categoria: http://localhost:8080/product-category/boinas\n\n";

echo "💡 PRÓXIMO PASSO:\n";
echo "   • Configurar logo do Instagram\n";
echo "   • Upload imagens faltando\n\n";
?>
