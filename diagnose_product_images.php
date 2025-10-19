<?php
/**
 * Diagnostic Script - Product Image Analysis
 *
 * Usage: Copy to WordPress root and access via browser:
 * http://localhost:8080/diagnose_product_images.php
 */

// Load WordPress
require_once('./wp-load.php');

header('Content-Type: text/html; charset=utf-8');

?>
<!DOCTYPE html>
<html>
<head>
    <title>Diagnóstico de Imagens de Produtos - Boinas</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #0073aa;
            padding-bottom: 10px;
        }
        h2 {
            color: #0073aa;
            margin-top: 30px;
            background: #f0f6fc;
            padding: 10px;
            border-left: 4px solid #0073aa;
        }
        .section {
            margin: 20px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .product-item {
            border: 1px solid #ddd;
            padding: 10px;
            background: white;
            border-radius: 4px;
        }
        .product-item img {
            width: 100%;
            height: auto;
            display: block;
            border: 1px solid #eee;
        }
        .image-info {
            font-size: 12px;
            margin-top: 10px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 3px;
        }
        .code-block {
            background: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        .issue {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        .success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        table th, table td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        table th {
            background: #0073aa;
            color: white;
        }
        .css-property {
            color: #e06c75;
        }
        .css-value {
            color: #98c379;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>Relatório de Diagnóstico: Imagens dos Produtos (Categoria: Boinas)</h1>

    <?php
    // Get Boinas category
    $category = get_term_by('slug', 'boinas', 'product_cat');

    if (!$category) {
        echo '<div class="issue"><strong>ERRO:</strong> Categoria "boinas" não encontrada!</div>';

        // List all product categories
        $all_cats = get_terms(array(
            'taxonomy' => 'product_cat',
            'hide_empty' => false,
        ));

        echo '<h2>Categorias Disponíveis:</h2><ul>';
        foreach ($all_cats as $cat) {
            echo '<li>' . $cat->name . ' (slug: ' . $cat->slug . ')</li>';
        }
        echo '</ul>';

        exit;
    }

    echo '<div class="success"><strong>Categoria encontrada:</strong> ' . $category->name . ' (ID: ' . $category->term_id . ')</div>';

    // Get products in the category
    $args = array(
        'post_type' => 'product',
        'posts_per_page' => 12,
        'tax_query' => array(
            array(
                'taxonomy' => 'product_cat',
                'field' => 'term_id',
                'terms' => $category->term_id,
            ),
        ),
    );

    $products = new WP_Query($args);

    if (!$products->have_posts()) {
        echo '<div class="issue"><strong>AVISO:</strong> Nenhum produto encontrado na categoria "boinas"</div>';
        exit;
    }

    echo '<div class="section">';
    echo '<strong>Total de produtos encontrados:</strong> ' . $products->found_posts;
    echo '</div>';

    // Analyze theme and WooCommerce image settings
    echo '<h2>1. Configurações de Imagens do WooCommerce</h2>';
    echo '<div class="section">';
    echo '<table>';
    echo '<tr><th>Setting</th><th>Value</th></tr>';

    $thumbnail_size = wc_get_image_size('woocommerce_thumbnail');
    echo '<tr><td>Thumbnail Width</td><td>' . $thumbnail_size['width'] . 'px</td></tr>';
    echo '<tr><td>Thumbnail Height</td><td>' . $thumbnail_size['height'] . 'px</td></tr>';
    echo '<tr><td>Thumbnail Crop</td><td>' . ($thumbnail_size['crop'] ? 'Yes' : 'No') . '</td></tr>';

    $single_size = wc_get_image_size('woocommerce_single');
    echo '<tr><td>Single Image Width</td><td>' . $single_size['width'] . 'px</td></tr>';
    echo '<tr><td>Single Image Height</td><td>' . $single_size['height'] . 'px</td></tr>';

    echo '</table>';
    echo '</div>';

    // Analyze theme settings
    echo '<h2>2. Tema Ativo</h2>';
    echo '<div class="section">';
    $theme = wp_get_theme();
    echo '<strong>Tema:</strong> ' . $theme->get('Name') . ' ' . $theme->get('Version') . '<br>';
    if ($theme->parent()) {
        echo '<strong>Tema Pai:</strong> ' . $theme->parent()->get('Name') . '<br>';
    }
    echo '</div>';

    // Analyze first few products
    echo '<h2>3. Análise de Produtos (Primeiros 6)</h2>';

    $count = 0;
    while ($products->have_posts() && $count < 6) {
        $products->the_post();
        $product = wc_get_product(get_the_ID());
        $count++;

        echo '<div class="section">';
        echo '<h3>Produto #' . $count . ': ' . get_the_title() . '</h3>';

        $image_id = $product->get_image_id();

        if ($image_id) {
            $image_meta = wp_get_attachment_metadata($image_id);
            $image_url = wp_get_attachment_url($image_id);
            $thumbnail_url = wp_get_attachment_image_url($image_id, 'woocommerce_thumbnail');

            echo '<table>';
            echo '<tr><th>Property</th><th>Value</th></tr>';
            echo '<tr><td>Image ID</td><td>' . $image_id . '</td></tr>';
            echo '<tr><td>Original Size</td><td>' . ($image_meta['width'] ?? 'N/A') . ' x ' . ($image_meta['height'] ?? 'N/A') . '</td></tr>';
            echo '<tr><td>Full URL</td><td><a href="' . $image_url . '" target="_blank">View</a></td></tr>';
            echo '<tr><td>Thumbnail URL</td><td><a href="' . $thumbnail_url . '" target="_blank">View</a></td></tr>';
            echo '</table>';

            // Show the actual product image HTML as rendered by WooCommerce
            echo '<h4>HTML Renderizado:</h4>';
            echo '<div class="code-block">';
            $image_html = $product->get_image('woocommerce_thumbnail');
            echo htmlentities($image_html);
            echo '</div>';

            // Display the image
            echo '<div class="product-item">';
            echo $image_html;
            echo '<div class="image-info">';
            echo '<strong>Preview:</strong> Como aparece na página<br>';
            echo '<strong>Dimensões declaradas:</strong> ' . ($image_meta['width'] ?? 'N/A') . 'x' . ($image_meta['height'] ?? 'N/A');
            echo '</div>';
            echo '</div>';

        } else {
            echo '<div class="warning">Sem imagem configurada</div>';
        }

        echo '</div>';
    }

    wp_reset_postdata();

    // Check for custom CSS that might affect images
    echo '<h2>4. Análise de CSS Personalizado</h2>';
    echo '<div class="section">';

    $child_theme_css = get_stylesheet_directory() . '/style.css';
    if (file_exists($child_theme_css)) {
        $css_content = file_get_contents($child_theme_css);

        // Look for image-related CSS
        $patterns_to_check = array(
            'object-fit',
            'object-position',
            'background-position',
            'background-size',
            'overflow',
            'max-height',
            'min-height',
            '.product.*img',
            '.woocommerce.*img',
            'thumbnail'
        );

        $found_styles = array();
        foreach ($patterns_to_check as $pattern) {
            if (stripos($css_content, $pattern) !== false) {
                $found_styles[] = $pattern;
            }
        }

        if (!empty($found_styles)) {
            echo '<div class="warning">';
            echo '<strong>Propriedades CSS encontradas no child theme:</strong><br>';
            echo implode(', ', $found_styles);
            echo '</div>';
        } else {
            echo '<div class="success">Nenhuma propriedade CSS customizada encontrada que afete imagens</div>';
        }
    }

    echo '</div>';

    // Recommendations
    echo '<h2>5. Simulação: HTML de Grade de Produtos</h2>';
    echo '<div class="section">';
    echo '<p>Exemplo de como os produtos aparecem na página de categoria:</p>';

    $products->rewind_posts();

    echo '<div class="product-grid">';
    $sim_count = 0;
    while ($products->have_posts() && $sim_count < 6) {
        $products->the_post();
        $product = wc_get_product(get_the_ID());
        $sim_count++;

        echo '<div class="product-item">';
        echo '<a href="' . get_permalink() . '">';
        echo $product->get_image('woocommerce_thumbnail');
        echo '</a>';
        echo '<h4 style="margin: 10px 0; font-size: 14px;">' . get_the_title() . '</h4>';
        echo '<p style="margin: 5px 0; font-weight: bold;">' . $product->get_price_html() . '</p>';
        echo '</div>';
    }
    echo '</div>';

    echo '</div>';

    wp_reset_postdata();

    // CSS Analysis
    echo '<h2>6. Inspeção de Estilos Aplicados</h2>';
    echo '<div class="section">';
    echo '<p>Para identificar o problema de centralização, verifique:</p>';
    echo '<div class="code-block">';
    echo "// No navegador, inspecione um produto e verifique:\n\n";
    echo "1. Elemento img:\n";
    echo "   - object-fit: cover | contain | fill ?\n";
    echo "   - object-position: center | top | bottom ?\n";
    echo "   - max-height / height definidos?\n\n";
    echo "2. Container da imagem:\n";
    echo "   - overflow: hidden?\n";
    echo "   - display: flex? (align-items, justify-content)\n\n";
    echo "3. Classes aplicadas:\n";
    echo "   - .attachment-woocommerce_thumbnail\n";
    echo "   - .wp-post-image\n";
    echo "   - Outras classes do tema\n";
    echo '</div>';
    echo '</div>';

    ?>

    <h2>7. Próximos Passos Recomendados</h2>
    <div class="section">
        <ol>
            <li><strong>Acesse esta página:</strong> <code>http://localhost:8080/diagnose_product_images.php</code></li>
            <li><strong>Abra as Developer Tools</strong> (F12) e inspecione uma imagem de produto acima</li>
            <li><strong>Verifique na aba "Computed"</strong> os valores de:
                <ul>
                    <li>object-fit</li>
                    <li>object-position</li>
                    <li>height / max-height</li>
                    <li>overflow (do container)</li>
                </ul>
            </li>
            <li><strong>Compare</strong> com a página real: <code>http://localhost:8080/product-category/boinas/</code></li>
            <li><strong>Documente</strong> qualquer diferença nos estilos aplicados</li>
        </ol>
    </div>

    <h2>8. Possíveis Causas do Problema</h2>
    <div class="section">
        <div class="issue">
            <strong>Causa #1: object-fit incorreto</strong><br>
            Se <code>object-fit: cover</code> com <code>object-position: top</code>, as imagens mostrarão apenas a parte superior.<br>
            <em>Solução:</em> Alterar para <code>object-position: center</code>
        </div>

        <div class="issue">
            <strong>Causa #2: Container com overflow:hidden e altura fixa</strong><br>
            Se o container tem altura menor que a imagem e overflow:hidden, a imagem será cortada.<br>
            <em>Solução:</em> Ajustar altura do container ou remover overflow:hidden
        </div>

        <div class="issue">
            <strong>Causa #3: Imagens originais mal recortadas</strong><br>
            Se as imagens foram carregadas já cortadas ou com composição descentrada.<br>
            <em>Solução:</em> Regenerar thumbnails ou editar imagens originais
        </div>

        <div class="issue">
            <strong>Causa #4: CSS do tema com background-position incorreto</strong><br>
            Se imagens são aplicadas como background-image em vez de &lt;img&gt;.<br>
            <em>Solução:</em> Alterar background-position para center
        </div>
    </div>

</div>
</body>
</html>
