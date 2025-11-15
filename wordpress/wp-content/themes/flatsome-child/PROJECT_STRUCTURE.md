# Chapéus Lisboetas - Estrutura Completa do Projeto WordPress

## Informações Gerais
- **Local:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/`
- **WordPress Version:** 5.4.1 (May 2020)
- **PHP Version:** 7.4
- **Database Prefix:** `lx_` (NOT standard `wp_`)
- **Database:** lisboetas_web

---

## 1. ESTRUTURA DE TEMAS

### Tema Ativo: Flatsome (Premium Theme)
**Path Base:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/themes/flatsome/`

**Subdirectórios Principais:**
```
flatsome/
├── assets/                    # Stylesheets, images, JS libraries
│   ├── css/                   # Compiled CSS files
│   ├── img/                   # Theme images & icons
│   ├── js/                    # Theme JavaScript
│   └── libs/                  # 3rd party libraries (Swiper, AOS, GLightbox)
├── inc/                       # Core theme functionality
│   ├── admin/                 # Admin customizations
│   ├── blocks/                # Gutenberg blocks support
│   ├── builder/               # UX Builder (Flatsome's page builder)
│   │   ├── core/
│   │   ├── shortcodes/
│   │   └── components/
│   ├── classes/               # PHP classes
│   ├── extensions/            # Theme extensions
│   ├── functions/             # Core functions
│   ├── helpers/               # Helper functions
│   ├── integrations/          # 3rd party integrations
│   ├── post-types/            # Custom post types
│   ├── shortcodes/            # Custom shortcodes
│   ├── structure/             # Page structure templates
│   ├── widgets/               # WordPress widgets
│   └── woocommerce/           # WooCommerce overrides
├── template-parts/            # Modular template components
│   ├── header/                # Header variations (header-top.php, header-main.php, etc.)
│   ├── footer/                # Footer templates
│   ├── pages/                 # Page-specific templates
│   ├── posts/                 # Post-specific templates
│   ├── shortcodes/            # Shortcode templates
│   └── overlays/              # Overlay effects
├── woocommerce/               # WooCommerce template overrides
│   ├── cart/
│   ├── checkout/
│   ├── global/
│   ├── layouts/
│   ├── loop/
│   ├── myaccount/
│   ├── notices/
│   └── single-product/
├── languages/                 # Localization files
├── header.php                 # Main header template
├── footer.php                 # Main footer template
├── functions.php              # Parent theme functions (932 bytes - minimal)
├── style.css                  # Parent theme stylesheet
├── page-*.php                 # Page template variations
├── single.php                 # Single post template
├── index.php                  # Fallback template
├── 404.php                    # 404 error page
└── theme.json                 # Block editor settings
```

### Tema Child: Flatsome Child
**Path Base:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/themes/flatsome-child/`

**Estrutura:**
```
flatsome-child/
├── assets/
│   ├── images/
│   │   └── blog-placeholder.svg
│   └── js/
│       └── custom.js           # Custom JavaScript (carousel, animations)
├── style.css                   # Child theme stylesheet (3,036 lines)
├── functions.php               # Child theme functions (22K - heavily customized)
├── template-parts/             # Child-specific template overrides
│   └── (empty or minimal)
├── P0_QUICK_REFERENCE.md       # Phase 0 optimization checklist
├── P0_VALIDATION_REPORT.md     # Technical validation report
├── DESIGN_SYSTEM_REPORT.md     # Design system documentation
├── RELATORIO_IMPLEMENTACAO_UX_2025.md  # Full UX implementation report
├── SWIPER_IMPLEMENTATION_REPORT.md     # Carousel documentation
├── COLOR_PALETTE_PREVIEW.html  # Color palette preview
└── screenshot.png              # Theme screenshot
```

---

## 2. PLUGINS INSTALADOS

**Path:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/plugins/`

### Plugins Ativos:

1. **WooCommerce** (`woocommerce/`)
   - E-commerce platform
   - Integrations with Portuguese payment gateways

2. **WordPress SEO by Yoast** (`wordpress-seo/`)
   - SEO optimization
   - Sitemap & meta descriptions

3. **Cookie Law Info** (`cookie-law-info/`)
   - RGPD compliance
   - Cookie consent banner (CookieYes)

4. **Multibanco IfthenPay Gateway** (`multibanco-ifthen-software-gateway-for-woocommerce/`)
   - Portuguese payment gateway
   - MB Way + Multibanco support

