<?php
define('WP_USE_THEMES', false);
require(__DIR__ . '/wp-load.php');

$types = array('product','product_variation','page','post','nav_menu_item');
foreach ($types as $t) {
  $items = get_posts(array('post_type'=>$t,'post_status'=>'any','posts_per_page'=>-1));
  foreach ($items as $it) { wp_delete_post($it->ID, true); }
}

$taxes = array('product_cat','product_tag','product_visibility');
foreach ($taxes as $tax) {
  $terms = get_terms(array('taxonomy'=>$tax,'hide_empty'=>false));
  foreach ($terms as $term) { wp_delete_term($term->term_id, $tax); }
}

update_option('woocommerce_shop_page_id', 0);
update_option('woocommerce_cart_page_id', 0);
update_option('woocommerce_checkout_page_id', 0);
update_option('woocommerce_myaccount_page_id', 0);

flush_rewrite_rules();
wp_cache_flush();

echo 'FRESH_START_OK';
?>