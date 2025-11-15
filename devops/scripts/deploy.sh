#!/bin/bash
# deploy.sh - Blue-Green Deployment with Rollback
# Chapéus Lisboeta WooCommerce 2.0

set -euo pipefail

# Configuration
DEPLOY_ENV="${1:-staging}"
DEPLOY_VERSION="${2:-$(git describe --tags --always)}"
BACKUP_BEFORE_DEPLOY=true
HEALTH_CHECK_RETRIES=30
HEALTH_CHECK_INTERVAL=10

# PTisp SSH connection
PTISP_USER="ptisp"
PTISP_HOST="chapeuslisboeta.pt"
PTISP_PATH="/home/ptisp"

# Paths
BLUE_PATH="$PTISP_PATH/blue"
GREEN_PATH="$PTISP_PATH/green"
PUBLIC_PATH="$PTISP_PATH/public_html"
BACKUP_PATH="$PTISP_PATH/backups"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    send_notification "❌ DEPLOYMENT FAILED" "$1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Send notifications
send_notification() {
    local title="$1"
    local message="$2"

    # Telegram notification
    if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=🎩 $title

$message

Environment: $DEPLOY_ENV
Version: $DEPLOY_VERSION
Time: $(date +'%Y-%m-%d %H:%M:%S')" \
            -d "parse_mode=Markdown" > /dev/null || true
    fi

    # Email notification
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "[$DEPLOY_ENV] $title" admin@chapeuslisboeta.pt || true
    fi
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."

    # Check SSH connection
    if ! ssh -q ${PTISP_USER}@${PTISP_HOST} exit; then
        error "Cannot connect to PTisp server"
    fi
    info "✓ SSH connection verified"

    # Check disk space (require at least 5GB free)
    FREE_SPACE=$(ssh ${PTISP_USER}@${PTISP_HOST} "df -BG $PTISP_PATH | tail -1 | awk '{print \$4}' | sed 's/G//'")
    if [ "$FREE_SPACE" -lt 5 ]; then
        error "Insufficient disk space: ${FREE_SPACE}GB free (minimum 5GB required)"
    fi
    info "✓ Disk space: ${FREE_SPACE}GB available"

    # Check database connection
    if ! ssh ${PTISP_USER}@${PTISP_HOST} "wp db check --path=$PUBLIC_PATH" &> /dev/null; then
        error "Database connection failed"
    fi
    info "✓ Database connection verified"

    # Check WP-CLI
    if ! ssh ${PTISP_USER}@${PTISP_HOST} "wp --version" &> /dev/null; then
        error "WP-CLI not found on server"
    fi
    info "✓ WP-CLI available"

    # Check git repository
    if [ ! -d .git ]; then
        error "Not a git repository"
    fi
    info "✓ Git repository verified"

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        warning "Uncommitted changes detected"
        git status --short
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Deployment cancelled by user"
        fi
    fi

    # Check current site status
    CURRENT_VERSION=$(ssh ${PTISP_USER}@${PTISP_HOST} "wp core version --path=$PUBLIC_PATH")
    info "Current WordPress version: $CURRENT_VERSION"

    PLUGIN_UPDATES=$(ssh ${PTISP_USER}@${PTISP_HOST} "wp plugin list --path=$PUBLIC_PATH --update=available --format=count")
    if [ "$PLUGIN_UPDATES" -gt 0 ]; then
        warning "$PLUGIN_UPDATES plugin updates available"
    fi

    log "Pre-deployment checks completed successfully"
}

# Backup before deployment
backup_before_deploy() {
    log "Creating pre-deployment backup..."

    BACKUP_NAME="pre-deploy-$(date +%Y%m%d-%H%M%S)"

    # Database backup
    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e
        mkdir -p $BACKUP_PATH

        # Export database
        wp db export $BACKUP_PATH/$BACKUP_NAME.sql \
            --path=$PUBLIC_PATH \
            --add-drop-table \
            --single-transaction

        # Compress
        gzip $BACKUP_PATH/$BACKUP_NAME.sql

        # Create symlink to latest
        ln -sf $BACKUP_PATH/$BACKUP_NAME.sql.gz $BACKUP_PATH/pre-deploy-latest.sql.gz

        echo "Database backup: \$(du -h $BACKUP_PATH/$BACKUP_NAME.sql.gz | cut -f1)"
EOF

    # Files backup (incremental)
    info "Syncing changed files to local backup..."
    rsync -avz --backup --backup-dir=./backup/files-$BACKUP_NAME \
        --exclude='wp-content/cache' \
        --exclude='wp-content/uploads' \
        ${PTISP_USER}@${PTISP_HOST}:$PUBLIC_PATH/wp-content/ \
        ./backup/wp-content/ || warning "File backup failed (non-critical)"

    log "Backup completed successfully"
}

