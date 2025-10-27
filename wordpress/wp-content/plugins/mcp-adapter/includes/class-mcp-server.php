<?php
/**
 * MCP Server class
 * Handles Model Context Protocol server functionality
 */

if (!defined('ABSPATH')) {
    exit;
}

class MCP_Server {
    
    private $version = '2024-11-05';
    
    public function __construct() {
        // Initialize server
    }
    
    public function handle_request($request) {
        $method = $request->get_method();
        $body = $request->get_json_params();
        
        if ($method === 'POST') {
            return $this->handle_jsonrpc_request($body);
        } else {
            return $this->get_server_info();
        }
    }
    
    private function handle_jsonrpc_request($body) {
        if (!isset($body['jsonrpc']) || $body['jsonrpc'] !== '2.0') {
            return new WP_Error('invalid_request', 'Invalid JSON-RPC request');
        }
        
        $method = $body['method'] ?? '';
        $params = $body['params'] ?? array();
        $id = $body['id'] ?? null;
        
        switch ($method) {
            case 'initialize':
                return $this->initialize($params, $id);
            case 'tools/list':
                return $this->list_tools($id);
            case 'tools/call':
                return $this->call_tool($params, $id);
            case 'resources/list':
                return $this->list_resources($id);
            case 'resources/read':
                return $this->read_resource($params, $id);
            default:
                return $this->error_response('method_not_found', 'Method not found', $id);
        }
    }
    
    private function initialize($params, $id) {
        return array(
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => array(
                'protocolVersion' => $this->version,
                'capabilities' => array(
                    'tools' => array(),
                    'resources' => array(
                        'subscribe' => true,
                        'listChanged' => true
                    )
                ),
                'serverInfo' => array(
                    'name' => 'WordPress MCP Adapter',
                    'version' => MCP_ADAPTER_VERSION
                )
            )
        );
    }
    
    private function list_tools($id) {
        $tools = new MCP_Tools();
        $available_tools = $tools->get_tools();
        
        return array(
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => array(
                'tools' => $available_tools
            )
        );
    }
    
    private function call_tool($params, $id) {
        $tool_name = $params['name'] ?? '';
        $arguments = $params['arguments'] ?? array();
        
        $tools = new MCP_Tools();
        $result = $tools->call_tool($tool_name, $arguments);
        
        return array(
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => $result
        );
    }
    
    private function list_resources($id) {
        $resources = new MCP_Resources();
        $available_resources = $resources->get_resources();
        
        return array(
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => array(
                'resources' => $available_resources
            )
        );
    }
    
    private function read_resource($params, $id) {
        $uri = $params['uri'] ?? '';
        
        $resources = new MCP_Resources();
        $content = $resources->read_resource($uri);
        
        return array(
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => array(
                'contents' => $content
            )
        );
    }
    
    private function error_response($code, $message, $id = null) {
        return array(
            'jsonrpc' => '2.0',
            'id' => $id,
            'error' => array(
                'code' => $code,
                'message' => $message
            )
        );
    }
    
    private function get_server_info() {
        return array(
            'name' => 'WordPress MCP Adapter',
            'version' => MCP_ADAPTER_VERSION,
            'protocol_version' => $this->version,
            'status' => 'active',
            'endpoints' => array(
                'server' => rest_url('mcp/v1/server'),
                'tools' => rest_url('mcp/v1/tools'),
                'resources' => rest_url('mcp/v1/resources')
            )
        );
    }
}