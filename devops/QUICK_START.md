# Chapéus Lisboeta DevOps - Quick Start Guide

Get the entire DevOps infrastructure running in **30 minutes**.

## Prerequisites Checklist

- [ ] PTisp hosting account active
- [ ] Domain DNS pointed to PTisp server
- [ ] SSH access to server configured
- [ ] AWS account created (for S3 backups)
- [ ] Cloudflare account created (for CDN/WAF)
- [ ] Telegram bot created (for alerts)
- [ ] Docker Desktop installed (for monitoring)
- [ ] Git repository cloned locally

## Step 1: Configure Environment (5 minutes)

```bash
# Clone repository
cd /Users/bilal/Programaçao/Tiago\ Andrado/full-chapeus-lisboetas\ \(2\)/devops

# Create environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required variables:**

```bash
# PTisp Server
PTISP_USER=ptisp
PTISP_HOST=chapeuslisboeta.pt

# Database (from WordPress wp-config.php)
DB_HOST=localhost
DB_NAME=lisboetas_web
DB_USER=lisboetas
DB_PASSWORD=e$$4rU9h8

# AWS S3 (create at https://console.aws.amazon.com/iam/)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=chapeus-backups-eu
S3_REGION=eu-west-3

# Cloudflare (get from https://dash.cloudflare.com/profile/api-tokens)
CF_API_TOKEN=...
CF_ZONE_ID=...

# Telegram (create bot via @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_CHAT_ID=...

# WooCommerce API (WP Admin → WooCommerce → Settings → Advanced → REST API)
WC_API_KEY=ck_...
WC_API_SECRET=cs_...
```

## Step 2: Setup Infrastructure as Code (10 minutes)

```bash
# Install Terraform
brew install terraform  # macOS
# or download from https://www.terraform.io/downloads

# Navigate to Terraform directory
cd terraform/environments/production

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Apply infrastructure
terraform apply
# Type 'yes' when prompted

# Save outputs
terraform output > ../../terraform-outputs.txt
```

**What this creates:**
- Cloudflare DNS records
- Cloudflare WAF rules
- Cloudflare page rules (caching)
- AWS S3 backup bucket
- S3 lifecycle policies
- IAM user for backups

## Step 3: Deploy Monitoring Stack (5 minutes)

```bash
# Navigate to monitoring directory
cd ../../monitoring

# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Wait 30 seconds for services to start
sleep 30

# Verify services
docker-compose ps

# Access dashboards
open http://localhost:3000  # Grafana (admin/ChapeusAdmin2024!)
open http://localhost:9090  # Prometheus
open http://localhost:9093  # Alertmanager
```

**Grafana setup:**
1. Login at http://localhost:3000
2. Navigate to Dashboards
3. Import pre-built dashboards from `grafana/dashboard-files/`
4. Configure notification channels (Settings → Alerting → Notification channels)

## Step 4: Setup Backup System (5 minutes)

```bash
# Navigate to scripts directory
cd ../scripts

# Make scripts executable
chmod +x *.sh *.py

# Generate encryption key on server
ssh ptisp@chapeuslisboeta.pt "openssl rand -base64 32 > /home/ptisp/.backup-key && chmod 600 /home/ptisp/.backup-key"

# Test backup (dry run)
./backup-3-2-1.sh daily

# Verify backup created
ssh ptisp@chapeuslisboeta.pt "ls -lh /home/ptisp/backups/"

# Verify S3 upload
aws s3 ls s3://chapeus-backups-eu/
```

## Step 5: Install Cron Jobs (5 minutes)

```bash
# Copy crontab to server
scp ../cron/crontab.txt ptisp@chapeuslisboeta.pt:/tmp/

# Install cron jobs on server
ssh ptisp@chapeuslisboeta.pt << 'EOF'
    # Backup existing crontab
    crontab -l > /tmp/crontab.backup 2>/dev/null || true

    # Install new crontab
    crontab /tmp/crontab.txt

    # Verify installation
    crontab -l | head -20
EOF

# Check cron logs
ssh ptisp@chapeuslisboeta.pt "tail -f /var/log/cron.log"
```

## Step 6: Test Deployment (5 minutes)

```bash
# First deployment to staging
./deploy.sh staging

# Wait for deployment to complete
# Check deployment report
cat deployment-report-*.txt

# Verify staging site
curl -I https://staging.chapeuslisboeta.pt

# If staging OK, deploy to production
./deploy.sh production v2.0.0

# Verify production
curl -I https://chapeuslisboeta.pt
open https://chapeuslisboeta.pt
```

## Verification Checklist

After setup, verify everything works:

### Backups
- [ ] Hourly backup running (check `/var/log/backup-hourly.log`)
- [ ] Daily backup running (check `/var/log/backup-daily.log`)
- [ ] Backups appear in S3 (`aws s3 ls s3://chapeus-backups-eu/`)
- [ ] Local backups synced (`ls ~/chapeus-backups/`)
- [ ] Backup verification passing