# Deploy to blue environment
deploy_blue() {
    log "Deploying to BLUE environment..."

    # Create blue directory if not exists
    ssh ${PTISP_USER}@${PTISP_HOST} "mkdir -p $BLUE_PATH"

    # Sync WordPress core and theme files
    info "Uploading WordPress files..."
    rsync -avz --delete \
        --exclude='wp-content/uploads' \
        --exclude='wp-content/cache' \
        --exclude='wp-content/backup' \
        --exclude='wp-config.php' \
        --exclude='.env' \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='.DS_Store' \
        ./wordpress/ ${PTISP_USER}@${PTISP_HOST}:$BLUE_PATH/

    # Copy wp-config.php from production
    ssh ${PTISP_USER}@${PTISP_HOST} "cp $PUBLIC_PATH/wp-config.php $BLUE_PATH/"

    # Share uploads directory (symlink)
    ssh ${PTISP_USER}@${PTISP_HOST} << 'EOF'
        set -e
        rm -rf $BLUE_PATH/wp-content/uploads
        ln -sf $PUBLIC_PATH/wp-content/uploads $BLUE_PATH/wp-content/uploads
EOF

    # Run database migrations
    info "Running database migrations..."
    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e

        # Update database
        wp core update-db --path=$BLUE_PATH

        # Update plugins (security updates only)
        wp plugin update --all --path=$BLUE_PATH || true

        # Update themes (exclude Flatsome)
        wp theme update --all --exclude=flatsome,flatsome-child --path=$BLUE_PATH || true

        # Clear all caches
        wp cache flush --path=$BLUE_PATH
        wp rewrite flush --path=$BLUE_PATH

        # Regenerate thumbnails for AI photos (background task)
        nohup wp media regenerate --yes --path=$BLUE_PATH > /tmp/regenerate.log 2>&1 &
EOF

    # Set correct permissions
    ssh ${PTISP_USER}@${PTISP_HOST} << 'EOF'
        set -e
        find $BLUE_PATH -type d -exec chmod 755 {} \;
        find $BLUE_PATH -type f -exec chmod 644 {} \;
        chown -R www-data:www-data $BLUE_PATH
EOF

    log "Blue deployment complete"
}

# Health check
health_check() {
    local url="$1"
    local retries=0
    local name="${2:-site}"

    log "Running health checks on $url..."

    while [ $retries -lt $HEALTH_CHECK_RETRIES ]; do
        # HTTP status check
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")

        if [ "$HTTP_CODE" = "200" ]; then
            info "✓ HTTP status: $HTTP_CODE"

            # WooCommerce API check
            if [ -n "${WC_API_KEY:-}" ]; then
                WC_STATUS=$(curl -sf "$url/wp-json/wc/v3/system_status" \
                    -H "Authorization: Bearer $WC_API_KEY" | jq -e '.environment.wp_active' || echo "false")

                if [ "$WC_STATUS" = "true" ]; then
                    info "✓ WooCommerce API: healthy"
                    log "Health check passed for $name!"
                    return 0
                else
                    warning "WooCommerce API check failed"
                fi
            else
                # Skip WC check if no API key
                log "Health check passed for $name (basic)!"
                return 0
            fi
        else
            warning "HTTP status: $HTTP_CODE"
        fi

        retries=$((retries + 1))
        if [ $retries -lt $HEALTH_CHECK_RETRIES ]; then
            info "Retry $retries/$HEALTH_CHECK_RETRIES in ${HEALTH_CHECK_INTERVAL}s..."
            sleep $HEALTH_CHECK_INTERVAL
        fi
    done

    error "Health check failed after $HEALTH_CHECK_RETRIES attempts"
}

# Switch traffic (atomic)
switch_traffic() {
    log "Switching traffic from GREEN to BLUE..."

    ssh ${PTISP_USER}@${PTISP_HOST} << 'EOF'
        set -e

        # Atomic symlink switch
        ln -sfn $BLUE_PATH ${PTISP_PATH}/public_html_new
        mv -Tf ${PTISP_PATH}/public_html_new $PUBLIC_PATH

        # Clear PHP opcache
        if command -v php &> /dev/null; then
            php -r 'opcache_reset();' || true
        fi

        # Reload PHP-FPM
        if command -v systemctl &> /dev/null; then
            sudo systemctl reload php8.3-fpm || true
        fi

        # Clear WordPress caches
        wp cache flush --path=$PUBLIC_PATH

        # Warm up cache (background)
        nohup bash -c '
            for url in / /shop/ /cart/ /checkout/; do
                curl -s "https://chapeuslisboeta.pt$url" > /dev/null
                sleep 1
            done
        ' > /tmp/warmup.log 2>&1 &
EOF

    # Purge CDN cache
    if [ -n "${CF_ZONE_ID:-}" ] && [ -n "${CF_API_TOKEN:-}" ]; then
        info "Purging Cloudflare cache..."
        curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            --data '{"purge_everything":true}' > /dev/null || warning "CDN purge failed"
    fi

    log "Traffic switched successfully"
}

