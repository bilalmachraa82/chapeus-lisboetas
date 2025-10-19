<?php
/**
 * Fix Product Images Centering Issue
 *
 * This script adds CSS to the child theme to fix the product image centering problem
 * where images show only the top portion instead of being centered.
 *
 * Usage:
 * 1. Copy to WordPress root
 * 2. Run via browser: http://localhost:8080/fix_product_images_centering.php
 * 3. Or via WP-CLI: wp eval-file fix_product_images_centering.php
 */

// Load WordPress
require_once('./wp-load.php');

// Check if we're running in CLI or browser
$is_cli = php_sapi_name() === 'cli';

if (!$is_cli) {
    header('Content-Type: text/html; charset=utf-8');
    echo '<!DOCTYPE html><html><head><title>Fix Product Images</title>';
    echo '<style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 4px; margin: 10px 0; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 4px; margin: 10px 0; }
        .info { background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 4px; margin: 10px 0; }
        .code { background: #f5f5f5; padding: 15px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; margin: 10px 0; }
        h1 { color: #333; border-bottom: 2px solid #0073aa; padding-bottom: 10px; }
        h2 { color: #0073aa; margin-top: 30px; }
    </style></head><body>';
    echo '<h1>Fix Product Images Centering</h1>';
}

function log_message($message, $type = 'info') {
    global $is_cli;

    if ($is_cli) {
        echo "[$type] $message\n";
    } else {
        echo "<div class='$type'>$message</div>";
    }
}

// Get the child theme stylesheet path
$child_theme = get_stylesheet_directory();
$child_theme_style = $child_theme . '/style.css';

log_message("Child Theme Directory: $child_theme", 'info');
log_message("Style.css Path: $child_theme_style", 'info');

// Check if file exists and is writable
if (!file_exists($child_theme_style)) {
    log_message("ERROR: Child theme style.css not found at: $child_theme_style", 'error');
    exit(1);
}

if (!is_writable($child_theme_style)) {
    log_message("ERROR: style.css is not writable. Check file permissions.", 'error');
    exit(1);
}

// Read current CSS
$current_css = file_get_contents($child_theme_style);

// Check if fix already applied
if (strpos($current_css, 'FIX: Product Image Centering') !== false) {
    log_message("Fix already applied! The CSS fix is already in the child theme.", 'info');

    if (!$is_cli) {
        echo '<div class="info"><strong>Next steps:</strong><br>';
        echo '1. Visit <a href="/product-category/boinas/" target="_blank">/product-category/boinas/</a><br>';
        echo '2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)<br>';
        echo '3. Check if images are now centered</div>';
    }

    exit(0);
}

// CSS Fix to add
$css_fix = "

/****************************************************************/
/*************** FIX: Product Image Centering ******************/
/****************************************************************/
/* Added: " . date('Y-m-d H:i:s') . " */
/* Issue: Product images showing only top portion instead of centered */
/* Solution: Add explicit object-position: center */

/* Fix product thumbnails in category/shop pages */
.woocommerce ul.products li.product img.attachment-woocommerce_thumbnail,
.woocommerce .product-small .box-image img,
ul.products li.product .image_container img,
.product_thumbnail img,
.attachment-woocommerce_thumbnail,
.woocommerce-product-gallery__image img {
  object-fit: cover !important;
  object-position: center center !important;
}

/* Ensure image containers properly contain images */
.product-small .box-image,
ul.products li.product .image_container,
.woocommerce ul.products li.product .image_container {
  overflow: hidden;
  position: relative;
  display: block;
}

/* Fix mini cart and widget thumbnails */
.woocommerce ul.product_list_widget li img,
.widget_shopping_cart img,
.woocommerce.widget_shopping_cart .cart_list li img,
.woocommerce-mini-cart-item img {
  object-fit: cover !important;
  object-position: center center !important;
}

/* Fix related products */
.related.products ul.products li.product img,
.upsells.products ul.products li.product img {
  object-fit: cover !important;
  object-position: center center !important;
}

/* Fix for product blocks/grids */
.wc-block-grid__product-image img {
  object-fit: cover !important;
  object-position: center center !important;
}

/****************************************************************/
/****************** END OF FIX **********************************/
/****************************************************************/
";

// Backup current CSS
$backup_file = $child_theme . '/style.css.backup.' . date('Y-m-d-His');
if (copy($child_theme_style, $backup_file)) {
    log_message("Created backup: $backup_file", 'success');
} else {
    log_message("WARNING: Could not create backup file", 'error');
}

// Append the CSS fix
if (file_put_contents($child_theme_style, $current_css . $css_fix)) {
    log_message("SUCCESS: CSS fix has been added to the child theme!", 'success');

    if (!$is_cli) {
        echo '<div class="success"><strong>Fix Applied Successfully!</strong></div>';

        echo '<h2>CSS Added:</h2>';
        echo '<div class="code">' . htmlspecialchars($css_fix) . '</div>';

        echo '<h2>Next Steps:</h2>';
        echo '<div class="info">';
        echo '<ol>';
        echo '<li><strong>Clear WordPress cache</strong> (if using a cache plugin)</li>';
        echo '<li><strong>Clear browser cache</strong>: Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)</li>';
        echo '<li><strong>Test the pages:</strong>';
        echo '<ul>';
        echo '<li><a href="/product-category/boinas/" target="_blank">Boinas Category</a></li>';
        echo '<li><a href="/shop/" target="_blank">Shop Page</a></li>';
        echo '<li><a href="/" target="_blank">Homepage</a></li>';
        echo '</ul></li>';
        echo '<li>If images still look wrong, you may need to <strong>regenerate thumbnails</strong></li>';
        echo '</ol>';
        echo '</div>';

        echo '<h2>Regenerate Thumbnails (Optional)</h2>';
        echo '<div class="info">';
        echo '<p>For best results, regenerate all product thumbnails:</p>';
        echo '<ol>';
        echo '<li>Install "Regenerate Thumbnails" plugin from WordPress.org</li>';
        echo '<li>Go to Tools → Regenerate Thumbnails</li>';
        echo '<li>Click "Regenerate All Thumbnails"</li>';
        echo '</ol>';
        echo '<p><strong>Or via WP-CLI:</strong></p>';
        echo '<div class="code">docker exec -it chapeus_wordpress wp media regenerate --yes</div>';
        echo '</div>';

        echo '<h2>Rollback (If Needed)</h2>';
        echo '<div class="info">';
        echo '<p>If you need to undo this change, restore the backup:</p>';
        echo '<div class="code">mv ' . $backup_file . ' ' . $child_theme_style . '</div>';
        echo '</div>';
    }

} else {
    log_message("ERROR: Could not write to style.css", 'error');
    exit(1);
}

// Clear theme cache if any
if (function_exists('wp_cache_flush')) {
    wp_cache_flush();
    log_message("WordPress cache flushed", 'info');
}

if (!$is_cli) {
    echo '</body></html>';
}

log_message("Done!", 'success');
