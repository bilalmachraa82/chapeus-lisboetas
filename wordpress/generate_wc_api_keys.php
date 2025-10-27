<?php
/**
 * Script para gerar chaves API do WooCommerce
 */

// Carregar WordPress
require_once('/var/www/html/wp-load.php');

// Verificar se WooCommerce está ativo
if (!class_exists('WooCommerce')) {
    echo "❌ WooCommerce não está ativo!\n";
    exit(1);
}

// Verificar se o usuário tem permissões
if (!current_user_can('manage_woocommerce')) {
    // Fazer login como admin
    $admin_user = get_user_by('login', 'admin');
    if (!$admin_user) {
        $admin_user = get_users(array('role' => 'administrator', 'number' => 1))[0];
    }
    
    if ($admin_user) {
        wp_set_current_user($admin_user->ID);
    }
}

global $wpdb;

// Gerar chaves API
$description = 'MCP Integration - ' . date('Y-m-d H:i:s');
$permissions = 'read_write';
$user_id = 1; // Admin user

// Gerar consumer key e secret
$consumer_key = 'ck_' . wc_rand_hash();
$consumer_secret = 'cs_' . wc_rand_hash();

// Inserir na base de dados
$data = array(
    'user_id' => $user_id,
    'description' => $description,
    'permissions' => $permissions,
    'consumer_key' => wc_api_hash($consumer_key),
    'consumer_secret' => $consumer_secret,
    'nonces' => '',
    'truncated_key' => substr($consumer_key, -7),
    'last_access' => null
);

$table_name = $wpdb->prefix . 'woocommerce_api_keys';

// Verificar se a tabela existe
$table_exists = $wpdb->get_var("SHOW TABLES LIKE '$table_name'") == $table_name;

if (!$table_exists) {
    echo "❌ Tabela de chaves API do WooCommerce não existe. Criando...\n";
    
    // Criar tabela
    $charset_collate = $wpdb->get_charset_collate();
    $sql = "CREATE TABLE $table_name (
        key_id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
        user_id bigint(20) unsigned NOT NULL,
        description varchar(200) NULL,
        permissions varchar(10) NOT NULL,
        consumer_key char(64) NOT NULL,
        consumer_secret char(43) NOT NULL,
        nonces longtext NULL,
        truncated_key char(7) NOT NULL,
        last_access datetime NULL DEFAULT NULL,
        PRIMARY KEY (key_id),
        KEY consumer_key (consumer_key),
        KEY consumer_secret (consumer_secret)
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}

$result = $wpdb->insert($table_name, $data);

if ($result === false) {
    echo "❌ Erro ao criar chaves API: " . $wpdb->last_error . "\n";
    exit(1);
}

echo "✅ Chaves API do WooCommerce criadas com sucesso!\n\n";
echo "📋 INFORMAÇÕES DAS CHAVES API:\n";
echo "================================\n";
echo "Descrição: $description\n";
echo "Permissões: $permissions\n";
echo "Consumer Key: $consumer_key\n";
echo "Consumer Secret: $consumer_secret\n";
echo "================================\n\n";

echo "🔗 ENDPOINT MCP:\n";
echo "URL: " . home_url('/wp-json/mcp/v1/server') . "\n\n";

echo "🔧 CONFIGURAÇÃO PARA CLAUDE CODE:\n";
echo "WP_API_URL=" . home_url('/wp-json') . "\n";
echo "WOO_CUSTOMER_KEY=$consumer_key\n";
echo "WOO_CUSTOMER_SECRET=$consumer_secret\n";
echo "CUSTOM_HEADERS='{\"X-WC-Consumer-Key\":\"$consumer_key\",\"X-WC-Consumer-Secret\":\"$consumer_secret\"}'\n\n";

// Salvar informações num ficheiro
$config_file = '/var/www/html/mcp_config.txt';
$config_content = "# Configuração MCP para WordPress/WooCommerce\n";
$config_content .= "# Gerado em: " . date('Y-m-d H:i:s') . "\n\n";
$config_content .= "WP_API_URL=" . home_url('/wp-json') . "\n";
$config_content .= "WOO_CUSTOMER_KEY=$consumer_key\n";
$config_content .= "WOO_CUSTOMER_SECRET=$consumer_secret\n";
$config_content .= "CUSTOM_HEADERS='{\"X-WC-Consumer-Key\":\"$consumer_key\",\"X-WC-Consumer-Secret\":\"$consumer_secret\"}'\n";
$config_content .= "MCP_ENDPOINT=" . home_url('/wp-json/mcp/v1/server') . "\n";

file_put_contents($config_file, $config_content);
echo "💾 Configuração salva em: $config_file\n";

echo "\n✅ Processo concluído com sucesso!\n";
?>