# Chapéus Lisboeta - DevOps Infrastructure

Complete deployment, backup, monitoring, and cost optimization infrastructure for the WooCommerce 2.0 rebuild.

## Quick Start

```bash
# 1. Setup environment
cd devops
cp .env.example .env
# Edit .env with your credentials

# 2. Deploy monitoring stack
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# 3. Setup Terraform (infrastructure as code)
cd terraform/environments/production
terraform init
terraform plan
terraform apply

# 4. Configure cron jobs
crontab -e
# Paste contents from cron/crontab.txt

# 5. Test deployment
cd ../../..
./scripts/deploy.sh staging

# 6. Test backup
./scripts/backup-3-2-1.sh daily
```

## Directory Structure

```
devops/
├── DEPLOYMENT_STRATEGY.md      # Complete DevOps documentation
├── README.md                    # This file
├── .env.example                 # Environment variables template
│
├── terraform/                   # Infrastructure as Code
│   ├── environments/
│   │   ├── production/
│   │   │   └── main.tf         # Cloudflare + AWS S3 setup
│   │   └── staging/
│   └── modules/
│
├── scripts/                     # Automation scripts
│   ├── deploy.sh               # Blue-green deployment
│   ├── backup-3-2-1.sh         # 3-2-1 backup strategy
│   ├── cost-optimizer.py       # Cost optimization
│   ├── test-recovery.sh        # Monthly recovery drills
│   └── rollback.sh             # Emergency rollback
│
├── monitoring/                  # Observability stack
│   ├── docker-compose.monitoring.yml
│   ├── prometheus/
│   │   ├── prometheus.yml      # Scrape configs
│   │   └── alerts.yml          # Alert rules
│   ├── grafana/
│   │   ├── dashboards/         # Pre-built dashboards
│   │   └── datasources/        # Data source configs
│   ├── alertmanager/
│   │   └── alertmanager.yml    # Notification routing
│   └── blackbox/
│       └── blackbox.yml        # Endpoint monitoring
│
├── security/                    # Security configs
│   ├── nginx/
│   │   └── chapeuslisboeta.pt.conf
│   ├── modsecurity/
│   │   └── custom-rules.conf
│   └── fail2ban/
│       └── wordpress.conf
│
├── cron/                        # Scheduled tasks
│   └── crontab.txt             # Cron job definitions
│
└── docs/                        # Additional documentation
    ├── runbooks/               # Incident response guides
    ├── architecture/           # Architecture diagrams
    └── sla/                    # SLA definitions
```

## Key Features

### 1. Zero-Downtime Deployment

Blue-green deployment strategy with automated health checks and rollback:

```bash
# Deploy to production
./scripts/deploy.sh production v2.0.0

# Deploy to staging
./scripts/deploy.sh staging

# Automatic rollback on failure
# Manual rollback if needed: ./scripts/rollback.sh
```

**Features:**
- Pre-deployment backup
- Atomic symlink switching
- Health checks (HTTP, WordPress API, WooCommerce API)
- Automatic rollback on failure
- CDN cache purging
- PHP-FPM reload
- Deployment reports

### 2. 3-2-1 Backup Strategy

**3 Copies:**
1. PTisp server (production)
2. Local backup (developer machine/NAS)
3. AWS S3 (offsite cloud)

**2 Media Types:**
- PTisp NVMe SSD
- AWS S3 Glacier

**1 Offsite:**
- AWS S3 eu-west-3 (Paris)

```bash
# Hourly backups (database only)
./scripts/backup-3-2-1.sh hourly

# Daily backups (database + files)
./scripts/backup-3-2-1.sh daily

# Weekly backups (full + optimize DB)
./scripts/backup-3-2-1.sh weekly

# Monthly backups (full + WooCommerce data export)
./scripts/backup-3-2-1.sh monthly
```

**Guarantees:**
- RPO: <1 hour (Recovery Point Objective)
- RTO: <30 minutes (Recovery Time Objective)
- Retention: 90 days
- Encryption: AES-256-CBC with PBKDF2
- Automated verification
- Monthly recovery drills

### 3. Monitoring & Alerts

**Stack:**
- Prometheus (metrics collection)
- Grafana (visualization)
- Alertmanager (notifications)
- Blackbox Exporter (uptime monitoring)
- Node Exporter (server metrics)
- cAdvisor (container metrics)

**Access:**
- Grafana: http://localhost:3000 (admin/ChapeusAdmin2024!)
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093

**Dashboards:**
- Website Uptime & Performance
- WordPress Health
- WooCommerce Metrics
- Server Resources (CPU, RAM, Disk)
- Backup Status
- Cost Optimization

**Alert Channels:**
- Telegram (instant)
- Email (critical + daily reports)
- SMS (P1 critical only)

### 4. Cost Optimization

Monthly target: **€49.99**

```bash
# Run optimization
python3 scripts/cost-optimizer.py

# Scheduled daily via cron
```

