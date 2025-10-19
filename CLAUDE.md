# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**Client:** Chapéus Lisboeta (Tiago Andrade & Sr. Andrade) - Traditional Portuguese hat retailer in Chiado, Lisbon

**Critical Background:**
- Lost previous site, data, and backups due to provider failure
- Estimated loss: €2,000-€5,000 in sales over 6-12 months recovery period
- **Top Priority:** Data autonomy, robust backups, and anti-loss guarantees
- Timeline: Launch before Black Friday (peak e-commerce season)

**Mission:** Professional, autonomous e-commerce site with complete client control and data protection. The client must NEVER lose data again.

## Tech Stack

**WordPress Environment:**
- WordPress 5.4.1 with PHP 7.4 (legacy version - be cautious with plugin compatibility)
- WooCommerce e-commerce platform
- Flatsome Premium theme (included in project)
- Docker-based development: MariaDB 10.6 + Apache

**Hosting (Production):**
- PTisp Premium (1 year included)
- Datacenter: Lisbon (3ms latency)
- NVMe: 40GB at 3,500 MB/s
- RAM: 3GB dedicated
- Backups: Daily for 30 days (JetBackup) with 1-click restore
- Security: Imunify360 + Anti-DDoS 40 Gbps
- Support: 24/7 phone support (<15 min response)

**Payment & Shipping (Portugal-specific):**
- IfthenPay gateway (MB Way + Multibanco, 0.8-1% fees, preferred by 70% of Portuguese customers)
- CTT Expresso shipping with automatic tracking and label generation

**Automation & AI:**
- Python scripts for catalog/image processing
- Google Sheets as master product catalog
- Google Gemini Flash 2.5 for AI image generation
- Node.js/Puppeteer for web scraping
- Supabase MCP for database operations

## Environment Setup

**Prerequisites:**
- Python 3.9+ (currently using Python 3.9.6)
- Docker Desktop (for WordPress local dev)
- Node.js 18+ (for Puppeteer/MCP tools)

**Install Python dependencies:**
```bash
# Core Google Sheets integration
pip install gspread google-auth gspread-formatting

# Catalog management
pip install pandas requests beautifulsoup4 openpyxl pillow

# Image processing (Gemini AI)
pip install -r requirements-image-processing.txt
# Contains: google-generativeai, requests, Pillow, instaloader, python-dotenv, tqdm
```

**Environment variables:**
```bash
# Required for Google Sheets access
export GOOGLE_SHEETS_ID="1m5ObJBG3CXetWNN9BoXwE69EVA5RH-xMqozhY3d7ptw"
export GOOGLE_SERVICE_ACCOUNT_FILE="config/google-service-account.json"
export GOOGLE_SHEETS_TAB="Catalogo"  # optional, defaults to "Catalogo"

# Required for image processing
export GEMINI_API_KEY="your_gemini_api_key"  # Get from https://makersuite.google.com/app/apikey

# Optional
export IMAGE_BASE_URL="https://chapeuslisboeta.pt/wp-content/uploads/"
```

**Note:** Service account `sheets-api-reader@corded-smithy-453023-b7.iam.gserviceaccount.com` has read/write access to the Google Sheet. Credentials are in `config/google-service-account.json` (already configured).

## Common Development Commands

### Docker Environment

```bash
# Start WordPress + MySQL containers
docker-compose up -d

# Stop containers
docker-compose stop

# View logs
docker logs chapeus_wordpress -f
docker logs chapeus_mysql -f

# Access WordPress container shell
docker exec -it chapeus_wordpress bash

# Access MySQL directly
docker exec -it chapeus_mysql mysql -u root -prootpassword lisboetas_web

# Backup database
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup.sql

# Fix permissions after adding themes/plugins
docker exec chapeus_wordpress chown -R www-data:www-data /var/www/html/wp-content
```

**Important:** If Flatsome theme is missing after restart:
```bash
# Reinstall Flatsome theme
cd /Users/bilal/Programaçao/Tiago\ Andrado/full-chapeus-lisboetas\ \(2\)
unzip -q flatsome-extracted/Theme\ Files/flatsome.zip -d wordpress/wp-content/themes/
unzip -q flatsome-extracted/Theme\ Files/flatsome-child.zip -d wordpress/wp-content/themes/
docker exec chapeus_wordpress chown -R www-data:www-data /var/www/html/wp-content/themes/flatsome*
```