5. **CTT Expresso para WooCommerce** (`ctt-expresso-para-woocommerce/`)
   - Portuguese shipping integration
   - Automatic label generation

6. **Flexible Shipping** (`flexible-shipping/`)
   - Advanced shipping options
   - Zone-based rates

7. **Classic Editor** (`classic-editor/`)
   - Legacy editor support (WP 5.4.1 compatibility)

8. **Regenerate Thumbnails** (`regenerate-thumbnails/`)
   - Image optimization utilities

9. **Akismet** (`akismet/`)
   - Spam protection

10. **MCP Adapter** (`mcp-adapter/`)
    - Custom plugin for MCP integration

---

## 3. SEÇÕES DA HOMEPAGE (Páginas/Blocos)

A homepage é construída com **Gutenberg Blocks** (WordPress native page builder), NÃO com Elementor/WPBakery.

### Estrutura de Seções Identificadas:

**Via custom.js tag (linhas 9-90):**

1. **Hero Section** (`hero-cover-2025`)
   - Full-width cover block
   - Background image com overlay
   - CTA button "Agendar visita"

2. **Coleções em Destaque** (`.is-featured-collections`)
   - Grid de cards com carousel (Swiper.js)
   - Seção dinâmica com animações AOS

3. **Momentos com Chapéus** (`.is-momentos-gallery`)
   - Instagram gallery integration
   - GLightbox lightbox (3.2.0)
   - Swiper carousel implementation

4. **Porque Escolher Chapéus Lisboetas** (`.is-why-choose`)
   - Feature list section
   - Bullet points com animações

5. **Receba Novidades** (`.is-newsletter-cta`)
   - Newsletter signup form
   - Form with AOS fade-up animation

6. **Top Bar Marquee** (`.top-bar-marquee`)
   - Scrolling message: "Envios grátis acima de 50€ · Rua 1.º de Dezembro, 85/87 & R. Áurea 261, Lisboa"

---

## 4. PAGE BUILDER & TECNOLOGIAS

### Page Builder: **Flatsome UX Builder** (NOT Elementor/WPBakery)
- Nativo do tema Flatsome
- Baseado em **Gutenberg Blocks** (WordPress native)
- Localização: `/wordpress/wp-content/themes/flatsome/inc/builder/`

**Key Components:**
- UX Builder core: `inc/builder/core/ux-builder.php`
- Shortcodes: `inc/builder/shortcodes/`
- Components: `inc/builder/components/`

### JavaScript Enhancements (Child Theme):

**Swiper.js** (v11.0.0)
- CDN: `https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js`
- Usado para: Carrosséis de coleções e galeria

**AOS (Animate On Scroll)** (v2.3.4)
- CDN: `https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js`
- Usado para: Fade-up animations em seções

**GLightbox** (v3.2.0)
- CDN: `https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/js/glightbox.min.js`
- Usado para: Instagram gallery lightbox

### Enqueue Points (functions.php):
- Swiper.js: Line 3-25
- AOS: Line 27-50
- GLightbox: Line 52-75
- Custom JS: Line 78-94 (cache busting com filemtime)

---

## 5. ARQUIVOS-CHAVE PARA EDIÇÃO

### CSS Customizações:

1. **Child Theme Stylesheet** ⭐ PRIMARY
   - **Path:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/themes/flatsome-child/style.css`
   - **Size:** 3,036 lines
   - **Seções principais:**
     - Lines 44-120: Color variables & typography
     - Lines 1,000-1,600: Component styling
     - Lines 1,900-2,100: P0 Critical Fixes (Hero, overlay, contrast)

2. **Parent Theme Stylesheet**
   - **Path:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/themes/flatsome/style.css`
   - **Size:** 618 bytes (minimal - defers to child)
   - **Use:** Don't edit - child theme overrides

### JavaScript Customizações:

1. **Custom JS** ⭐ PRIMARY
   - **Path:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/themes/flatsome-child/assets/js/custom.js`
   - **Responsável por:**
     - Seção tagging (`.is-featured-collections`, `.is-momentos-gallery`, etc.)
     - Carousel initialization (Swiper)
     - Animation triggers (AOS)
     - Newsletter form integration

### PHP Functions:

1. **Child Theme Functions** ⭐ PRIMARY
   - **Path:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/themes/flatsome-child/functions.php`
   - **Size:** 22K
   - **Key functions:**
     - `chapeus_enqueue_swiper()` - Load Swiper.js
     - `chapeus_enqueue_aos()` - Load AOS
     - `chapeus_enqueue_glightbox()` - Load GLightbox
     - `tagDynamicSections()` - Tag sections for styling
     - Frontend-only customizations (is_admin() checks)

