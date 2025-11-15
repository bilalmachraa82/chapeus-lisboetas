# Project Overview

This project is a collection of scripts designed to manage and enhance a WooCommerce product catalog for an online hat store, "Chapéus Lisboetas". The core functionality revolves around using Google's Gemini AI to generate high-quality, editorial-style product images and integrate them into a WordPress/WooCommerce environment.

The project uses a combination of Python, Node.js, and shell scripts to automate the entire workflow, from data extraction and AI image generation to updating the live e-commerce site.

## Key Technologies

*   **Backend:** Python, Node.js
*   **AI:** Google Gemini 2.5 Flash Image
*   **E-commerce Platform:** WordPress with WooCommerce
*   **Database:** (Implicitly) MySQL/MariaDB for WordPress
*   **Containerization:** Docker (for the WordPress environment)
*   **Image Processing:** Pillow
*   **Dependencies (Python):** `google-genai`, `google-api-core`, `pillow`
*   **Dependencies (Node.js):** `csv-parse`, `node-fetch`

## Architecture

The project follows a script-based architecture, where individual scripts are responsible for specific tasks in a larger pipeline. The main components are:

1.  **Data Scripts:** A variety of scripts for cleaning, exporting, and preparing the product catalog data (e.g., `export_master_catalog.py`, `clean_duplicate_products.py`).
2.  **AI Image Generation:** The `gemini_editorial_v2.py` script is the heart of the AI integration. It reads product data, generates prompts, and uses the Gemini API to create three distinct, professional-looking images for each product.
3.  **Image Upload & Processing:** The `upload-all-images.js` script handles uploading images to a Supabase edge function, likely for a Shopify integration. Other scripts like `optimize_ai_images.py` and `regenerate_thumbnails.sh` are used for image management.
4.  **WordPress/WooCommerce Integration:** Several scripts interact directly with the WordPress site via `wp-cli` inside a Docker container to register new images, update product galleries, and set featured images (e.g., `register_enhanced_images.py`, `associate_enhanced_images.py`).
5.  **Orchestration:** The `complete_ai_integration.sh` shell script acts as a master pipeline, executing all the necessary steps in the correct order to fully integrate the AI-generated content.

## Building and Running

### Prerequisites

*   Python 3 with `pip`
*   Node.js with `npm`
*   Docker
*   A running WordPress Docker container named `chapeus_wordpress`.

### Installation

1.  **Python Dependencies:**
    ```bash
    pip install google-genai google-api-core pillow
    ```

2.  **Node.js Dependencies:**
    ```bash
    npm install
    ```

### Key Commands

*   **Run the full AI integration pipeline:**
    ```bash
    ./scripts/complete_ai_integration.sh
    ```
    *To run in test mode without making actual changes, use the `--dry-run` flag.*

*   **Generate AI editorial photos for products:**
    ```bash
    # For a few test products
    python3 scripts/gemini_editorial_v2.py --test

    # For the entire catalog
    python3 scripts/gemini_editorial_v2.py
    ```

*   **Upload images to Shopify (via Supabase):**
    ```bash
    node scripts/upload-all-images.js
    ```

## Development Conventions

*   **Configuration:** Scripts are configured via environment variables (e.g., `GEMINI_KEY_PRIMARY`, `SUPABASE_EDGE_URL`) and command-line arguments.
*   **Modularity:** The workflow is broken down into smaller, single-purpose scripts, which are then composed into larger pipelines.
*   **Error Handling:** Scripts generally include error handling and logging. The main pipeline script (`complete_ai_integration.sh`) exits on error.
*   **Reporting:** The pipeline generates detailed reports in the `relatorios/` directory, tracking the progress and outcome of the AI integration.
*   **Idempotency:** Some scripts appear to be designed to be re-runnable, checking for existing data before processing (e.g., `verify_pending_products.py`).
