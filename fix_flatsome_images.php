<?php
/**
 * Fix Flatsome Product Images Centering Issue
 *
 * Problema: Imagens de produtos mostram apenas a parte superior em vez de centralizadas
 * Causa: Conflito entre object-position e custom crop ratio (43:55) vs containers quadrados
 * Solução: CSS customizado para forçar centralização vertical
 *
 * Usage:
 * 1. Acessar via browser: http://localhost:8080/fix_flatsome_images.php
 * 2. Ou via CLI: docker exec -it chapeus_wordpress php /var/www/html/fix_flatsome_images.php
 */

// Load WordPress
require_once('./wp-load.php');

// Check if running in CLI or browser
$is_cli = php_sapi_name() === 'cli';

if (!$is_cli) {
    header('Content-Type: text/html; charset=utf-8');
    echo '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Fix Flatsome Images</title>';
    echo '<style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .success { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 4px; margin: 15px 0; }
        .error { background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; border-radius: 4px; margin: 15px 0; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 4px; margin: 15px 0; }
        .info { background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; border-radius: 4px; margin: 15px 0; }
        .code { background: #f8f9fa; padding: 15px; border-radius: 4px; font-family: "Courier New", monospace; font-size: 13px; white-space: pre-wrap; margin: 10px 0; border: 1px solid #e9ecef; overflow-x: auto; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; margin-bottom: 20px; }
        h2 { color: #34495e; margin-top: 30px; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        h3 { color: #7f8c8d; }
        .btn { display: inline-block; background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 10px 5px; font-weight: bold; }
        .btn:hover { background: #2980b9; }
        .diagnostic { background: #f8f9fa; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .diagnostic-item { margin: 10px 0; padding: 10px; background: white; border-radius: 4px; }
        .diagnostic-label { font-weight: bold; color: #2c3e50; }
        .diagnostic-value { color: #7f8c8d; margin-left: 10px; }
    </style></head><body><div class="container">';
    echo '<h1>🔧 Fix Flatsome Product Images</h1>';
}

function log_message($message, $type = 'info') {
    global $is_cli;
    if ($is_cli) {
        $prefix = strtoupper($type);
        echo "[$prefix] $message\n";
    } else {
        echo "<div class='$type'>$message</div>";
    }
}

// === DIAGNÓSTICO ===
if (!$is_cli) {
    echo '<h2>📊 Diagnóstico Atual</h2>';
    echo '<div class="diagnostic">';

    // Tema ativo
    $theme = wp_get_theme();
    echo '<div class="diagnostic-item">';
    echo '<span class="diagnostic-label">Tema Ativo:</span>';
    echo '<span class="diagnostic-value">' . $theme->get('Name') . ' v' . $theme->get('Version') . '</span>';
    echo '</div>';

    // Configurações WooCommerce
    $catalog_width = get_option('woocommerce_thumbnail_image_width', 'N/A');
    $catalog_size = get_option('shop_catalog_image_size');
    $thumb_size = get_option('shop_thumbnail_image_size');
    $crop_width = get_option('woocommerce_thumbnail_cropping_custom_width', 'N/A');
    $crop_height = get_option('woocommerce_thumbnail_cropping_custom_height', 'N/A');

    echo '<div class="diagnostic-item">';
    echo '<span class="diagnostic-label">Largura Thumbnail WooCommerce:</span>';
    echo '<span class="diagnostic-value">' . $catalog_width . 'px</span>';
    echo '</div>';

    echo '<div class="diagnostic-item">';
    echo '<span class="diagnostic-label">Crop Customizado:</span>';
    echo '<span class="diagnostic-value">' . $crop_width . ':' . $crop_height . ' (proporção retrato)</span>';
    if ($crop_width == 43 && $crop_height == 55) {
        echo ' <strong style="color: #dc3545;">⚠️ PROBLEMA: Crop vertical em container quadrado!</strong>';
    }
    echo '</div>';

    echo '<div class="diagnostic-item">';
    echo '<span class="diagnostic-label">Catalog Image Size:</span>';
    echo '<span class="diagnostic-value">' . ($catalog_size['width'] ?? 'N/A') . 'x' . ($catalog_size['height'] ?? 'N/A') . 'px</span>';
    echo '</div>';

    echo '</div>';
}

log_message("Iniciando diagnóstico...", 'info');
log_message("Tema: " . wp_get_theme()->get('Name'), 'info');

// Verificar se existe Custom CSS no WordPress Customizer
$custom_css = wp_get_custom_css();
$has_fix = strpos($custom_css, 'FLATSOME_IMAGE_FIX') !== false;

if ($has_fix) {
    log_message("✅ A correção JÁ está aplicada no WordPress Customizer!", 'success');

    if (!$is_cli) {
        echo '<div class="info">';
        echo '<h3>Status: Correção já aplicada</h3>';
        echo '<p>O CSS customizado já está ativo no WordPress Customizer.</p>';
        echo '<p><strong>Próximos passos:</strong></p>';
        echo '<ol>';
        echo '<li>Limpe o cache do navegador (Ctrl+Shift+R ou Cmd+Shift+R)</li>';
        echo '<li>Teste as páginas:</li>';
        echo '<ul>';
        echo '<li><a href="/product-category/boinas/" target="_blank">Categoria Boinas</a></li>';
        echo '<li><a href="/shop/" target="_blank">Loja</a></li>';
        echo '<li><a href="/" target="_blank">Homepage</a></li>';
        echo '</ul>';
        echo '<li>Se ainda houver problemas, considere regenerar thumbnails</li>';
        echo '</ol>';
        echo '</div>';
    }

} else {
    log_message("Correção não encontrada. Preparando para adicionar CSS...", 'info');
}

// CSS Fix específico para Flatsome
$css_fix = "
/* ========================================================================
   FLATSOME_IMAGE_FIX - Product Images Centering
   Adicionado em: " . date('Y-m-d H:i:s') . "

   PROBLEMA: Imagens mostrando apenas topo devido a:
   - Crop customizado 43:55 (vertical) em containers quadrados
   - object-position não centralizado corretamente

   SOLUÇÃO: Forçar centralização vertical das imagens
   ======================================================================== */

/* Fix principal para imagens de produtos em grid */
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

/* Fix para produtos relacionados e upsells */
.related.products .product-small .box-image img,
.upsells.products .product-small .box-image img {
    object-fit: cover !important;
    object-position: center center !important;
}

/* Fix para grid columns do Flatsome */
.grid-col .box-image img {
    object-fit: cover !important;
    object-position: center center !important;
}

/* Garantir que containers mantêm aspect ratio */
.product-small .box-image {
    overflow: hidden;
    position: relative;
}

/* Fix para imagens em quick view */
.mfp-content .product-small .box-image img {
    object-fit: cover !important;
    object-position: center center !important;
}

/* END FLATSOME_IMAGE_FIX */
";

if (!$has_fix) {
    // Adicionar CSS ao WordPress Customizer
    $new_custom_css = $custom_css . "\n" . $css_fix;

    // Usar wp_update_custom_css_post para salvar
    $result = wp_update_custom_css_post(array(
        'css' => $new_custom_css,
    ));

    if (!is_wp_error($result)) {
        log_message("✅ CSS adicionado com sucesso ao WordPress Customizer!", 'success');

        if (!$is_cli) {
            echo '<div class="success">';
            echo '<h3>✅ Correção Aplicada com Sucesso!</h3>';
            echo '<p>O CSS customizado foi adicionado ao WordPress Customizer.</p>';
            echo '</div>';

            echo '<h2>📝 CSS Adicionado:</h2>';
            echo '<div class="code">' . htmlspecialchars($css_fix) . '</div>';

            echo '<h2>🧪 Teste Agora:</h2>';
            echo '<div class="info">';
            echo '<ol>';
            echo '<li><strong>Limpe o cache:</strong> Ctrl+Shift+R (Windows) ou Cmd+Shift+R (Mac)</li>';
            echo '<li><strong>Teste estas páginas:</strong></li>';
            echo '<ul style="margin: 10px 0;">';
            echo '<li><a href="/product-category/boinas/" target="_blank" class="btn">Ver Categoria Boinas</a></li>';
            echo '<li><a href="/shop/" target="_blank" class="btn">Ver Loja</a></li>';
            echo '<li><a href="/" target="_blank" class="btn">Ver Homepage</a></li>';
            echo '</ul>';
            echo '</ol>';
            echo '</div>';

            echo '<h2>🔄 Regenerar Thumbnails (Recomendado)</h2>';
            echo '<div class="warning">';
            echo '<p><strong>Para melhor resultado, regenere os thumbnails:</strong></p>';
            echo '<p>As imagens foram cortadas com proporção 43:55 (vertical) mas os containers são quadrados. Regenerar thumbnails recriará as imagens com crop centralizado.</p>';
            echo '<p><strong>Opção 1 - Via Plugin:</strong></p>';
            echo '<ol>';
            echo '<li>Instale o plugin "Regenerate Thumbnails"</li>';
            echo '<li>Vá em Tools → Regenerate Thumbnails</li>';
            echo '<li>Clique em "Regenerate All Thumbnails"</li>';
            echo '</ol>';
            echo '<p><strong>Opção 2 - Via WP-CLI (mais rápido):</strong></p>';
            echo '<div class="code">docker exec -it chapeus_wordpress bash -c "wp media regenerate --yes --allow-root"</div>';
            echo '</div>';

            echo '<h2>↩️ Reverter (Se Necessário)</h2>';
            echo '<div class="info">';
            echo '<p>Para desfazer esta alteração:</p>';
            echo '<ol>';
            echo '<li>Vá em <strong>Appearance → Customize → Additional CSS</strong></li>';
            echo '<li>Procure por <code>FLATSOME_IMAGE_FIX</code></li>';
            echo '<li>Delete todo o bloco de CSS entre os comentários</li>';
            echo '<li>Clique em "Publish"</li>';
            echo '</ol>';
            echo '</div>';
        }
    } else {
        log_message("❌ Erro ao adicionar CSS: " . $result->get_error_message(), 'error');
    }
}

// Clear cache
if (function_exists('wp_cache_flush')) {
    wp_cache_flush();
    log_message("Cache limpo", 'info');
}

if (!$is_cli) {
    echo '</div></body></html>';
}

log_message("Processo concluído!", 'success');
