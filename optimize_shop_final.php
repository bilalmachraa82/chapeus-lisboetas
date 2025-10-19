<?php
/**
 * 🎨 OTIMIZAR SHOP - Página Premium sem Repetição
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎨 OTIMIZANDO SHOP - VERSÃO PREMIUM\n\n";
echo str_repeat("=", 70) . "\n\n";

// ============================================================================
// 1. IDENTIFICAR BEST SELLERS (produtos com imagens)
// ============================================================================

echo "1️⃣ IDENTIFICANDO BEST SELLERS...\n\n";

$all_products = get_posts(array(
    'post_type' => 'product',
    'post_status' => 'publish',
    'posts_per_page' => -1,
    'orderby' => 'date',
    'order' => 'DESC'
));

$products_with_images = array();
$products_no_images = array();
$seen = array();

foreach ($all_products as $p) {
    // Evitar duplicados
    if (in_array($p->ID, $seen)) continue;
    $seen[] = $p->ID;
    
    if (has_post_thumbnail($p->ID)) {
        $products_with_images[] = $p->ID;
    } else {
        $products_no_images[] = $p->ID;
    }
}

echo "   ✅ Produtos com imagens: " . count($products_with_images) . "\n";
echo "   ⚠️  Produtos sem imagens: " . count($products_no_images) . "\n\n";

// Marcar primeiros 12 com imagens como featured
$featured_count = 0;
foreach ($products_with_images as $pid) {
    if ($featured_count >= 12) break;
    
    wp_set_object_terms($pid, 'featured', 'product_visibility', true);
    $featured_count++;
}

echo "   ✅ $featured_count produtos marcados como featured\n\n";

// ============================================================================
// 2. CRIAR PÁGINA SHOP PREMIUM
// ============================================================================

echo "2️⃣ CRIANDO PÁGINA SHOP PREMIUM...\n\n";

$premium_shop_content = '
[section bg_color="rgba(250,250,248,1)" padding="60px"]
[row]
[col span="12" align="center"]
<h1 style="font-family: \'Playfair Display\', serif; font-size: 3rem; color: #1B1464; margin-bottom: 10px;">Chapéus Lisboetas</h1>
<p style="font-size: 1.25rem; color: #6D4C41; margin-bottom: 40px;">Tradição Artesanal Portuguesa desde 1950</p>
[/col]
[/row]
[/section]

[section label="Filtros e Produtos" padding="40px"]
[row]

[col span="3" span__sm="12" class="sidebar"]

<div class="widget" style="background: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
<h3 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; font-size: 1.125rem; margin-bottom: 15px; border-bottom: 2px solid #FFD700; padding-bottom: 10px;">📁 Categorias</h3>
<ul style="list-style: none; padding: 0;">
<li style="margin: 8px 0;"><a href="/product-category/boinas" style="color: #6D4C41; text-decoration: none; transition: color 0.3s;">Boinas (81)</a></li>
<li style="margin: 8px 0;"><a href="/product-category/bones" style="color: #6D4C41; text-decoration: none;">Bonés (33)</a></li>
<li style="margin: 8px 0;"><a href="/product-category/bucket-hats" style="color: #6D4C41; text-decoration: none;">Bucket Hats (29)</a></li>
<li style="margin: 8px 0;"><a href="/product-category/capelines" style="color: #6D4C41; text-decoration: none;">Capelines (12)</a></li>
<li style="margin: 8px 0;"><a href="/product-category/fedoras" style="color: #6D4C41; text-decoration: none;">Fedoras (7)</a></li>
<li style="margin: 8px 0;"><a href="/product-category/gorros" style="color: #6D4C41; text-decoration: none;">Gorros (3)</a></li>
<li style="margin: 8px 0;"><a href="/product-category/acessorios" style="color: #6D4C41; text-decoration: none;">Acessórios (13)</a></li>
</ul>
</div>

<div class="widget" style="background: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
<h3 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; font-size: 1.125rem; margin-bottom: 15px; border-bottom: 2px solid #FFD700; padding-bottom: 10px;">💶 Preços</h3>
<p style="margin: 8px 0;"><a href="/shop?min_price=30&max_price=50" style="color: #6D4C41; text-decoration: none;">€30 - €50</a></p>
<p style="margin: 8px 0;"><a href="/shop?min_price=50&max_price=70" style="color: #6D4C41; text-decoration: none;">€50 - €70</a></p>
<p style="margin: 8px 0;"><a href="/shop?min_price=70&max_price=90" style="color: #6D4C41; text-decoration: none;">€70+</a></p>
</div>

<div class="widget" style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); padding: 25px; border-radius: 8px; text-align: center;">
<h3 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; font-size: 1.125rem; margin-bottom: 10px;">🎁 Frete Grátis</h3>
<p style="color: #1B1464; font-size: 0.875rem; margin: 0;">Em compras acima de €75</p>
</div>

[/col]

[col span="9" span__sm="12"]

<div style="margin-bottom: 30px;">
<h2 style="font-family: \'Playfair Display\', serif; color: #1B1464; font-size: 2rem; margin-bottom: 5px;">✨ Em Destaque</h2>
<p style="color: #6D4C41;">Os nossos chapéus mais populares</p>
</div>

[ux_products ids="' . implode(',', array_slice($products_with_images, 0, 12)) . '" columns="3" show_cat="0" show_quick_view="1"]

<div style="margin: 50px 0 30px;">
<h2 style="font-family: \'Playfair Display\', serif; color: #1B1464; font-size: 2rem; margin-bottom: 5px;">🆕 Novidades</h2>
<p style="color: #6D4C41;">Acabaram de chegar</p>
</div>

[ux_products ids="' . implode(',', array_slice($products_with_images, 12, 12)) . '" columns="3" show_cat="0" show_quick_view="1"]

<div style="margin: 50px 0 30px;">
<h2 style="font-family: \'Playfair Display\', serif; color: #1B1464; font-size: 2rem; margin-bottom: 5px;">📦 Mais Produtos</h2>
<p style="color: #6D4C41;">Toda a nossa coleção</p>
</div>

[ux_products ids="' . implode(',', array_slice($products_with_images, 24, 24)) . '" columns="3" show_cat="0" show_quick_view="1"]

[/col]

[/row]
[/section]

[section bg_color="#1B1464" dark="true" padding="60px"]
[row]
[col span="3" span__sm="6" align="center"]
<div style="padding: 20px;">
<div style="font-size: 3rem; margin-bottom: 10px;">🇵🇹</div>
<h3 style="color: #FFD700; font-size: 1.125rem; margin-bottom: 8px;">Artesanato Português</h3>
<p style="color: rgba(255,255,255,0.8); font-size: 0.875rem;">Tradição desde 1950</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 20px;">
<div style="font-size: 3rem; margin-bottom: 10px;">✋</div>
<h3 style="color: #FFD700; font-size: 1.125rem; margin-bottom: 8px;">Feito à Mão</h3>
<p style="color: rgba(255,255,255,0.8); font-size: 0.875rem;">Cada peça é única</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 20px;">
<div style="font-size: 3rem; margin-bottom: 10px;">🚚</div>
<h3 style="color: #FFD700; font-size: 1.125rem; margin-bottom: 8px;">Envio Rápido</h3>
<p style="color: rgba(255,255,255,0.8); font-size: 0.875rem;">Grátis acima de €75</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 20px;">
<div style="font-size: 3rem; margin-bottom: 10px;">🔄</div>
<h3 style="color: #FFD700; font-size: 1.125rem; margin-bottom: 8px;">Devoluções Fáceis</h3>
<p style="color: rgba(255,255,255,0.8); font-size: 0.875rem;">14 dias garantia</p>
</div>
[/col]
[/row]
[/section]
';

// Atualizar página teste-html (que está a funcionar)
$test_html_page = get_page_by_path('teste-html');
if ($test_html_page) {
    wp_update_post(array(
        'ID' => $test_html_page->ID,
        'post_content' => $premium_shop_content,
        'post_title' => 'Loja Premium'
    ));
    echo "   ✅ Página /teste-html atualizada com design premium\n\n";
}

// Também atualizar /loja
$loja_page = get_page_by_path('loja');
if ($loja_page) {
    wp_update_post(array(
        'ID' => $loja_page->ID,
        'post_content' => $premium_shop_content
    ));
    echo "   ✅ Página /loja atualizada\n\n";
}

// ============================================================================
// 3. CRIAR PÁGINA "SHOP" REDIRECIONANDO PARA TESTE-HTML
// ============================================================================

echo "3️⃣ CONFIGURANDO REDIRECIONAMENTO...\n\n";

// Fazer shop apontar para conteúdo premium
$shop_page_id = wc_get_page_id('shop');
if ($shop_page_id) {
    wp_update_post(array(
        'ID' => $shop_page_id,
        'post_content' => $premium_shop_content
    ));
    echo "   ✅ Página /shop atualizada com conteúdo premium\n\n";
}

// ============================================================================
// 4. ATUALIZAR MENU PARA APONTAR PARA PÁGINA QUE FUNCIONA
// ============================================================================

echo "4️⃣ ATUALIZANDO MENU...\n\n";

$menu_name = 'Menu Principal';
$menu_obj = wp_get_nav_menu_object($menu_name);

if ($menu_obj) {
    $menu_items = wp_get_nav_menu_items($menu_obj->term_id);
    
    foreach ($menu_items as $item) {
        if ($item->title == 'Loja' || $item->title == 'Shop') {
            // Atualizar para apontar para teste-html
            wp_update_post(array(
                'ID' => $item->ID,
                'post_title' => 'Loja',
            ));
            update_post_meta($item->ID, '_menu_item_url', home_url('/teste-html'));
        }
    }
    
    echo "   ✅ Menu atualizado para apontar para /teste-html\n\n";
}

// ============================================================================
// 5. CSS ADICIONAL PARA PRODUTOS
// ============================================================================

echo "5️⃣ APLICANDO CSS PREMIUM...\n\n";

$product_css = "
/* Produtos Premium */
.product {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 30px;
}

