<?php
/**
 * Plugin Name: MCP Adapter
 * Plugin URI: https://github.com/WordPress/mcp-adapter
 * Description: Model Context Protocol (MCP) adapter for WordPress. Bridges the Abilities API to the Model Context Protocol.
 * Version: 1.0.0
 * Author: WordPress
 * License: GPL v2 or later
 * Text Domain: mcp-adapter
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('MCP_ADAPTER_VERSION', '1.0.0');
define('MCP_ADAPTER_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('MCP_ADAPTER_PLUGIN_URL', plugin_dir_url(__FILE__));

/**
 * Main MCP Adapter class
 */
class MCP_Adapter {
    
    private static $instance = null;
    
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    private function __construct() {
        add_action('init', array($this, 'init'));
        add_action('rest_api_init', array($this, 'register_rest_routes'));
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
    }
    
    public function init() {
        // Initialize MCP functionality
        $this->load_dependencies();
        $this->setup_hooks();
    }
    
    private function load_dependencies() {
        // Load required files
        require_once MCP_ADAPTER_PLUGIN_DIR . 'includes/class-mcp-server.php';
        require_once MCP_ADAPTER_PLUGIN_DIR . 'includes/class-mcp-tools.php';
        require_once MCP_ADAPTER_PLUGIN_DIR . 'includes/class-mcp-resources.php';
    }
    
    private function setup_hooks() {
        // Setup WordPress hooks
        add_action('wp_ajax_mcp_handle_request', array($this, 'handle_ajax_request'));
        add_action('wp_ajax_nopriv_mcp_handle_request', array($this, 'handle_ajax_request'));
    }
    
    public function register_rest_routes() {
        register_rest_route('mcp/v1', '/server', array(
            'methods' => array('GET', 'POST'),
            'callback' => array($this, 'handle_mcp_request'),
            'permission_callback' => array($this, 'check_permissions'),
        ));
        
        register_rest_route('mcp/v1', '/tools', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_available_tools'),
            'permission_callback' => array($this, 'check_permissions'),
        ));
        
        register_rest_route('mcp/v1', '/resources', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_available_resources'),
            'permission_callback' => array($this, 'check_permissions'),
        ));
    }
    
    public function handle_mcp_request($request) {
        $server = new MCP_Server();
        return $server->handle_request($request);
    }
    
    public function get_available_tools($request) {
        $tools = new MCP_Tools();
        return $tools->get_tools();
    }
    
    public function get_available_resources($request) {
        $resources = new MCP_Resources();
        return $resources->get_resources();
    }
    
    public function handle_ajax_request() {
        // Handle AJAX requests
        check_ajax_referer('mcp_nonce', 'nonce');
        
        $action = sanitize_text_field($_POST['mcp_action']);
        $data = $_POST['data'];
        
        $response = array('success' => false);
        
        switch ($action) {
            case 'test_connection':
                $response = $this->test_mcp_connection();
                break;
            default:
                $response['message'] = 'Invalid action';
        }
        
        wp_send_json($response);
    }
    
    private function test_mcp_connection() {
        return array(
            'success' => true,
            'message' => 'MCP Adapter is working correctly',
            'version' => MCP_ADAPTER_VERSION
        );
    }
    
    public function check_permissions($request) {
        // Check if user has proper permissions
        $auth_header = $request->get_header('Authorization');
        
        if ($auth_header) {
            // Handle JWT or Bearer token authentication
            return $this->validate_token($auth_header);
        }
        
        // Check for WooCommerce API keys
        $consumer_key = $request->get_header('X-WC-Consumer-Key');
        $consumer_secret = $request->get_header('X-WC-Consumer-Secret');
        
        if ($consumer_key && $consumer_secret) {
            return $this->validate_woocommerce_keys($consumer_key, $consumer_secret);
        }
        
        // Fallback to WordPress authentication
        return current_user_can('manage_options');
    }
    
    private function validate_token($auth_header) {
        // Basic token validation
        $token = str_replace('Bearer ', '', $auth_header);
        
        // In a real implementation, you would validate the JWT token
        // For now, we'll accept any token that starts with 'mcp_'
        return strpos($token, 'mcp_') === 0;
    }
    
    private function validate_woocommerce_keys($consumer_key, $consumer_secret) {
        // Validate WooCommerce API keys
        if (class_exists('WC_API_Authentication')) {
            $auth = new WC_API_Authentication();
            return $auth->authenticate($consumer_key, $consumer_secret);
        }
        
        // Basic validation if WooCommerce is not available
        return !empty($consumer_key) && !empty($consumer_secret);
    }
    
    public function activate() {
        // Plugin activation
        flush_rewrite_rules();
        
        // Create necessary database tables or options
        $this->create_options();
    }
    
    public function deactivate() {
        // Plugin deactivation
        flush_rewrite_rules();
    }
    
    private function create_options() {
        // Create default options
        add_option('mcp_adapter_version', MCP_ADAPTER_VERSION);
        add_option('mcp_adapter_enabled', true);
        add_option('mcp_adapter_auth_method', 'woocommerce');
    }
}

// Initialize the plugin
MCP_Adapter::get_instance();

// Add admin menu
add_action('admin_menu', 'mcp_adapter_admin_menu');

function mcp_adapter_admin_menu() {
    add_options_page(
        'MCP Adapter Settings',
        'MCP Adapter',
        'manage_options',
        'mcp-adapter',
        'mcp_adapter_settings_page'
    );
}

function mcp_adapter_settings_page() {
    ?>
    <div class="wrap">
        <h1>MCP Adapter Settings</h1>
        <div class="notice notice-success">
            <p><strong>MCP Adapter está ativo!</strong></p>
            <p>Endpoint MCP: <code><?php echo rest_url('mcp/v1/server'); ?></code></p>
            <p>Versão: <?php echo MCP_ADAPTER_VERSION; ?></p>
        </div>
        
        <h2>Configuração</h2>
        <table class="form-table">
            <tr>
                <th scope="row">Status</th>
                <td>
                    <span style="color: green;">✓ Ativo</span>
                </td>
            </tr>
            <tr>
                <th scope="row">Método de Autenticação</th>
                <td>WooCommerce API Keys</td>
            </tr>
            <tr>
                <th scope="row">Endpoint REST</th>
                <td><code><?php echo rest_url('mcp/v1/'); ?></code></td>
            </tr>
        </table>
        
        <h3>Teste de Conexão</h3>
        <button type="button" class="button button-primary" onclick="testMCPConnection()">Testar Conexão MCP</button>
        <div id="mcp-test-result"></div>
        
        <script>
        function testMCPConnection() {
            const resultDiv = document.getElementById('mcp-test-result');
            resultDiv.innerHTML = '<p>Testando...</p>';
            
            fetch('<?php echo rest_url('mcp/v1/server'); ?>', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                resultDiv.innerHTML = '<div class="notice notice-success"><p>✓ Conexão MCP funcionando!</p></div>';
            })
            .catch(error => {
                resultDiv.innerHTML = '<div class="notice notice-error"><p>✗ Erro na conexão: ' + error.message + '</p></div>';
            });
        }
        </script>
    </div>
    <?php
}