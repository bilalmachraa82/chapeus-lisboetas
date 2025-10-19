#!/usr/bin/env python3
"""
🚀 Premium Site Builder
Aplica identidade da marca e cria site premium completo
"""

import json
import subprocess
from pathlib import Path

class PremiumSiteBuilder:
    def __init__(self):
        self.brand_identity = self.load_brand_identity()
        
    def load_brand_identity(self) -> dict:
        """Carregar identidade da marca"""
        with open('brand_identity.json', 'r') as f:
            return json.load(f)
    
    def apply_premium_design(self):
        """Aplicar design premium baseado na identidade da marca"""
        print("=" * 70)
        print("🎨 PREMIUM SITE BUILDER")
        print("=" * 70)
        print("\n🚀 Aplicando Design Premium...\n")
        
        colors = self.brand_identity['colors']
        typography = self.brand_identity['typography']
        
        # Gerar CSS customizado
        custom_css = f"""
/* Chapéus Lisboetas - Premium Custom CSS */

:root {{
    /* Cores da Marca */
    --color-primary: {colors['primary']};
    --color-secondary: {colors['secondary']};
    --color-accent: {colors['accent']};
    --color-neutral-dark: {colors['neutral_dark']};
    --color-neutral-light: {colors['neutral_light']};
    --color-background: {colors['background']};
    --color-text-dark: {colors['text_dark']};
    --color-text-light: {colors['text_light']};
    
    /* Tipografia */
    --font-heading: '{typography['heading_font']}', serif;
    --font-body: '{typography['body_font']}', sans-serif;
    --font-accent: '{typography['accent_font']}', sans-serif;
}}

/* Tipografia Premium */
body {{
    font-family: var(--font-body);
    color: var(--color-text-dark);
    background-color: var(--color-background);
    font-size: 16px;
    line-height: 1.6;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-heading);
    font-weight: {typography['heading_weight']};
    color: var(--color-primary);
    letter-spacing: -0.02em;
}}

h1 {{ font-size: 3.5rem; line-height: 1.1; }}
h2 {{ font-size: 2.5rem; line-height: 1.2; }}
h3 {{ font-size: 1.875rem; line-height: 1.3; }}

/* Botões Premium */
.button, .btn, .woocommerce-Button {{
    font-family: var(--font-accent);
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    background: var(--color-primary);
    border: none;
    padding: 15px 35px;
    border-radius: 3px;
    transition: all 0.3s ease;
}}

.button:hover {{
    background: var(--color-secondary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
}}

/* Header Premium */
.header {{
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}

.header-main {{
    border-bottom: 1px solid var(--color-neutral-light);
}}

/* Navigation */
.nav > li > a {{
    color: var(--color-text-dark);
    font-family: var(--font-accent);
    font-weight: 500;
    letter-spacing: 0.03em;
    transition: color 0.3s;
}}

.nav > li > a:hover {{
    color: var(--color-primary);
}}

/* Produtos */
.product {{
    background: white;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
}}

.product:hover {{
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}}

.product-title {{
    font-family: var(--font-heading);
    font-size: 1.125rem;
    color: var(--color-text-dark);
}}

.price {{
    font-family: var(--font-accent);
    font-weight: 600;
    font-size: 1.5rem;
    color: var(--color-primary);
}}

/* Footer Premium */
.footer {{
    background: var(--color-neutral-dark);
    color: var(--color-neutral-light);
}}

.footer a {{
    color: var(--color-neutral-light);
    transition: color 0.3s;
}}

.footer a:hover {{
    color: white;
}}

/* Trust Badges */
.trust-badges {{
    display: flex;
    gap: 30px;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
    background: var(--color-background);
}}

.trust-badge {{
    text-align: center;
    padding: 20px;
}}

.trust-badge-icon {{
    font-size: 2.5rem;
    color: var(--color-primary);
    margin-bottom: 10px;
}}

.trust-badge-text {{
    font-family: var(--font-accent);
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--color-text-light);
}}

/* Homepage Hero */
.hero-section {{
    background: linear-gradient(135deg, {colors['neutral_light']} 0%, {colors['background']} 100%);
    padding: 80px 0;
    text-align: center;
}}

.hero-title {{
    font-size: 4rem;
    margin-bottom: 20px;
    color: var(--color-primary);
}}

.hero-subtitle {{
    font-size: 1.5rem;
    color: var(--color-text-light);
    margin-bottom: 30px;
}}

/* Responsivo */
@media (max-width: 768px) {{
    h1 {{ font-size: 2.5rem; }}
    h2 {{ font-size: 2rem; }}
    .hero-title {{ font-size: 2.5rem; }}
    .hero-subtitle {{ font-size: 1.25rem; }}
}}
"""
        
        return custom_css
    
    def generate_php_config(self) -> str:
        """Gerar configuração PHP para WordPress"""
        colors = self.brand_identity['colors']
        typography = self.brand_identity['typography']
        
        php_config = f"""<?php
/**
 * Configuração Premium - Chapéus Lisboetas
 */

define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "🎨 APLICANDO DESIGN PREMIUM...\\n\\n";

// ============================================================================
// CORES DA MARCA
// ============================================================================

set_theme_mod('color_primary', '{colors['primary']}');
set_theme_mod('color_secondary', '{colors['secondary']}');
set_theme_mod('color_success', '#2E7D32');
set_theme_mod('color_alert', '#FFA000');

// Header
set_theme_mod('header_bg_color', '#FFFFFF');
set_theme_mod('header_color_dark', '{colors['text_dark']}');

// Footer
set_theme_mod('footer_bg_color', '{colors['neutral_dark']}');
set_theme_mod('footer_color', '{colors['neutral_light']}');

// Backgrounds
set_theme_mod('body_bg_color', '{colors['background']}');

// Tipografia
set_theme_mod('type_texts', '{typography['body_font']}');
set_theme_mod('type_headings', '{typography['heading_font']}');
set_theme_mod('type_nav', '{typography['accent_font']}');

// Layout
set_theme_mod('site_width', '1200px');
set_theme_mod('header_height', '80');
set_theme_mod('category_grid_style', 'overlay');

echo "✅ Cores aplicadas\\n";

// ============================================================================
// HOMEPAGE PREMIUM
// ============================================================================

$homepage_content = '[section bg_color="linear-gradient(135deg, {colors['neutral_light']} 0%, {colors['background']} 100%)" padding="80px" class="hero-section"]
[row]
[col span="12" align="center"]
<h1 style="font-size: 4rem; color: {colors['primary']}; font-family: {typography['heading_font']}, serif; margin-bottom: 20px;">Chapéus Lisboetas</h1>
<p class="lead" style="font-size: 1.5rem; color: {colors['text_light']}; margin-bottom: 30px;">Tradição Artesanal Portuguesa desde 1950</p>
<p style="font-size: 1.125rem; color: {colors['text_light']}; max-width: 600px; margin: 0 auto 40px;">Cada chapéu é uma obra de arte, feito à mão com técnicas transmitidas através de gerações.</p>
[button text="Explorar Coleção" link="/shop" color="primary" size="large" radius="3"]
[/col]
[/row]
[/section]

[section label="Trust Badges" bg_color="{colors['background']}" padding="40px"]
[row]
[col span="3" align="center"]
<div class="trust-badge">
<div class="trust-badge-icon">🇵🇹</div>
<div class="trust-badge-text">Artesanato<br>Português</div>
</div>
[/col]
[col span="3" align="center"]
<div class="trust-badge">
<div class="trust-badge-icon">✋</div>
<div class="trust-badge-text">Feito<br>à Mão</div>
</div>
[/col]
[col span="3" align="center"]
<div class="trust-badge">
<div class="trust-badge-icon">📅</div>
<div class="trust-badge-text">Desde<br>1950</div>
</div>
[/col]
[col span="3" align="center"]
<div class="trust-badge">
<div class="trust-badge-icon">💎</div>
<div class="trust-badge-text">Qualidade<br>Premium</div>
</div>
[/col]
[/row]
[/section]

[section label="Produtos Destaque" padding="60px"]
[row]
[col span="12" align="center"]
<h2 style="color: {colors['primary']}; margin-bottom: 10px;">Destaques da Coleção</h2>
<p style="color: {colors['text_light']}; font-size: 1.125rem;">Chapéus que contam histórias</p>
[/col]
[/row]
[ux_products columns="4" show="featured" orderby="rand"]
[row style__margin-top="30px"]
[col span="12" align="center"]
[button text="Ver Toda a Coleção" link="/shop" style="outline" color="primary"]
[/col]
[/row]
[/section]

[section label="Sobre" bg_color="{colors['neutral_light']}" padding="80px"]
[row]
[col span="6" span__sm="12"]
<h2 style="color: {colors['primary']};">Tradição e Excelência</h2>
<p style="font-size: 1.125rem; line-height: 1.8;">Há mais de 70 anos, a Chapéus Lisboetas dedica-se à arte milenar da chapelaria tradicional portuguesa. Cada peça é cuidadosamente confeccionada com materiais nobres e técnicas artesanais transmitidas através de gerações.</p>
<p>Combinamos tradição com design contemporâneo, criando chapéus que são verdadeiras obras de arte para usar no dia a dia.</p>
[button text="Nossa História" link="/sobre" style="outline" color="primary" class="margin-top"]
[/col]
[col span="6" span__sm="12"]
[ux_image id="placeholder" height="400px" image_overlay="rgba(139, 69, 19, 0.1)"]
[/col]
[/row]
[/section]

[section label="Newsletter" bg_color="{colors['primary']}" dark="true" padding="60px"]
[row]
[col span="12" align="center"]
<h3 style="color: white; margin-bottom: 10px;">Fique por Dentro</h3>
<p style="color: rgba(255,255,255,0.9); font-size: 1.125rem;">Receba novidades, coleções exclusivas e ofertas especiais</p>
[/col]
[/row]
[row]
[col span="6" span__sm="12" align="center" class="margin-auto"]
[contact-form-7 id="1" title="Newsletter"]
[/col]
[/row]
[/section]';

// Criar ou atualizar homepage
$existing_home = get_page_by_path('home');
if ($existing_home) {{
    wp_update_post(array(
        'ID' => $existing_home->ID,
        'post_content' => $homepage_content
    ));
    $page_id = $existing_home->ID;
    echo "✅ Homepage atualizada\\n";
}} else {{
    $page_id = wp_insert_post(array(
        'post_title' => 'Home',
        'post_content' => $homepage_content,
        'post_status' => 'publish',
        'post_type' => 'page'
    ));
    echo "✅ Homepage criada\\n";
}}

update_option('page_on_front', $page_id);
update_option('show_on_front', 'page');

// ============================================================================
// CSS CUSTOMIZADO
// ============================================================================

$custom_css = file_get_contents('/tmp/premium_custom.css');
wp_update_custom_css_post($custom_css);

echo "✅ CSS customizado aplicado\\n";

// ============================================================================
// FINAL
// ============================================================================

echo "\\n";
echo "══════════════════════════════════════════════════════════════════\\n";
echo "✅ DESIGN PREMIUM APLICADO!\\n";
echo "══════════════════════════════════════════════════════════════════\\n";
echo "\\n";
echo "🌐 Verificar: http://localhost:8080\\n";
echo "\\n";
?>
"""
        return php_config
    
    def build(self):
        """Construir site premium"""
        print("🚀 Gerando arquivos de configuração...\n")
        
        # Gerar CSS
        css = self.apply_premium_design()
        with open('/tmp/premium_custom.css', 'w') as f:
            f.write(css)
        print("✅ CSS premium gerado\n")
        
        # Gerar PHP config
        php = self.generate_php_config()
        with open('/tmp/apply_premium_design.php', 'w') as f:
            f.write(php)
        print("✅ Configuração PHP gerada\n")
        
        print("=" * 70)
        print("✅ ARQUIVOS PRONTOS PARA APLICAR!")
        print("=" * 70)
        print("\n📝 Próximos passos:")
        print("   1. Copiar arquivos para Docker")
        print("   2. Executar script PHP")
        print("   3. Verificar resultado\n")

if __name__ == "__main__":
    builder = PremiumSiteBuilder()
    builder.build()