.product:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(27, 20, 100, 0.15);
}

.product-image {
    position: relative;
    overflow: hidden;
    aspect-ratio: 1/1;
}

.product-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.product:hover .product-image img {
    transform: scale(1.08);
}

.product-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.125rem;
    color: #1B1464;
    margin: 15px 0 10px;
    padding: 0 15px;
    line-height: 1.4;
}

.price {
    font-family: 'Montserrat', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: #FFD700;
    padding: 0 15px 15px;
}

.price del {
    color: #999;
    font-size: 1.125rem;
    margin-right: 8px;
}

.button {
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    color: #1B1464;
    border: none;
    padding: 12px 30px;
    border-radius: 6px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
    font-family: 'Montserrat', sans-serif;
}

.button:hover {
    background: linear-gradient(135deg, #1B1464 0%, #2A1F7D 100%);
    color: #FFD700;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(27, 20, 100, 0.3);
}

/* Sidebar */
.sidebar a:hover {
    color: #FFD700 !important;
    padding-left: 5px;
    transition: all 0.2s;
}

/* Badge Featured */
.featured-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    background: #FFD700;
    color: #1B1464;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    z-index: 10;
}

/* Responsive */
@media (max-width: 768px) {
    .sidebar {
        margin-bottom: 30px;
    }
    
    h1 {
        font-size: 2rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
}
";

// Adicionar ao CSS existente
$existing_css = wp_get_custom_css();
$updated_css = $existing_css . "\n\n/* Premium Shop Styles */\n" . $product_css;
wp_update_custom_css_post($updated_css);

echo "   ✅ CSS premium aplicado\n\n";

// ============================================================================
// 6. LIMPAR CACHES
// ============================================================================

echo "6️⃣ LIMPANDO CACHES...\n\n";

wp_cache_flush();
wc_delete_product_transients();
delete_transient('flatsome_settings');

echo "   ✅ Caches limpos\n\n";

// ============================================================================
// FINAL
// ============================================================================

echo str_repeat("=", 70) . "\n";
echo "✅ SHOP PREMIUM OTIMIZADA!\n";
echo str_repeat("=", 70) . "\n\n";

echo "🎨 MELHORIAS APLICADAS:\n";
echo "   • " . count($products_with_images) . " produtos únicos sem repetição\n";
echo "   • 12 produtos em destaque (com imagens)\n";
echo "   • Sidebar com categorias e filtros\n";
echo "   • Design premium com hover effects\n";
echo "   • Trust badges na footer\n";
echo "   • CSS customizado avançado\n";
echo "   • Layout responsivo mobile\n\n";

echo "🌐 PÁGINAS ATUALIZADAS:\n";
echo "   • /teste-html (PRINCIPAL - funciona)\n";
echo "   • /loja (alternativa)\n";
echo "   • /shop (atualizada)\n\n";

echo "🧪 TESTAR:\n";
echo "   1. http://localhost:8080/teste-html (MELHOR)\n";
echo "   2. http://localhost:8080/shop\n";
echo "   3. http://localhost:8080/loja\n\n";

echo "💡 PRÓXIMOS PASSOS:\n";
echo "   • Hard refresh (Cmd+Shift+R)\n";
echo "   • Verificar produtos sem repetição\n";
echo "   • Testar categorias na sidebar\n";
echo "   • Verificar mobile responsive\n\n";

?>
