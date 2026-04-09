#!/usr/bin/env bash
# wiki-ingest-cron.sh — Nightly incremental ingest for the engineering wiki.
# Detects new/modified sources since last run, triggers ingest, runs lint,
# auto-commits changes, and logs results.
#
# Usage:
#   bash scripts/knowledge/wiki-ingest-cron.sh [--dry-run]
#
# Issue: #2036
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WIKI_DOMAIN="engineering"
WIKI_DIR="${REPO_ROOT}/knowledge/wikis/${WIKI_DOMAIN}"
WIKI_PAGES_DIR="${WIKI_DIR}/wiki"
LOG_DIR="${REPO_ROOT}/logs/wiki-ingest"
MARKER_FILE="${WIKI_DIR}/.last-ingest-run"
DATE_TAG="$(date +%Y%m%d)"
DATE_ISO="$(date +%Y-%m-%d)"
LOG_FILE="${LOG_DIR}/ingest-${DATE_TAG}.log"

DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

# ── Ensure log directory exists ──────────────────────────────────────────────
mkdir -p "${LOG_DIR}"

# ── Logging helper ───────────────────────────────────────────────────────────
log() {
  local msg="[$(date +%Y-%m-%dT%H:%M:%S)] $*"
  echo "$msg" | tee -a "${LOG_FILE}"
}

log "=== Wiki incremental ingest started ==="
log "Domain: ${WIKI_DOMAIN}"
log "Dry run: ${DRY_RUN}"

# ── Count pages before ingest ────────────────────────────────────────────────
PAGE_COUNT_BEFORE=$(find "${WIKI_PAGES_DIR}" -name '*.md' 2>/dev/null | wc -l)
log "Page count before: ${PAGE_COUNT_BEFORE}"

# ── Determine last-run timestamp ─────────────────────────────────────────────
if [[ -f "${MARKER_FILE}" ]]; then
  LAST_RUN=$(cat "${MARKER_FILE}")
  log "Last ingest run: ${LAST_RUN}"
else
  # First run — use epoch (scan everything)
  LAST_RUN="1970-01-01T00:00:00"
  log "No previous run marker found — scanning all sources"
fi

# ── Source class directories to scan for new/modified files ──────────────────
# Maps to SOURCE_INVENTORY.md classes 1-8
SOURCE_DIRS=(
  "${REPO_ROOT}/docs/methodology"
  "${REPO_ROOT}/docs/modules"
  "${REPO_ROOT}/.claude/memory/topics"
  "${REPO_ROOT}/docs/architecture"
  "${REPO_ROOT}/knowledge/seeds"
  "${REPO_ROOT}/knowledge/dark-intelligence"
  "${REPO_ROOT}/knowledge/wikis/${WIKI_DOMAIN}/raw"
)

# Single files to check (Class 8)
SOURCE_FILES=(
  "${REPO_ROOT}/.claude/memory/KNOWLEDGE.md"
)

# ── Scan for modified sources ────────────────────────────────────────────────
MODIFIED_SOURCES=()

for dir in "${SOURCE_DIRS[@]}"; do
  if [[ ! -d "${dir}" ]]; then
    log "SKIP: directory not found: ${dir}"
    continue
  fi
  while IFS= read -r file; do
    [[ -n "${file}" ]] && MODIFIED_SOURCES+=("${file}")
  done < <(find "${dir}" -type f \( -name '*.md' -o -name '*.yaml' -o -name '*.yml' -o -name '*.json' \) -newer "${MARKER_FILE}" 2>/dev/null || true)
done

for file in "${SOURCE_FILES[@]}"; do
  if [[ -f "${file}" ]]; then
    if [[ ! -f "${MARKER_FILE}" ]] || [[ "${file}" -nt "${MARKER_FILE}" ]]; then
      MODIFIED_SOURCES+=("${file}")
    fi
  fi
done

log "Modified sources found: ${#MODIFIED_SOURCES[@]}"

