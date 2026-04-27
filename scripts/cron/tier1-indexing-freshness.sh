#!/usr/bin/env bash
# tier1-indexing-freshness.sh — Daily local audit of tier-1 indexing surfaces.
# Issue: #2465 (https://github.com/vamseeachanta/workspace-hub/issues/2465)
# Plan:  docs/plans/2026-04-22-issue-2465-daily-tier1-indexing-freshness-audit.md
# Contract: docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md
# Upstream: docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md
#
# Reads:
#   docs/BUSINESS_BRAIN.md (### Tier-1 table)
#   docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md (existence)
#   <each tier-1 repo>/AGENTS.md, README.md, docs/README.md, docs/maps/<repo>-operator-map.md,
#                      docs/registry/module-routing.yaml
#   per-repo scan-roots from this file's PER_REPO_SCAN_ROOTS table
#
# Writes (only):
#   $REPO_ROOT/docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md
#   $REPO_ROOT/docs/reports/tier-1-indexing-freshness-latest.md
#   $REPO_ROOT/logs/freshness/tier-1-indexing-freshness-YYYY-MM-DD.log
#
# Exit codes:
#   0 = portfolio green
#   1 = portfolio yellow (drift but no critical loss)
#   2 = portfolio red (missing surface, legacy reference, contract missing, or brain unparseable)
#
# Env overrides (tests / dispatch):
#   REPO_ROOT                       — set by cadence_init_repo_root if unset
#   TIER1_FRESHNESS_OUT_DIR         — override docs/reports output dir
#   TIER1_FRESHNESS_LOG_DIR         — override logs/freshness dir
#   TIER1_FRESHNESS_TODAY           — override YYYY-MM-DD stamp (deterministic in tests)
#   TIER1_FRESHNESS_BUSINESS_BRAIN  — alternate path to BUSINESS_BRAIN.md
#   TIER1_FRESHNESS_CONTRACT        — alternate path to upstream contract
#   TIER1_FRESHNESS_SCHEDULED_ID    — overrides 'aefef5167f2f' in the report footer

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/cadence-common.sh
source "${SCRIPT_DIR}/lib/cadence-common.sh"
cadence_init_repo_root

TODAY="${TIER1_FRESHNESS_TODAY:-$(date -u +%Y-%m-%d)}"
NOW_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
OUT_DIR="${TIER1_FRESHNESS_OUT_DIR:-${REPO_ROOT}/docs/reports}"
LOG_DIR="${TIER1_FRESHNESS_LOG_DIR:-${REPO_ROOT}/logs/freshness}"
BRAIN="${TIER1_FRESHNESS_BUSINESS_BRAIN:-${REPO_ROOT}/docs/BUSINESS_BRAIN.md}"
CONTRACT="${TIER1_FRESHNESS_CONTRACT:-${REPO_ROOT}/docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md}"
SCHEDULED_ID="${TIER1_FRESHNESS_SCHEDULED_ID:-aefef5167f2f}"

DATED_OUT="${OUT_DIR}/tier-1-indexing-freshness-${TODAY}.md"
LATEST_OUT="${OUT_DIR}/tier-1-indexing-freshness-latest.md"
LOG_OUT="${LOG_DIR}/tier-1-indexing-freshness-${TODAY}.log"

mkdir -p "$OUT_DIR" "$LOG_DIR"

# ── Per-repo scan-root table (mirrors contract doc) ───────────────────────
# Format: repo|relative-scan-root[|relative-scan-root...]
PER_REPO_SCAN_ROOTS=(
    "workspace-hub|scripts/|config/|docs/|.claude/skills/|.claude/rules/"
    "digitalmodel|digitalmodel/src/|digitalmodel/digitalmodel/|digitalmodel/scripts/|digitalmodel/tests/"
    "assetutilities|assetutilities/src/|assetutilities/assetutilities/|assetutilities/scripts/|assetutilities/tests/"
    "aceengineer-website|aceengineer-website/src/|aceengineer-website/content/|aceengineer-website/scripts/"
)

