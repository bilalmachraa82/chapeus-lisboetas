<?php
define('WP_USE_THEMES', false);
require(__DIR__ . '/wp-load.php');

function ensure_page($title) {
  $page = get_page_by_title($title);
  if ($page) return $page->ID;
  return wp_insert_post([
    'post_title' => $title,
    'post_content' => '',
    'post_status' => 'publish',
    'post_type' => 'page'
  ]);
}

$shop_id = wc_get_page_id('shop');
if ($shop_id <= 0) { $shop_id = ensure_page('Shop'); }
update_option('woocommerce_shop_page_id', $shop_id);

$cart_id = get_option('woocommerce_cart_page_id');
if (!$cart_id) { $cart_id = ensure_page('Cart'); }
update_option('woocommerce_cart_page_id', $cart_id);

$checkout_id = get_option('woocommerce_checkout_page_id');
if (!$checkout_id) { $checkout_id = ensure_page('Checkout'); }
update_option('woocommerce_checkout_page_id', $checkout_id);

$myaccount_id = get_option('woocommerce_myaccount_page_id');
if (!$myaccount_id) { $myaccount_id = ensure_page('My account'); }
update_option('woocommerce_myaccount_page_id', $myaccount_id);

if (!get_option('permalink_structure')) {
  update_option('permalink_structure', '/%postname%/');
}
flush_rewrite_rules();
wp_cache_flush();

echo "OK: Shop=$shop_id Cart=$cart_id Checkout=$checkout_id MyAccount=$myaccount_id\n";
?>