<?php
/**
 * 🎨 Upload e Configuração Automática do Logo
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎨 CONFIGURANDO LOGO DO INSTAGRAM...\n\n";
echo str_repeat("=", 70) . "\n\n";

// ============================================================================
// 1. UPLOAD DO LOGO
// ============================================================================

echo "1️⃣ UPLOAD DO LOGO...\n\n";

$logo_path = '/tmp/logo.jpg';

if (!file_exists($logo_path)) {
    echo "   ❌ Logo não encontrado em $logo_path\n\n";
    exit(1);
}

echo "   ✅ Logo encontrado\n";

// Upload para media library
$filename = 'chapeus-lisboetas-logo.jpg';
$upload_file = wp_upload_bits($filename, null, file_get_contents($logo_path));

if ($upload_file['error']) {
    echo "   ❌ Erro no upload: {$upload_file['error']}\n\n";
    exit(1);
}

echo "   ✅ Logo carregado: {$upload_file['file']}\n";

// Criar attachment
$attachment = array(
    'post_mime_type' => $upload_file['type'],
    'post_title' => 'Chapéus Lisboetas - Logo',
    'post_content' => '',
    'post_status' => 'inherit'
);

$attach_id = wp_insert_attachment($attachment, $upload_file['file']);

if (!$attach_id) {
    echo "   ❌ Erro ao criar attachment\n\n";
    exit(1);
}

echo "   ✅ Attachment criado (ID: $attach_id)\n";

// Gerar metadata
require_once(ABSPATH . 'wp-admin/includes/image.php');
$attach_data = wp_generate_attachment_metadata($attach_id, $upload_file['file']);
wp_update_attachment_metadata($attach_id, $attach_data);

echo "   ✅ Metadata gerado\n\n";

// ============================================================================
// 2. CONFIGURAR LOGO NO SITE
// ============================================================================

echo "2️⃣ CONFIGURANDO LOGO NO TEMA...\n\n";

// Site logo (WordPress)
update_option('site_logo', $attach_id);

// Custom logo (WordPress theme customizer)
set_theme_mod('custom_logo', $attach_id);

// Flatsome logo
set_theme_mod('site_logo', $attach_id);
set_theme_mod('logo', get_attached_file($attach_id));
set_theme_mod('logo_width', 150);

echo "   ✅ Logo configurado como site logo\n";
echo "   ✅ Logo configurado no Flatsome\n";
echo "   ✅ Largura: 150px\n\n";

// ============================================================================
// 3. CONFIGURAR FAVICON
// ============================================================================

echo "3️⃣ CONFIGURANDO FAVICON...\n\n";

// Usar mesmo logo como favicon
update_option('site_icon', $attach_id);
set_theme_mod('site_icon', $attach_id);

echo "   ✅ Favicon configurado\n\n";

// ============================================================================
// 4. AJUSTAR CORES BASEADAS NO LOGO
// ============================================================================

echo "4️⃣ AJUSTANDO CORES BASEADAS NO LOGO...\n\n";

// Logo tem: Amarelo (#FFD700ish), Azul Navy (#1B1464ish)
$logo_colors = array(
    'primary' => '#FFD700',      // Amarelo do fundo
    'secondary' => '#1B1464',    // Azul do chapéu
    'accent' => '#8B4513',       // Marrom chapéu (manter)
    'header_bg' => '#FFFFFF',
    'header_color' => '#1B1464'
);

foreach ($logo_colors as $key => $color) {
    set_theme_mod("color_$key", $color);
}

echo "   ✅ Cores ajustadas para match com logo:\n";
echo "      • Primária: {$logo_colors['primary']} (Amarelo)\n";
echo "      • Secundária: {$logo_colors['secondary']} (Azul Navy)\n";
echo "      • Accent: {$logo_colors['accent']} (Marrom)\n\n";

// ============================================================================
// 5. CONFIGURAR HEADER
// ============================================================================

echo "5️⃣ CONFIGURANDO HEADER...\n\n";

// Header settings
set_theme_mod('header_height', 80);
set_theme_mod('logo_position', 'left');
set_theme_mod('header_style', 'normal');
set_theme_mod('header_bg_color', '#FFFFFF');
set_theme_mod('header_color', '#1B1464');

echo "   ✅ Header height: 80px\n";
echo "   ✅ Logo position: Left\n";
echo "   ✅ Header style: Normal\n\n";

// ============================================================================
// 6. ATUALIZAR CSS CUSTOMIZADO
// ============================================================================

echo "6️⃣ ATUALIZANDO CSS CUSTOMIZADO...\n\n";

$custom_css = "
/* Logo e Header */
.header-logo img {
    max-width: 150px;
    height: auto;
}

