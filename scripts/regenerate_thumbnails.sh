#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="$ROOT_DIR/relatorios/THUMBNAILS_REGEN_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$ROOT_DIR/relatorios"
cd "$ROOT_DIR"
command -v docker >/dev/null || { echo "docker not found" >&2; exit 1; }
SECONDS=0
echo "Running wp media regenerate --yes --allow-root" | tee -a "$LOG_FILE"
docker exec chapeus_wordpress wp media regenerate --yes --allow-root 2>&1 | tee -a "$LOG_FILE"
echo "Completed in $SECONDS seconds" | tee -a "$LOG_FILE"