# Rollback
rollback() {
    error "Deployment failed! Rolling back..."

    ssh ${PTISP_USER}@${PTISP_HOST} << 'EOF'
        set -e

        # Switch back to green
        ln -sfn $GREEN_PATH ${PTISP_PATH}/public_html_new
        mv -Tf ${PTISP_PATH}/public_html_new $PUBLIC_PATH

        # Restore database if needed
        if [ -f $BACKUP_PATH/pre-deploy-latest.sql.gz ]; then
            echo "Restoring database backup..."
            gunzip -c $BACKUP_PATH/pre-deploy-latest.sql.gz | \
                wp db import - --path=$PUBLIC_PATH
        fi

        # Clear caches
        wp cache flush --path=$PUBLIC_PATH

        # Reload PHP-FPM
        if command -v systemctl &> /dev/null; then
            sudo systemctl reload php8.3-fpm || true
        fi
EOF

    # Purge CDN
    if [ -n "${CF_ZONE_ID:-}" ] && [ -n "${CF_API_TOKEN:-}" ]; then
        curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            --data '{"purge_everything":true}' > /dev/null || true
    fi

    send_notification "🔄 ROLLBACK COMPLETED" "Deployment was rolled back to previous version"
    log "Rollback completed"
    exit 1
}

# Post-deployment tasks
post_deployment() {
    log "Running post-deployment tasks..."

    # Swap blue/green for next deployment
    ssh ${PTISP_USER}@${PTISP_HOST} << 'EOF'
        set -e

        # Swap directories
        if [ -d $GREEN_PATH.old ]; then
            rm -rf $GREEN_PATH.old
        fi

        mv $GREEN_PATH $GREEN_PATH.old
        mv $BLUE_PATH $GREEN_PATH
        mv $GREEN_PATH.old $BLUE_PATH
EOF

    # Tag successful deployment
    git tag "deploy-$DEPLOY_ENV-$(date +%Y%m%d-%H%M%S)" || true

    # Generate deployment report
    cat > "deployment-report-$(date +%Y%m%d-%H%M%S).txt" << EOF
Deployment Report
=================

Environment: $DEPLOY_ENV
Version: $DEPLOY_VERSION
Date: $(date +'%Y-%m-%d %H:%M:%S')
Deployed by: $(whoami)

Git commit: $(git rev-parse HEAD)
Git branch: $(git rev-parse --abbrev-ref HEAD)

WordPress version: $(ssh ${PTISP_USER}@${PTISP_HOST} "wp core version --path=$PUBLIC_PATH")
PHP version: $(ssh ${PTISP_USER}@${PTISP_HOST} "php -v | head -1")

Active plugins: $(ssh ${PTISP_USER}@${PTISP_HOST} "wp plugin list --status=active --path=$PUBLIC_PATH --format=count")

Status: SUCCESS ✓
EOF

    log "Post-deployment tasks completed"
}

# Main deployment flow
main() {
    log "=== Starting deployment of version $DEPLOY_VERSION to $DEPLOY_ENV ==="

    # Step 1: Pre-deployment checks
    pre_deployment_checks

    # Step 2: Backup
    if [ "$BACKUP_BEFORE_DEPLOY" = true ]; then
        backup_before_deploy
    fi

    # Step 3: Deploy to blue
    deploy_blue || rollback

    # Step 4: Health check blue environment
    health_check "https://blue.chapeuslisboeta.pt" "blue environment" || rollback

    # Step 5: Switch traffic
    switch_traffic

    # Step 6: Health check production
    health_check "https://chapeuslisboeta.pt" "production" || rollback

    # Step 7: Post-deployment
    post_deployment

    log "=== Deployment completed successfully! 🎉 ==="

    # Send success notification
    send_notification "✅ DEPLOYMENT SUCCESS" "Version $DEPLOY_VERSION deployed to $DEPLOY_ENV successfully"

    # Display next steps
    cat << EOF

Next Steps:
-----------
1. Verify site manually: https://chapeuslisboeta.pt
2. Check admin panel: https://chapeuslisboeta.pt/wp-admin
3. Monitor logs: ssh $PTISP_USER@$PTISP_HOST "tail -f /var/log/nginx/error.log"
4. If issues occur, rollback: ./rollback.sh

Deployment report: deployment-report-*.txt
EOF
}

# Trap errors
trap rollback ERR

# Run deployment
main

exit 0
