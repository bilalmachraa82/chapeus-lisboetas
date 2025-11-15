#!/bin/bash
# Simple manual import of 9 remaining test products
# Uses exact workflow that worked for gorro-miki-12601

set -e  # Exit on error

echo "🚀 IMPORTING REMAINING TEST PRODUCTS"
echo "======================================"

# Function to import one product
import_product() {
    local SEARCH_TERM="$1"
    local EDITORIAL_PATH="$2"
    local ANGLE_PATH="$3"
    local LIFESTYLE_PATH="$4"
    local PRODUCT_NAME="$5"

    echo ""
    echo "====================================================================="
    echo "📦 $PRODUCT_NAME"
    echo "====================================================================="

    # Find product
    echo "  🔍 Searching for product..."
    PRODUCT_ID=$(docker exec chapeus_wordpress wp post list \
        --post_type=product \
        --s="$SEARCH_TERM" \
        --fields=ID \
        --format=csv \
        --allow-root | tail -n 1)

    if [ -z "$PRODUCT_ID" ]; then
        echo "  ❌ Product not found for: $SEARCH_TERM"
        return 1
    fi

    echo "  ✓ Found product ID: $PRODUCT_ID"

    # Import Editorial
    echo "  📸 Importing Editorial (Featured)..."
    EDITORIAL_ID=$(docker exec chapeus_wordpress wp media import \
        "$EDITORIAL_PATH" \
        --post_id=$PRODUCT_ID \
        --title="AI - $PRODUCT_NAME - Editorial" \
        --porcelain \
        --allow-root)

    if [ -z "$EDITORIAL_ID" ]; then
        echo "  ❌ Failed to import editorial"
        return 1
    fi

    echo "    ✓ Imported (ID: $EDITORIAL_ID)"

    # Set as featured
    docker exec chapeus_wordpress wp post meta update \
        $PRODUCT_ID _thumbnail_id $EDITORIAL_ID --allow-root
    echo "    ✓ Set as featured image"

    GALLERY_IDS=""

    # Import Angle
    if [ -n "$ANGLE_PATH" ] && [ -f "$ANGLE_PATH" ]; then
        echo "  📸 Importing Angle (Gallery)..."
        ANGLE_ID=$(docker exec chapeus_wordpress wp media import \
            "$ANGLE_PATH" \
            --post_id=$PRODUCT_ID \
            --title="AI - $PRODUCT_NAME - Angle" \
            --porcelain \
            --allow-root)

        if [ -n "$ANGLE_ID" ]; then
            echo "    ✓ Imported (ID: $ANGLE_ID)"
            GALLERY_IDS="$ANGLE_ID"
        fi
    fi

    # Import Lifestyle
    if [ -n "$LIFESTYLE_PATH" ] && [ -f "$LIFESTYLE_PATH" ]; then
        # Extract scenario from path
        SCENARIO="Lifestyle"
        if [[ "$LIFESTYLE_PATH" == *"alfama"* ]]; then
            SCENARIO="Lifestyle Alfama"
        elif [[ "$LIFESTYLE_PATH" == *"eletrico"* ]]; then
            SCENARIO="Lifestyle Elétrico"
        elif [[ "$LIFESTYLE_PATH" == *"miradouro"* ]]; then
            SCENARIO="Lifestyle Miradouro"
        elif [[ "$LIFESTYLE_PATH" == *"tejo"* ]]; then
            SCENARIO="Lifestyle Tejo"
        elif [[ "$LIFESTYLE_PATH" == *"cafe"* ]]; then
            SCENARIO="Lifestyle Café"
        fi

        echo "  📸 Importing $SCENARIO (Gallery)..."
        LIFESTYLE_ID=$(docker exec chapeus_wordpress wp media import \
            "$LIFESTYLE_PATH" \
            --post_id=$PRODUCT_ID \
            --title="AI - $PRODUCT_NAME - $SCENARIO" \
            --porcelain \
            --allow-root)

        if [ -n "$LIFESTYLE_ID" ]; then
            echo "    ✓ Imported (ID: $LIFESTYLE_ID)"
            if [ -n "$GALLERY_IDS" ]; then
                GALLERY_IDS="$GALLERY_IDS,$LIFESTYLE_ID"
            else
                GALLERY_IDS="$LIFESTYLE_ID"
            fi
        fi
    fi

    # Set gallery
    if [ -n "$GALLERY_IDS" ]; then
        docker exec chapeus_wordpress wp post meta update \
            $PRODUCT_ID _product_image_gallery "$GALLERY_IDS" --allow-root
        echo "    ✓ Gallery updated"
    fi

    # Regenerate thumbnails
    echo "  🔄 Regenerating thumbnails..."
    docker exec chapeus_wordpress wp media regenerate \
        $EDITORIAL_ID $GALLERY_IDS --yes --allow-root > /dev/null 2>&1
    echo "    ✓ Thumbnails regenerated"

    echo "  ✅ SUCCESS: $PRODUCT_NAME"
    return 0
}