**Local URLs:**
- Site: http://localhost:8080
- Admin: http://localhost:8080/wp-admin
- phpMyAdmin: http://localhost:8081

**Database credentials:**
- Host: localhost:3306
- Database: `lisboetas_web`
- User: `lisboetas`
- Password: `e$$4rU9h8`
- Root password: `rootpassword`
- Table prefix: `lx_` (not standard `wp_`)

### Python Catalog Management

```bash
# Install dependencies
pip install gspread google-auth gspread-formatting pandas requests beautifulsoup4

# Environment setup
export GOOGLE_SHEETS_ID="1m5ObJBG3CXetWNN9BoXwE69EVA5RH-xMqozhY3d7ptw"
export GOOGLE_SERVICE_ACCOUNT_FILE="config/google-service-account.json"

# Sync Google Sheet to local catalog
python3 scripts/sync_google_sheet.py

# Apply formatting and create dashboard tabs in Google Sheet
python3 scripts/beautify_google_sheet.py

# Generate WooCommerce-ready catalog
python3 scripts/generate_wc_catalog.py

# Scrape product details from supplier site
python3 scripts/catalog_scraper.py

# Export summaries
python3 scripts/export_catalog_summary.py
python3 scripts/export_master_catalog.py
```

### Image Processing Pipeline

```bash
# Install image processing dependencies
pip install -r requirements-image-processing.txt

# Download Instagram photos and generate professional e-commerce images
python3 instagram-to-professional-images.py --limit 10

# Dry run (download only, no AI processing)
python3 instagram-to-professional-images.py --limit 5 --dry-run

# Process with custom username
python3 instagram-to-professional-images.py --username chapeuslisboetas --limit 20
```

The image pipeline uses Google Gemini Flash 2.5 to transform Instagram photos into 4 professional e-commerce images per product (front view, 3/4 angle, detail close-up, lifestyle).

### Node.js/Puppeteer

```bash
# Install dependencies
npm install

# Scripts use Puppeteer for web automation
node download_from_shortcodes.py  # Example scraper
```

## Architecture

### Catalog Management Flow (Current Workflow)

```
Google Sheets "WEBSITE Produtos Catálogo"
  (17 worksheets: BOINAS INVERNO, VERÃO, PANAMÁ, etc.)
    ↓
sync_google_sheet.py
  - Pulls all product data from all worksheets
  - Merges with existing catalogo.json
  - Auto-scrapes missing descriptions from supplier URLs
    ↓
catalogo.json (local cache - 62 products with prices)
    ↓
validate_and_enrich.py
  - Validates all image URLs
  - Downloads images to output_catalogo/images/{SKU}/
  - Creates Clean & Ready / Pendentes reports
    ↓
beautify_google_sheet.py
  - Creates Dashboard, Faltas, Resumos tabs
  - Applies brand formatting (#EECAC9 / #A8DADF)
  - Adds Status/Preview columns with formulas
    ↓
generate_wc_catalog.py
  - Generates WooCommerce CSV import file
  - Maps categories (BOINAS INVERNO → Chapéus > Boinas > Inverno)
  - Includes images, specs, descriptions
    ↓
WordPress/WooCommerce Import
  - Products → Import CSV
  - Assign images from Media Library
  - Product goes live
```

**Key files:**
- `scripts/sync_google_sheet.py`: Pulls data from 17 Google Sheet tabs → catalogo.json (with auto-scraping)
- `scripts/validate_and_enrich.py`: Validates URLs, downloads images, creates clean/pending reports
- `scripts/beautify_google_sheet.py`: Formats sheet, creates Dashboard/Faltas/Resumos tabs
- `scripts/catalog_scraper.py`: Scrapes hologrammeparis.com for descriptions/specs
- `scripts/generate_wc_catalog.py`: Creates WooCommerce CSV with category mapping
- `output_catalogo/catalogo.json`: Master catalog (62 products validated)
- `output_catalogo/catalogo_clean_ready.csv`: Products ready for WooCommerce
- `output_catalogo/catalogo_pending.csv`: Products needing manual review
- `output_catalogo/images/{SKU}/`: Downloaded product images organized by SKU