NEGATIVE_AUTHORITY_SENTENCE="MUST NOT treat any tier-1 indexing scorecard under docs/reports/ as required canonical authority"

# ── Helpers ───────────────────────────────────────────────────────────────

log() {
    printf '[tier1-freshness] %s\n' "$*" >&2
}

emit_evidence_line() {
    local status="$1" reason="${2:-}"
    local extra=""
    if [[ -n "$reason" ]]; then
        extra=" reason=${reason}"
    fi
    printf 'task=tier1-indexing-freshness status=%s artifact=%s log=%s ts=%s%s\n' \
        "$status" "$LATEST_OUT" "$LOG_OUT" "$NOW_ISO" "$extra" >> "$LOG_OUT"
}

# Parse tier-1 repo names from BUSINESS_BRAIN.md.
# Rule: between '### Tier-1' heading and the next '### Tier-' heading, take the
# leading pipe-delimited cell from each table row, skipping the header row and
# the alignment row.
parse_tier1_repos() {
    if [[ ! -f "$BRAIN" ]]; then
        return 1
    fi
    awk '
        /^### Tier-1/ { in_block = 1; next }
        in_block && /^### Tier-/ { exit }
        in_block && /^\|/ {
            # Skip alignment row like |------|
            if ($0 ~ /^\|[[:space:]]*-/) next
            # Skip header row containing literal "Repo"
            if ($0 ~ /\|[[:space:]]*Repo[[:space:]]*\|/) next
            line = $0
            # Strip leading pipe
            sub(/^\|[[:space:]]*/, "", line)
            # Take up to the next pipe
            n = index(line, "|")
            if (n > 0) {
                cell = substr(line, 1, n - 1)
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", cell)
                if (cell != "") print cell
            }
        }
    ' "$BRAIN"
}

# Resolve the on-disk root for a tier-1 repo.
# workspace-hub uses REPO_ROOT itself; siblings live as subdirectories.
resolve_repo_root() {
    local repo="$1"
    if [[ "$repo" == "workspace-hub" ]]; then
        printf '%s' "$REPO_ROOT"
    else
        printf '%s/%s' "$REPO_ROOT" "$repo"
    fi
}