2. **Parent Theme Functions** 
   - **Path:** `/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/themes/flatsome/functions.php`
   - **Size:** 932 bytes (minimal)
   - **Use:** Don't edit - parent theme logic

### Header/Footer Templates:

**Header Files:**
- `/wordpress/wp-content/themes/flatsome/template-parts/header/header-wrapper.php`
- `/wordpress/wp-content/themes/flatsome/template-parts/header/header-top.php`
- `/wordpress/wp-content/themes/flatsome/template-parts/header/header-main.php`
- `/wordpress/wp-content/themes/flatsome/template-parts/header/header-bottom.php`
- `/wordpress/wp-content/themes/flatsome/template-parts/header/page-loader.php`

**Header Partials:**
- `/wordpress/wp-content/themes/flatsome/template-parts/header/partials/` (26 files)

**Footer Files:**
- `/wordpress/wp-content/themes/flatsome/template-parts/footer/`

---

## 6. DESIGN SYSTEM (Child Theme)

### Color Variables (style.css, lines 44-120):
```css
/* BRAND CORE */
--chap-primary: #8B4513;           /* Saddle Brown */
--chap-primary-light: #A0522D;     /* Sienna - Hover */
--chap-primary-dark: #654321;      /* Dark Saddle */

/* ACTION COLORS */
--chap-action-primary: #E07A31;    /* Terracotta - CTAs */
--chap-action-hover: #C77E3B;      /* Darker Terracotta */
--chap-action-light: #F4A460;      /* Sandy Brown */

/* CONTRAST */
--chap-contrast-dark: #2C323A;     /* Deep Navy */
--chap-contrast-medium: #36454F;   /* Charcoal */
--chap-contrast-light: #5B7B8F;    /* Slate Blue */

/* SUPPORTING */
--chap-soft-rose: #D8A29E;         /* Soft Rose */
--chap-highlight: #F4E4C1;         /* Cream */
```

### Typography:
- **Headings:** Cormorant Garamond (elegant serif)
- **Body:** Inter (modern sans-serif)
- **Base size:** 16px
- **Line height:** 1.6

### WCAG Compliance:
- Terracotta on White: 4.54:1 (AA)
- Saddle Brown on Cream: 5.2:1 (AA)
- Navy on White: 12.8:1 (AAA)

---

## 7. HOMEPAGE DETECTION (Front Page Tracking)

**Homepage is identified via:**
- WordPress: `is_front_page()` conditional
- Custom JS: Text matching in heading elements:
  - "coleções em destaque"
  - "momentos com chapéus"
  - "porque escolher"
  - "receba novidades"

**Frontend Hooks (custom.js):**
- `tagDynamicSections()` - Runs on DOM ready
- Adds CSS classes to sections for styling
- Triggers AOS animations
- Initializes Swiper carousels

---

## 8. WooCommerce INTEGRATION

**Templates Override Location:**
- `/wordpress/wp-content/themes/flatsome/woocommerce/`

**Key Directories:**
- `cart/` - Shopping cart templates
- `checkout/` - Checkout page templates
- `global/` - Global WooCommerce templates
- `loop/` - Product loop & listing
- `single-product/` - Single product page
- `myaccount/` - User account pages

**Portuguese Integrations:**
1. **IfthenPay Gateway** - Multibanco + MB Way (0.8-1% fees)
2. **CTT Expresso** - Shipping with automatic labels
3. **Flexible Shipping** - Zone-based rates

---

## 9. QUICK REFERENCE PATHS

| Component | Path | Notes |
|-----------|------|-------|
| **Child Theme CSS** | `/wordpress/wp-content/themes/flatsome-child/style.css` | PRIMARY - Edit here |
| **Child Theme JS** | `/wordpress/wp-content/themes/flatsome-child/assets/js/custom.js` | PRIMARY - Edit here |
| **Child Theme PHP** | `/wordpress/wp-content/themes/flatsome-child/functions.php` | PRIMARY - Edit here |
| **Parent Theme** | `/wordpress/wp-content/themes/flatsome/` | DO NOT EDIT |
| **WooCommerce** | `/wordpress/wp-content/plugins/woocommerce/` | Plugin - DO NOT EDIT core |
| **Header Templates** | `/wordpress/wp-content/themes/flatsome/template-parts/header/` | Flatsome defaults |
| **Footer Templates** | `/wordpress/wp-content/themes/flatsome/template-parts/footer/` | Flatsome defaults |
| **UX Builder** | `/wordpress/wp-content/themes/flatsome/inc/builder/` | Page builder logic |
| **Plugin List** | `/wordpress/wp-content/plugins/` | 10 plugins active |