### Google Sheets Structure

**Master Google Sheet:** `https://docs.google.com/spreadsheets/d/1m5ObJBG3CXetWNN9BoXwE69EVA5RH-xMqozhY3d7ptw/edit`

**Sheet Name:** "WEBSITE Produtos Catálogo"

**Available Worksheets (Product Categories):**
- BOINAS INVERNO (Winter Berets - priority 1)
- BOINAS VERÃO (Summer Berets - priority 2)
- PANAMÁ (Panama Hats - priority 3)
- ARTIGOS EM PELE, CORTIÇA, GORROS, CHAPÉUS LÃ, DIVERSOS, FEMININO, CERIMÓNIA, PALHA
- À PROVA D'ÁGUA, PROTEÇÃO SOLAR, CHAPÉUS EM TECIDO, VISEIRAS, BONÉS, COWBOY

**Main tab: `Catalogo`** (to be created by scripts)
- Columns: SKU, Nome, Preço, Descrição curta, Descrição longa, Tags, Cor, Tamanho, Composição, Pack, URL fornecedor, URLs extra, Imagens, Prioridade, Destaque homepage?, Última atualização, Responsável, Notas internas
- Auto-generated `Status` column: OK / Sem foto / Sem preço / Rever link / Sem descrição (with conditional color formatting: green/amber/red)
- Auto-generated `Preview` column: Uses `IMAGE()` formula with 120×120px thumbnails (row height: 140px)
- Header formatting: Brand colors (#EECAC9 Rose / #A8DADF Aqua) with Montserrat typography
- First 3 columns frozen for easy navigation

**Auto-generated tabs** (created by `beautify_google_sheet.py`):
- `Dashboard`: KPIs (total products, pending items, featured products), sparkline coverage charts, quick links
- `Faltas`: Products missing images from `relatorios/produtos_sem_imagem.csv`, with "Nova URL/Foto" + "Notas" tracking columns
- `Resumo Coleções`: Summary by collection type from `output_catalogo/catalogo_summary_sheet.csv`
- `Resumo Tipos`: Summary by product category from `output_catalogo/catalogo_summary_sheet_tipo.csv`
- `Histórico`: Change log (onEdit timestamps, author, old/new values) - requires Apps Script
- `Guia`: Quick reference guide with CLI commands and workflow instructions
- `Clean & Ready`: Validated products ready for WooCommerce import (from `validate_and_enrich.py`)
- `Pendentes`: Products with gaps/scrape failures requiring manual review

**Current Status (Oct 2025):**
- Base catalog: **62 products** with prices and unique URLs → `output_catalogo/catalogo_master_with_price.csv`
- **Latest validation (validate_and_enrich.py):** 54 clean / 8 pending
  - `catalogo_clean_ready.csv` - 54 products ready for WooCommerce import
  - `catalogo_pending.csv` - 8 products needing manual review (missing descriptions/compositions)
- Google Sheet accessible via service account (verified ✓)
- Premium layout applied: Dashboard with KPIs (54 validados / 8 pendentes), Clean & Ready tab, Pendentes tab with "Observações"
- Images: Downloaded and organized in `output_catalogo/images/{SKU}/`
- Reconciliation reports: `catalogo_comparison_detail.csv`, `catalogo_comparison_summary.csv`

**Product Priority Order:**
1. **BOINAS INVERNO** (prioridade máxima - peak season)
2. **BOINAS VERÃO** (prioridade alta)
3. **PANAMÁ** (prioridade média)
4. **Other categories** (prioridade normal)

### Apps Script Integration

Copy `apps_script/catalogo.gs` to Google Sheets Apps Script editor for:
- Auto-timestamp on edits (`onEdit` trigger)
- Author tracking
- Change history logging
- URL validation
- Duplicate SKU detection
- Custom menu "Chapéus Premium"

### Image Processing Architecture

```
Google Sheet "Imagens" column (Google Photos links)
    ↓
validate_and_enrich.py
    ↓
[Validate URLs] → Check accessibility
    ↓
[Download images] → output_catalogo/images/{SKU}/
    ↓
[Organize by product] → Multiple angles per SKU
    ↓
WooCommerce Media Library
```

**Image sources (priority order):**
1. Google Photos links in "Imagens" column (client's photos)
2. Supplier URLs in "URL fornecedor" column (hologrammeparis.com)
3. URLs extra column (additional sources)

**Optional AI enhancement:**
- `instagram-to-professional-images.py` available if needed to transform casual photos
- Uses Gemini Flash 2.5 to generate professional e-commerce images
- Currently not in active use (using direct supplier images)

### WordPress Database Structure

- Custom table prefix: `lx_` instead of `wp_`
- WooCommerce product meta stored in `lx_postmeta`
- Portuguese payment gateway integrations (Multibanco, Moloni)
- 381MB media library in `backup/wp/wp-content/uploads/`

## Critical Business Rules

### Catalog Management
- **NO PRICE = NO PUBLISH:** Products without price in Google Sheet are IGNORED (physical store only, not e-commerce)
- **SKU Variations:** Same SKU base + different letters (18456-A, 18456-B) = product variations (fabric/color)
- **Priority Import Order:** Winter → Summer → Panama → Others (matching peak sales seasons)
- **Supplier Authorization:** Full permission to use images and copy content from hologrammeparis.com
- **Image Requirements:** Minimum 1500×1500px, high resolution, multiple angles preferred, front view MANDATORY as main image

### Design References & Style
- **Rothys.com:** Elegant image+text combinations, balanced proportions, clean dropdown menus, hero sections
- **American Apparel:** Maximum practicality, obvious/direct text, fast navigation (≤3 clicks to any product)
- **Brand Colors:** To be defined with client (palette codes in HEX)
- **Typography:** Elegante for headings, clean sans-serif for body, 16px base size, 1.6 line-height
- **Spacing:** 8px base unit for all spacing

### WordPress Configuration
- **Legacy WordPress:** v5.4.1 (May 2020) on PHP 7.4 - be cautious with plugin compatibility
- **Database prefix:** `lx_` not `wp_` - ALWAYS use this prefix for direct queries
- **Revolution Slider:** Disabled due to PHP 7.4 incompatibility
- **URLs:** Production domain references may exist; use "Better Search Replace" plugin for migrations

### Required Integrations (Non-Negotiable)
- **Payment:** IfthenPay (MB Way + Multibanco) - Portuguese market standard
- **Shipping:** CTT Expresso with automatic labels and tracking
- **RGPD:** CookieYes banner, full privacy policy, opt-in checkboxes
- **SEO:** Yoast with schema markup (Organization, LocalBusiness, Product, BreadcrumbList)
- **Analytics:** Google Analytics 4 + GTM with e-commerce events
- **Translation:** WPML PT/EN (bonus if accepted before Oct 11)
- **Cache:** WP Rocket for performance
- **Backups:** UpdraftPlus (redundancy on top of hosting backups)

### Image Management
- **Source:** Product images from Google Photos links in Google Sheet "Imagens" column
- **Optional AI Enhancement:** Gemini Flash 2.5 can transform casual photos → professional e-commerce images (not currently in use)
- **Current approach:** Direct use of supplier images from URLs in Google Sheet
- **Image validation:** `validate_and_enrich.py` checks URLs and downloads images
- **Storage:** Images organized in `output_catalogo/images/` by SKU

## MCP Integration

This project uses Supabase MCP for potential database operations (configured in `mcp_config.json`). Chrome DevTools MCP available for browser automation:

```bash
# Start Chrome DevTools MCP server
npx -y chrome-devtools-mcp@latest
```

## Development Workflow

### 1. Update Product Catalog
```bash
# Edit Google Sheet directly (client or developer)
# Then sync to local cache
python3 scripts/sync_google_sheet.py

# Generate WooCommerce import CSV
python3 scripts/generate_wc_catalog.py

# Import via WordPress admin or WP-CLI
# WooCommerce → Products → Import
```

### 2. Validate and Download Product Images
```bash
# Validate URLs and download images from Google Sheet
python3 scripts/validate_and_enrich.py

# Output:
# - Checks all "Imagens" and "URL fornecedor" columns
# - Downloads images to output_catalogo/images/{SKU}/
# - Creates catalogo_clean_ready.csv (products ready for WooCommerce)
# - Creates catalogo_pending.csv (products needing manual review)

# Optional: AI image enhancement (if needed in future)
# python3 instagram-to-professional-images.py --limit 10
```

### 3. Scrape Supplier Product Data
```bash
# Scrape descriptions/specs from hologrammeparis.com
python3 scripts/catalog_scraper.py

# Auto-enriches catalogo.json with:
# - Long descriptions
# - Materials/composition
# - Technical specifications
```

### 4. Database Operations
```bash
# ALWAYS backup first
docker exec chapeus_mysql mysqldump -u root -prootpassword lisboetas_web > backup_$(date +%Y%m%d).sql

# Direct SQL queries (remember lx_ prefix!)
docker exec -it chapeus_mysql mysql -u root -prootpassword lisboetas_web

# Example: Update site URLs
docker exec chapeus_mysql mysql -u root -prootpassword lisboetas_web -e \
  "UPDATE lx_options SET option_value = 'http://localhost:8080'
   WHERE option_name IN ('siteurl', 'home');"
```

### 5. Testing & Quality Assurance
- **Local site:** http://localhost:8080
- **Admin panel:** http://localhost:8080/wp-admin
- **Database UI:** http://localhost:8081 (phpMyAdmin)
- **Performance target:** PageSpeed >85 mobile, >90 desktop
- **Browser testing:** Chrome, Firefox, Safari (desktop + mobile)

## Decision-Making Guidelines

### FLEXIBLE (Claude has autonomy):
- File organization and structure
- Tool selection (if better alternatives exist)
- Implementation order (if logic is more efficient)
- Visual design details (within provided references)
- Technical component naming (as long as documented)

### RIGID (non-negotiable):
- All promised client functionalities must be delivered
- Stack: WordPress, WooCommerce, Flatsome theme
- Integrations: IfthenPay, CTT Expresso, RGPD compliance
- Timeline: 4-6 weeks for Phase 1
- Budget: €1,887 for Phase 1
- Security and backup guarantees (anti-data-loss priority)
- RGPD legal compliance (mandatory in Portugal)
- Catalog structure from Google Sheet (import as-is)

### ALWAYS ASK BEFORE:
- Choices affecting budget (extra paid plugins)
- Impactful design decisions (layout, colors, UX)
- Scope changes from agreed project
- Removing promised functionalities
- Changing core tech stack

## Project Phases

**Phase 1 (4-6 weeks, €1,887):**
- WordPress setup + Flatsome theme
- WooCommerce configuration
- Complete catalog import
- IfthenPay + CTT integration
- RGPD compliance (CookieYes)
- SEO setup (Yoast)
- Client training (1h session)
- 3 months support included

**Phase 2 (Optional, €1,348-€1,938):**
- AI Chatbot (Tidio/Elfsight, 24/7 support)
- Automated product importer (web scraper + WooCommerce API)
- Scheduled updates (cron jobs)
- ~€500/year maintenance after Year 1

**Current Status:** Phase 1 in development, catalog foundation with 62 products ready, Google Sheets dashboard implemented

## Python Scripts Status & Verification

### ✅ Verified Working Scripts

All Python scripts **compile successfully** and key dependencies are **installed and working**:

**Dependencies Status:**
- ✓ `gspread` - Google Sheets API client
- ✓ `google-auth` - Google OAuth2 authentication
- ✓ `gspread-formatting` - Advanced sheet formatting
- ✓ `requests` - HTTP client
- ✓ `beautifulsoup4` - HTML parsing

**Google Sheet Access:**
- ✓ Service account credentials configured (`config/google-service-account.json`)
- ✓ Connection to sheet `1m5ObJBG3CXetWNN9BoXwE69EVA5RH-xMqozhY3d7ptw` verified
- ✓ Sheet title: "WEBSITE Produtos Catálogo"
- ✓ 17 product category worksheets accessible

**Core Scripts (in execution order):**
1. `scripts/sync_google_sheet.py` - ✓ Syncs all 17 worksheets from Google Sheet → `catalogo.json`
2. `scripts/validate_and_enrich.py` - ✓ Validates URLs, downloads images, scrapes descriptions → `catalogo_clean_ready.csv` + `catalogo_pending.csv`
3. `scripts/beautify_google_sheet.py` - ✓ Creates Dashboard/Faltas/Clean & Ready/Pendentes tabs with premium formatting
4. `scripts/generate_wc_catalog.py` - ✓ Generates WooCommerce import CSV with category mapping
5. `scripts/catalog_scraper.py` - ✓ Helper: Scrapes hologrammeparis.com product pages
6. `instagram-to-professional-images.py` - ⚠️ Optional: AI image enhancement (not in current workflow)

**Known Issues:**
- ⚠️ urllib3 warning about OpenSSL (non-blocking, LibreSSL 2.8.3 vs OpenSSL 1.1.1+ - affects SSL but doesn't break functionality)
- Import order issue in `sync_google_sheet.py` line 222-226: `scrape_product_page` import should be at top of file (currently works but not PEP8 compliant)

### 🔧 Scripts Requiring Setup

**For `instagram-to-professional-images.py`:**
```bash
# Install dependencies
pip install -r requirements-image-processing.txt

# Set API key
export GEMINI_API_KEY="your_key_from_makersuite.google.com"

# Test with dry run
python3 instagram-to-professional-images.py --limit 5 --dry-run
```

**For catalog scraping:**
- Ensure `openpyxl` installed: `pip install openpyxl`
- Verify Excel file path: `WEBSITE Produtos Catálogo.xlsx` in project root

## Client Information

**Store Details:**
- **Physical location:** Chiado, Lisboa (traditional Portuguese neighborhood)
- **Owner:** Tiago Andrade & Sr. Andrade
- **Phone/WhatsApp:** +351 918 911 308
- **Instagram:** @chapeuslisboetas (372 posts available for image processing)
- **Main supplier:** hologrammeparis.com (authorized content use)

**Admin Users in Database:**
- vm (pb@virtualmente.pt)
- lisboetas (mail@chapeuslisboetas.com)
- well (wellcardoso.pt@gmail.com)

**Meeting Schedule:**
- Weekly meetings: Fridays 15h (60 min)
- Client availability: 10h-16h weekdays
- Response time: <24h email, <2h WhatsApp (9h-18h)

## Key Performance Metrics (Success Criteria)

**Technical (Launch):**
- PageSpeed Mobile: >85
- PageSpeed Desktop: >90
- Time to First Byte: <600ms
- SSL Rating: A+ (SSLLabs)
- Zero 404 errors on internal links

**Business (30 days post-launch):**
- Conversion rate: >1% (e-commerce fashion average)
- Bounce rate: <60%
- Pages/session: >2.5
- Cart abandonment: <70%
- Newsletter sign-ups: >2% of visitors

**SEO (30 days):**
- Google impressions: >1,000/month
- Organic clicks: >50/month
- Top 10 keywords: >5 (branded + generic)
- All pages with meta descriptions: 100%
- Image alt text coverage: >95%

## Support & Maintenance

**Included (3 months, no extra cost):**
- Bug fixes and corrections
- Minor design adjustments
- Backoffice usage questions
- Core/plugin updates
- Backup restoration if needed
- Small configuration changes

**Post-3 months options:**
- Option A: Full client autonomy (free, manual provided)
- Option B: Maintenance plan (€150/month, 2h dev included)
- Option C: Pay-as-you-go (€75/hour, 1h minimum)

**Emergency contacts:**
- PTisp hosting: 24/7 phone support
- Bilal/AiParaTi: 3 months included support
- Procedure documented in client manual

---

**Project prepared by:** Bilal Machraa / AiParaTi
**For:** Chapéus Lisboeta (Tiago Andrade)
**Date:** October 2025
**Version:** 1.0
**Mission:** "Complete data protection and Portuguese premium technology. This time, with total guarantees."