**Optimizations:**
- Image compression (WebP conversion)
- CDN aggressive caching (Cloudflare)
- Database cleanup (transients, revisions)
- Old file cleanup
- S3 Glacier archival
- Resource monitoring

**Expected Savings:**
- €240+ annually vs managed WooCommerce hosting
- 60-80% image size reduction
- 90%+ CDN cache hit ratio
- 50%+ database size reduction

### 5. Security

**Layers:**
1. Cloudflare WAF (DDoS protection)
2. ModSecurity (application firewall)
3. Nginx rate limiting
4. Fail2ban (brute force protection)
5. Let's Encrypt SSL (A+ rating)
6. GDPR automation

**Features:**
- Portuguese-specific WAF rules
- Login rate limiting (3 attempts/minute)
- API rate limiting (100 req/minute)
- Automatic SSL renewal
- Security headers (HSTS, CSP, etc.)
- GDPR data export/deletion

## Environment Setup

### 1. Required Environment Variables

Create `.env` file:

```bash
# PTisp Server
PTISP_USER=ptisp
PTISP_HOST=chapeuslisboeta.pt
PTISP_PATH=/home/ptisp

# Database
DB_HOST=localhost
DB_NAME=lisboetas_web
DB_USER=lisboetas
DB_PASSWORD=your_password_here

# AWS S3
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
S3_BUCKET=chapeus-backups-eu
S3_REGION=eu-west-3

# Cloudflare
CF_API_TOKEN=your_token_here
CF_ZONE_ID=your_zone_id_here

# WooCommerce API
WC_API_KEY=your_api_key_here
WC_API_SECRET=your_api_secret_here

# Notifications
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
SMTP_PASSWORD=your_smtp_password_here

# Monitoring
GRAFANA_ADMIN_PASSWORD=ChapeusAdmin2024!
```

### 2. Install Dependencies

**On PTisp Server:**

```bash
# WP-CLI
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Python dependencies
pip3 install boto3 requests pillow mysql-connector-python
```

**On Local Machine:**

```bash
# Terraform
brew install terraform  # macOS
# or: https://www.terraform.io/downloads

# Docker Desktop (for monitoring stack)
# Download from: https://www.docker.com/products/docker-desktop

# Python dependencies
pip3 install -r requirements-devops.txt
```

### 3. Setup Cron Jobs

```bash
# Edit crontab
crontab -e

# Paste from cron/crontab.txt:

# Hourly database backup
0 * * * * /home/ptisp/devops/scripts/backup-3-2-1.sh hourly >> /var/log/backup-hourly.log 2>&1

# Daily full backup
0 2 * * * /home/ptisp/devops/scripts/backup-3-2-1.sh daily >> /var/log/backup-daily.log 2>&1

# Weekly backup + optimization
0 3 * * 0 /home/ptisp/devops/scripts/backup-3-2-1.sh weekly >> /var/log/backup-weekly.log 2>&1

# Monthly backup
0 4 1 * * /home/ptisp/devops/scripts/backup-3-2-1.sh monthly >> /var/log/backup-monthly.log 2>&1

# Daily cost optimization
0 5 * * * /usr/bin/python3 /home/ptisp/devops/scripts/cost-optimizer.py >> /var/log/cost-optimizer.log 2>&1

# Monthly recovery drill
0 6 1 * * /home/ptisp/devops/scripts/test-recovery.sh >> /var/log/recovery-test.log 2>&1
```

## Common Operations

### Deploy New Version

```bash
# 1. Commit changes
git add .
git commit -m "feat: new feature"
git push

# 2. Deploy to staging first
./scripts/deploy.sh staging

# 3. Test staging site
open https://staging.chapeuslisboeta.pt

# 4. Deploy to production
./scripts/deploy.sh production v2.0.0

# 5. Monitor deployment
tail -f deployment-report-*.txt

# 6. Verify production
open https://chapeuslisboeta.pt
```

### Restore from Backup

```bash
# 1. List available backups
aws s3 ls s3://chapeus-backups-eu/

# 2. Download backup
aws s3 cp s3://chapeus-backups-eu/chapeus-db-20250114-120000.sql.gz.enc /tmp/

# 3. Decrypt and restore
openssl enc -aes-256-cbc -d -pbkdf2 -pass file:/home/ptisp/.backup-key \
    -in /tmp/chapeus-db-20250114-120000.sql.gz.enc | \
    gunzip | \
    wp db import - --path=/home/ptisp/public_html

# 4. Verify restoration
wp db check --path=/home/ptisp/public_html
```

### Emergency Rollback

```bash
# Automatic rollback (if deployment fails)
# Already handled by deploy.sh

# Manual rollback
./scripts/rollback.sh

# Verify rollback
curl -I https://chapeuslisboeta.pt
```

### Check System Health

