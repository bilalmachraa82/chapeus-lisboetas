<?php
/**
 * MCP Tools class
 * Handles WordPress and WooCommerce tools for MCP
 */

if (!defined('ABSPATH')) {
    exit;
}

class MCP_Tools {
    
    public function __construct() {
        // Initialize tools
    }
    
    public function get_tools() {
        $tools = array();
        
        // WordPress tools
        $tools[] = array(
            'name' => 'get_posts',
            'description' => 'Get WordPress posts',
            'inputSchema' => array(
                'type' => 'object',
                'properties' => array(
                    'post_type' => array(
                        'type' => 'string',
                        'description' => 'Post type to retrieve',
                        'default' => 'post'
                    ),
                    'posts_per_page' => array(
                        'type' => 'number',
                        'description' => 'Number of posts to retrieve',
                        'default' => 10
                    ),
                    'post_status' => array(
                        'type' => 'string',
                        'description' => 'Post status',
                        'default' => 'publish'
                    )
                )
            )
        );
        
        $tools[] = array(
            'name' => 'create_post',
            'description' => 'Create a new WordPress post',
            'inputSchema' => array(
                'type' => 'object',
                'properties' => array(
                    'title' => array(
                        'type' => 'string',
                        'description' => 'Post title'
                    ),
                    'content' => array(
                        'type' => 'string',
                        'description' => 'Post content'
                    ),
                    'post_type' => array(
                        'type' => 'string',
                        'description' => 'Post type',
                        'default' => 'post'
                    ),
                    'post_status' => array(
                        'type' => 'string',
                        'description' => 'Post status',
                        'default' => 'draft'
                    )
                ),
                'required' => array('title', 'content')
            )
        );
        
        // WooCommerce tools (if WooCommerce is active)
        if (class_exists('WooCommerce')) {
            $tools[] = array(
                'name' => 'get_products',
                'description' => 'Get WooCommerce products',
                'inputSchema' => array(
                    'type' => 'object',
                    'properties' => array(
                        'per_page' => array(
                            'type' => 'number',
                            'description' => 'Number of products to retrieve',
                            'default' => 10
                        ),
                        'status' => array(
                            'type' => 'string',
                            'description' => 'Product status',
                            'default' => 'publish'
                        ),
                        'category' => array(
                            'type' => 'string',
                            'description' => 'Product category slug'
                        )
                    )
                )
            );
            
            $tools[] = array(
                'name' => 'create_product',
                'description' => 'Create a new WooCommerce product',
                'inputSchema' => array(
                    'type' => 'object',
                    'properties' => array(
                        'name' => array(
                            'type' => 'string',
                            'description' => 'Product name'
                        ),
                        'description' => array(
                            'type' => 'string',
                            'description' => 'Product description'
                        ),
                        'regular_price' => array(
                            'type' => 'string',
                            'description' => 'Product regular price'
                        ),
                        'sale_price' => array(
                            'type' => 'string',
                            'description' => 'Product sale price'
                        ),
                        'sku' => array(
                            'type' => 'string',
                            'description' => 'Product SKU'
                        ),
                        'stock_quantity' => array(
                            'type' => 'number',
                            'description' => 'Stock quantity'
                        )
                    ),
                    'required' => array('name', 'regular_price')
                )
            );
            
            $tools[] = array(
                'name' => 'update_product',
                'description' => 'Update a WooCommerce product',
                'inputSchema' => array(
                    'type' => 'object',
                    'properties' => array(
                        'product_id' => array(
                            'type' => 'number',
                            'description' => 'Product ID to update'
                        ),
                        'name' => array(
                            'type' => 'string',
                            'description' => 'Product name'
                        ),
                        'description' => array(
                            'type' => 'string',
                            'description' => 'Product description'
                        ),
                        'regular_price' => array(
                            'type' => 'string',
                            'description' => 'Product regular price'
                        ),
                        'sale_price' => array(
                            'type' => 'string',
                            'description' => 'Product sale price'
                        ),
                        'stock_quantity' => array(
                            'type' => 'number',
                            'description' => 'Stock quantity'
                        )
                    ),
                    'required' => array('product_id')
                )
            );
        }
        
        return $tools;
    }
    
    public function call_tool($tool_name, $arguments) {
        switch ($tool_name) {
            case 'get_posts':
                return $this->get_posts($arguments);
            case 'create_post':
                return $this->create_post($arguments);
            case 'get_products':
                return $this->get_products($arguments);
            case 'create_product':
                return $this->create_product($arguments);
            case 'update_product':
                return $this->update_product($arguments);
            default:
                return array(
                    'isError' => true,
                    'content' => array(
                        array(
                            'type' => 'text',
                            'text' => 'Tool not found: ' . $tool_name
                        )
                    )
                );
        }
    }
    
