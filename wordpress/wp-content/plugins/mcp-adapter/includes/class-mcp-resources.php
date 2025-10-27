<?php
/**
 * MCP Resources class
 * Handles WordPress and WooCommerce resources for MCP
 */

if (!defined('ABSPATH')) {
    exit;
}

class MCP_Resources {
    
    public function __construct() {
        // Initialize resources
    }
    
    public function get_resources() {
        $resources = array();
        
        // WordPress resources
        $resources[] = array(
            'uri' => 'wordpress://posts',
            'name' => 'WordPress Posts',
            'description' => 'All WordPress posts',
            'mimeType' => 'application/json'
        );
        
        $resources[] = array(
            'uri' => 'wordpress://pages',
            'name' => 'WordPress Pages',
            'description' => 'All WordPress pages',
            'mimeType' => 'application/json'
        );
        
        $resources[] = array(
            'uri' => 'wordpress://users',
            'name' => 'WordPress Users',
            'description' => 'All WordPress users',
            'mimeType' => 'application/json'
        );
        
        // WooCommerce resources (if WooCommerce is active)
        if (class_exists('WooCommerce')) {
            $resources[] = array(
                'uri' => 'woocommerce://products',
                'name' => 'WooCommerce Products',
                'description' => 'All WooCommerce products',
                'mimeType' => 'application/json'
            );
            
            $resources[] = array(
                'uri' => 'woocommerce://orders',
                'name' => 'WooCommerce Orders',
                'description' => 'All WooCommerce orders',
                'mimeType' => 'application/json'
            );
            
            $resources[] = array(
                'uri' => 'woocommerce://customers',
                'name' => 'WooCommerce Customers',
                'description' => 'All WooCommerce customers',
                'mimeType' => 'application/json'
            );
            
            $resources[] = array(
                'uri' => 'woocommerce://categories',
                'name' => 'Product Categories',
                'description' => 'All product categories',
                'mimeType' => 'application/json'
            );
        }
        
        return $resources;
    }
    
    public function read_resource($uri) {
        $parts = parse_url($uri);
        $scheme = $parts['scheme'] ?? '';
        $path = ltrim($parts['path'] ?? '', '/');
        
        switch ($scheme) {
            case 'wordpress':
                return $this->read_wordpress_resource($path);
            case 'woocommerce':
                return $this->read_woocommerce_resource($path);
            default:
                return array(
                    array(
                        'type' => 'text',
                        'text' => 'Unknown resource scheme: ' . $scheme
                    )
                );
        }
    }
    
    private function read_wordpress_resource($path) {
        switch ($path) {
            case 'posts':
                return $this->get_wordpress_posts();
            case 'pages':
                return $this->get_wordpress_pages();
            case 'users':
                return $this->get_wordpress_users();
            default:
                return array(
                    array(
                        'type' => 'text',
                        'text' => 'Unknown WordPress resource: ' . $path
                    )
                );
        }
    }
    
    private function read_woocommerce_resource($path) {
        if (!class_exists('WooCommerce')) {
            return array(
                array(
                    'type' => 'text',
                    'text' => 'WooCommerce is not active'
                )
            );
        }
        
        switch ($path) {
            case 'products':
                return $this->get_woocommerce_products();
            case 'orders':
                return $this->get_woocommerce_orders();
            case 'customers':
                return $this->get_woocommerce_customers();
            case 'categories':
                return $this->get_product_categories();
            default:
                return array(
                    array(
                        'type' => 'text',
                        'text' => 'Unknown WooCommerce resource: ' . $path
                    )
                );
        }
    }
    
    private function get_wordpress_posts() {
        $posts = get_posts(array(
            'numberposts' => 50,
            'post_status' => 'publish'
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
                'url' => get_permalink($post->ID),
                'author' => get_the_author_meta('display_name', $post->post_author)
            );
        }
        
        return array(
            array(
                'type' => 'text',
                'text' => json_encode($result, JSON_PRETTY_PRINT)
            )
        );
    }
    