SUCCESS=0
FAILED=0

# PRODUCT 1: Luvas Masculinas (17119)
import_product "17119" \
    "/var/www/html/wp-content/uploads/products/artigos em pele/gants-17119/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/artigos em pele/gants-17119/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/artigos em pele/gants-17119/img_01_lifestyle_cafe_test.jpg" \
    "Luvas Masculinas" && ((SUCCESS++)) || ((FAILED++))

# PRODUCT 2: Luvas Femininas (17120)
import_product "17120" \
    "/var/www/html/wp-content/uploads/products/artigos em pele/gants-17120/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/artigos em pele/gants-17120/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/artigos em pele/gants-17120/img_01_lifestyle_alfama_test.jpg" \
    "Luvas Femininas" && ((SUCCESS++)) || ((FAILED++))

# PRODUCT 3: Boina Harris Tweed (18438mc)
import_product "18438" \
    "/var/www/html/wp-content/uploads/products/boinas inverno/bone-18438mc-18502mi/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/boinas inverno/bone-18438mc-18502mi/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/boinas inverno/bone-18438mc-18502mi/img_01_lifestyle_tejo_test.jpg" \
    "Boina Harris Tweed" && ((SUCCESS++)) || ((FAILED++))

# PRODUCT 4: Chapéu Feminino Ráfia (970)
import_product "970" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-art-970-pack-12/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-art-970-pack-12/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-art-970-pack-12/img_01_lifestyle_eletrico_test.jpg" \
    "Chapéu Feminino Ráfia" && ((SUCCESS++)) || ((FAILED++))

# PRODUCT 5: Chapéu Impermeável (181056)
import_product "181056" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-impermeavel-art-181056-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_01_lifestyle_cafe_test.jpg" \
    "Chapéu Impermeável" && ((SUCCESS++)) || ((FAILED++))

# PRODUCT 6: Chapéu Dobrável (181054)
import_product "181054" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-impermeavel-art-181054-pack-12-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-impermeavel-art-181054-pack-12-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/chapeu-impermeavel-art-181054-pack-12-tags-fabricado-na-italia-la-esmagavel-impermeavel/img_01_lifestyle_miradouro_test.jpg" \
    "Chapéu Dobrável" && ((SUCCESS++)) || ((FAILED++))

# PRODUCT 7: Boina Jornaleiro (tags-fabricado-na-italia-la-pura)
import_product "jornaleiro" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/tags-fabricado-na-italia-la-pura/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/tags-fabricado-na-italia-la-pura/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/chapéus lã/tags-fabricado-na-italia-la-pura/img_01_lifestyle_cafe_test.jpg" \
    "Boina Jornaleiro" && ((SUCCESS++)) || ((FAILED++))

# PRODUCT 8: Boné Cowboy (15125)
import_product "15125" \
    "/var/www/html/wp-content/uploads/products/cowboy/bone-15125/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/cowboy/bone-15125/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/cowboy/bone-15125/img_01_lifestyle_tejo_test.jpg" \
    "Boné Cowboy" && ((SUCCESS++)) || ((FAILED++))

# PRODUCT 9: Chapéu Palha (941216)
import_product "941216" \
    "/var/www/html/wp-content/uploads/products/palha/palha-941216-couro/img_01_editorial_test.jpg" \
    "/var/www/html/wp-content/uploads/products/palha/palha-941216-couro/img_01_angle_test.jpg" \
    "/var/www/html/wp-content/uploads/products/palha/palha-941216-couro/img_01_lifestyle_miradouro_test.jpg" \
    "Chapéu Palha" && ((SUCCESS++)) || ((FAILED++))

# Clear cache
echo ""
echo "======================================"
echo "🧹 Clearing cache..."
echo "======================================"
docker exec chapeus_wordpress wp cache flush --allow-root
echo "✓ Cache cleared"

# Final report
echo ""
echo "======================================"
echo "📊 IMPORT COMPLETE"
echo "======================================"
echo "✅ Success: $SUCCESS/9"
echo "❌ Failed: $FAILED/9"

if [ $SUCCESS -gt 0 ]; then
    echo ""
    echo "🎉 AI photos now visible!"
    echo "👉 View: http://localhost:8080/loja/"
fi

echo "======================================"