    private function get_posts($args) {
        $posts = get_posts(array(
            'post_type' => $args['post_type'] ?? 'post',
            'numberposts' => $args['posts_per_page'] ?? 10,
            'post_status' => $args['post_status'] ?? 'publish'
        ));
        
        $result = array();
        foreach ($posts as $post) {
            $result[] = array(
                'id' => $post->ID,
                'title' => $post->post_title,
                'content' => $post->post_content,
                'excerpt' => $post->post_excerpt,
                'date' => $post->post_date,
                'status' => $post->post_status,
                'url' => get_permalink($post->ID)
            );
        }
        
        return array(
            'content' => array(
                array(
                    'type' => 'text',
                    'text' => 'Found ' . count($result) . ' posts: ' . json_encode($result, JSON_PRETTY_PRINT)
                )
            )
        );
    }
    
    private function create_post($args) {
        $post_data = array(
            'post_title' => $args['title'],
            'post_content' => $args['content'],
            'post_type' => $args['post_type'] ?? 'post',
            'post_status' => $args['post_status'] ?? 'draft'
        );
        
        $post_id = wp_insert_post($post_data);
        
        if (is_wp_error($post_id)) {
            return array(
                'isError' => true,
                'content' => array(
                    array(
                        'type' => 'text',
                        'text' => 'Error creating post: ' . $post_id->get_error_message()
                    )
                )
            );
        }
        
        return array(
            'content' => array(
                array(
                    'type' => 'text',
                    'text' => 'Post created successfully with ID: ' . $post_id
                )
            )
        );
    }
    
    private function get_products($args) {
        if (!class_exists('WooCommerce')) {
            return array(
                'isError' => true,
                'content' => array(
                    array(
                        'type' => 'text',
                        'text' => 'WooCommerce is not active'
                    )
                )
            );
        }
        
        $query_args = array(
            'limit' => $args['per_page'] ?? 10,
            'status' => $args['status'] ?? 'publish'
        );
        
        if (isset($args['category'])) {
            $query_args['category'] = $args['category'];
        }
        
        $products = wc_get_products($query_args);
        $result = array();
        
        foreach ($products as $product) {
            $result[] = array(
                'id' => $product->get_id(),
                'name' => $product->get_name(),
                'sku' => $product->get_sku(),
                'price' => $product->get_price(),
                'regular_price' => $product->get_regular_price(),
                'sale_price' => $product->get_sale_price(),
                'stock_quantity' => $product->get_stock_quantity(),
                'stock_status' => $product->get_stock_status(),
                'status' => $product->get_status()
            );
        }
        
        return array(
            'content' => array(
                array(
                    'type' => 'text',
                    'text' => 'Found ' . count($result) . ' products: ' . json_encode($result, JSON_PRETTY_PRINT)
                )
            )
        );
    }
    
    private function create_product($args) {
        if (!class_exists('WooCommerce')) {
            return array(
                'isError' => true,
                'content' => array(
                    array(
                        'type' => 'text',
                        'text' => 'WooCommerce is not active'
                    )
                )
            );
        }
        
        $product = new WC_Product_Simple();
        $product->set_name($args['name']);
        $product->set_regular_price($args['regular_price']);
        
        if (isset($args['description'])) {
            $product->set_description($args['description']);
        }
        
        if (isset($args['sale_price'])) {
            $product->set_sale_price($args['sale_price']);
        }
        
        if (isset($args['sku'])) {
            $product->set_sku($args['sku']);
        }
        
        if (isset($args['stock_quantity'])) {
            $product->set_stock_quantity($args['stock_quantity']);
            $product->set_manage_stock(true);
        }
        
        $product_id = $product->save();
        
        return array(
            'content' => array(
                array(
                    'type' => 'text',
                    'text' => 'Product created successfully with ID: ' . $product_id
                )
            )
        );
    }
    
    private function update_product($args) {
        if (!class_exists('WooCommerce')) {
            return array(
                'isError' => true,
                'content' => array(
                    array(
                        'type' => 'text',
                        'text' => 'WooCommerce is not active'
                    )
                )
            );
        }
        
        $product_id = $args['product_id'];
        $product = wc_get_product($product_id);
        
        if (!$product) {
            return array(
                'isError' => true,
                'content' => array(
                    array(
                        'type' => 'text',
                        'text' => 'Product not found with ID: ' . $product_id
                    )
                )
            );
        }
        
        if (isset($args['name'])) {
            $product->set_name($args['name']);
        }
        
        if (isset($args['description'])) {
            $product->set_description($args['description']);
        }
        
        if (isset($args['regular_price'])) {
            $product->set_regular_price($args['regular_price']);
        }
        
        if (isset($args['sale_price'])) {
            $product->set_sale_price($args['sale_price']);
        }
        
        if (isset($args['stock_quantity'])) {
            $product->set_stock_quantity($args['stock_quantity']);
            $product->set_manage_stock(true);
        }
        
        $product->save();
        
        return array(
            'content' => array(
                array(
                    'type' => 'text',
                    'text' => 'Product updated successfully: ' . $product_id
                )
            )
        );
    }
}