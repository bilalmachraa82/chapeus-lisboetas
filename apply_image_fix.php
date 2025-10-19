<?php
/**
 * Aplicar Fix de Imagens Flatsome - Versão Simplificada
 * Adiciona CSS diretamente ao banco de dados
 */

require_once('./wp-load.php');

// CSS Fix
$css_fix = "
/* ========================================================================
   FLATSOME_IMAGE_FIX - Product Images Centering
   Adicionado: " . date('Y-m-d H:i:s') . "
   ======================================================================== */

/* Fix principal - centralizar imagens de produtos */
.product-small .box-image img,
.has-equal-box-heights .box-image img,
.woocommerce ul.products li.product .box-image img {
    object-fit: cover !important;
    object-position: center center !important;
}

/* Fix para produto em hover */
.product-small .box-image .image-cover img {
    object-fit: cover !important;
    object-position: center center !important;
}

/* Fix para thumbnails em widgets e mini cart */
.woocommerce ul.product_list_widget li img,
.widget_shopping_cart .cart_list li img,
.woocommerce-mini-cart-item img {
    object-fit: cover !important;
    object-position: center center !important;
}

/* Fix para produtos relacionados */
.related.products .product-small .box-image img,
.upsells.products .product-small .box-image img {
    object-fit: cover !important;
    object-position: center center !important;
}

/* Fix para grid do Flatsome */
.grid-col .box-image img {
    object-fit: cover !important;
    object-position: center center !important;
}

/* END FLATSOME_IMAGE_FIX */
";

// Pegar CSS atual
$current_css = wp_get_custom_css();

// Verificar se já tem o fix
if (strpos($current_css, 'FLATSOME_IMAGE_FIX') !== false) {
    echo "✅ Fix já aplicado!\n";
    echo "\nAcesse: http://localhost:8080/product-category/boinas/\n";
    exit(0);
}

// Adicionar CSS via opção do tema
$theme_slug = get_stylesheet();
$css_post = wp_get_custom_css_post($theme_slug);

if ($css_post) {
    // Atualizar post existente
    $new_content = $current_css . "\n" . $css_fix;

    global $wpdb;
    $result = $wpdb->update(
        $wpdb->posts,
        array('post_content' => $new_content),
        array('ID' => $css_post->ID),
        array('%s'),
        array('%d')
    );

    if ($result !== false) {
        echo "✅ CSS adicionado com sucesso!\n\n";
        echo "CSS adicionado:\n";
        echo "================\n";
        echo $css_fix . "\n";
        echo "================\n\n";
        echo "PRÓXIMOS PASSOS:\n";
        echo "1. Limpe o cache do navegador (Ctrl+Shift+R)\n";
        echo "2. Teste: http://localhost:8080/product-category/boinas/\n";
        echo "3. Teste: http://localhost:8080/shop/\n";
        echo "4. Se necessário, regenere thumbnails:\n";
        echo "   docker exec -it chapeus_wordpress bash -c \"wp media regenerate --yes --allow-root\"\n";
    } else {
        echo "❌ Erro ao atualizar CSS\n";
    }
} else {
    echo "⚠️ Post de CSS customizado não encontrado\n";
    echo "Criando via opção direta...\n";

    // Criar via update_option como fallback
    global $wpdb;

    $custom_css_option = 'theme_mods_' . $theme_slug;
    $theme_mods = get_option($custom_css_option, array());

    if (!is_array($theme_mods)) {
        $theme_mods = array();
    }

    $theme_mods['custom_css'] = $current_css . "\n" . $css_fix;

    $result = update_option($custom_css_option, $theme_mods);

    if ($result) {
        echo "✅ CSS adicionado via theme mods!\n";
        echo "\nTeste: http://localhost:8080/product-category/boinas/\n";
    } else {
        echo "❌ Erro ao adicionar CSS\n";
    }
}

// Limpar cache
wp_cache_flush();
echo "\n✅ Cache limpo!\n";