.site-logo {
    display: inline-block;
}

.site-logo img {
    width: 150px;
    height: auto;
}

/* Ajustar cores do logo */
.header-main {
    background: #FFFFFF;
    border-bottom: 2px solid #FFD700;
}

.header-nav {
    background: #FFFFFF;
}

/* Botões com cor do logo */
.button.primary {
    background-color: #FFD700;
    color: #1B1464;
    font-weight: 600;
}

.button.primary:hover {
    background-color: #1B1464;
    color: #FFD700;
}

/* Nav links */
.nav > li > a {
    color: #1B1464;
    font-weight: 500;
}

.nav > li > a:hover {
    color: #FFD700;
}

/* Footer */
.footer {
    background: #1B1464;
    color: #FFFFFF;
}

.footer a {
    color: #FFD700;
}

.footer a:hover {
    color: #FFFFFF;
}
";

// Adicionar ao existing CSS
$existing_css = wp_get_custom_css_post();
if ($existing_css) {
    $existing_content = $existing_css->post_content;
    $updated_content = $existing_content . "\n\n" . $custom_css;
    wp_update_custom_css_post($updated_content);
} else {
    wp_update_custom_css_post($custom_css);
}

echo "   ✅ CSS customizado atualizado\n\n";

// ============================================================================
// 7. CONFIGURAR SITE IDENTITY
// ============================================================================

echo "7️⃣ CONFIGURANDO SITE IDENTITY...\n\n";

update_option('blogname', 'Chapéus Lisboetas');
update_option('blogdescription', 'Tradição Artesanal Portuguesa desde 1950');

echo "   ✅ Site title: Chapéus Lisboetas\n";
echo "   ✅ Tagline: Tradição Artesanal Portuguesa desde 1950\n\n";

// ============================================================================
// 8. LIMPAR CACHES
// ============================================================================

echo "8️⃣ LIMPANDO CACHES...\n\n";

wp_cache_flush();
delete_transient('flatsome_settings');
delete_transient('flatsome_customize_preview');

// Regenerar CSS do Flatsome
if (function_exists('flatsome_regenerate_css')) {
    flatsome_regenerate_css();
}

echo "   ✅ Caches limpos\n";
echo "   ✅ CSS regenerado\n\n";

// ============================================================================
// FINAL
// ============================================================================

echo str_repeat("=", 70) . "\n";
echo "✅ LOGO CONFIGURADO COM SUCESSO!\n";
echo str_repeat("=", 70) . "\n\n";

echo "🎨 RESUMO:\n";
echo "   • Logo upload: ✅\n";
echo "   • Site logo: ✅ (ID: $attach_id)\n";
echo "   • Favicon: ✅\n";
echo "   • Cores ajustadas: ✅ (Amarelo + Azul Navy)\n";
echo "   • Header configurado: ✅\n";
echo "   • CSS customizado: ✅\n\n";

echo "🌐 VERIFICAR:\n";
echo "   • Homepage: http://localhost:8080\n";
echo "   • Logo deve aparecer no header\n";
echo "   • Favicon no tab do browser\n\n";

echo "💡 SE LOGO NÃO APARECER:\n";
echo "   1. Hard refresh: Cmd+Shift+R\n";
echo "   2. Clear browser cache\n";
echo "   3. Verificar: Admin → Appearance → Customize\n\n";

echo "🎨 CORES DO LOGO:\n";
echo "   • Amarelo: #FFD700 (fundo)\n";
echo "   • Azul Navy: #1B1464 (chapéu)\n";
echo "   • Marrom: #8B4513 (acento)\n\n";

?>