---

## 10. LOCAL ENVIRONMENT

**Docker Services:**
- WordPress: `chapeus_wordpress` (Port 8080)
- MySQL: `chapeus_mysql` (Port 3306)
- phpMyAdmin: Port 8081

**Database:**
- Name: `lisboetas_web`
- User: `lisboetas`
- Password: `e$$4rU9h8`
- Root: `rootpassword`
- Prefix: `lx_`

**Access URLs:**
- Site: `http://localhost:8080`
- Admin: `http://localhost:8080/wp-admin`
- phpMyAdmin: `http://localhost:8081`

---

## 11. RECENT CHANGES (From git log)

**Latest commits:**
1. a59aeb9d - feat(ux): Complete Phase 1 optimization - All client feedback applied
2. 462900ad - feat(ux): Complete Phase 1 fixes - All critical issues resolved
3. 7f986e64 - fix(critical): Inline CSS para GARANTIR fixes no browser
4. 2c7a059b - feat(ux): P1 Zebra Section Backgrounds Auto-Apply
5. a8691349 - fix(ux): ISSUE-010 Sobre-Nós Hero Section Background Color

**Current Branch:** `ux-improvements-fase1-p0`
**Main Branch:** `clean-main`

---

## 12. DEPLOYMENT NOTES

**Theme Child Path (for Docker/Production):**
```bash
# In Docker:
/var/www/html/wp-content/themes/flatsome-child/

# Local macOS:
/Users/bilal/Programaçao/Tiago Andrado/full-chapeus-lisboetas (2)/wordpress/wp-content/themes/flatsome-child/
```

**Cache Busting:**
- Child theme uses `filemtime()` on custom.js
- CSS changes require browser hard refresh (Cmd+Shift+R / Ctrl+F5)
- WP Rocket cache should be cleared if installed

**Performance Targets:**
- PageSpeed Mobile: >85
- PageSpeed Desktop: >90
- LCP: <2.5s
- CLS: <0.1

---

## 13. DOCUMENTATION FILES IN CHILD THEME

All in: `/wordpress/wp-content/themes/flatsome-child/`

1. **P0_QUICK_REFERENCE.md** (266 lines)
   - Quick checklist for Phase 0 validations
   - Testing procedures
   - Troubleshooting

2. **P0_VALIDATION_REPORT.md**
   - Technical validation of Phase 0 changes
   - WCAG compliance testing
   - Performance metrics

3. **RELATORIO_IMPLEMENTACAO_UX_2025.md** (extensive)
   - Full UX implementation details
   - Color system documentation
   - Component styling guide

4. **DESIGN_SYSTEM_REPORT.md**
   - Design system specifications
   - Color palette
   - Typography rules

5. **SWIPER_IMPLEMENTATION_REPORT.md**
   - Carousel implementation details
   - JavaScript integration guide

6. **COLOR_PALETTE_PREVIEW.html**
   - Interactive color palette preview
   - WCAG contrast checker results

---

## 🎯 SUMMARY FOR DEVELOPERS

### To edit the homepage:

1. **CSS styling:** Edit `/wordpress/wp-content/themes/flatsome-child/style.css`
   - Use color variables defined at top
   - Sections tagged by custom.js (`.is-featured-collections`, etc.)

2. **JavaScript:** Edit `/wordpress/wp-content/themes/flatsome-child/assets/js/custom.js`
   - Section detection & tagging
   - Carousel & animation initialization

3. **PHP functions:** Edit `/wordpress/wp-content/themes/flatsome-child/functions.php`
   - Enqueue scripts/styles
   - Filter homepage content
   - Add custom hooks

4. **Homepage content:** Edit in WordPress admin
   - Site > Home page (via WordPress page editor)
   - Uses Gutenberg blocks (WordPress native)
   - No Elementor/WPBakery

5. **Header/Footer:** Edit in Flatsome theme settings OR create overrides in child theme template-parts/

### Do NOT edit:
- Parent theme files (`/flatsome/`)
- Plugin core files
- Database tables directly (use WordPress functions)

---

**Last Updated:** November 6, 2025
**Project:** Chapéus Lisboetas - Phase 1 UX Improvements
**Status:** Active Development Branch (ux-improvements-fase1-p0)

