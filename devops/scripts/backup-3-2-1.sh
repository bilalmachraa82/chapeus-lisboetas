#!/bin/bash
# backup-3-2-1.sh - Enterprise 3-2-1 Backup Strategy
# 3 Copies | 2 Media Types | 1 Offsite
# Chapéus Lisboeta WooCommerce 2.0

set -euo pipefail

# Configuration
SITE_URL="chapeuslisboeta.pt"
PTISP_USER="ptisp"
PTISP_HOST="chapeuslisboeta.pt"
BACKUP_DIR="/home/ptisp/backups"
LOCAL_BACKUP_DIR="$HOME/chapeus-backups"
S3_BUCKET="chapeus-backups-eu"
S3_REGION="eu-west-3"
RETENTION_DAYS=90
ENCRYPTION_KEY="/home/ptisp/.backup-key"

# Backup types
BACKUP_TYPE="${1:-daily}"  # hourly, daily, weekly, monthly

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local timestamp="[$(date +'%Y-%m-%d %H:%M:%S')]"
    echo -e "${GREEN}$timestamp${NC} $1" | tee -a /var/log/backup.log
}

error() {
    local timestamp="[$(date +'%Y-%m-%d %H:%M:%S')]"
    echo -e "${RED}$timestamp [ERROR]${NC} $1" | tee -a /var/log/backup.log
    send_alert "❌ BACKUP FAILED" "$1"
    exit 1
}

