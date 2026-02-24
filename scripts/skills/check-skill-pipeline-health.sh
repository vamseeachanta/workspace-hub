#!/usr/bin/env bash
# check-skill-pipeline-health.sh — Verify the skill-learner pipeline is live
#
# Checks:
#   1. skill-learner hook is installed (post-commit or session hook)
#   2. .claude/state/ has recent skill-related updates (last 7 days)
#   3. New skills or skill updates were committed in the last 7 days
#   4. pending-reviews/ has recent entries (session signal capture is live)
#
# Output:
#   - Human-readable health summary to stdout
#   - Exit 0 = healthy, exit 1 = unhealthy (one or more checks failed)
#   - --json flag: emit JSON summary to stdout instead
#
# Usage:
#   scripts/skills/check-skill-pipeline-health.sh [--json] [--days N]

set -uo pipefail

# ── Resolve workspace root ────────────────────────────────────────────────────
resolve_root() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local candidate
    candidate="$(cd "$script_dir/../.." && pwd)"
    if [[ -d "$candidate/.claude" ]]; then
        echo "$candidate"
        return
    fi
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        [[ -d "$dir/.claude" ]] && echo "$dir" && return
        dir="$(dirname "$dir")"
    done
    echo "$PWD"
}

ROOT="$(resolve_root)"
STATE_DIR="$ROOT/.claude/state"
HOOKS_DIR="$ROOT/.claude/hooks"
SKILLS_DIR="$ROOT/.claude/skills"

OUTPUT_JSON=false
DAYS=7

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) OUTPUT_JSON=true ;;
        --days) shift; DAYS="${1:-7}" ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
    shift
done

# ── Helper: seconds since file was last modified ──────────────────────────────
seconds_since_modified() {
    local file="$1"
    if [[ ! -f "$file" ]]; then echo 99999999; return; fi
    local mtime now
    mtime=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null || echo 0)
    now=$(date +%s)
    echo $(( now - mtime ))
}

threshold_seconds=$(( DAYS * 86400 ))
run_date="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ── Check 1: skill-learner hook installed ────────────────────────────────────
hook_installed=false
hook_path=""
hook_detail="not found"

