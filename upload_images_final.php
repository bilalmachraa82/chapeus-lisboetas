<?php
/**
 * 📸 Upload FINAL de Imagens - Associar fotos aos produtos
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "📸 UPLOAD DE IMAGENS - INICIANDO...\n\n";

// Carregar JSON com classificação
$json = file_get_contents('/tmp/catalog_completo_classificado.json');
$data = json_decode($json, true);
$products_data = $data['products'] ?? [];

echo "✅ " . count($products_data) . " produtos no catálogo\n\n";

// Listar imagens disponíveis
$images_dir = '/tmp/images';
$images = glob($images_dir . '/*.{jpg,jpeg,png,JPG,JPEG,PNG}', GLOB_BRACE);

echo "✅ " . count($images) . " imagens encontradas\n\n";

// Criar mapa de nome de arquivo -> caminho completo
$image_map = [];
foreach ($images as $img_path) {
    $filename = basename($img_path);
    $image_map[$filename] = $img_path;
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
echo "🚀 FAZENDO UPLOAD E ASSOCIANDO IMAGENS\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n";

$uploaded = 0;
$skipped = 0;
$not_found = 0;

foreach ($products_data as $index => $product_info) {
    // Gerar SKU
    $tipo = $product_info['classification']['tipo'] ?? 'outros';
    $tipo_code = strtoupper(substr(str_replace('-', '', $tipo), 0, 6));
    $sku = sprintf("CL-%s-%04d", $tipo_code, $index + 1);
    
    // Encontrar produto
    $product_id = wc_get_product_id_by_sku($sku);
    
    if (!$product_id) {
        continue;
    }
    
    // Verificar se já tem imagem
    if (has_post_thumbnail($product_id)) {
        $skipped++;
        continue;
    }
    
    // Obter nome do ficheiro original
    $original_filename = basename($product_info['file_path'] ?? '');
    
    if (!$original_filename) {
        $not_found++;
        continue;
    }
    
    // Procurar imagem no mapa
    $image_path = $image_map[$original_filename] ?? null;
    
    if (!$image_path || !file_exists($image_path)) {
        $not_found++;
        continue;
    }
    
    // Upload da imagem
    $upload_file = wp_upload_bits(
        $original_filename,
        null,
        file_get_contents($image_path)
    );
    
    if (!$upload_file['error']) {
        // Criar attachment
        $attachment = array(
            'post_mime_type' => $upload_file['type'],
            'post_title' => $product_info['classification']['nome_produto'] ?? sanitize_file_name($original_filename),
            'post_content' => '',
            'post_status' => 'inherit'
        );
        
        $attach_id = wp_insert_attachment($attachment, $upload_file['file']);
        
        if ($attach_id) {
            // Gerar metadata
            require_once(ABSPATH . 'wp-admin/includes/image.php');
            $attach_data = wp_generate_attachment_metadata($attach_id, $upload_file['file']);
            wp_update_attachment_metadata($attach_id, $attach_data);
            
            // Associar ao produto
            set_post_thumbnail($product_id, $attach_id);
            
            $uploaded++;
            
            if ($uploaded % 20 == 0) {
                echo "   ⏳ $uploaded imagens processadas...\n";
            }
        }
    }
}

echo "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
echo "✅ UPLOAD COMPLETO!\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n";

echo "📊 Resultados:\n";
echo "   • Imagens carregadas: $uploaded\n";
echo "   • Já tinham imagem: $skipped\n";
echo "   • Não encontradas: $not_found\n";
echo "   • Total produtos: " . count($products_data) . "\n\n";

echo "🌐 Verificar loja: http://localhost:8080/shop\n\n";
?>