if [[ ${#MODIFIED_SOURCES[@]} -eq 0 ]]; then
  log "No new/modified sources detected — skipping ingest"
  # Update marker even if nothing to ingest (so next run only scans from now)
  if [[ "${DRY_RUN}" == "false" ]]; then
    date -u +%Y-%m-%dT%H:%M:%S > "${MARKER_FILE}"
  fi
  log "=== Wiki incremental ingest completed (no changes) ==="
  exit 0
fi

# ── Log each modified source ─────────────────────────────────────────────────
for src in "${MODIFIED_SOURCES[@]}"; do
  log "  Modified: ${src#${REPO_ROOT}/}"
done

# ── Run ingest for each modified source ──────────────────────────────────────
INGEST_OK=0
INGEST_FAIL=0

for src in "${MODIFIED_SOURCES[@]}"; do
  rel_path="${src#${REPO_ROOT}/}"
  log "Ingesting: ${rel_path}"

  if [[ "${DRY_RUN}" == "true" ]]; then
    log "  [dry-run] Would run: uv run scripts/knowledge/llm_wiki.py ingest ${rel_path} --wiki ${WIKI_DOMAIN}"
    INGEST_OK=$((INGEST_OK + 1))
    continue
  fi

  if cd "${REPO_ROOT}" && uv run scripts/knowledge/llm_wiki.py ingest "${src}" --wiki "${WIKI_DOMAIN}" >> "${LOG_FILE}" 2>&1; then
    log "  OK: ${rel_path}"
    INGEST_OK=$((INGEST_OK + 1))
  else
    log "  FAIL: ${rel_path} (exit code $?)"
    INGEST_FAIL=$((INGEST_FAIL + 1))
  fi
done

log "Ingest results: ${INGEST_OK} OK, ${INGEST_FAIL} failed"

# ── Run lint ─────────────────────────────────────────────────────────────────
log "Running lint..."
LINT_EXIT=0
if [[ "${DRY_RUN}" == "false" ]]; then
  if cd "${REPO_ROOT}" && uv run scripts/knowledge/llm_wiki.py lint --wiki "${WIKI_DOMAIN}" >> "${LOG_FILE}" 2>&1; then
    log "Lint: PASS"
  else
    LINT_EXIT=$?
    log "Lint: FAIL (exit code ${LINT_EXIT})"
  fi
else
  log "[dry-run] Would run: uv run scripts/knowledge/llm_wiki.py lint --wiki ${WIKI_DOMAIN}"
fi

# ── Count pages after ingest ─────────────────────────────────────────────────
PAGE_COUNT_AFTER=$(find "${WIKI_PAGES_DIR}" -name '*.md' 2>/dev/null | wc -l)
DELTA=$((PAGE_COUNT_AFTER - PAGE_COUNT_BEFORE))
log "Page count after: ${PAGE_COUNT_AFTER} (delta: ${DELTA:+${DELTA}}${DELTA})"

# ── Page count drop detection (deletion alert) ──────────────────────────────
if [[ ${DELTA} -lt 0 ]]; then
  log "WARNING: Page count dropped by ${DELTA#-} pages — possible accidental deletion"
  if [[ "${DRY_RUN}" == "false" ]]; then
    # Create a GitHub issue to alert about page count drop
    EXISTING_ISSUE=$(cd "${REPO_ROOT}" && gh issue list --label "wiki-alert" --state open --json number --jq '.[0].number' 2>/dev/null || true)
    if [[ -z "${EXISTING_ISSUE}" ]]; then
      cd "${REPO_ROOT}" && gh issue create \
        --title "Wiki alert: page count dropped (${PAGE_COUNT_BEFORE} -> ${PAGE_COUNT_AFTER})" \
        --body "The nightly wiki ingest detected a page count drop in the **${WIKI_DOMAIN}** wiki.

- Before: ${PAGE_COUNT_BEFORE} pages
- After: ${PAGE_COUNT_AFTER} pages
- Delta: ${DELTA}
- Date: ${DATE_ISO}
- Log: \`logs/wiki-ingest/ingest-${DATE_TAG}.log\`

Please investigate whether pages were accidentally deleted." \
        --label "wiki-alert,priority:high" 2>> "${LOG_FILE}" || log "WARN: Failed to create GitHub issue for page drop"
    else
      log "Open wiki-alert issue already exists (#${EXISTING_ISSUE}) — skipping duplicate"
    fi
  fi
fi

# ── Lint failure alert ───────────────────────────────────────────────────────
if [[ ${LINT_EXIT} -ne 0 ]]; then
  log "WARNING: Lint failed — wiki quality issues detected"
  if [[ "${DRY_RUN}" == "false" ]]; then
    EXISTING_LINT_ISSUE=$(cd "${REPO_ROOT}" && gh issue list --label "wiki-lint" --state open --json number --jq '.[0].number' 2>/dev/null || true)
    if [[ -z "${EXISTING_LINT_ISSUE}" ]]; then
      cd "${REPO_ROOT}" && gh issue create \
        --title "Wiki lint failure: ${WIKI_DOMAIN} (${DATE_ISO})" \
        --body "The nightly wiki ingest lint check failed for the **${WIKI_DOMAIN}** wiki.

- Date: ${DATE_ISO}
- Log: \`logs/wiki-ingest/ingest-${DATE_TAG}.log\`
- Ingest results: ${INGEST_OK} OK, ${INGEST_FAIL} failed

Run \`uv run scripts/knowledge/llm_wiki.py lint --wiki ${WIKI_DOMAIN}\` to see details." \
        --label "wiki-lint" 2>> "${LOG_FILE}" || log "WARN: Failed to create GitHub issue for lint failure"
    else
      log "Open wiki-lint issue already exists (#${EXISTING_LINT_ISSUE}) — skipping duplicate"
    fi
  fi
fi

# ── Auto-commit if pages changed ────────────────────────────────────────────
if [[ "${DRY_RUN}" == "false" ]]; then
  cd "${REPO_ROOT}"
  if git diff --quiet "knowledge/wikis/${WIKI_DOMAIN}/" 2>/dev/null && \
     [[ -z "$(git ls-files --others --exclude-standard "knowledge/wikis/${WIKI_DOMAIN}/")" ]]; then
    log "No wiki file changes to commit"
  else
    git add "knowledge/wikis/${WIKI_DOMAIN}/"
    git commit -m "chore(wiki): incremental ingest ${DATE_ISO} (#2036)

Sources processed: ${INGEST_OK} OK, ${INGEST_FAIL} failed
Page delta: ${DELTA} (${PAGE_COUNT_BEFORE} -> ${PAGE_COUNT_AFTER})" || log "WARN: git commit failed (maybe nothing staged)"
    log "Committed wiki changes"
  fi

  # Update marker file
  date -u +%Y-%m-%dT%H:%M:%S > "${MARKER_FILE}"
  log "Updated last-run marker: $(cat "${MARKER_FILE}")"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
log "=== Wiki incremental ingest completed ==="
log "Summary: sources=${#MODIFIED_SOURCES[@]} ingested_ok=${INGEST_OK} ingested_fail=${INGEST_FAIL} lint_exit=${LINT_EXIT} pages_before=${PAGE_COUNT_BEFORE} pages_after=${PAGE_COUNT_AFTER} delta=${DELTA}"

# Exit non-zero if there were failures
if [[ ${INGEST_FAIL} -gt 0 ]] || [[ ${LINT_EXIT} -ne 0 ]]; then
  exit 1
fi