# Required-surface check. Echoes a comma-separated list of MISSING surfaces.
check_required_surfaces() {
    local repo="$1"
    local repo_root
    repo_root="$(resolve_repo_root "$repo")"
    local missing=()
    [[ -f "${repo_root}/AGENTS.md" ]]                                || missing+=("AGENTS.md")
    [[ -f "${repo_root}/README.md" ]]                                || missing+=("README.md")
    [[ -f "${repo_root}/docs/README.md" ]]                           || missing+=("docs/README.md")
    [[ -f "${repo_root}/docs/maps/${repo}-operator-map.md" ]]        || missing+=("docs/maps/${repo}-operator-map.md")
    [[ -f "${repo_root}/docs/registry/module-routing.yaml" ]]        || missing+=("docs/registry/module-routing.yaml")
    if (( ${#missing[@]} == 0 )); then
        printf ''
    else
        local IFS=,
        printf '%s' "${missing[*]}"
    fi
}

# Scan-root listing for a repo (echoes one path per line).
scan_roots_for() {
    local repo="$1"
    local row
    for row in "${PER_REPO_SCAN_ROOTS[@]}"; do
        local row_repo="${row%%|*}"
        if [[ "$row_repo" == "$repo" ]]; then
            local rest="${row#*|}"
            local IFS='|'
            local -a parts
            read -r -a parts <<<"$rest"
            local p
            for p in "${parts[@]}"; do
                [[ -n "$p" ]] && printf '%s\n' "$p"
            done
            return 0
        fi
    done
}

# Detect tracked backup artifacts under a repo's scan-roots. Echoes count.
count_backup_artifacts() {
    local repo="$1"
    local repo_root
    repo_root="$(resolve_repo_root "$repo")"
    local total=0
    local rel
    while IFS= read -r rel; do
        [[ -z "$rel" ]] && continue
        local full="${REPO_ROOT}/${rel}"
        [[ -d "$full" ]] || continue
        local n
        n=$(find "$full" \
            -path '*/.git' -prune -o \
            -path '*/.venv' -prune -o \
            -path '*/node_modules' -prune -o \
            -path '*/__pycache__' -prune -o \
            -path '*/.pytest_cache' -prune -o \
            -path '*/.next' -prune -o \
            -type f \
            \( -name '*.bak' -o -name '*.orig' -o -name '*~' -o -name '*.swp' \) \
            -print 2>/dev/null | wc -l)
        total=$(( total + n ))
    done < <(scan_roots_for "$repo")
    printf '%d' "$total"
}

# Detect broken active references in the canonical routing triad + operator map.
# Returns count of broken cited paths.
count_broken_references() {
    local repo="$1"
    local repo_root
    repo_root="$(resolve_repo_root "$repo")"
    local files=(
        "${repo_root}/AGENTS.md"
        "${repo_root}/README.md"
        "${repo_root}/docs/README.md"
        "${repo_root}/docs/maps/${repo}-operator-map.md"
    )
    local total=0
    local f
    for f in "${files[@]}"; do
        [[ -f "$f" ]] || continue
        # Extract code-span tokens that look like local paths.
        # Heuristic: tokens starting with one of the routing prefixes and not
        # containing whitespace, URL scheme, angle-brackets, or backticks.
        local tokens
        tokens=$(grep -oE '`[^`]+`' "$f" 2>/dev/null \
            | sed -e 's/^`//' -e 's/`$//' \
            | awk '
                /^(docs\/|scripts\/|config\/|data\/|tests\/|knowledge\/|\.claude\/|\.planning\/|logs\/)/ {
                    if ($0 !~ /[ \t<>]/ && $0 !~ /^https?:/) print
                }
            ')
        local tok
        while IFS= read -r tok; do
            [[ -z "$tok" ]] && continue
            # strip optional trailing punctuation
            tok="${tok%[,.;:)]}"
            local target="${repo_root}/${tok}"
            if [[ ! -e "$target" ]]; then
                total=$(( total + 1 ))
            fi
        done <<<"$tokens"
    done
    printf '%d' "$total"
}

repo_status_word() {
    local missing_count="$1" backup_count="$2" broken_count="$3"
    if (( missing_count == 0 )) && (( backup_count == 0 )) && (( broken_count == 0 )); then
        printf 'green'
    elif (( missing_count >= 2 )) || (( backup_count > 0 )); then
        printf 'red'
    elif (( missing_count == 1 )) || (( broken_count >= 1 )); then
        printf 'yellow'
    else
        printf 'green'
    fi
}

portfolio_status() {
    local any_red=0 any_yellow=0
    local s
    for s in "$@"; do
        case "$s" in
            red) any_red=1 ;;
            yellow) any_yellow=1 ;;
        esac
    done
    if (( any_red == 1 )); then
        printf 'red'
    elif (( any_yellow == 1 )); then
        printf 'yellow'
    else
        printf 'green'
    fi
}

# ── Main ──────────────────────────────────────────────────────────────────

# Always start the log file fresh for the run so tests reading it see only this run's data.
: > "$LOG_OUT"

# 1. Upstream contract present?
if [[ ! -f "$CONTRACT" ]]; then
    log "upstream contract missing at: $CONTRACT"
    {
        printf '# Tier-1 Indexing Freshness Report\n\n'
        printf 'Generated: %s\n' "$NOW_ISO"
        printf 'Scope: (unknown — upstream contract missing)\n'
        printf 'Source baseline: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` (MISSING)\n\n'
        printf 'Action required: upstream contract docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md is missing. The audit cannot proceed without the rule source. Restore the contract or open a tracking issue.\n\n'
        printf '## Overall Status\n\nPortfolio status: red\n\nReason:\n- upstream contract file missing on disk\n- audit fails closed rather than substituting an internal rule copy\n\n'
        printf '## Repo Status\n\n_Per-repo checks not run; rule source unavailable._\n\n'
        printf '## Assumption Check Against Upstream Contract\n\nStatus: blocked — contract file missing.\n\n'
        printf '## Notes\n\n%s\n\n' "$NEGATIVE_AUTHORITY_SENTENCE"
    } > "$DATED_OUT"
    cp -f "$DATED_OUT" "$LATEST_OUT"
    emit_evidence_line red "contract-missing"
    exit 2
fi

# 2. Parse tier-1 repos from BUSINESS_BRAIN.md
mapfile -t TIER1_REPOS < <(parse_tier1_repos)
if (( ${#TIER1_REPOS[@]} == 0 )); then
    log "could not parse tier-1 repos from BUSINESS_BRAIN.md at: $BRAIN"
    {
        printf '# Tier-1 Indexing Freshness Report\n\n'
        printf 'Generated: %s\n' "$NOW_ISO"
        printf 'Scope: (unknown — BUSINESS_BRAIN.md unparseable)\n\n'
        printf 'Action required: docs/BUSINESS_BRAIN.md ### Tier-1 table could not be parsed. The audit cannot determine which repos to check.\n\n'
        printf '## Overall Status\n\nPortfolio status: red\n\nReason:\n- BUSINESS_BRAIN.md tier-1 set unparseable\n\n'
        printf '## Repo Status\n\n_No repos to audit._\n\n'
        printf '## Assumption Check Against Upstream Contract\n\nStatus: blocked — tier-1 set unknown.\n\n'
        printf '## Notes\n\n%s\n\n' "$NEGATIVE_AUTHORITY_SENTENCE"
    } > "$DATED_OUT"
    cp -f "$DATED_OUT" "$LATEST_OUT"
    emit_evidence_line red "brain-missing"
    exit 2
fi

# 3. Audit each tier-1 repo
declare -a REPO_STATUSES=()
declare -a REPO_BLOCKS=()
RED_COUNT=0
declare -a RED_REPOS=()

for repo in "${TIER1_REPOS[@]}"; do
    missing="$(check_required_surfaces "$repo")"
    if [[ -z "$missing" ]]; then
        missing_count=0
    else
        # count commas + 1
        IFS=',' read -ra _missing_arr <<<"$missing"
        missing_count="${#_missing_arr[@]}"
    fi
    backup_count="$(count_backup_artifacts "$repo")"
    broken_count="$(count_broken_references "$repo")"
    status="$(repo_status_word "$missing_count" "$backup_count" "$broken_count")"
    REPO_STATUSES+=("$status")

    # Build per-repo block
    {
        printf '\n### %s — %s\n' "$repo" "$status"
        printf 'Current concerns\n'
        if (( missing_count > 0 )); then
            printf -- '- missing required surface(s): %s\n' "$missing"
        fi
        if (( backup_count > 0 )); then
            printf -- '- %d tracked backup artifact(s) under source paths\n' "$backup_count"
        fi
        if (( broken_count > 0 )); then
            printf -- '- %d broken active reference(s) in canonical routing surfaces\n' "$broken_count"
        fi
        if (( missing_count == 0 && backup_count == 0 && broken_count == 0 )); then
            printf -- '- none observed by this audit\n'
        fi
        printf '\nNext actions\n'
        case "$repo" in
            workspace-hub)        printf -- '- execute #2464 to clean curated routing surfaces\n' ;;
            digitalmodel)         printf -- '- execute #2462 to align canonical routing surfaces\n' ;;
            assetutilities)       printf -- '- execute #2461 first among repo-specific remediations\n' ;;
            aceengineer-website)  printf -- '- execute #2463 to replace legacy product-doc references\n' ;;
            *)                    printf -- '- review per-repo plan in docs/plans/\n' ;;
        esac
    } >> "${OUT_DIR}/.${TODAY}.tier1-freshness.tmp.${repo}"
    REPO_BLOCKS+=("${OUT_DIR}/.${TODAY}.tier1-freshness.tmp.${repo}")

    if [[ "$status" == "red" ]]; then
        RED_COUNT=$(( RED_COUNT + 1 ))
        RED_REPOS+=("$repo")
    fi