    private function get_wordpress_pages() {
        $pages = get_pages(array(
            'number' => 50,
            'post_status' => 'publish'
        ));
        
        $result = array();
        foreach ($pages as $page) {
            $result[] = array(
                'id' => $page->ID,
                'title' => $page->post_title,
                'content' => $page->post_content,
                'date' => $page->post_date,
                'status' => $page->post_status,
                'url' => get_permalink($page->ID),
                'parent' => $page->post_parent
            );
        }
        
        return array(
            array(
                'type' => 'text',
                'text' => json_encode($result, JSON_PRETTY_PRINT)
            )
        );
    }
    
    private function get_wordpress_users() {
        $users = get_users(array(
            'number' => 50
        ));
        
        $result = array();
        foreach ($users as $user) {
            $result[] = array(
                'id' => $user->ID,
                'username' => $user->user_login,
                'email' => $user->user_email,
                'display_name' => $user->display_name,
                'roles' => $user->roles,
                'registered' => $user->user_registered
            );
        }
        
        return array(
            array(
                'type' => 'text',
                'text' => json_encode($result, JSON_PRETTY_PRINT)
            )
        );
    }
    
    private function get_woocommerce_products() {
        $products = wc_get_products(array(
            'limit' => 50,
            'status' => 'publish'
        ));
        
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
                'status' => $product->get_status(),
                'categories' => wp_get_post_terms($product->get_id(), 'product_cat', array('fields' => 'names')),
                'description' => $product->get_description(),
                'short_description' => $product->get_short_description()
            );
        }
        
        return array(
            array(
                'type' => 'text',
                'text' => json_encode($result, JSON_PRETTY_PRINT)
            )
        );
    }
    
    private function get_woocommerce_orders() {
        $orders = wc_get_orders(array(
            'limit' => 50,
            'status' => array('wc-processing', 'wc-completed', 'wc-pending')
        ));
        
        $result = array();
        foreach ($orders as $order) {
            $result[] = array(
                'id' => $order->get_id(),
                'order_number' => $order->get_order_number(),
                'status' => $order->get_status(),
                'total' => $order->get_total(),
                'currency' => $order->get_currency(),
                'date_created' => $order->get_date_created()->date('Y-m-d H:i:s'),
                'customer_id' => $order->get_customer_id(),
                'billing_email' => $order->get_billing_email(),
                'billing_first_name' => $order->get_billing_first_name(),
                'billing_last_name' => $order->get_billing_last_name(),
                'items_count' => $order->get_item_count()
            );
        }
        
        return array(
            array(
                'type' => 'text',
                'text' => json_encode($result, JSON_PRETTY_PRINT)
            )
        );
    }
    
    private function get_woocommerce_customers() {
        $customers = get_users(array(
            'role' => 'customer',
            'number' => 50
        ));
        
        $result = array();
        foreach ($customers as $customer) {
            $customer_data = new WC_Customer($customer->ID);
            $result[] = array(
                'id' => $customer->ID,
                'username' => $customer->user_login,
                'email' => $customer->user_email,
                'first_name' => $customer_data->get_first_name(),
                'last_name' => $customer_data->get_last_name(),
                'billing_country' => $customer_data->get_billing_country(),
                'billing_city' => $customer_data->get_billing_city(),
                'orders_count' => wc_get_customer_order_count($customer->ID),
                'total_spent' => wc_get_customer_total_spent($customer->ID),
                'date_registered' => $customer->user_registered
            );
        }
        
        return array(
            array(
                'type' => 'text',
                'text' => json_encode($result, JSON_PRETTY_PRINT)
            )
        );
    }
    
    private function get_product_categories() {
        $categories = get_terms(array(
            'taxonomy' => 'product_cat',
            'hide_empty' => false,
            'number' => 50
        ));
        
        $result = array();
        foreach ($categories as $category) {
            $result[] = array(
                'id' => $category->term_id,
                'name' => $category->name,
                'slug' => $category->slug,
                'description' => $category->description,
                'count' => $category->count,
                'parent' => $category->parent
            );
        }
        
        return array(
            array(
                'type' => 'text',
                'text' => json_encode($result, JSON_PRETTY_PRINT)
            )
        );
    }
}