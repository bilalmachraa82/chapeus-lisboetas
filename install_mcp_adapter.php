<?php
/**
 * Script para instalar e ativar o plugin mcp-adapter no WordPress
 */

// Carregar o WordPress
require_once __DIR__ . '/wp-load.php';

// Verificar se o usuário tem permissões de administrador
if (!current_user_can('install_plugins')) {
    echo "❌ Erro: Você precisa estar logado como administrador para instalar plugins.\n";
    exit(1);
}

echo "🚀 Iniciando instalação do plugin mcp-adapter...\n";

// Incluir as funções necessárias para instalação de plugins
require_once ABSPATH . 'wp-admin/includes/plugin-install.php';
require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/misc.php';
require_once ABSPATH . 'wp-admin/includes/class-wp-upgrader.php';

// Verificar se o plugin já está instalado
$plugin_slug = 'mcp-adapter';
$plugin_file = 'mcp-adapter/mcp-adapter.php';

if (is_plugin_active($plugin_file)) {
    echo "✅ Plugin mcp-adapter já está instalado e ativo!\n";
    exit(0);
}

// Verificar se o plugin está instalado mas não ativo
$installed_plugins = get_plugins();
if (isset($installed_plugins[$plugin_file])) {
    echo "📦 Plugin mcp-adapter já está instalado. Ativando...\n";
    $result = activate_plugin($plugin_file);
    if (is_wp_error($result)) {
        echo "❌ Erro ao ativar o plugin: " . $result->get_error_message() . "\n";
        exit(1);
    } else {
        echo "✅ Plugin mcp-adapter ativado com sucesso!\n";
        exit(0);
    }
}

echo "📥 Baixando e instalando o plugin mcp-adapter...\n";

// Buscar informações do plugin
$api = plugins_api('plugin_information', array(
    'slug' => $plugin_slug,
    'fields' => array(
        'short_description' => false,
        'sections' => false,
        'requires' => false,
        'rating' => false,
        'ratings' => false,
        'downloaded' => false,
        'last_updated' => false,
        'added' => false,
        'tags' => false,
        'compatibility' => false,
        'homepage' => false,
        'donate_link' => false,
    ),
));

if (is_wp_error($api)) {
    echo "❌ Erro ao buscar informações do plugin: " . $api->get_error_message() . "\n";
    echo "ℹ️  Tentando instalar via GitHub...\n";
    
    // Tentar instalar via GitHub
    $github_url = 'https://github.com/WordPress/mcp-adapter/archive/refs/heads/main.zip';
    
    // Criar um upgrader silencioso
    class Silent_Upgrader_Skin extends WP_Upgrader_Skin {
        public function feedback($string, ...$args) {
            // Silenciar output
        }
    }
    
    $upgrader = new Plugin_Upgrader(new Silent_Upgrader_Skin());
    $result = $upgrader->install($github_url);
    
    if (is_wp_error($result)) {
        echo "❌ Erro ao instalar via GitHub: " . $result->get_error_message() . "\n";
        echo "ℹ️  Por favor, instale o plugin manualmente:\n";
        echo "   1. Vá para wp-admin/plugins.php\n";
        echo "   2. Clique em 'Adicionar Novo'\n";
        echo "   3. Procure por 'mcp-adapter'\n";
        echo "   4. Instale e ative o plugin\n";
        exit(1);
    }
} else {
    // Instalar via repositório oficial
    class Silent_Upgrader_Skin extends WP_Upgrader_Skin {
        public function feedback($string, ...$args) {
            // Silenciar output
        }
    }
    
    $upgrader = new Plugin_Upgrader(new Silent_Upgrader_Skin());
    $result = $upgrader->install($api->download_link);
    
    if (is_wp_error($result)) {
        echo "❌ Erro ao instalar o plugin: " . $result->get_error_message() . "\n";
        exit(1);
    }
}

echo "✅ Plugin instalado com sucesso!\n";

// Ativar o plugin
echo "🔌 Ativando o plugin...\n";
$activate_result = activate_plugin($plugin_file);

if (is_wp_error($activate_result)) {
    echo "❌ Erro ao ativar o plugin: " . $activate_result->get_error_message() . "\n";
    exit(1);
}

echo "✅ Plugin mcp-adapter instalado e ativado com sucesso!\n";
echo "🎉 Configuração do MCP Adapter concluída!\n";

// Verificar se o WooCommerce está ativo
if (!is_plugin_active('woocommerce/woocommerce.php')) {
    echo "⚠️  Aviso: WooCommerce não está ativo. Certifique-se de que está instalado e ativo.\n";
} else {
    echo "✅ WooCommerce detectado e ativo!\n";
}

echo "\n📋 Próximos passos:\n";
echo "1. Gerar chaves API do WooCommerce\n";
echo "2. Configurar o MCP no Claude Code\n";
echo "3. Testar a sincronização\n";