#!/bin/bash
# Fix 5 orphan AI photos - associate with correct products

echo "🔧 FIXING ORPHAN AI PHOTOS"
echo "========================================="

# Function to find product and associate photo
fix_product() {
    local SEARCH_TERMS=("$@")
    local PHOTO_ID="${SEARCH_TERMS[-2]}"
    local PRODUCT_NAME="${SEARCH_TERMS[-1]}"
    unset 'SEARCH_TERMS[-1]'
    unset 'SEARCH_TERMS[-1]'
    
    echo ""
    echo "📦 $PRODUCT_NAME"
    echo "   Photo ID: $PHOTO_ID"
    
    # Try each search term
    for TERM in "${SEARCH_TERMS[@]}"; do
        echo "   Trying: $TERM"
        
        PRODUCT_ID=$(docker exec chapeus_wordpress wp post list \
            --post_type=product \
            --s="$TERM" \
            --fields=ID \
            --format=csv \
            --allow-root 2>/dev/null | tail -n 1)
        
        # Check if we got a valid numeric ID
        if [[ "$PRODUCT_ID" =~ ^[0-9]+$ ]]; then
            echo "   ✓ Found product ID: $PRODUCT_ID"
            
            # Associate photo
            docker exec chapeus_wordpress wp post meta update \
                $PRODUCT_ID _thumbnail_id $PHOTO_ID --allow-root >/dev/null 2>&1
            
            # Regenerate thumbnails
            docker exec chapeus_wordpress wp media regenerate \
                $PHOTO_ID --yes --allow-root >/dev/null 2>&1
            
            echo "   ✅ SUCCESS: Photo associated!"
            return 0
        fi
    done
    
    echo "   ❌ FAILED: No valid product ID found"
    return 1
}

# 1. Boina Harris Tweed - Photo 2684
fix_product "harris" "tweed" "18438" "18502" "2684" "Boina Harris Tweed"

# 2. Chapéu Dobrável - Photo 2697
fix_product "dobravel" "181054" "esmagavel" "2697" "Chapéu Dobrável"

# 3. Boina Jornaleiro - Photo 2700
fix_product "la pura" "italiana" "jornaleiro" "2700" "Boina Jornaleiro"

# 4. Boné Cowboy - Photo 2703
fix_product "cowboy" "15125" "bone" "2703" "Boné Cowboy"

# 5. Chapéu Palha - Photo 2706
fix_product "palha" "941216" "couro" "2706" "Chapéu Palha"

# Clear cache
echo ""
echo "========================================="
echo "🧹 Clearing cache..."
docker exec chapeus_wordpress wp cache flush --allow-root
echo "✓ Cache cleared"

echo ""
echo "========================================="
echo "✅ ORPHAN PHOTOS FIX COMPLETE"
echo "========================================="
