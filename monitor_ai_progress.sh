#!/bin/bash
# AI Processing Monitor - Real-time progress tracker

echo "🤖 AI PROCESSING MONITOR"
echo "========================"
echo ""

while true; do
    # Count processed images
    COUNT=$(find wordpress/wp-content/uploads/products -name "*_pro.*" 2>/dev/null | wc -l | tr -d ' ')
    
    # Calculate percentage
    PERCENT=$(echo "scale=1; $COUNT*100/766" | bc)
    
    # Estimate time remaining (based on 6.8 imgs/min)
    REMAINING_IMGS=$((766 - COUNT))
    REMAINING_MINS=$(echo "scale=0; $REMAINING_IMGS/6.8" | bc)
    
    # Check if process still running
    if ps aux | grep -v grep | grep "10547" > /dev/null 2>&1; then
        STATUS="🟢 RUNNING"
    else
        STATUS="⚪ COMPLETED"
    fi
    
    clear
    echo "🤖 AI PROCESSING MONITOR"
    echo "========================"
    echo ""
    echo "Status: $STATUS"
    echo "Progress: $COUNT / 766 images ($PERCENT%)"
    echo "Remaining: ~$REMAINING_MINS minutes"
    echo ""
    echo "Press Ctrl+C to exit"
    echo ""
    echo "Last 5 products:"
    find wordpress/wp-content/uploads/products -name "*_pro.*" -type f -exec dirname {} \; 2>/dev/null | sort -u | tail -5 | xargs -I {} basename {}
    
    sleep 10
done