warning() {
    local timestamp="[$(date +'%Y-%m-%d %H:%M:%S')]"
    echo -e "${YELLOW}$timestamp [WARNING]${NC} $1" | tee -a /var/log/backup.log
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Send alerts
send_alert() {
    local title="$1"
    local message="$2"

    # Telegram
    if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=🔒 $title

$message

Type: $BACKUP_TYPE
Time: $(date +'%Y-%m-%d %H:%M:%S')" > /dev/null || true
    fi

    # Email
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "Backup Alert: $title" admin@chapeuslisboeta.pt || true
    fi
}

# Generate backup filename
get_backup_name() {
    local type="$1"
    local suffix="${2:-}"
    echo "chapeus-${type}-$(date +%Y%m%d-%H%M%S)${suffix}"
}

# Check encryption key
check_encryption_key() {
    if ! ssh ${PTISP_USER}@${PTISP_HOST} "[ -f $ENCRYPTION_KEY ]"; then
        log "Generating encryption key..."
        ssh ${PTISP_USER}@${PTISP_HOST} "openssl rand -base64 32 > $ENCRYPTION_KEY && chmod 600 $ENCRYPTION_KEY"
    fi
}

# Database backup
backup_database() {
    local backup_name="$(get_backup_name 'db')"
    log "Starting database backup: $backup_name"

    # Export database with optimization
    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e
        mkdir -p $BACKUP_DIR

        # Export with mysqldump optimizations
        wp db export - --path=/home/ptisp/public_html \
            --add-drop-table \
            --single-transaction \
            --quick \
            --lock-tables=false \
            --skip-add-locks | \
        gzip -9 | \
        openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:$ENCRYPTION_KEY \
            > $BACKUP_DIR/$backup_name.sql.gz.enc

        # Verify backup exists
        if [ ! -s $BACKUP_DIR/$backup_name.sql.gz.enc ]; then
            echo "ERROR: Database backup file is empty"
            exit 1
        fi

        # Print size
        du -h $BACKUP_DIR/$backup_name.sql.gz.enc | cut -f1
EOF

    if [ $? -eq 0 ]; then
        log "Database backup successful"
        echo "$backup_name.sql.gz.enc"
        return 0
    else
        error "Database backup failed"
    fi
}

# Files backup
backup_files() {
    local backup_name="$(get_backup_name 'files')"
    log "Starting files backup: $backup_name"

    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e
        mkdir -p $BACKUP_DIR

        # Create incremental backup of wp-content
        tar czf - \
            --exclude='*/cache/*' \
            --exclude='*/backup*' \
            --exclude='*/tmp/*' \
            --exclude='*.log' \
            --exclude='*/wflogs/*' \
            -C /home/ptisp/public_html wp-content | \
        openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:$ENCRYPTION_KEY \
            > $BACKUP_DIR/$backup_name.tar.gz.enc

        # Verify
        if [ ! -s $BACKUP_DIR/$backup_name.tar.gz.enc ]; then
            echo "ERROR: Files backup is empty"
            exit 1
        fi

        du -h $BACKUP_DIR/$backup_name.tar.gz.enc | cut -f1
EOF

    if [ $? -eq 0 ]; then
        log "Files backup complete"
        echo "$backup_name.tar.gz.enc"
        return 0
    else
        error "Files backup failed"
    fi
}

# Full WordPress backup
backup_full_wordpress() {
    local backup_name="$(get_backup_name 'full')"
    log "Starting full WordPress backup: $backup_name"

    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e
        mkdir -p $BACKUP_DIR

        # Full site backup (excluding uploads for size)
        tar czf - \
            --exclude='wp-content/uploads/*' \
            --exclude='*/cache/*' \
            --exclude='*/backup*' \
            -C /home/ptisp public_html | \
        openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:$ENCRYPTION_KEY \
            > $BACKUP_DIR/$backup_name-site.tar.gz.enc

        du -h $BACKUP_DIR/$backup_name-site.tar.gz.enc | cut -f1
EOF

    log "Full WordPress backup complete"
    echo "$backup_name-site.tar.gz.enc"
}

# Uploads backup (AI photos)
backup_uploads() {
    local backup_name="$(get_backup_name 'uploads')"
    log "Starting uploads backup: $backup_name"

    # Incremental backup of uploads (7,827 AI photos)
    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e
        mkdir -p $BACKUP_DIR

        # Create file list for incremental
        find /home/ptisp/public_html/wp-content/uploads \
            -type f -mtime -7 > /tmp/uploads-changed.txt

        # Backup only changed files
        tar czf - \
            -C /home/ptisp/public_html/wp-content \
            -T /tmp/uploads-changed.txt | \
        openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:$ENCRYPTION_KEY \
            > $BACKUP_DIR/$backup_name.tar.gz.enc

        rm /tmp/uploads-changed.txt

        du -h $BACKUP_DIR/$backup_name.tar.gz.enc | cut -f1
EOF

    log "Uploads backup complete"
    echo "$backup_name.tar.gz.enc"
}

# Download backup to local (Copy 2)
download_to_local() {
    local backup_file="$1"
    log "Downloading to local backup: $backup_file"

    mkdir -p "$LOCAL_BACKUP_DIR"

    # Use rsync for resumable transfers
    rsync -avz --progress \
        ${PTISP_USER}@${PTISP_HOST}:$BACKUP_DIR/$backup_file \
        "$LOCAL_BACKUP_DIR/" || {
        warning "Local download failed, trying scp..."
        scp ${PTISP_USER}@${PTISP_HOST}:$BACKUP_DIR/$backup_file \
            "$LOCAL_BACKUP_DIR/" || {
            error "Failed to download backup locally"
        }
    }

    log "Local backup saved to: $LOCAL_BACKUP_DIR/$backup_file"
}

# Upload to S3 (Copy 3 - Offsite)
upload_to_s3() {
    local backup_file="$1"
    local storage_class="${2:-GLACIER_IR}"
    log "Uploading to S3: $backup_file (storage: $storage_class)"

    # Check if AWS CLI is available
    if ! command -v aws &> /dev/null; then
        warning "AWS CLI not found, skipping S3 upload"
        return 1
    fi

    # Upload from local copy
    local local_file="$LOCAL_BACKUP_DIR/$backup_file"

    if [ -f "$local_file" ]; then
        aws s3 cp "$local_file" "s3://$S3_BUCKET/$backup_file" \
            --storage-class "$storage_class" \
            --metadata "backup-date=$(date -Iseconds),backup-type=$BACKUP_TYPE,site=$SITE_URL" \
            --server-side-encryption AES256 \
            --region "$S3_REGION" || {
            error "S3 upload failed"
        }

        # Verify upload
        if aws s3api head-object \
            --bucket "$S3_BUCKET" \
            --key "$backup_file" \
            --region "$S3_REGION" &> /dev/null; then
            log "S3 upload verified: s3://$S3_BUCKET/$backup_file"
            return 0
        else
            error "S3 upload verification failed"
        fi
    else
        error "Local backup file not found: $local_file"
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    log "Verifying backup integrity: $backup_file"

    # Test decryption and compression
    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e

        # Test decrypt and decompress (first 1KB only)
        if openssl enc -aes-256-cbc -d -pbkdf2 -pass file:$ENCRYPTION_KEY \
            -in $BACKUP_DIR/$backup_file 2>/dev/null | \
           gzip -t 2>/dev/null || tar tz 2>/dev/null; then
            echo "Backup verification: PASS"
            exit 0
        else
            echo "Backup verification: FAIL"
            exit 1
        fi
EOF

    if [ $? -eq 0 ]; then
        log "✓ Backup verification passed"
        return 0
    else
        error "✗ Backup verification failed"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days"

    # Remote cleanup
    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e

        DELETED=\$(find $BACKUP_DIR -type f -name "chapeus-*" -mtime +$RETENTION_DAYS -delete -print | wc -l)
        echo "Deleted \$DELETED old backups from server"
EOF

    # Local cleanup
    if [ -d "$LOCAL_BACKUP_DIR" ]; then
        local deleted=$(find "$LOCAL_BACKUP_DIR" -type f -name "chapeus-*" -mtime +$RETENTION_DAYS -delete -print | wc -l)
        log "Deleted $deleted old local backups"
    fi

    # S3 lifecycle (managed by Terraform)
    info "S3 lifecycle policy manages S3 cleanup automatically"
}

# Export WooCommerce data
export_woocommerce_data() {
    local backup_name="$(get_backup_name 'wc-data' '.csv')"
    log "Exporting WooCommerce data..."

    ssh ${PTISP_USER}@${PTISP_HOST} << EOF
        set -e
        mkdir -p $BACKUP_DIR/woocommerce

        # Export products
        wp wc product list --format=csv --path=/home/ptisp/public_html \
            > $BACKUP_DIR/woocommerce/${backup_name}-products.csv

        # Export orders (last 90 days)
        wp wc order list --format=csv --path=/home/ptisp/public_html \
            --after="$(date -d '90 days ago' +%Y-%m-%d)" \
            > $BACKUP_DIR/woocommerce/${backup_name}-orders.csv

        # Export customers
        wp wc customer list --format=csv --path=/home/ptisp/public_html \
            > $BACKUP_DIR/woocommerce/${backup_name}-customers.csv

        # Compress all CSV files
        tar czf $BACKUP_DIR/${backup_name}.tar.gz \
            -C $BACKUP_DIR/woocommerce .

        rm -rf $BACKUP_DIR/woocommerce

        du -h $BACKUP_DIR/${backup_name}.tar.gz | cut -f1
EOF

    log "WooCommerce data export complete"
    echo "${backup_name}.tar.gz"
}

# Generate backup report
generate_report() {
    local backups=("$@")
    log "Generating backup report..."

    # Calculate total size
    local total_size=0
    for backup in "${backups[@]}"; do
        if ssh ${PTISP_USER}@${PTISP_HOST} "[ -f $BACKUP_DIR/$backup ]"; then
            size=$(ssh ${PTISP_USER}@${PTISP_HOST} "stat -f%z $BACKUP_DIR/$backup 2>/dev/null || stat -c%s $BACKUP_DIR/$backup")
            total_size=$((total_size + size))
        fi
    done

    total_size_mb=$((total_size / 1024 / 1024))

    # Create report
    cat > "/tmp/backup-report-$(date +%Y%m%d).txt" << EOF
Chapéus Lisboeta - Backup Report
================================

Date: $(date +'%Y-%m-%d %H:%M:%S')
Type: $BACKUP_TYPE
Status: SUCCESS ✓

Backups Created:
$(printf '%s\n' "${backups[@]}")

Total Size: ${total_size_mb}MB

3-2-1 Strategy:
- Copy 1: PTisp server ($BACKUP_DIR)
- Copy 2: Local backup ($LOCAL_BACKUP_DIR)
- Copy 3: AWS S3 (s3://$S3_BUCKET)

Retention: $RETENTION_DAYS days
Encryption: AES-256-CBC with PBKDF2

Next Backup: $BACKUP_TYPE (scheduled via cron)
EOF

    cat "/tmp/backup-report-$(date +%Y%m%d).txt"
}

# Main backup process
main() {
    log "=== Starting 3-2-1 Backup Process ($BACKUP_TYPE) ==="

    local backups=()
    local success=true

    # Check prerequisites
    check_encryption_key

    case "$BACKUP_TYPE" in
        hourly)
            # Database only
            db_backup=$(backup_database) || success=false
            [ "$success" = true ] && backups+=("$db_backup")
            ;;

        daily)
            # Database + Files
            db_backup=$(backup_database) || success=false
            [ "$success" = true ] && backups+=("$db_backup")

            files_backup=$(backup_files) || success=false
            [ "$success" = true ] && backups+=("$files_backup")
            ;;

        weekly)
            # Full backup + optimization
            db_backup=$(backup_database) || success=false
            [ "$success" = true ] && backups+=("$db_backup")

            files_backup=$(backup_files) || success=false
            [ "$success" = true ] && backups+=("$files_backup")

            uploads_backup=$(backup_uploads) || success=false
            [ "$success" = true ] && backups+=("$uploads_backup")

            # Optimize database
            ssh ${PTISP_USER}@${PTISP_HOST} "wp db optimize --path=/home/ptisp/public_html" || true
            ;;

        monthly)
            # Full system backup
            db_backup=$(backup_database) || success=false
            [ "$success" = true ] && backups+=("$db_backup")

            full_backup=$(backup_full_wordpress) || success=false
            [ "$success" = true ] && backups+=("$full_backup")

            uploads_backup=$(backup_uploads) || success=false
            [ "$success" = true ] && backups+=("$uploads_backup")

            wc_backup=$(export_woocommerce_data) || success=false
            [ "$success" = true ] && backups+=("$wc_backup")
            ;;

        *)
            error "Invalid backup type: $BACKUP_TYPE (use: hourly, daily, weekly, monthly)"
            ;;
    esac

    if [ "$success" = false ]; then
        error "Backup process failed"
    fi

    # Verify all backups
    for backup in "${backups[@]}"; do
        verify_backup "$backup" || success=false
    done

    if [ "$success" = false ]; then
        error "Backup verification failed"
    fi

    # Download to local (Copy 2)
    for backup in "${backups[@]}"; do
        download_to_local "$backup" || warning "Local download failed for $backup"
    done

    # Upload to S3 (Copy 3)
    for backup in "${backups[@]}"; do
        case "$BACKUP_TYPE" in
            hourly)
                upload_to_s3 "$backup" "STANDARD_IA" || warning "S3 upload failed for $backup"
                ;;
            daily)
                upload_to_s3 "$backup" "GLACIER_IR" || warning "S3 upload failed for $backup"
                ;;
            weekly|monthly)
                upload_to_s3 "$backup" "DEEP_ARCHIVE" || warning "S3 upload failed for $backup"
                ;;
        esac
    done

    # Cleanup old backups
    cleanup_old_backups

    # Generate report
    generate_report "${backups[@]}"

    # Send success notification
    send_alert "✅ BACKUP SUCCESS" "Backup completed successfully

Type: $BACKUP_TYPE
Files: ${#backups[@]}
Total: $(du -sh "$LOCAL_BACKUP_DIR" 2>/dev/null | cut -f1 || echo 'N/A')"

    log "=== Backup Process Completed Successfully ==="
}

# Run backup
main

exit 0
