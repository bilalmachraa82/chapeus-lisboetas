#!/bin/bash
# Setup completo WordPress + WooCommerce via PHP direto

set -e

echo "🚀 Configurando WordPress completo..."

# Script PHP para instalar WooCommerce
cat > /tmp/install-woocommerce.php << 'EOPHP'
<?php
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🛒 Instalando WooCommerce...\n";

// Incluir funcionalidades de plugins
include_once(ABSPATH . 'wp-admin/includes/plugin-install.php');
include_once(ABSPATH . 'wp-admin/includes/file.php');
include_once(ABSPATH . 'wp-admin/includes/misc.php');
include_once(ABSPATH . 'wp-admin/includes/class-wp-upgrader.php');

// Instalar WooCommerce
$plugin_slug = 'woocommerce';

// Verificar se já está instalado
if (!is_plugin_active('woocommerce/woocommerce.php')) {
    $api = plugins_api('plugin_information', array('slug' => $plugin_slug));
    
    if (is_wp_error($api)) {
        die("❌ Erro ao buscar WooCommerce: " . $api->get_error_message() . "\n");
    }
    
    $upgrader = new Plugin_Upgrader(new WP_Ajax_Upgrader_Skin());
    $result = $upgrader->install($api->download_link);
    
    if (is_wp_error($result)) {
        die("❌ Erro ao instalar: " . $result->get_error_message() . "\n");
    }
    
    // Ativar
    $activate = activate_plugin('woocommerce/woocommerce.php');
    
    if (is_wp_error($activate)) {
        die("❌ Erro ao ativar: " . $activate->get_error_message() . "\n");
    }
    
    echo "✅ WooCommerce instalado e ativado!\n";
} else {
    echo "✅ WooCommerce já está ativo!\n";
}

// Configurar WooCommerce
echo "⚙️  Configurando WooCommerce...\n";

update_option('woocommerce_store_address', 'Rua Exemplo 123');
update_option('woocommerce_store_city', 'Lisboa');
update_option('woocommerce_default_country', 'PT');
update_option('woocommerce_currency', 'EUR');
update_option('woocommerce_currency_pos', 'right_space');
update_option('woocommerce_price_decimal_sep', ',');
update_option('woocommerce_price_thousand_sep', '.');
update_option('woocommerce_price_num_decimals', '2');
update_option('woocommerce_calc_taxes', 'no');
update_option('woocommerce_enable_guest_checkout', 'yes');
update_option('woocommerce_enable_signup_and_login_from_checkout', 'yes');

// Criar páginas WooCommerce se não existirem
$pages = array(
    'shop' => array('name' => 'shop', 'title' => 'Loja', 'content' => ''),
    'cart' => array('name' => 'cart', 'title' => 'Carrinho', 'content' => '[woocommerce_cart]'),
    'checkout' => array('name' => 'checkout', 'title' => 'Finalizar Compra', 'content' => '[woocommerce_checkout]'),
    'myaccount' => array('name' => 'my-account', 'title' => 'Minha Conta', 'content' => '[woocommerce_my_account]'),
);

foreach ($pages as $key => $page) {
    $page_id = get_option('woocommerce_' . $key . '_page_id');
    if (!$page_id || !get_post($page_id)) {
        $page_data = array(
            'post_status' => 'publish',
            'post_type' => 'page',
            'post_name' => $page['name'],
            'post_title' => $page['title'],
            'post_content' => $page['content'],
            'comment_status' => 'closed'
        );
        $page_id = wp_insert_post($page_data);
        update_option('woocommerce_' . $key . '_page_id', $page_id);
        echo "✅ Página criada: {$page['title']}\n";
    }
}

// Configurar permalinks
update_option('permalink_structure', '/%postname%/');
flush_rewrite_rules();

// Habilitar API REST
update_option('woocommerce_api_enabled', 'yes');

echo "✅ Configuração completa!\n";
echo "\n";
echo "════════════════════════════════════════════════════════════\n";
echo "✅ WORDPRESS + WOOCOMMERCE CONFIGURADO!\n";
echo "════════════════════════════════════════════════════════════\n";
echo "\n";
echo "🌐 URLs:\n";
echo "   WordPress: http://localhost:8080\n";
echo "   Admin:     http://localhost:8080/wp-admin\n";
echo "   Loja:      http://localhost:8080/shop\n";
echo "\n";
echo "🔑 Login:\n";
echo "   User: admin\n";
echo "   Pass: ChapeusAdmin2024!\n";
echo "\n";
echo "🎯 Próximo: python3 import_produtos_local.py\n";
echo "\n";
?>
EOPHP

# Executar script PHP no container
docker cp /tmp/install-woocommerce.php chapeus_wordpress:/tmp/
docker exec chapeus_wordpress php /tmp/install-woocommerce.php

echo "✅ Setup completo!"
