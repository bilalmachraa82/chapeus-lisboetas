# Chapéus Lisboeta - Production Infrastructure as Code
# Terraform configuration for PTisp + Cloudflare setup

terraform {
  required_version = ">= 1.5"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "chapeus-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "eu-west-3"  # Paris (closest to Lisbon)
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# Variables
variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID"
  type        = string
}

variable "ptisp_ip" {
  description = "PTisp server IP address"
  type        = string
  default     = "188.93.56.10"  # Replace with actual IP
}

variable "domain" {
  description = "Main domain"
  type        = string
  default     = "chapeuslisboeta.pt"
}

# Providers
provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

provider "aws" {
  region = "eu-west-3"
}

# Cloudflare Zone
resource "cloudflare_zone" "chapeus" {
  account_id = var.cloudflare_account_id
  zone       = var.domain
  plan       = "pro"  # €20/month - includes WAF, advanced DDoS, 20GB video streaming
}

# DNS Records
resource "cloudflare_record" "root" {
  zone_id = cloudflare_zone.chapeus.id
  name    = "@"
  value   = var.ptisp_ip
  type    = "A"
  proxied = true
  ttl     = 1
  comment = "PTisp hosting server"
}

resource "cloudflare_record" "www" {
  zone_id = cloudflare_zone.chapeus.id
  name    = "www"
  value   = var.domain
  type    = "CNAME"
  proxied = true
  ttl     = 1
  comment = "WWW redirect"
}

resource "cloudflare_record" "staging" {
  zone_id = cloudflare_zone.chapeus.id
  name    = "staging"
  value   = var.ptisp_ip
  type    = "A"
  proxied = true
  ttl     = 1
  comment = "Staging environment"
}

resource "cloudflare_record" "blue" {
  zone_id = cloudflare_zone.chapeus.id
  name    = "blue"
  value   = var.ptisp_ip
  type    = "A"
  proxied = false  # Direct access for health checks
  ttl     = 120
  comment = "Blue deployment environment"
}

resource "cloudflare_record" "green" {
  zone_id = cloudflare_zone.chapeus.id
  name    = "green"
  value   = var.ptisp_ip
  type    = "A"
  proxied = false
  ttl     = 120
  comment = "Green deployment environment"
}

# Email records (for transactional emails via SMTP2GO)
resource "cloudflare_record" "mx1" {
  zone_id  = cloudflare_zone.chapeus.id
  name     = "@"
  value    = "mx1.smtp2go.com"
  type     = "MX"
  priority = 10
  ttl      = 3600
}

resource "cloudflare_record" "mx2" {
  zone_id  = cloudflare_zone.chapeus.id
  name     = "@"
  value    = "mx2.smtp2go.com"
  type     = "MX"
  priority = 20
  ttl      = 3600
}

resource "cloudflare_record" "spf" {
  zone_id = cloudflare_zone.chapeus.id
  name    = "@"
  value   = "v=spf1 include:smtp2go.com ~all"
  type    = "TXT"
  ttl     = 3600
}

resource "cloudflare_record" "dmarc" {
  zone_id = cloudflare_zone.chapeus.id
  name    = "_dmarc"
  value   = "v=DMARC1; p=quarantine; rua=mailto:admin@chapeuslisboeta.pt"
  type    = "TXT"
  ttl     = 3600
}

# Security Settings
resource "cloudflare_zone_settings_override" "chapeus_security" {
  zone_id = cloudflare_zone.chapeus.id

  settings {
    # Security
    security_level         = "high"
    ssl                   = "strict"
    min_tls_version       = "1.2"
    tls_1_3               = "on"
    automatic_https_rewrites = "on"
    always_use_https      = "on"
    opportunistic_encryption = "on"

    # Performance
    brotli                = "on"
    early_hints          = "on"
    http2                = "on"
    http3                = "on"
    zero_rtt             = "on"
    rocket_loader        = "off"  # Conflicts with WooCommerce
    mirage               = "on"   # Image optimization

    # DDoS Protection
    challenge_ttl        = 1800
    browser_check        = "on"

    # Caching
    cache_level          = "aggressive"
    development_mode     = "off"

    # Other
    ip_geolocation       = "on"
    email_obfuscation    = "on"
    hotlink_protection   = "on"
    websockets          = "on"
  }
}

# Page Rules
resource "cloudflare_page_rule" "cache_images" {
  zone_id  = cloudflare_zone.chapeus.id
  target   = "${var.domain}/wp-content/uploads/*"
  priority = 1

  actions {
    cache_level         = "cache_everything"
    edge_cache_ttl      = 2628000  # 1 month
    browser_cache_ttl   = 604800   # 1 week
  }
}

resource "cloudflare_page_rule" "cache_static" {
  zone_id  = cloudflare_zone.chapeus.id
  target   = "${var.domain}/*.{jpg,jpeg,png,gif,webp,svg,css,js,woff,woff2,ttf,eot,ico}"
  priority = 2

  actions {
    cache_level         = "cache_everything"
    edge_cache_ttl      = 604800  # 1 week
    browser_cache_ttl   = 86400   # 1 day
  }
}

resource "cloudflare_page_rule" "no_cache_checkout" {
  zone_id  = cloudflare_zone.chapeus.id
  target   = "${var.domain}/checkout/*"
  priority = 3

  actions {
    cache_level = "bypass"
  }
}

