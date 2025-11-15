<?php
/**
 * Script para importar produtos faltantes do CSV via WP-CLI
 * Uso: wp eval-file import_missing_products.php --allow-root
 */

if (!defined('WP_CLI')) {
    die('Este script deve ser executado via WP-CLI');
}

// Função para limpar e normalizar texto
function clean_text($text) {
    return trim(str_replace(["\r", "\n"], ' ', $text));
}

// Caminho do CSV
$csv_file = '/tmp/missing.csv';

if (!file_exists($csv_file)) {
    WP_CLI::error("CSV não encontrado: $csv_file");
}

WP_CLI::log("Lendo CSV: $csv_file");

// Ler CSV
$handle = fopen($csv_file, 'r');
if (!$handle) {
    WP_CLI::error("Não foi possível abrir o CSV");
}

// Ler header
$header = fgetcsv($handle);
if (!$header) {
    WP_CLI::error("CSV vazio ou inválido");
}

// Encontrar índices das colunas
$sku_col = array_search('SKU', $header);
$name_col = array_search('Name', $header);
$price_col = array_search('Regular price', $header);
$categories_col = array_search('Categories', $header);
$desc_col = array_search('Description', $header);
$short_desc_col = array_search('Short description', $header);
$images_col = array_search('Images', $header);
$stock_col = array_search('In stock?', $header);

if ($sku_col === false || $name_col === false || $price_col === false) {
    WP_CLI::error("Colunas obrigatórias não encontradas no CSV");
}

WP_CLI::log("Colunas mapeadas: SKU=$sku_col, Name=$name_col, Price=$price_col");

$imported = 0;
$skipped = 0;
$errors = 0;

// Processar linhas
while (($row = fgetcsv($handle)) !== false) {
    // Garantir que a linha tem todas as colunas
    if (count($row) < count($header)) {
        continue;
    }

    $sku = clean_text($row[$sku_col]);
    $name = clean_text($row[$name_col]);
    $price = clean_text($row[$price_col]);

    // Validar dados básicos
    if (empty($sku) || empty($price) || strpos($price, 'Tag') !== false) {
        continue;
    }

    // Verificar se produto já existe
    $existing_id = wc_get_product_id_by_sku($sku);
    if ($existing_id) {
        $skipped++;
        continue;
    }

    try {
        // Criar produto
        $product = new WC_Product_Simple();
        $product->set_sku($sku);
        $product->set_name($name);
        $product->set_regular_price($price);

        // Descrição
        if ($desc_col !== false && !empty($row[$desc_col])) {
            $product->set_description(clean_text($row[$desc_col]));
        }

        // Descrição curta
        if ($short_desc_col !== false && !empty($row[$short_desc_col])) {
            $product->set_short_description(clean_text($row[$short_desc_col]));
        }

        // Categorias
        if ($categories_col !== false && !empty($row[$categories_col])) {
            $categories = explode('>', $row[$categories_col]);
            $cat_ids = [];
            foreach ($categories as $cat_name) {
                $cat_name = trim($cat_name);
                $term = get_term_by('name', $cat_name, 'product_cat');
                if ($term) {
                    $cat_ids[] = $term->term_id;
                }
            }
            if (!empty($cat_ids)) {
                $product->set_category_ids($cat_ids);
            }
        }

        // Estoque
        if ($stock_col !== false) {
            $in_stock = clean_text($row[$stock_col]);
            if ($in_stock === '1' || strtolower($in_stock) === 'yes') {
                $product->set_stock_status('instock');
            } else {
                $product->set_stock_status('outofstock');
            }
        }

        // Salvar produto
        $product_id = $product->save();

        if ($product_id) {
            WP_CLI::success("Importado: $sku - $name (ID: $product_id)");
            $imported++;
        } else {
            WP_CLI::warning("Falha ao salvar: $sku - $name");
            $errors++;
        }

    } catch (Exception $e) {
        WP_CLI::warning("Erro ao importar $sku: " . $e->getMessage());
        $errors++;
    }
}

fclose($handle);

WP_CLI::log("\n" . str_repeat('=', 60));
WP_CLI::success("Importação concluída!");
WP_CLI::log("Importados: $imported");
WP_CLI::log("Ignorados (já existem): $skipped");
WP_CLI::log("Erros: $errors");
WP_CLI::log(str_repeat('=', 60));
