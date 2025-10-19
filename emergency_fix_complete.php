<?php
/**
 * 🚨 EMERGENCY FIX - CORRIGIR TUDO AGORA!
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🚨 EMERGENCY FIX - CORRIGINDO TUDO!\n\n";
echo str_repeat("=", 70) . "\n\n";

// ============================================================================
// 1. VERIFICAR E RECRIAR PÁGINA SHOP
// ============================================================================

echo "1️⃣ CORRIGINDO PÁGINA SHOP...\n\n";

$shop_page_id = wc_get_page_id('shop');

if ($shop_page_id <= 0) {
    echo "   ⚠️  Página Shop não existe! Criando...\n";
    $shop_page_id = wp_insert_post(array(
        'post_title' => 'Shop',
        'post_name' => 'shop',
        'post_content' => '[products limit="12" columns="4"]',
        'post_status' => 'publish',
        'post_type' => 'page',
        'post_author' => 1
    ));
    update_option('woocommerce_shop_page_id', $shop_page_id);
    echo "   ✅ Shop criada com ID: $shop_page_id\n";
} else {
    echo "   ✅ Shop existe (ID: $shop_page_id)\n";
    
    // Atualizar conteúdo para garantir
    wp_update_post(array(
        'ID' => $shop_page_id,
        'post_content' => '[products limit="12" columns="4"]'
    ));
}

// ============================================================================
// 2. VERIFICAR PRODUTOS PUBLICADOS
// ============================================================================

echo "\n2️⃣ VERIFICANDO PRODUTOS...\n\n";

$args = array(
    'post_type' => 'product',
    'post_status' => 'publish',
    'posts_per_page' => -1,
    'fields' => 'ids'
);

$product_ids = get_posts($args);
$total_products = count($product_ids);

echo "   ✅ Total produtos: $total_products\n";

if ($total_products == 0) {
    echo "\n   ❌ ERRO CRÍTICO: NENHUM PRODUTO ENCONTRADO!\n";
    echo "   Produtos foram apagados ou não existem.\n\n";
    exit(1);
}

// ============================================================================
// 3. FORÇAR VISIBILIDADE DE TODOS OS PRODUTOS
// ============================================================================

echo "\n3️⃣ FORÇANDO VISIBILIDADE DE PRODUTOS...\n\n";

$visible_count = 0;
$featured_count = 0;

foreach ($product_ids as $product_id) {
    $product = wc_get_product($product_id);
    
    if (!$product) continue;
    
    // Remover termos de visibilidade que escondem produto
    wp_remove_object_terms($product_id, array(
        'exclude-from-catalog',
        'exclude-from-search'
    ), 'product_visibility');
    
    // Adicionar termo visible
    wp_set_object_terms($product_id, 'visible', 'product_visibility', true);
    
    // Garantir que está publicado
    if (get_post_status($product_id) != 'publish') {
        wp_update_post(array(
            'ID' => $product_id,
            'post_status' => 'publish'
        ));
    }
    
    $visible_count++;
    
    // Marcar alguns como featured
    if ($featured_count < 12) {
        wp_set_object_terms($product_id, 'featured', 'product_visibility', true);
        $featured_count++;
    }
}

echo "   ✅ $visible_count produtos forçados visíveis\n";
echo "   ✅ $featured_count produtos marcados featured\n";

// ============================================================================
// 4. RE-UPLOAD TODAS AS IMAGENS
// ============================================================================

echo "\n4️⃣ RE-UPLOAD DE IMAGENS...\n\n";

// Carregar JSON
$json_file = '/tmp/catalog_completo_classificado.json';
if (!file_exists($json_file)) {
    echo "   ❌ JSON não encontrado!\n\n";
} else {
    $json = file_get_contents($json_file);
    $data = json_decode($json, true);
    $products_data = $data['products'] ?? array();
    
    // Mapear imagens disponíveis
    $images_dir = '/tmp/images';
    $images = glob($images_dir . '/*.{jpg,jpeg,png,JPG,JPEG,PNG}', GLOB_BRACE);
    
    $image_map = array();
    foreach ($images as $img_path) {
        $filename = basename($img_path);
        $image_map[$filename] = $img_path;
    }
    
    echo "   📸 " . count($images) . " imagens disponíveis\n\n";
    
    $uploaded = 0;
    $skipped = 0;
    
    foreach ($products_data as $index => $product_info) {
        // Gerar SKU
        $tipo = $product_info['classification']['tipo'] ?? 'outros';
        $tipo_code = strtoupper(substr(str_replace('-', '', $tipo), 0, 6));
        $sku = sprintf("CL-%s-%04d", $tipo_code, $index + 1);
        
        // Encontrar produto
        $product_id = wc_get_product_id_by_sku($sku);
        
        if (!$product_id) continue;
        
        // Se já tem imagem, pular
        if (has_post_thumbnail($product_id)) {
            $skipped++;
            continue;
        }
        
        // Obter nome do ficheiro
        $original_filename = basename($product_info['file_path'] ?? '');
        if (!$original_filename) continue;
        
        // Procurar imagem
        $image_path = $image_map[$original_filename] ?? null;
        
        if (!$image_path || !file_exists($image_path)) {
            continue;
        }
        
        // Upload
        $upload_file = wp_upload_bits(
            $original_filename,
            null,
            file_get_contents($image_path)
        );
        
        if (!$upload_file['error']) {
            $attachment = array(
                'post_mime_type' => $upload_file['type'],
                'post_title' => sanitize_file_name($original_filename),
                'post_content' => '',
                'post_status' => 'inherit'
            );
            
            $attach_id = wp_insert_attachment($attachment, $upload_file['file']);
            
            if ($attach_id) {
                require_once(ABSPATH . 'wp-admin/includes/image.php');
                $attach_data = wp_generate_attachment_metadata($attach_id, $upload_file['file']);
                wp_update_attachment_metadata($attach_id, $attach_data);
                
                set_post_thumbnail($product_id, $attach_id);
                $uploaded++;
                
                if ($uploaded % 20 == 0) {
                    echo "   ⏳ $uploaded imagens processadas...\n";
                }
            }
        }
    }
    
    echo "\n   ✅ $uploaded novas imagens carregadas\n";
    echo "   ⚪ $skipped já tinham imagem\n";
}

// ============================================================================
// 5. CONFIGURAR WOOCOMMERCE DISPLAY
// ============================================================================

echo "\n5️⃣ CONFIGURANDO WOOCOMMERCE...\n\n";

// Shop page display
update_option('woocommerce_shop_page_display', '');
update_option('woocommerce_category_archive_display', '');

// Catalog
update_option('woocommerce_catalog_columns', 4);
update_option('woocommerce_catalog_rows', 3);

// Thumbnail regeneration
update_option('woocommerce_thumbnail_image_width', 300);
update_option('woocommerce_thumbnail_image_height', 300);
update_option('woocommerce_thumbnail_cropping', '1:1');

echo "   ✅ Display configurado\n";
echo "   ✅ Catálogo: 4 colunas x 3 linhas\n";
echo "   ✅ Thumbnails: 300x300\n";

// ============================================================================
// 6. PERMALINKS & REWRITE RULES
// ============================================================================

echo "\n6️⃣ ATUALIZANDO PERMALINKS...\n\n";

update_option('permalink_structure', '/%postname%/');

// Force WooCommerce endpoints
delete_option('rewrite_rules');
flush_rewrite_rules(true);

echo "   ✅ Permalinks: /%postname%/\n";
echo "   ✅ Rewrite rules regeneradas\n";

// ============================================================================
// 7. LIMPAR TODOS OS CACHES
// ============================================================================

echo "\n7️⃣ LIMPANDO CACHES...\n\n";

// WordPress
wp_cache_flush();

// WooCommerce
if (function_exists('wc_delete_product_transients')) {
    foreach ($product_ids as $pid) {
        wc_delete_product_transients($pid);
    }
}

// Delete transients
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_transient_%'");
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_site_transient_%'");

echo "   ✅ WordPress cache limpo\n";
echo "   ✅ WooCommerce transients limpos\n";
echo "   ✅ Database transients limpos\n";

// ============================================================================
// 8. CRIAR PÁGINA DE TESTE
// ============================================================================

echo "\n8️⃣ CRIANDO PÁGINA DE TESTE...\n\n";

$test_content = '<h2>Teste de Produtos</h2>

<h3>Shortcode Simples:</h3>
[products limit="8" columns="4"]

<h3>Produtos Recentes:</h3>
[recent_products limit="8" columns="4"]

<h3>Produtos Destaque:</h3>
[featured_products limit="8" columns="4"]

<h3>Categoria Boinas:</h3>
[product_category category="boinas" limit="8"]';

$test_page = get_page_by_path('teste-produtos');
if (!$test_page) {
    wp_insert_post(array(
        'post_title' => 'Teste Produtos',
        'post_name' => 'teste-produtos',
        'post_content' => $test_content,
        'post_status' => 'publish',
        'post_type' => 'page'
    ));
    echo "   ✅ Página de teste criada: /teste-produtos\n";
} else {
    echo "   ⚪ Página de teste já existe\n";
}

// ============================================================================
// 9. ESTATÍSTICAS FINAIS
// ============================================================================

echo "\n9️⃣ ESTATÍSTICAS FINAIS...\n\n";

$with_images = 0;
$without_images = 0;

foreach ($product_ids as $pid) {
    if (has_post_thumbnail($pid)) {
        $with_images++;
    } else {
        $without_images++;
    }
}

echo "   📊 PRODUTOS:\n";
echo "      • Total: $total_products\n";
echo "      • Com imagens: $with_images\n";
echo "      • Sem imagens: $without_images\n";
echo "      • Percentagem: " . round(($with_images / $total_products) * 100, 1) . "%\n";

// ============================================================================
// FINAL
// ============================================================================

echo "\n" . str_repeat("=", 70) . "\n";
echo "✅ EMERGENCY FIX COMPLETO!\n";
echo str_repeat("=", 70) . "\n\n";

echo "🧪 TESTAR AGORA:\n";
echo "   • Shop: http://localhost:8080/shop\n";
echo "   • Teste: http://localhost:8080/teste-produtos\n";
echo "   • Categoria: http://localhost:8080/product-category/boinas\n";
echo "   • Produto: http://localhost:8080/product/boina-patchwork-tweed-multicolor\n\n";

echo "⚠️  SE AINDA NÃO APARECER:\n";
echo "   1. Ctrl+Shift+R no browser (hard refresh)\n";
echo "   2. docker restart chapeus_wordpress\n";
echo "   3. Verificar /teste-produtos\n\n";

?>
