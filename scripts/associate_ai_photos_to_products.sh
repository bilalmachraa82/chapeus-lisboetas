#!/bin/bash
# Associate AI photos to WooCommerce products

echo "🔗 Associando fotos AI aos produtos WooCommerce..."
echo "=================================================="

# Get all products
PRODUCTS=$(docker exec chapeus_wordpress wp post list --post_type=product --fields=ID,post_title --format=csv --allow-root | tail -n +2)

TOTAL=0
SUCCESS=0
ERRORS=0

while IFS=',' read -r PRODUCT_ID PRODUCT_TITLE; do
    # Remove quotes
    PRODUCT_TITLE=$(echo "$PRODUCT_TITLE" | tr -d '"')
    
    echo ""
    echo "📦 Produto: $PRODUCT_TITLE (ID: $PRODUCT_ID)"
    
    # Find AI photos for this product (by title match)
    AI_PHOTOS=$(docker exec chapeus_wordpress wp post list \
        --post_type=attachment \
        --s="$PRODUCT_TITLE" \
        --fields=ID \
        --format=csv \
        --allow-root | tail -n +2)
    
    if [ -z "$AI_PHOTOS" ]; then
        echo "  ⚠️  Nenhuma foto AI encontrada"
        ((ERRORS++))
        continue
    fi
    
    # Convert to array
    PHOTO_IDS=($AI_PHOTOS)
    COUNT=${#PHOTO_IDS[@]}
    
    if [ $COUNT -eq 0 ]; then
        echo "  ⚠️  Nenhuma foto AI encontrada"
        ((ERRORS++))
        continue
    fi
    
    echo "  ✓ Encontradas $COUNT fotos AI"
    
    # Set first photo as featured image
    FEATURED_ID=${PHOTO_IDS[0]}
    docker exec chapeus_wordpress wp post meta update $PRODUCT_ID _thumbnail_id $FEATURED_ID --allow-root
    echo "  ✓ Featured image definida (ID: $FEATURED_ID)"
    
    # Add remaining photos to gallery
    if [ $COUNT -gt 1 ]; then
        # Build gallery string (comma-separated IDs)
        GALLERY_IDS=$(IFS=,; echo "${PHOTO_IDS[*]:1}")
        docker exec chapeus_wordpress wp post meta update $PRODUCT_ID _product_image_gallery "$GALLERY_IDS" --allow-root
        echo "  ✓ Gallery atualizada com $(($COUNT - 1)) fotos"
    fi
    
    ((TOTAL++))
    ((SUCCESS++))
    
done <<< "$PRODUCTS"

echo ""
echo "=================================================="
echo "✅ CONCLUÍDO"
echo "   Total produtos processados: $TOTAL"
echo "   Sucesso: $SUCCESS"
echo "   Erros: $ERRORS"
echo "=================================================="

# Flush cache
docker exec chapeus_wordpress wp cache flush --allow-root
echo "✓ Cache limpo"
