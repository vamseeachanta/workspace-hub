#!/usr/bin/env bash
# ABOUTME: Template for domain-specific literature download scripts
# ABOUTME: Placeholders: {{DOMAIN}}, {{DEST}}, {{URLS}} — filled by research-domain.py
# Usage: bash download-literature.sh [--dry-run]

set -euo pipefail

DEST="{{DEST}}"
LOG_DIR="$(git rev-parse --show-toplevel)/.claude/work-queue/assets"
LOG_FILE="${LOG_DIR}/download-{{DOMAIN}}.log"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

mkdir -p "${DEST}"
mkdir -p "${LOG_DIR}"

# shellcheck source=scripts/lib/download-helpers.sh
source "$(git rev-parse --show-toplevel)/scripts/lib/download-helpers.sh"

log "=== {{DOMAIN}} Literature Download ==="
log "Destination: ${DEST}"
log "Dry run: ${DRY_RUN}"

# ─────────────────────────────────────────────
# DOWNLOADS — auto-generated + manually curated
# ─────────────────────────────────────────────

{{URLS}}

log "=== Download complete ==="
