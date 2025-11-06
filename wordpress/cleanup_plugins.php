<?php
// Cleanup duplicate plugins script

$current_plugins = 'a:27:{i:0;s:37:"ajax-search-lite/ajax-search-lite.php";i:1;s:11:"amp/amp.php";i:2;s:95:"automatic-translator-addon-for-loco-translate/automatic-translator-addon-for-loco-translate.php";i:3;s:33:"classic-editor/classic-editor.php";i:4;s:36:"cleantalk-spam-protect/cleantalk.php";i:5;s:31:"creame-whatsapp-me/joinchat.php";i:6;s:29:"easy-wp-smtp/easy-wp-smtp.php";i:7;s:43:"everest-admin-theme/everest-admin-theme.php";i:8;s:64:"export-media-with-selected-content/export-media-with-content.php";i:9;s:47:"file-manager-advanced/file_manager_advanced.php";i:10;s:29:"health-check/health-check.php";i:11;s:31:"joinchat-plus/joinchat-plus.php";i:12;i:13;s:23:"loco-translate/loco.php";i:14;s:21:"mailin/sendinblue.php";i:15;s:33:"preloader-plus/preloader-plus.php";i:16;s:25:"quadmenu-pro/quadmenu.php";i:17;s:47:"really-simple-ssl/rlrsssl-really-simple-ssl.php";i:18;s:23:"revslider/revslider.php";i:19;s:56:"transposh-translation-filter-for-wordpress/transposh.php";i:20;s:65:"wc-secondary-product-thumbnail/wc-secondary-product-thumbnail.php";i:21;s:48:"weight-based-shipping-for-woocommerce/plugin.php";i:22;s:27:"woocommerce/woocommerce.php";i:23;s:41:"wordpress-importer/wordpress-importer.php";i:24;s:24:"wordpress-seo/wp-seo.php";i:25;s:29:"wp-mail-smtp/wp_mail_smtp.php";i:26;s:69:"yith-woocommerce-request-a-quote/yith-woocommerce-request-a-quote.php";}';

$plugins = unserialize($current_plugins);

// Remove duplicates and problematic plugins
$remove = [
    "easy-wp-smtp/easy-wp-smtp.php",  // Duplicate of wp-mail-smtp
    "joinchat-plus/joinchat-plus.php", // Duplicate of joinchat
];

// Filter out the duplicates
$clean_plugins = array_filter($plugins, function($plugin) use ($remove) {
    return !in_array($plugin, $remove);
});

// Re-index array
$clean_plugins = array_values($clean_plugins);

// Generate UPDATE query
$serialized = serialize($clean_plugins);
$escaped = addslashes($serialized);

echo "UPDATE lx_options SET option_value = '$escaped' WHERE option_name = 'active_plugins';\n";