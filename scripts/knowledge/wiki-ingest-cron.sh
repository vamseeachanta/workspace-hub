#!/usr/bin/env bash
# wiki-ingest-cron.sh — Nightly incremental ingest for the engineering wiki
#
# Scans source class directories for files modified since last run,
# triggers ingest via llm_wiki.py, runs lint, auto-commits changes.
#
# Usage: bash scripts/knowledge/wiki-ingest-cron.sh [--dry-run]
# Issue: #2036
set -uo pipefail

export PATH="${HOME}/.local/bin:${HOME}/.cargo/bin:/usr/local/bin:${PATH}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DATE=$(date -u +%Y-%m-%d)
DRY_RUN=false

for arg in "$@"; do
    [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

# ── Directories and paths ────────────────────────────────────────────────────
WIKI_ROOT="${REPO_ROOT}/knowledge/wikis/engineering"
LOG_DIR="${REPO_ROOT}/logs/wiki-ingest"
LOG_FILE="${LOG_DIR}/ingest-${DATE}.log"
MARKER_FILE="${WIKI_ROOT}/.last-ingest-timestamp"

mkdir -p "$LOG_DIR"

log() { echo "[wiki-ingest] $(date -u +%H:%M:%S) $*" | tee -a "$LOG_FILE"; }

WIKI_PAGES_DIR="${WIKI_ROOT}/wiki"
DATE_TAG="$(date +%Y%m%d)"

log "=== Engineering wiki incremental ingest: ${DATE} ==="
log "Dry run: ${DRY_RUN}"

# ── Hostname guard ───────────────────────────────────────────────────────────
source "${REPO_ROOT}/scripts/lib/workstation-lib.sh"
if ! ws_is "full"; then
    log "SKIP: not a full-variant machine (hostname=$(hostname -s), variant=$(ws_variant))"
    exit 0
fi

# ── Git helpers ──────────────────────────────────────────────────────────────
GIT_SAFE_LOG_PREFIX="[wiki-ingest]"
source "${REPO_ROOT}/scripts/cron/lib/git-safe.sh"
git_safe_init "$REPO_ROOT" 2>>"$LOG_FILE"

# ── Git pull ─────────────────────────────────────────────────────────────────
log "Pulling latest changes"
cd "$REPO_ROOT" || { log "ERROR: cannot cd to ${REPO_ROOT}"; exit 1; }
git_safe_pull 2>>"$LOG_FILE" || {
    log "WARNING: git pull failed — continuing with local state"
}

# ── Determine last-run timestamp ─────────────────────────────────────────────
if [[ -f "$MARKER_FILE" ]]; then
    LAST_RUN=$(cat "$MARKER_FILE")
    log "Last ingest run: ${LAST_RUN}"
else
    # First run: use epoch 0 so everything qualifies
    LAST_RUN="1970-01-01T00:00:00"
    log "First run — no marker file found, scanning all sources"
fi

# ── Source class directories to scan ─────────────────────────────────────────
# These align with SOURCE_INVENTORY.md classes 1-8.
SOURCE_LABELS=(
    "methodology"
    "modules"
    "session-learnings"
    "architecture"
    "knowledge-seeds"
    "dark-intelligence"
    "session-memory"
)
SOURCE_PATHS=(
    "docs/methodology"
    "docs/modules"
    ".claude/memory/topics"
    "docs/architecture"
    "knowledge/seeds"
    "knowledge/dark-intelligence"
    ".claude/memory/KNOWLEDGE.md"
)

# ── Scan for new/modified source files ───────────────────────────────────────
NEW_FILES=()
MODIFIED_FILES=()
TOTAL_CANDIDATES=0

for i in "${!SOURCE_LABELS[@]}"; do
    class_label="${SOURCE_LABELS[$i]}"
    src_rel="${SOURCE_PATHS[$i]}"
    src_path="${REPO_ROOT}/${src_rel}"

    if [[ ! -e "$src_path" ]]; then
        log "  [${class_label}] path not found: ${src_rel} — skipping"
        continue
    fi

    if [[ -f "$src_path" ]]; then
        # Single file source (e.g., KNOWLEDGE.md)
        TOTAL_CANDIDATES=$((TOTAL_CANDIDATES + 1))
        if [[ ! -f "$MARKER_FILE" ]]; then
            NEW_FILES+=("${src_path}")
            log "  [${class_label}] new: $(basename "$src_path")"
        elif [[ "$src_path" -nt "$MARKER_FILE" ]]; then
            MODIFIED_FILES+=("${src_path}")
            log "  [${class_label}] modified: $(basename "$src_path")"
        fi
    elif [[ -d "$src_path" ]]; then
        # Directory source — find files newer than marker
        while IFS= read -r -d '' file; do
            # Skip hidden files and non-content files
            bname="$(basename "$file")"
            [[ "$bname" == .* ]] && continue
            TOTAL_CANDIDATES=$((TOTAL_CANDIDATES + 1))

            if [[ ! -f "$MARKER_FILE" ]]; then
                NEW_FILES+=("$file")
                log "  [${class_label}] new: ${bname}"
            elif [[ "$file" -nt "$MARKER_FILE" ]]; then
                MODIFIED_FILES+=("$file")
                log "  [${class_label}] modified: ${bname}"
            fi
        done < <(find "$src_path" -type f \( -name '*.md' -o -name '*.yaml' -o -name '*.yml' -o -name '*.json' -o -name '*.jsonl' -o -name '*.txt' \) -print0 2>/dev/null)
    fi
done

CHANGED_COUNT=$(( ${#NEW_FILES[@]} + ${#MODIFIED_FILES[@]} ))
log "Scan complete: ${CHANGED_COUNT} changed file(s) out of ${TOTAL_CANDIDATES} total"

# ── Lint function ────────────────────────────────────────────────────────────
_run_lint() {
    log "Running wiki lint..."
    local lint_output
    local lint_exit=0

    lint_output=$(cd "$REPO_ROOT" && uv run scripts/knowledge/llm_wiki.py lint --wiki engineering 2>&1) || lint_exit=$?

    echo "$lint_output" >> "$LOG_FILE"

    if [[ $lint_exit -ne 0 ]]; then
        log "WARNING: lint found issues (exit code ${lint_exit})"
        local issue_count
        issue_count=$(echo "$lint_output" | grep -c '^\s*\[' 2>/dev/null || echo "0")
        log "  Lint issues found: ${issue_count}"
        return 1
    else
        log "Lint passed — wiki is healthy"
        return 0
    fi
}

# ── Count wiki pages ─────────────────────────────────────────────────────────
_count_wiki_pages() {
    local count=0
    for subdir in entities concepts sources standards workflows comparisons; do
        local dir="${WIKI_ROOT}/wiki/${subdir}"
        if [[ -d "$dir" ]]; then
            count=$((count + $(find "$dir" -name '*.md' -type f 2>/dev/null | wc -l)))
        fi
    done
    echo "$count"
}

# ── Count pages before ingest ────────────────────────────────────────────────
PAGE_COUNT_BEFORE=$(_count_wiki_pages)
log "Page count before: ${PAGE_COUNT_BEFORE}"

# ── Handle no-changes case ───────────────────────────────────────────────────
if [[ "$CHANGED_COUNT" -eq 0 ]]; then
    log "No new or modified sources — nothing to ingest"
    log "Running lint check on existing wiki..."
    _run_lint || true
    if [[ "$DRY_RUN" == "false" ]]; then
        date -u +%Y-%m-%dT%H:%M:%S > "$MARKER_FILE"
    fi
    log "=== Done (no changes) ==="
    exit 0
fi

# ── Run ingest for each changed file ─────────────────────────────────────────
INGEST_COUNT=0
INGEST_ERRORS=0
INGESTED_FILES=()

run_ingest() {
    local file="$1"
    local rel_path
    rel_path=$(realpath --relative-to="$REPO_ROOT" "$file" 2>/dev/null || echo "$file")

    log "  Ingesting: ${rel_path}"

    if [[ "$DRY_RUN" == "true" ]]; then
        log "    [dry-run] would run: uv run scripts/knowledge/llm_wiki.py ingest ${rel_path} --wiki engineering"
        INGEST_COUNT=$((INGEST_COUNT + 1))
        INGESTED_FILES+=("$rel_path")
        return 0
    fi

    local ingest_output
    if ingest_output=$(cd "$REPO_ROOT" && uv run scripts/knowledge/llm_wiki.py ingest "$file" --wiki engineering 2>&1); then
        INGEST_COUNT=$((INGEST_COUNT + 1))
        INGESTED_FILES+=("$rel_path")
        log "    OK"
    else
        INGEST_ERRORS=$((INGEST_ERRORS + 1))
        log "    ERROR: ingest failed for ${rel_path}"
        log "    Output: ${ingest_output}"
    fi
}

# Process new files first, then modified files
for file in "${NEW_FILES[@]}"; do
    run_ingest "$file"
done

for file in "${MODIFIED_FILES[@]}"; do
    run_ingest "$file"
done

log "Ingest complete: ${INGEST_COUNT} processed, ${INGEST_ERRORS} error(s)"

# ── Cross-wiki link discovery (post-ingest) ────────────────────────────────
# Runs cross-link discovery after ingest to keep cross-links.md current.
# Only applies when pages were actually ingested (skip on no-change runs).
# Issue: #2011
if [[ "$INGEST_COUNT" -gt 0 ]]; then
    log "Running cross-wiki link discovery..."
    if [[ "$DRY_RUN" == "true" ]]; then
        cd "$REPO_ROOT" && uv run scripts/knowledge/wiki-cross-links.py --dry-run --quiet 2>>"$LOG_FILE" || \
            log "WARNING: cross-link discovery (dry-run) failed"
    else
        cd "$REPO_ROOT" && uv run scripts/knowledge/wiki-cross-links.py --apply --quiet 2>>"$LOG_FILE" || \
            log "WARNING: cross-link discovery failed"
    fi
else
    log "Skipping cross-link discovery (no pages ingested)"
fi

# ── Run lint ─────────────────────────────────────────────────────────────────
LINT_OK=true
_run_lint || LINT_OK=false

# ── Page count and delta detection ───────────────────────────────────────────
PAGE_COUNT_AFTER=$(_count_wiki_pages)
DELTA=$((PAGE_COUNT_AFTER - PAGE_COUNT_BEFORE))
log "Page count after: ${PAGE_COUNT_AFTER} (delta: ${DELTA})"

# ── Page count drop alert ────────────────────────────────────────────────────
if [[ ${DELTA} -lt 0 ]]; then
    log "WARNING: Page count dropped by ${DELTA#-} pages — possible accidental deletion"
    if [[ "$DRY_RUN" == "false" ]]; then
        EXISTING_ISSUE=$(cd "$REPO_ROOT" && gh issue list --label "wiki-alert" --state open --json number --jq '.[0].number' 2>/dev/null || true)
        if [[ -z "$EXISTING_ISSUE" ]]; then
            cd "$REPO_ROOT" && gh issue create \
                --title "Wiki alert: page count dropped (${PAGE_COUNT_BEFORE} -> ${PAGE_COUNT_AFTER})" \
                --body "The nightly wiki ingest detected a page count drop in the **engineering** wiki.

- Before: ${PAGE_COUNT_BEFORE} pages
- After: ${PAGE_COUNT_AFTER} pages
- Delta: ${DELTA}
- Date: ${DATE}
- Log: \`logs/wiki-ingest/ingest-${DATE}.log\`

Please investigate whether pages were accidentally deleted." \
                --label "wiki-alert,priority:high" 2>>"$LOG_FILE" || log "WARN: Failed to create GitHub issue for page drop"
        else
            log "Open wiki-alert issue already exists (#${EXISTING_ISSUE}) — skipping duplicate"
        fi
    fi
fi

# ── Lint failure alert ───────────────────────────────────────────────────────
if [[ "$LINT_OK" == "false" ]]; then
    log "WARNING: Lint failed — wiki quality issues detected"
    if [[ "$DRY_RUN" == "false" ]]; then
        EXISTING_LINT_ISSUE=$(cd "$REPO_ROOT" && gh issue list --label "wiki-lint" --state open --json number --jq '.[0].number' 2>/dev/null || true)
        if [[ -z "$EXISTING_LINT_ISSUE" ]]; then
            cd "$REPO_ROOT" && gh issue create \
                --title "Wiki lint failure: engineering (${DATE})" \
                --body "The nightly wiki ingest lint check failed for the **engineering** wiki.

- Date: ${DATE}
- Log: \`logs/wiki-ingest/ingest-${DATE}.log\`
- Ingest results: ${INGEST_COUNT} OK, ${INGEST_ERRORS} failed

Run \`uv run scripts/knowledge/llm_wiki.py lint --wiki engineering\` to see details." \
                --label "wiki-lint" 2>>"$LOG_FILE" || log "WARN: Failed to create GitHub issue for lint failure"
        else
            log "Open wiki-lint issue already exists (#${EXISTING_LINT_ISSUE}) — skipping duplicate"
        fi
    fi
fi

# ── Update timestamp marker ──────────────────────────────────────────────────
if [[ "$DRY_RUN" == "false" ]]; then
    date -u +%Y-%m-%dT%H:%M:%S > "$MARKER_FILE"
    log "Updated marker file: ${MARKER_FILE}"
fi

# ── Auto-commit changes ─────────────────────────────────────────────────────
if [[ "$DRY_RUN" == "false" ]]; then
    cd "$REPO_ROOT" || exit 1
    if ! git diff --quiet knowledge/wikis/engineering/ 2>/dev/null || \
       ! git diff --cached --quiet knowledge/wikis/engineering/ 2>/dev/null || \
       [[ -n "$(git ls-files --others --exclude-standard knowledge/wikis/engineering/ 2>/dev/null)" ]]; then

        log "Committing wiki changes..."

        COMMIT_MSG="chore(wiki): incremental ingest ${DATE} — ${INGEST_COUNT} file(s) (#2036)"
        if [[ ${#INGESTED_FILES[@]} -le 5 ]]; then
            COMMIT_MSG="${COMMIT_MSG}

Files ingested:
$(printf '  - %s\n' "${INGESTED_FILES[@]}")"
        fi

        git_safe_commit "$COMMIT_MSG" \
            "knowledge/wikis/engineering/" \
            "$MARKER_FILE"
        git_safe_push 2>>"$LOG_FILE" || {
            log "WARNING: push failed — changes remain local"
        }

        log "Changes committed and pushed"
    else
        log "No wiki file changes to commit"
        # Still commit updated marker
        git add "$MARKER_FILE" 2>/dev/null || true
        git_safe_commit "chore(wiki): update ingest marker ${DATE}" "$MARKER_FILE" 2>/dev/null || true
    fi
fi

# ── Summary ──────────────────────────────────────────────────────────────────
log ""
log "=== Ingest Summary ==="
log "  Date:            ${DATE}"
log "  Files scanned:   ${TOTAL_CANDIDATES}"
log "  Files ingested:  ${INGEST_COUNT}"
log "  Ingest errors:   ${INGEST_ERRORS}"
log "  Lint passed:     ${LINT_OK}"
log "  Wiki pages:      ${PAGE_COUNT_AFTER}"
log "  Page delta:      ${DELTA}"
log "  Dry run:         ${DRY_RUN}"
log "=== Done ==="

# Exit non-zero if there were failures
if [[ ${INGEST_ERRORS} -gt 0 ]] || [[ "$LINT_OK" == "false" ]]; then
    exit 1
fi
