#!/usr/bin/env bash
# WRK-1384: Relocate local-analysis files to /mnt/ace/ knowledge center
# Generated: 2026-03-24
#
# Usage:
#   bash relocate-to-ace.sh [--dry-run]
#
# This script uses rsync to COPY files (non-destructive).
# Originals remain until you manually delete them after verification.
set -euo pipefail

SRC="/mnt/remote/ace-linux-2/local-analysis"
DST="/mnt/ace"
DRY_RUN=""
LOG_FILE="/mnt/local-analysis/workspace-hub/.claude/work-queue/assets/workspace-hub-1384/relocation-log-$(date +%Y%m%d-%H%M%S).txt"

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN="--dry-run"
  echo "=== DRY RUN MODE ==="
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "Starting relocation from $SRC to $DST"
log "Dry run: ${DRY_RUN:-no}"

# ── Category 1: Engineering Projects → client_projects/ ─────────────────
PROJECTS=(
  "0111 RII:0111-RII"
  "0112 CN Adapter:0112-CN-Adapter"
  "0116 Thinwall Pipe FEA:0116-Thinwall-Pipe-FEA"
  "0119 Programming:0119-Programming"
  "0127 Mooring:0127-Mooring"
  "0132:0132"
  "0154 TVO:0154-TVO"
  "0159 Anchor FEA:0159-Anchor-FEA"
  "0162-001:0162-001"
  "0163-FDAS:0163-FDAS"
  "0182:0182"
  "0190:0190"
  "0198:0198"
  "Sewol:Sewol"
  "0000 Completed:0000-Completed"
)

for entry in "${PROJECTS[@]}"; do
  src_name="${entry%%:*}"
  dst_name="${entry##*:}"
  if [[ -d "$SRC/$src_name" ]]; then
    log "Syncing: $src_name → client_projects/$dst_name/"
    mkdir -p "$DST/client_projects/$dst_name"
    rsync -avh --progress $DRY_RUN "$SRC/$src_name/" "$DST/client_projects/$dst_name/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
  else
    log "SKIP (not found): $src_name"
  fi
done

# ── Category 2: Conference Literature → docs/conferences/ ───────────────
if [[ -d "$SRC/0000 Conferences" ]]; then
  log "Syncing: 0000 Conferences → docs/conferences/"
  mkdir -p "$DST/docs/conferences"
  rsync -avh --progress $DRY_RUN "$SRC/0000 Conferences/" "$DST/docs/conferences/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
fi

# ── Category 3: Business/Admin → aceengineer-admin/ ─────────────────────
if [[ -d "$SRC/0000 GDrive" ]]; then
  log "Syncing: 0000 GDrive → aceengineer-admin/gdrive-export/"
  mkdir -p "$DST/aceengineer-admin/gdrive-export"
  rsync -avh --progress $DRY_RUN "$SRC/0000 GDrive/" "$DST/aceengineer-admin/gdrive-export/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
fi

if [[ -d "$SRC/0000 www" ]]; then
  log "Syncing: 0000 www → aceengineer-admin/www-archive/"
  mkdir -p "$DST/aceengineer-admin/www-archive"
  rsync -avh --progress $DRY_RUN "$SRC/0000 www/" "$DST/aceengineer-admin/www-archive/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
fi

# ── Category 4: Data/Research → data/ ───────────────────────────────────
if [[ -d "$SRC/OSI" ]]; then
  log "Syncing: OSI → data/osi-datasets/"
  mkdir -p "$DST/data/osi-datasets"
  rsync -avh --progress $DRY_RUN "$SRC/OSI/" "$DST/data/osi-datasets/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
fi

if [[ -f "$SRC/OrcFxAPIConfig.py" ]]; then
  log "Syncing: OrcFxAPIConfig.py → digitalmodel/"
  rsync -avh --progress $DRY_RUN "$SRC/OrcFxAPIConfig.py" "$DST/digitalmodel/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
fi

# ── Category 5: Reference → docs/ ──────────────────────────────────────
if [[ -d "$SRC/repo" ]]; then
  log "Syncing: repo → docs/engineering-drawings/"
  mkdir -p "$DST/docs/engineering-drawings"
  rsync -avh --progress $DRY_RUN "$SRC/repo/" "$DST/docs/engineering-drawings/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
fi

if [[ -d "$SRC/github_ref" ]]; then
  log "Syncing: github_ref → docs/github-references/"
  mkdir -p "$DST/docs/github-references"
  rsync -avh --progress $DRY_RUN "$SRC/github_ref/" "$DST/docs/github-references/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
fi

log "=== Relocation complete ==="
log "Review log: $LOG_FILE"
log ""
log "Items NOT relocated (manual review needed):"
log "  - Temp (77G) - mixed content"
log "  - InstallationFiles (18G) - software installers"
log "  - itunes (16G) - personal media"
log "  - 0000 BigData (415M) - training materials"
log "  - DataStax-Community Edition (100M)"
log "  - HadoopCourse (37M)"
log "  - solidworks (42M)"
log "  - 0000 Tecplot (5.4M)"
log ""
log "Items safe to delete:"
log "  - \$RECYCLE.BIN, System Volume Information, DumpStack.log.tmp"
log "  - msdia80.dll, acma_wood.ps1, Dropbox (empty), Son_Server2"