# Look for any hook referencing "skill" in name or content
for hook_file in "$HOOKS_DIR"/*.sh "$HOOKS_DIR"/post-commit; do
    [[ -f "$hook_file" ]] || continue
    fname="$(basename "$hook_file")"
    if [[ "$fname" == *skill* ]] || grep -qi "skill" "$hook_file" 2>/dev/null; then
        hook_installed=true
        hook_path="$hook_file"
        hook_detail="found: $fname"
        break
    fi
done

# Also check .git hooks directory
git_hooks_dir="$ROOT/.git/hooks"
if [[ -f "$git_hooks_dir/post-commit" ]] && grep -qi "skill" "$git_hooks_dir/post-commit" 2>/dev/null; then
    hook_installed=true
    hook_detail="found: .git/hooks/post-commit (skill reference)"
fi

# ── Check 2: recent skill-related state updates ──────────────────────────────
state_recent=false
state_detail="no recent state updates"
recent_state_file=""

for f in "$STATE_DIR/skills-research-log.jsonl" \
          "$STATE_DIR/skills-graph-review-log.jsonl" \
          "$STATE_DIR/curation-log.yaml" \
          "$STATE_DIR/skill-scores.yaml" \
          "$STATE_DIR/learned-patterns.json"; do
    secs=$(seconds_since_modified "$f")
    if [[ "$secs" -lt "$threshold_seconds" ]]; then
        state_recent=true
        recent_state_file="$(basename "$f") ($(( secs / 86400 ))d ago)"
        state_detail="recent: $recent_state_file"
        break
    fi
done

# ── Check 3: skill commits in last N days ────────────────────────────────────
skills_committed=false
skills_commit_detail="no skill commits in last ${DAYS}d"

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    skill_commit_count=$(
        git -C "$ROOT" log --since="${DAYS} days ago" --name-only --pretty=format: 2>/dev/null \
          | grep -i "skills/" | wc -l | tr -d ' '
    )
    if [[ "$skill_commit_count" -gt 0 ]]; then
        skills_committed=true
        skills_commit_detail="${skill_commit_count} skill file changes in last ${DAYS}d"
    fi
fi

# ── Check 4: pending-reviews has recent entries ──────────────────────────────
reviews_active=false
reviews_detail="no recent session signal captures"
pending_dir="$STATE_DIR/pending-reviews"

if [[ -d "$pending_dir" ]]; then
    recent_review=$(
        find "$pending_dir" -name "*.jsonl" -newer "$ROOT/.git/index" 2>/dev/null \
          | head -1
    )
    if [[ -z "$recent_review" ]]; then
        # Fallback: check mtime directly
        newest_file=$(find "$pending_dir" -name "*.jsonl" -printf '%T@ %p\n' 2>/dev/null \
            | sort -rn | head -1 | awk '{print $2}')
        if [[ -n "$newest_file" ]]; then
            secs=$(seconds_since_modified "$newest_file")
            if [[ "$secs" -lt "$threshold_seconds" ]]; then
                reviews_active=true
                reviews_detail="recent: $(basename "$newest_file") ($(( secs / 86400 ))d ago)"
            fi
        fi
    else
        reviews_active=true
        reviews_detail="recent: $(basename "$recent_review")"
    fi
fi

# ── Determine overall health ──────────────────────────────────────────────────
overall_healthy=true
warnings=()

$hook_installed    || { overall_healthy=false; warnings+=("WARN: skill-learner hook not detected"); }
$state_recent      || warnings+=("WARN: no recent skill state updates in last ${DAYS}d")
$skills_committed  || warnings+=("WARN: no skill commits in last ${DAYS}d")
$reviews_active    || warnings+=("WARN: session signal pipeline appears quiet")

# Pipeline is considered dead if both state and commits are stale
if ! $state_recent && ! $skills_committed; then
    overall_healthy=false
fi

status_str="healthy"
$overall_healthy || status_str="unhealthy"

# ── Output ────────────────────────────────────────────────────────────────────
if [[ "$OUTPUT_JSON" == false ]]; then
    echo "=== Skill Pipeline Health Check — $run_date ==="
    echo ""
    printf "  %-35s %s\n" "Hook installed:" "$(  $hook_installed && echo 'YES' || echo 'NO')  ($hook_detail)"
    printf "  %-35s %s\n" "Recent state updates:" "$($state_recent && echo 'YES' || echo 'NO')  ($state_detail)"
    printf "  %-35s %s\n" "Skills committed (${DAYS}d):" "$($skills_committed && echo 'YES' || echo 'NO')  ($skills_commit_detail)"
    printf "  %-35s %s\n" "Session signals active:" "$(  $reviews_active && echo 'YES' || echo 'NO')  ($reviews_detail)"
    echo ""
    if [[ ${#warnings[@]} -gt 0 ]]; then
        for w in "${warnings[@]}"; do echo "  $w"; done
        echo ""
    fi
    echo "  Overall: $status_str"
fi

if [[ "$OUTPUT_JSON" == true ]]; then
    warn_json="["
    first=true
    for w in "${warnings[@]}"; do
        "$first" || warn_json+=","
        warn_json+="\"$w\""
        first=false
    done
    warn_json+="]"

    cat <<EOF
{"date":"$run_date","status":"$status_str","hook_installed":$hook_installed,"state_recent":$state_recent,"skills_committed":$skills_committed,"reviews_active":$reviews_active,"hook_detail":"$hook_detail","state_detail":"$state_detail","skills_commit_detail":"$skills_commit_detail","reviews_detail":"$reviews_detail","warnings":$warn_json}
EOF
fi

$overall_healthy
