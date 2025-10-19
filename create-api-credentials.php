<?php
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🔑 Criando credenciais API WooCommerce...\n\n";

// Gerar Consumer Key e Consumer Secret
$user_id = 1; // Admin user

// Criar API key no WooCommerce
global $wpdb;

// Verificar se WooCommerce está ativo
if (!class_exists('WooCommerce')) {
    die("❌ WooCommerce não está instalado!\n");
}

// Dados da API Key
$consumer_key = 'ck_' . wp_generate_password(40, false);
$consumer_secret = 'cs_' . wp_generate_password(40, false);

// Inserir na tabela de keys do WooCommerce
$table_name = $wpdb->prefix . 'woocommerce_api_keys';

$data = array(
    'user_id' => $user_id,
    'description' => 'Import Script - Auto Generated',
    'permissions' => 'read_write',
    'consumer_key' => wc_api_hash($consumer_key),
    'consumer_secret' => $consumer_secret,
    'truncated_key' => substr($consumer_key, -7),
);

$wpdb->insert($table_name, $data);

if ($wpdb->insert_id) {
    echo "✅ Credenciais API criadas com sucesso!\n\n";
    echo "════════════════════════════════════════════════════════════\n";
    echo "🔑 CREDENCIAIS WOOCOMMERCE REST API:\n";
    echo "════════════════════════════════════════════════════════════\n\n";
    echo "Consumer Key:\n";
    echo $consumer_key . "\n\n";
    echo "Consumer Secret:\n";
    echo $consumer_secret . "\n\n";
    echo "════════════════════════════════════════════════════════════\n\n";
    echo "📝 Copiar estas credenciais para import_produtos_local.py:\n\n";
    echo "WC_CONSUMER_KEY = \"$consumer_key\"\n";
    echo "WC_CONSUMER_SECRET = \"$consumer_secret\"\n\n";
} else {
    echo "❌ Erro ao criar credenciais: " . $wpdb->last_error . "\n";
}
?>
