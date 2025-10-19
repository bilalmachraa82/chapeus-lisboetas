<?php
/**
 * Importar produtos diretamente no WordPress via PHP
 * Não precisa de REST API - mais rápido e simples!
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

if (!class_exists('WooCommerce')) {
    die("❌ WooCommerce não está instalado!\n");
}

echo "🚀 Importando 180 produtos...\n\n";

// Carregar JSON
$json_file = '/tmp/catalog_completo_classificado.json';
if (!file_exists($json_file)) {
    die("❌ Arquivo não encontrado: $json_file\n");
}

$data = json_decode(file_get_contents($json_file), true);
$products = $data['products'] ?? [];

if (empty($products)) {
    die("❌ Nenhum produto encontrado no JSON\n");
}

echo "✅ " . count($products) . " produtos carregados do JSON\n\n";

$imported = 0;
$failed = 0;
$total = count($products);

foreach ($products as $index => $product_info) {
    $classification = $product_info['classification'] ?? [];
    
    // Dados básicos
    $tipo = $classification['tipo'] ?? 'outros';
    $genero = $classification['genero'] ?? 'unisex';
    $nome = $classification['nome_produto'] ?? "Produto " . ($index + 1);
    $desc_curta = $classification['descricao_curta'] ?? '';
    $desc_longa = $classification['descricao_longa'] ?? '';
    $preco = $classification['preco_sugerido_eur'] ?? 45;
    $stock = $classification['stock_sugerido'] ?? 10;
    $tags = $classification['tags'] ?? [];
    $material = $classification['material_aparente'] ?? '';
    $temporada = $classification['temporada'] ?? '';
    
    // SKU
    $tipo_code = strtoupper(str_replace('-', '', $tipo));
    $tipo_code = substr($tipo_code, 0, 6);
    $sku = sprintf("CL-%s-%04d", $tipo_code, $index + 1);
    
    // Verificar se produto já existe
    $existing = wc_get_product_id_by_sku($sku);
    if ($existing) {
        if (($index + 1) % 20 == 0) {
            echo "⏭️  [$" . ($index + 1) . "/$total] $nome (já existe)\n";
        }
        $imported++;
        continue;
    }
    
    // Criar produto
    $product = new WC_Product_Simple();
    $product->set_name($nome);
    $product->set_sku($sku);
    $product->set_regular_price($preco);
    $product->set_description($desc_longa);
    $product->set_short_description($desc_curta);
    $product->set_manage_stock(true);
    $product->set_stock_quantity($stock);
    $product->set_stock_status('instock');
    $product->set_weight('0.2');
    $product->set_status('publish');
    
    // Salvar produto
    $product_id = $product->save();
    
    if ($product_id) {
        // Adicionar tags
        if (!empty($tags)) {
            $tag_ids = [];
            foreach (array_slice($tags, 0, 5) as $tag) {
                $term = wp_insert_term($tag, 'product_tag');
                if (!is_wp_error($term)) {
                    $tag_ids[] = $term['term_id'];
                }
            }
            if (!empty($tag_ids)) {
                wp_set_object_terms($product_id, $tag_ids, 'product_tag');
            }
        }
        
        // Adicionar atributos
        $attributes = [];
        
        if ($material) {
            $attr = new WC_Product_Attribute();
            $attr->set_name('Material');
            $attr->set_options([ucfirst($material)]);
            $attr->set_visible(true);
            $attributes[] = $attr;
        }
        
        if ($temporada) {
            $attr = new WC_Product_Attribute();
            $attr->set_name('Temporada');
            $attr->set_options([ucfirst($temporada)]);
            $attr->set_visible(true);
            $attributes[] = $attr;
        }
        
        if (!empty($attributes)) {
            $product->set_attributes($attributes);
            $product->save();
        }
        
        $imported++;
        
        // Progresso a cada 10
        if (($index + 1) % 10 == 0) {
            echo "✅ [" . ($index + 1) . "/$total] $nome (€$preco)\n";
        }
    } else {
        $failed++;
        if ($failed <= 5) {
            echo "❌ [" . ($index + 1) . "/$total] Falhou: $nome\n";
        }
    }
    
    // Flush a cada 50 para não sobrecarregar memória
    if (($index + 1) % 50 == 0) {
        wp_cache_flush();
        echo "💾 Checkpoint: $imported importados, $failed falharam\n\n";
    }
}

echo "\n";
echo "════════════════════════════════════════════════════════════\n";
echo "✅ IMPORTAÇÃO COMPLETA!\n";
echo "════════════════════════════════════════════════════════════\n";
echo "\n";
echo "📊 Resultados:\n";
echo "   • Importados: $imported\n";
echo "   • Falharam: $failed\n";
echo "   • Total: $total\n";
echo "   • Taxa sucesso: " . round(($imported/$total)*100, 1) . "%\n";
echo "\n";
echo "🌐 Ver produtos: http://localhost:8080/wp-admin/edit.php?post_type=product\n";
echo "🛒 Ver loja: http://localhost:8080/shop\n";
echo "\n";
?>
