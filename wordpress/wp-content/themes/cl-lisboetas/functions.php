<?php
add_action('wp_enqueue_scripts', function() {
  wp_enqueue_style('cl-lisboetas-style', get_stylesheet_uri(), [], '1.0.0');
});

add_action('after_setup_theme', function(){
  add_theme_support('custom-logo');
});
?>