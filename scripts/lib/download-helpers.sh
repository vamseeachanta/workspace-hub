#!/usr/bin/env bash
# ABOUTME: Shared download helpers — source this file; set LOG_FILE and DRY_RUN before sourcing
# Usage: source scripts/lib/download-helpers.sh
# Callers must export: LOG_FILE (path), DRY_RUN (true|false)

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${LOG_FILE}"
}

download() {
  local url="$1"
  local dest_dir="$2"
  local filename="${3:-}"
  [[ -z "${filename}" ]] && filename="$(basename "${url}" | sed 's/%20/ /g')"
  local dest_path="${dest_dir}/${filename}"

  if [[ -f "${dest_path}" ]]; then
    log "SKIP (exists): ${filename}"
    return 0
  fi

  if [[ "${DRY_RUN}" == "true" ]]; then
    log "DRY-RUN: would download ${url} → ${dest_path}"
    return 0
  fi

  log "DOWNLOADING: ${filename}"
  if wget -q --timeout=60 --tries=3 -O "${dest_path}" "${url}"; then
    local size
    size=$(du -sh "${dest_path}" | cut -f1)
    log "OK: ${filename} (${size})"
  else
    log "FAIL: ${filename} — ${url}"
    rm -f "${dest_path}"
    return 1
  fi
}