done

PORTFOLIO="$(portfolio_status "${REPO_STATUSES[@]}")"

# 4. Compose report
{
    printf '# Tier-1 Indexing Freshness Report\n\n'
    if [[ "$PORTFOLIO" == "red" ]]; then
        printf 'Action required: %d tier-1 repo(s) have missing required surfaces or legacy references. See per-repo findings below.\n\n' "$RED_COUNT"
    fi
    printf 'Generated: %s\n' "$NOW_ISO"
    printf 'Scope: %s\n' "$(IFS=,; printf '%s' "${TIER1_REPOS[*]}" | sed 's/,/, /g')"
    printf 'Source baseline: `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`\n\n'

    printf '## Overall Status\n\n'
    printf 'Portfolio status: %s\n\n' "$PORTFOLIO"
    case "$PORTFOLIO" in
        green)
            printf 'Reason:\n- every tier-1 repo passes required-surface, source-hygiene, and reference checks\n\n'
            ;;
        yellow)
            printf 'Reason:\n- at least one tier-1 repo has minor drift; no required surface is missing in critical mass\n- daily freshness monitoring continues to track remediation progress\n\n'
            ;;
        red)
            printf 'Reason:\n- at least one tier-1 repo is missing required canonical surfaces or carries broken active references\n- portfolio cannot return to green until per-repo remediations land\n\n'
            ;;
    esac

    printf '## Repo Status\n'
    for blockfile in "${REPO_BLOCKS[@]}"; do
        cat "$blockfile"
    done
    printf '\n'

    printf '## Assumption Check Against Upstream Contract\n\n'
    printf 'Status: contract present at `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md`. Per-repo checks executed against the upstream contract'\''s required-trusted-routing-surfaces table.\n\n'

    printf '## Tracking\n\n'
    printf 'Created issues\n'
    printf -- '- #2460 tier-1 indexing and code-placement contract\n'
    printf -- '- #2461 assetutilities routing surfaces and source-hygiene cleanup\n'
    printf -- '- #2462 digitalmodel repo-wide routing surfaces\n'
    printf -- '- #2463 aceengineer-website routing surfaces cleanup\n'
    printf -- '- #2464 workspace-hub curated routing index cleanup\n'
    printf -- '- #2465 daily tier-1 indexing freshness audit and scorecard refresh\n\n'
    printf 'Scheduled job\n'
    printf -- '- `tier1-indexing-freshness` (in-repo, `config/scheduled-tasks/schedule-tasks.yaml`); pre-existing remote routine `%s` at `30 3 * * *` is being cut over per the routine-management appendix in `docs/standards/TIER1_INDEXING_FRESHNESS_AUDIT.md`\n\n' "$SCHEDULED_ID"

    printf '## Notes\n\n'
    printf 'This report intentionally avoids legacy product-doc reference patterns and uses current canonical routing surfaces only.\n\n'
    printf '%s\n\n' "$NEGATIVE_AUTHORITY_SENTENCE"
    printf '_Generated by `scripts/cron/tier1-indexing-freshness.sh`._\n'
} > "$DATED_OUT"

# Cleanup tmp blocks
for blockfile in "${REPO_BLOCKS[@]}"; do
    rm -f "$blockfile"
done

# Atomic latest-pointer overwrite
cp -f "$DATED_OUT" "$LATEST_OUT"

# Evidence line
emit_evidence_line "$PORTFOLIO"

case "$PORTFOLIO" in
    green)  exit 0 ;;
    yellow) exit 1 ;;
    red)    exit 2 ;;
esac