resource "cloudflare_page_rule" "no_cache_cart" {
  zone_id  = cloudflare_zone.chapeus.id
  target   = "${var.domain}/cart/*"
  priority = 4

  actions {
    cache_level = "bypass"
  }
}

resource "cloudflare_page_rule" "no_cache_admin" {
  zone_id  = cloudflare_zone.chapeus.id
  target   = "${var.domain}/wp-admin/*"
  priority = 5

  actions {
    cache_level     = "bypass"
    security_level  = "high"
  }
}

# WAF Rules
resource "cloudflare_ruleset" "waf_custom" {
  zone_id     = cloudflare_zone.chapeus.id
  name        = "Chapeus Custom WAF Rules"
  description = "Portuguese e-commerce security rules"
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  rules {
    action      = "block"
    expression  = "(http.request.uri.path contains \"wp-login.php\" and ip.geoip.country ne \"PT\" and ip.geoip.country ne \"BR\")"
    description = "Block non-Portuguese logins"
    enabled     = true
  }

  rules {
    action      = "challenge"
    expression  = "(cf.threat_score gt 14)"
    description = "Challenge medium threats"
    enabled     = true
  }

  rules {
    action      = "block"
    expression  = "(http.request.uri.path contains \"xmlrpc.php\")"
    description = "Block XML-RPC attacks"
    enabled     = true
  }

  rules {
    action      = "block"
    expression  = "(http.request.method eq \"POST\" and http.request.uri.path contains \"/wp-admin/\" and not http.referer contains \"${var.domain}\")"
    description = "Block CSRF attempts"
    enabled     = true
  }

  rules {
    action      = "js_challenge"
    expression  = "(http.user_agent contains \"bot\" and not any(http.user_agent[*] in {\"googlebot\" \"bingbot\" \"slackbot\"}))"
    description = "Challenge suspicious bots"
    enabled     = true
  }
}

# Rate Limiting
resource "cloudflare_rate_limit" "login_limit" {
  zone_id = cloudflare_zone.chapeus.id

  threshold = 5
  period    = 60
  match {
    request {
      url_pattern = "${var.domain}/wp-login.php"
    }
  }

  action {
    mode    = "ban"
    timeout = 600
  }

  description = "Rate limit login attempts"
}

resource "cloudflare_rate_limit" "api_limit" {
  zone_id = cloudflare_zone.chapeus.id

  threshold = 100
  period    = 60
  match {
    request {
      url_pattern = "${var.domain}/wp-json/*"
    }
  }

  action {
    mode    = "challenge"
    timeout = 60
  }

  description = "Rate limit API requests"
}

# Load Balancer (for future multi-region expansion)
resource "cloudflare_load_balancer_pool" "ptisp_primary" {
  account_id = var.cloudflare_account_id
  name       = "ptisp-lisbon-primary"

  origins {
    name    = "ptisp-server-1"
    address = var.ptisp_ip
    enabled = true
  }

  check_regions = ["WEU"]  # Western Europe
  description   = "PTisp primary server pool"
  enabled       = true

  monitor = cloudflare_load_balancer_monitor.http_monitor.id
}

resource "cloudflare_load_balancer_monitor" "http_monitor" {
  account_id     = var.cloudflare_account_id
  type           = "https"
  expected_codes = "200"
  method         = "GET"
  timeout        = 5
  path           = "/wp-json"
  interval       = 60
  retries        = 2
  description    = "WordPress health check"

  header {
    header = "Host"
    values = [var.domain]
  }
}

# AWS S3 Backup Storage
resource "aws_s3_bucket" "backups" {
  bucket = "chapeus-backups-eu"

  tags = {
    Name        = "Chapeus Lisboeta Backups"
    Environment = "production"
    Project     = "chapeus-lisboeta"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "transition_to_glacier"
    status = "Enabled"

    transition {
      days          = 7
      storage_class = "GLACIER_IR"
    }

    transition {
      days          = 30
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = 90
    }
  }

  rule {
    id     = "delete_incomplete_uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM User for Backups
resource "aws_iam_user" "backup_user" {
  name = "chapeus-backup-user"
  path = "/backup/"

  tags = {
    Name    = "Backup Service Account"
    Project = "chapeus-lisboeta"
  }
}

resource "aws_iam_access_key" "backup_user" {
  user = aws_iam_user.backup_user.name
}

resource "aws_iam_user_policy" "backup_user" {
  name = "backup-policy"
  user = aws_iam_user.backup_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.backups.arn}",
          "${aws_s3_bucket.backups.arn}/*"
        ]
      }
    ]
  })
}

# DynamoDB for Terraform State Locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name    = "Terraform State Lock"
    Project = "chapeus-lisboeta"
  }
}

# Outputs
output "cloudflare_zone_id" {
  value       = cloudflare_zone.chapeus.id
  description = "Cloudflare Zone ID"
}

output "cloudflare_nameservers" {
  value       = cloudflare_zone.chapeus.name_servers
  description = "Nameservers to configure at domain registrar"
}

output "s3_backup_bucket" {
  value       = aws_s3_bucket.backups.bucket
  description = "S3 backup bucket name"
}

output "backup_user_access_key" {
  value       = aws_iam_access_key.backup_user.id
  description = "Backup user access key ID"
}

output "backup_user_secret_key" {
  value       = aws_iam_access_key.backup_user.secret
  description = "Backup user secret access key"
  sensitive   = true
}

output "load_balancer_hostname" {
  value       = cloudflare_load_balancer_pool.ptisp_primary.name
  description = "Load balancer pool hostname"
}