```bash
# Quick health check
curl -s https://chapeuslisboeta.pt/wp-json/ | jq .

# WooCommerce health
curl -s https://chapeuslisboeta.pt/wp-json/wc/v3/system_status \
    -H "Authorization: Bearer $WC_API_KEY" | jq .

# Server metrics
ssh ptisp@chapeuslisboeta.pt "top -bn1 | head -20"
ssh ptisp@chapeuslisboeta.pt "df -h"
ssh ptisp@chapeuslisboeta.pt "free -h"

# Check backups
ls -lh /home/ptisp/backups/
aws s3 ls s3://chapeus-backups-eu/ --human-readable

# View monitoring
open http://localhost:3000  # Grafana
```

### View Logs

```bash
# Deployment logs
tail -f deployment-report-*.txt

# Backup logs
tail -f /var/log/backup.log

# Cost optimization logs
tail -f /var/log/cost-optimizer.log

# WordPress errors
ssh ptisp@chapeuslisboeta.pt "tail -f /home/ptisp/public_html/wp-content/debug.log"

# Nginx errors
ssh ptisp@chapeuslisboeta.pt "tail -f /var/log/nginx/error.log"

# PHP-FPM errors
ssh ptisp@chapeuslisboeta.pt "tail -f /var/log/php8.3-fpm.log"
```

## Incident Response

### Site Down (P1)

```bash
# 1. Check site status
curl -I https://chapeuslisboeta.pt

# 2. Check services
ssh ptisp@chapeuslisboeta.pt << 'EOF'
    systemctl status nginx
    systemctl status php8.3-fpm
    systemctl status mysql
EOF

# 3. Check logs
ssh ptisp@chapeuslisboeta.pt "tail -100 /var/log/nginx/error.log"

# 4. Restart services if needed
ssh ptisp@chapeuslisboeta.pt << 'EOF'
    sudo systemctl restart php8.3-fpm
    sudo systemctl restart nginx
EOF

# 5. If still down, rollback
./scripts/rollback.sh
```

### High Load (P2)

```bash
# 1. Check current load
ssh ptisp@chapeuslisboeta.pt "uptime"

# 2. Check top processes
ssh ptisp@chapeuslisboeta.pt "top -bn1 | head -20"

# 3. Check slow queries
ssh ptisp@chapeuslisboeta.pt "mysql -e 'SHOW FULL PROCESSLIST;'"

# 4. Enable caching
ssh ptisp@chapeuslisboeta.pt "wp cache flush --path=/home/ptisp/public_html"

# 5. Purge CDN
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"purge_everything":true}'
```

### Backup Failed (P1)

```bash
# 1. Check backup logs
tail -100 /var/log/backup.log

# 2. Check disk space
ssh ptisp@chapeuslisboeta.pt "df -h"

# 3. Check S3 access
aws s3 ls s3://chapeus-backups-eu/

# 4. Manual backup
./scripts/backup-3-2-1.sh daily

# 5. Verify backup
ssh ptisp@chapeuslisboeta.pt "ls -lh /home/ptisp/backups/"
```

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Uptime | 99.9% | Prometheus blackbox_exporter |
| TTFB | <600ms | Core Web Vitals |
| LCP | <2.5s | Core Web Vitals |
| FID | <100ms | Core Web Vitals |
| CLS | <0.1 | Core Web Vitals |
| Checkout Speed | <3s | Custom metric |
| API Response | <500ms | WooCommerce API |
| Database Queries | <100ms avg | MySQL slow query log |
| CDN Cache Ratio | >90% | Cloudflare Analytics |

## Cost Breakdown

| Service | Cost/Month | Notes |
|---------|------------|-------|
| PTisp Hosting | €29.99 | Premium plan, Lisbon datacenter |
| Cloudflare Pro | €20.00 | WAF, DDoS, SSL, 20GB streaming |
| AWS S3 (Glacier) | ~€1.00 | ~250GB backups |
| **Total** | **€50.99** | **Target: <€52/month** |

**Savings vs Alternatives:**
- WP Engine: €290/month → **Save €239/month**
- Shopify Plus: €2,000/month → **Save €1,949/month**
- Managed WooCommerce: €79/month → **Save €28/month**

## Support

**Priority Levels:**
- P1 (Critical): Site down, no sales → Response: 15 minutes
- P2 (High): Performance issues → Response: 2 hours
- P3 (Medium): Non-critical bugs → Response: 1 day
- P4 (Low): Feature requests → Response: 1 week

**Contacts:**
- DevOps: Bilal Machraa (bilal@aiparati.com)
- Hosting: PTisp Support (24/7 phone)
- Client: Tiago Andrade (+351 918 911 308)

**Escalation:**
1. Check monitoring dashboards
2. Review runbooks (docs/runbooks/)
3. Contact DevOps engineer
4. Contact hosting support
5. Restore from backup if needed

## License

Proprietary - Chapéus Lisboeta © 2025

---

**Created by:** Bilal Machraa / AiParaTi
**Client:** Chapéus Lisboeta (Tiago Andrade)
**Last Updated:** 2025-01-14
**Version:** 2.0
**Mission:** "Zero data loss, maximum reliability, Portuguese excellence"