### Monitoring
- [ ] Grafana accessible (http://localhost:3000)
- [ ] Prometheus scraping targets (http://localhost:9090/targets)
- [ ] Website uptime showing (Grafana → Website Uptime dashboard)
- [ ] Alerts configured (Alertmanager → http://localhost:9093)
- [ ] Telegram notifications working

### Deployment
- [ ] Blue-green directories exist (`ssh ptisp@chapeuslisboeta.pt "ls -ld /home/ptisp/{blue,green}"`)
- [ ] Health checks passing
- [ ] Rollback tested
- [ ] CDN cache purging working

### Cost Optimization
- [ ] Image optimization running
- [ ] Database cleanup working
- [ ] Cost reports generating
- [ ] Cloudflare caching active (check analytics)

### Security
- [ ] SSL certificate valid (https://www.ssllabs.com/ssltest/)
- [ ] WAF rules active (Cloudflare dashboard)
- [ ] Rate limiting working (test login attempts)
- [ ] Security headers present (`curl -I https://chapeuslisboeta.pt`)

## Quick Commands Reference

### Daily Operations

```bash
# Check site health
curl -s https://chapeuslisboeta.pt/wp-json/ | jq .

# Check backup status
aws s3 ls s3://chapeus-backups-eu/ | tail -5

# View monitoring
open http://localhost:3000

# Check logs
ssh ptisp@chapeuslisboeta.pt "tail -100 /var/log/backup.log"
```

### Deploy New Version

```bash
# Deploy to staging first
./scripts/deploy.sh staging

# Test staging
open https://staging.chapeuslisboeta.pt

# Deploy to production
./scripts/deploy.sh production v2.0.1
```

### Restore from Backup

```bash
# List backups
aws s3 ls s3://chapeus-backups-eu/

# Download and restore
aws s3 cp s3://chapeus-backups-eu/chapeus-db-20250114.sql.gz.enc /tmp/
ssh ptisp@chapeuslisboeta.pt << 'EOF'
    openssl enc -aes-256-cbc -d -pbkdf2 -pass file:/home/ptisp/.backup-key \
        -in /tmp/chapeus-db-20250114.sql.gz.enc | \
        gunzip | \
        wp db import - --path=/home/ptisp/public_html
EOF
```

### Emergency Rollback

```bash
./scripts/rollback.sh
```

### View Metrics

```bash
# Server resources
ssh ptisp@chapeuslisboeta.pt "top -bn1 | head -20"

# Disk space
ssh ptisp@chapeuslisboeta.pt "df -h"

# Database size
ssh ptisp@chapeuslisboeta.pt "wp db size --path=/home/ptisp/public_html"

# WooCommerce stats
ssh ptisp@chapeuslisboeta.pt "wp wc product list --format=count --path=/home/ptisp/public_html"
```

## Troubleshooting

### Backup Fails

```bash
# Check disk space
ssh ptisp@chapeuslisboeta.pt "df -h"

# Check S3 credentials
aws s3 ls s3://chapeus-backups-eu/

# Check encryption key
ssh ptisp@chapeuslisboeta.pt "[ -f /home/ptisp/.backup-key ] && echo 'Key exists' || echo 'Key missing'"

# Run backup manually with debug
./scripts/backup-3-2-1.sh daily
```

### Monitoring Not Working

```bash
# Check Docker containers
docker-compose -f monitoring/docker-compose.monitoring.yml ps

# Restart monitoring stack
docker-compose -f monitoring/docker-compose.monitoring.yml restart

# Check logs
docker logs chapeus_prometheus
docker logs chapeus_grafana
```

### Deployment Fails

```bash
# Check deployment logs
cat deployment-report-*.txt

# Check server connection
ssh ptisp@chapeuslisboeta.pt "echo 'Connection OK'"

# Check WP-CLI
ssh ptisp@chapeuslisboeta.pt "wp --version"

# Manual rollback
./scripts/rollback.sh
```

### High Costs

```bash
# Run cost optimization
python3 scripts/cost-optimizer.py

# Check S3 storage
aws s3 ls s3://chapeus-backups-eu/ --recursive --human-readable --summarize

# Check Cloudflare usage
# Login to https://dash.cloudflare.com → Analytics
```

## Next Steps

After initial setup:

1. **Week 1:**
   - Monitor daily backup logs
   - Review Grafana dashboards daily
   - Test recovery procedure once
   - Verify all alerts working

2. **Week 2:**
   - Fine-tune alert thresholds
   - Optimize Cloudflare caching rules
   - Run cost optimization
   - Document any custom procedures

3. **Month 1:**
   - Conduct monthly recovery drill
   - Review cost report
   - Analyze performance metrics
   - Plan optimizations

4. **Ongoing:**
   - Review monthly cost reports
   - Update documentation
   - Test disaster recovery quarterly
   - Keep scripts updated

## Support

**Documentation:**
- Full DevOps guide: `DEPLOYMENT_STRATEGY.md`
- Detailed README: `README.md`
- Architecture diagrams: `docs/architecture/`
- Runbooks: `docs/runbooks/`

**Contacts:**
- DevOps Engineer: Bilal Machraa (bilal@aiparati.com)
- PTisp Support: 24/7 phone support
- Client: Tiago Andrade (+351 918 911 308)

**Resources:**
- Terraform docs: https://www.terraform.io/docs
- Prometheus docs: https://prometheus.io/docs
- Grafana docs: https://grafana.com/docs
- WP-CLI handbook: https://developer.wordpress.org/cli/

## Success Metrics

Target metrics after 30 days:

- [ ] **Uptime:** 99.9%+ (verified in Grafana)
- [ ] **RPO:** <1 hour (hourly backups working)
- [ ] **RTO:** <30 minutes (tested recovery)
- [ ] **Cost:** <€52/month (verified in cost reports)
- [ ] **Performance:** TTFB <600ms, LCP <2.5s
- [ ] **Security:** SSL A+ rating
- [ ] **Backups:** 90 days retention, 3 copies
- [ ] **Monitoring:** 100% alert coverage

---

**Ready to launch!** 🚀

All systems configured for:
- **Zero data loss** (3-2-1 backups)
- **Zero downtime** (blue-green deployments)
- **Zero surprises** (comprehensive monitoring)
- **Zero waste** (cost optimization)

**Client Mission:** "This time, with total guarantees." ✓

---

*Created by: Bilal Machraa / AiParaTi*
*For: Chapéus Lisboeta (Tiago Andrade)*
*Date: 2025-01-14*
*Version: 2.0*
