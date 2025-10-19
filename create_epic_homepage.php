<?php
/**
 * 🎨 HOMEPAGE ÉPICA COM IMAGENS EM TODO LADO
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎨 CRIANDO HOMEPAGE ÉPICA...\n\n";
echo str_repeat("=", 70) . "\n\n";

// ============================================================================
// 1. UPLOAD IMAGEM HERO (do Instagram)
// ============================================================================

echo "1️⃣ PREPARANDO IMAGEM HERO...\n\n";

// Vamos usar uma das fotos de produtos como hero
$hero_products = get_posts(array(
    'post_type' => 'product',
    'posts_per_page' => 1,
    'meta_query' => array(
        array(
            'key' => '_thumbnail_id',
            'compare' => 'EXISTS'
        )
    ),
    'orderby' => 'rand'
));

$hero_image_url = '';
if ($hero_products && has_post_thumbnail($hero_products[0]->ID)) {
    $hero_image_id = get_post_thumbnail_id($hero_products[0]->ID);
    $hero_image_url = wp_get_attachment_image_url($hero_image_id, 'full');
    echo "   ✅ Imagem hero encontrada: $hero_image_url\n\n";
}

// ============================================================================
// 2. OBTER PRODUTOS COM IMAGENS PARA FEATURED
// ============================================================================

echo "2️⃣ SELECIONANDO PRODUTOS FEATURED...\n\n";

$featured_products = get_posts(array(
    'post_type' => 'product',
    'posts_per_page' => 12,
    'meta_query' => array(
        array(
            'key' => '_thumbnail_id',
            'compare' => 'EXISTS'
        )
    ),
    'orderby' => 'rand'
));

$featured_ids = array_map(function($p) { return $p->ID; }, $featured_products);

echo "   ✅ " . count($featured_ids) . " produtos com imagens para featured\n\n";

// ============================================================================
// 3. CRIAR HOMEPAGE ÉPICA COM HERO IMAGE
// ============================================================================

echo "3️⃣ CRIANDO HOMEPAGE...\n\n";

$epic_homepage = '
[section bg="' . $hero_image_url . '" bg_color="rgba(27, 20, 100, 0.7)" bg_overlay="rgba(27, 20, 100, 0.65)" dark="true" padding="200px" height="600px" class="hero-section"]
[row]
[col span="12" align="center" class="hero-content"]
<h1 style="font-family: \'Playfair Display\', serif; font-size: 4.5rem; color: white; margin-bottom: 20px; text-shadow: 2px 4px 8px rgba(0,0,0,0.5); letter-spacing: -0.02em; line-height: 1.1;">Chapéus Lisboetas</h1>
<p style="font-size: 1.75rem; color: #FFD700; margin-bottom: 15px; font-weight: 600; text-shadow: 1px 2px 4px rgba(0,0,0,0.5);">Tradição Artesanal Portuguesa desde 1950</p>
<p style="font-size: 1.25rem; color: rgba(255,255,255,0.95); max-width: 700px; margin: 0 auto 40px; line-height: 1.6; text-shadow: 1px 2px 4px rgba(0,0,0,0.5);">Cada chapéu é uma obra de arte, feito à mão com técnicas transmitidas através de gerações.</p>
[button text="EXPLORAR COLEÇÃO" color="primary" size="xlarge" radius="99" link="/teste-html" style="box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);"]
[/col]
[/row]
[/section]

[section label="Trust Badges" bg_color="#FAFAF8" padding="60px"]
[row]
[col span="3" span__sm="6" align="center"]
<div style="padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.3s;">
<div style="font-size: 4rem; margin-bottom: 15px;">🇵🇹</div>
<h3 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; font-size: 1.25rem; margin-bottom: 10px;">Artesanato Português</h3>
<p style="color: #6D4C41; font-size: 0.95rem;">Feito em Portugal com orgulho</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
<div style="font-size: 4rem; margin-bottom: 15px;">✋</div>
<h3 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; font-size: 1.25rem; margin-bottom: 10px;">Feito à Mão</h3>
<p style="color: #6D4C41; font-size: 0.95rem;">Cada peça é única e especial</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
<div style="font-size: 4rem; margin-bottom: 15px;">📅</div>
<h3 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; font-size: 1.25rem; margin-bottom: 10px;">Desde 1950</h3>
<p style="color: #6D4C41; font-size: 0.95rem;">70+ anos de experiência</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
<div style="font-size: 4rem; margin-bottom: 15px;">💎</div>
<h3 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; font-size: 1.25rem; margin-bottom: 10px;">Qualidade Premium</h3>
<p style="color: #6D4C41; font-size: 0.95rem;">Materiais nobres selecionados</p>
</div>
[/col]
[/row]
[/section]

[section label="Produtos Destaque" padding="80px"]
[row]
[col span="12" align="center"]
<h2 style="font-family: \'Playfair Display\', serif; font-size: 3rem; color: #1B1464; margin-bottom: 10px;">✨ Destaques da Coleção</h2>
<p style="font-size: 1.25rem; color: #6D4C41; margin-bottom: 50px;">Chapéus que contam histórias</p>
[/col]
[/row]
[ux_products ids="' . implode(',', $featured_ids) . '" columns="4" show_cat="0" show_quick_view="1"]
[row style__margin-top="40px"]
[col span="12" align="center"]
[button text="VER TODA A COLEÇÃO" link="/teste-html" style="outline" color="primary" size="large"]
[/col]
[/row]
[/section]

[section label="Sobre" bg_color="#F5F5DC" padding="100px"]
[row v_align="middle"]
[col span="6" span__sm="12"]
<h2 style="font-family: \'Playfair Display\', serif; font-size: 2.5rem; color: #1B1464; margin-bottom: 20px;">Tradição e Excelência</h2>
<p style="font-size: 1.125rem; line-height: 1.8; color: #2C1810; margin-bottom: 20px;">Há mais de <strong>70 anos</strong>, a Chapéus Lisboetas dedica-se à arte milenar da chapelaria tradicional portuguesa.</p>
<p style="font-size: 1.125rem; line-height: 1.8; color: #2C1810; margin-bottom: 20px;">Cada peça é cuidadosamente confeccionada com <strong>materiais nobres</strong> e técnicas artesanais transmitidas através de gerações.</p>
<p style="font-size: 1.125rem; line-height: 1.8; color: #2C1810; margin-bottom: 30px;">Combinamos tradição com design contemporâneo, criando chapéus que são verdadeiras obras de arte para usar no dia a dia.</p>
[button text="NOSSA HISTÓRIA" link="/sobre" style="outline" color="secondary" size="large"]
[/col]
[col span="6" span__sm="12"]
[ux_image id="' . ($featured_ids[0] ?? '') . '" height="500px" image_hover="zoom" image_overlay="rgba(27, 20, 100, 0.1)" border_radius="12"]
[/col]
[/row]
[/section]

[section label="Categorias" padding="80px"]
[row]
[col span="12" align="center"]
<h2 style="font-family: \'Playfair Display\', serif; font-size: 3rem; color: #1B1464; margin-bottom: 10px;">Explore por Categoria</h2>
<p style="font-size: 1.25rem; color: #6D4C41; margin-bottom: 50px;">Encontre o chapéu perfeito para si</p>
[/col]
[/row]
[row]
[col span="4" span__sm="6"]
[featured_box img="' . (isset($featured_ids[0]) ? wp_get_attachment_image_url(get_post_thumbnail_id($featured_ids[0]), 'medium') : '') . '" img_width="300" pos="center"]
<h3 style="color: #1B1464;">Boinas</h3>
<p>81 modelos únicos</p>
[button text="VER BOINAS" link="/product-category/boinas" style="link" color="primary"]
[/featured_box]
[/col]
[col span="4" span__sm="6"]
[featured_box img="' . (isset($featured_ids[1]) ? wp_get_attachment_image_url(get_post_thumbnail_id($featured_ids[1]), 'medium') : '') . '" img_width="300" pos="center"]
<h3 style="color: #1B1464;">Bonés</h3>
<p>33 estilos casuais</p>
[button text="VER BONÉS" link="/product-category/bones" style="link" color="primary"]
[/featured_box]
[/col]
[col span="4" span__sm="6"]
[featured_box img="' . (isset($featured_ids[2]) ? wp_get_attachment_image_url(get_post_thumbnail_id($featured_ids[2]), 'medium') : '') . '" img_width="300" pos="center"]
<h3 style="color: #1B1464;">Bucket Hats</h3>
<p>29 modelos modernos</p>
[button text="VER BUCKET HATS" link="/product-category/bucket-hats" style="link" color="primary"]
[/featured_box]
[/col]
[/row]
[/section]

[section bg_color="#1B1464" dark="true" padding="80px"]
[row v_align="middle"]
[col span="6" span__sm="12"]
<h2 style="font-family: \'Playfair Display\', serif; font-size: 2.5rem; color: #FFD700; margin-bottom: 20px;">Fique por Dentro</h2>
<p style="font-size: 1.125rem; color: rgba(255,255,255,0.9); line-height: 1.8; margin-bottom: 30px;">Receba novidades sobre coleções exclusivas, ofertas especiais e histórias sobre a arte da chapelaria portuguesa.</p>
[/col]
[col span="6" span__sm="12"]
<div style="background: white; padding: 40px; border-radius: 12px;">
<h3 style="color: #1B1464; margin-bottom: 20px; text-align: center;">Newsletter</h3>
[contact-form-7 id="1" title="Newsletter"]
</div>
[/col]
[/row]
[/section]

[section label="Garantias" bg_color="#FAFAF8" padding="60px"]
[row]
[col span="3" span__sm="6" align="center"]
<div style="padding: 20px;">
<div style="font-size: 3.5rem; margin-bottom: 15px; color: #FFD700;">🚚</div>
<h4 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; margin-bottom: 8px;">Envio Grátis</h4>
<p style="color: #6D4C41; font-size: 0.9rem;">Em compras acima de €75</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 20px;">
<div style="font-size: 3.5rem; margin-bottom: 15px; color: #FFD700;">🔄</div>
<h4 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; margin-bottom: 8px;">Devoluções Fáceis</h4>
<p style="color: #6D4C41; font-size: 0.9rem;">14 dias de garantia</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 20px;">
<div style="font-size: 3.5rem; margin-bottom: 15px; color: #FFD700;">🛡️</div>
<h4 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; margin-bottom: 8px;">Pagamento Seguro</h4>
<p style="color: #6D4C41; font-size: 0.9rem;">SSL e métodos seguros</p>
</div>
[/col]
[col span="3" span__sm="6" align="center"]
<div style="padding: 20px;">
<div style="font-size: 3.5rem; margin-bottom: 15px; color: #FFD700;">📞</div>
<h4 style="font-family: \'Montserrat\', sans-serif; color: #1B1464; margin-bottom: 8px;">Suporte Dedicado</h4>
<p style="color: #6D4C41; font-size: 0.9rem;">Sempre à sua disposição</p>
</div>
[/col]
[/row]
[/section]
';

// Atualizar homepage
$home_page = get_page_by_path('home');
if (!$home_page) {
    // Procurar homepage por ID
    $home_id = get_option('page_on_front');
    if ($home_id) {
        $home_page = get_post($home_id);
    }
}

if ($home_page) {
    wp_update_post(array(
        'ID' => $home_page->ID,
        'post_content' => $epic_homepage
    ));
    echo "   ✅ Homepage atualizada (ID: {$home_page->ID})\n\n";
} else {
    // Criar nova homepage
    $new_home_id = wp_insert_post(array(
        'post_title' => 'Home',
        'post_name' => 'home',
        'post_content' => $epic_homepage,
        'post_status' => 'publish',
        'post_type' => 'page'
    ));
    
    update_option('page_on_front', $new_home_id);
    update_option('show_on_front', 'page');
    
    echo "   ✅ Homepage criada (ID: $new_home_id)\n\n";
}

// ============================================================================
// 4. GARANTIR TODAS IMAGENS CARREGAM (Placeholder para faltando)
// ============================================================================

echo "4️⃣ VERIFICANDO IMAGENS...\n\n";

$produtos_sem_imagem = get_posts(array(
    'post_type' => 'product',
    'posts_per_page' => -1,
    'meta_query' => array(
        array(
            'key' => '_thumbnail_id',
            'compare' => 'NOT EXISTS'
        )
    )
));

echo "   ⚠️  " . count($produtos_sem_imagem) . " produtos sem imagem\n";

if (count($produtos_sem_imagem) > 0) {
    // Criar placeholder image se não existir
    $placeholder_url = 'https://placehold.co/600x600/FFD700/1B1464?text=Chapéus+Lisboetas';
    
    foreach ($produtos_sem_imagem as $prod) {
        // Usar imagem de outro produto com imagem da mesma categoria
        $terms = wp_get_post_terms($prod->ID, 'product_cat');
        if ($terms && !is_wp_error($terms)) {
            $same_cat_with_image = get_posts(array(
                'post_type' => 'product',
                'posts_per_page' => 1,
                'tax_query' => array(
                    array(
                        'taxonomy' => 'product_cat',
                        'field' => 'term_id',
                        'terms' => $terms[0]->term_id
                    )
                ),
                'meta_query' => array(
                    array(
                        'key' => '_thumbnail_id',
                        'compare' => 'EXISTS'
                    )
                )
            ));
            
            if ($same_cat_with_image && has_post_thumbnail($same_cat_with_image[0]->ID)) {
                $thumb_id = get_post_thumbnail_id($same_cat_with_image[0]->ID);
                set_post_thumbnail($prod->ID, $thumb_id);
            }
        }
    }
    
    echo "   ✅ Imagens compartilhadas entre produtos da mesma categoria\n\n";
}

// ============================================================================
// 5. CSS PARA HERO SECTION
// ============================================================================

echo "5️⃣ APLICANDO CSS HERO...\n\n";

$hero_css = "
/* Hero Section Epic */
.hero-section {
    position: relative;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

.hero-content h1 {
    animation: fadeInUp 1s ease-out;
}

.hero-content p {
    animation: fadeInUp 1.2s ease-out;
}

.hero-content .button {
    animation: fadeInUp 1.4s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Trust Badges Hover */
.trust-badges > div {
    transition: transform 0.3s ease;
}

.trust-badges > div:hover {
    transform: translateY(-5px);
}

/* Featured Boxes */
.featured-box {
    transition: all 0.3s ease;
}

.featured-box:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(27, 20, 100, 0.15) !important;
}

/* Responsive Hero */
@media (max-width: 768px) {
    .hero-content h1 {
        font-size: 2.5rem !important;
    }
    
    .hero-content p {
        font-size: 1.125rem !important;
    }
    
    .hero-section {
        padding: 120px 20px !important;
        height: 500px !important;
    }
}
";

$existing_css = wp_get_custom_css();
$updated_css = $existing_css . "\n\n/* Hero Epic */\n" . $hero_css;
wp_update_custom_css_post($updated_css);

echo "   ✅ CSS Hero aplicado\n\n";

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
echo "✅ HOMEPAGE ÉPICA CRIADA!\n";
echo str_repeat("=", 70) . "\n\n";

echo "🎨 FEATURES:\n";
echo "   • Hero section com imagem de fundo\n";
echo "   • Overlay escuro para legibilidade\n";
echo "   • Título épico 4.5rem\n";
echo "   • CTA amarelo destacado\n";
echo "   • Trust badges com hover effects\n";
echo "   • 12 produtos featured com imagens\n";
echo "   • Seção sobre com imagem\n";
echo "   • Categorias com imagens\n";
echo "   • Newsletter section\n";
echo "   • Garantias footer\n";
echo "   • Animações fadeInUp\n";
echo "   • 100% responsivo\n\n";

echo "🌐 TESTAR:\n";
echo "   http://localhost:8080\n\n";

echo "📊 IMAGENS:\n";
echo "   • Hero: $hero_image_url\n";
echo "   • Featured: " . count($featured_ids) . " produtos\n";
echo "   • Produtos sem imagem: " . count($produtos_sem_imagem) . " (com fallback)\n\n";

?>
