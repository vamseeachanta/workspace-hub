#!/usr/bin/env bash
# extract-learnings.sh — Post-commit learning extraction pipeline
# Phase 4 of #1760 (self-improvement commands)
#
# After each commit or session, this script:
# 1. Analyzes what changed and what went wrong during the session
# 2. Identifies patterns, pitfalls, and wins
# 3. Auto-creates GitHub issues for anything worth capturing
# 4. Updates relevant skills if a pattern matches an existing one
#
# Runs as post-commit hook or standalone via ./scripts/learnings/extract-learnings.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
LOGS_DIR="${REPO_ROOT}/logs/learnings"
mkdir -p "$LOGS_DIR"

# ── Configuration ────────────────────────────────────────────────────
# Issue creation threshold: minimum confidence score to auto-create
AUTO_ISSUE_THRESHOLD="${AUTO_ISSUE_THRESHOLD:-70}"
# Max issues per session
MAX_ISSUES_PER_SESSION="${MAX_ISSUES_PER_SESSION:-3}"
# Labels for auto-created issues
DEFAULT_LABELS="cat:platform,domain:knowledge,auto-generated"

# ── Inputs ──────────────────────────────────────────────────────────
LATEST_COMMIT="${1:-HEAD}"
SESSION_LOG="${REPO_ROOT}/logs/orchestrator/sessions/latest.jsonl"

# ── Analyze what changed ────────────────────────────────────────────
analyze_commit() {
  local commit="$1"
  local files
  files="$(git diff-tree --no-commit-id --name-only -r "$commit" 2>/dev/null || true)"
  
  if [[ -z "$files" ]]; then
    return
  fi
  
  # Categorize changes
  local skill_changes=0
  local doc_changes=0
  local code_changes=0
  local config_changes=0
  local test_changes=0
  
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    case "$file" in
      *skills*|*.claude/*) skill_changes=$((skill_changes + 1)) ;;
      docs/*|*.md) doc_changes=$((doc_changes + 1)) ;;
      tests/*|test_*) test_changes=$((test_changes + 1)) ;;
      config/*|.claude/*) config_changes=$((config_changes + 1)) ;;
      *) code_changes=$((code_changes + 1)) ;;
    esac
  done <<< "$files"
  
  # If skill changes > 0, flag for potential pattern capture
  if [[ $skill_changes -gt 0 ]]; then
    echo "skill_update:detected:$skill_changes files modified"
  fi
  
  # If code changes without test changes, flag as TDD gap
  if [[ $code_changes -gt 0 && $test_changes -eq 0 ]]; then
    echo "tdd_gap:potential:$code_changes implementation files without test changes"
  fi
  
  # If lots of config changes, flag for drift check
  if [[ $config_changes -gt 3 ]]; then
    echo "config_drift:potential:$config_changes config files changed"
  fi
}

# ── Extract corrections from commit ─────────────────────────────────
extract_corrections() {
  # Look for correction patterns in recent commits
  # Pattern: fix after a feature commit = something went wrong
  local commit_msg
  commit_msg="$(git log -1 --format='%s %b' "$LATEST_COMMIT" 2>/dev/null || true)"
  
  # Check for fix commits that reference earlier feature commits
  if echo "$commit_msg" | grep -qiE '^(fix|chore.fix)'; then
    local refs_to
    refs_to="$(echo "$commit_msg" | grep -oE '#[0-9]+' | head -3 || true)"
    if [[ -n "$refs_to" ]]; then
      echo "correction:detected:fix references $refs_to"
    fi
  fi
}

# ── Check for repeated patterns ─────────────────────────────────────
detect_repeated_pattern() {
  local signal="$1"
  local type="${signal%%:*}"
  
  case "$type" in
    skill_update)
      # Check if similar skill was updated recently
      local recent
      recent="$(find "${REPO_ROOT}/.claude/skills/" -name "SKILL.md" -mtime -3 2>/dev/null | wc -l)"
      if [[ $recent -gt 5 ]]; then
        echo "repeated:$signal (5+ skill updates in 3 days)"
      fi
      ;;
    tdd_gap)
      # Check if this is part of a pattern
      local recent_fixes
      recent_fixes="$(git log --oneline -30 --format='%s' 2>/dev/null | grep -ciE 'fix.*test|test.*fix|add.*test' || echo 0)"
      if [[ $recent_fixes -gt 3 ]]; then
        echo "repeated:$signal ($recent_fixes test-related fixes in 30 commits)"
      fi
      ;;
  esac
}

# ── Generate issue content ──────────────────────────────────────────
generate_issue_body() {
  local pattern="$1"
  local date
  date="$(date +%Y-%m-%d)"
  
  cat <<EOF
## Auto-Generated: $pattern ($date)

### Context
$pattern

### Evidence
- Commit: $(git log -1 --format='%h' "$LATEST_COMMIT" 2>/dev/null || echo 'unknown')
- Message: $(git log -1 --format='%s' "$LATEST_COMMIT" 2>/dev/null || echo 'unknown')
- Files changed: $(git diff-tree --no-commit-id --name-only -r "$LATEST_COMMIT" 2>/dev/null | wc -l || echo 0)

### Analysis Needed
- [ ] Verify this pattern is worth capturing
- [ ] Create or update a skill if applicable
- [ ] Close if not actionable

### Related
$(gh issue list --search "\$(echo "$pattern" | cut -d: -f1)" --state open --limit 3 2>/dev/null | head -3 | sed 's/^/- /' || true)
EOF
}

# ── Main Pipeline ───────────────────────────────────────────────────
main() {
  local timestamp
  timestamp="$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')"
  
  echo "=== Learning Extraction Pipeline ($timestamp) ==="
  
  # Step 1: Analyze commit
  local signals=()
  while IFS= read -r signal; do
    [[ -z "$signal" ]] && continue
    signals+=("$signal")
    local repeated
    repeated="$(detect_repeated_pattern "$signal")"
    if [[ -n "$repeated" ]]; then
      echo "[LEARNING] Repeated pattern: $repeated"
      # Log the repeated pattern
      printf '{"timestamp":"%s","pattern":"%s","commit":"%s"}\n' "$timestamp" "$repeated" "$(git log -1 --format='%h' "$LATEST_COMMIT" 2>/dev/null)" >> "$LOGS_DIR/patterns.jsonl"
    fi
  done < <(analyze_commit "$LATEST_COMMIT"; extract_corrections)
  
  # Step 2: Check session logs for corrections
  if [[ -f "$SESSION_LOG" ]]; then
    local corrections
    corrections="$(grep -c '"correction"' "$SESSION_LOG" 2>/dev/null || echo 0)"
    if [[ $corrections -gt 5 ]]; then
      echo "[LEARNING] $corrections corrections detected in session log"
      signals+=("session_corrections:$corrections")
    fi
  fi
  
  if [[ ${#signals[@]} -eq 0 ]]; then
    echo "[LEARNING] No learning signals detected for this commit."
    exit 0
  fi
  
  # Step 3: Generate issue recommendations
  local issues_created=0
  for signal in "${signals[@]}"; do
    if [[ $issues_created -ge $MAX_ISSUES_PER_SESSION ]]; then
      echo "[LEARNING] Max issues per session reached ($MAX_ISSUES_PER_SESSION)"
      break
    fi
    
    # Calculate priority score
    local score=50
    local type="${signal%%:*}"
    case "$type" in
      tdd_gap) score=60 ;;
      skill_update) score=40 ;;
      config_drift) score=55 ;;
      repeated) score=75 ;;
      session_corrections) score=80 ;;
    esac
    
    # Extract count if present
    local count
    count="$(echo "$signal" | grep -oE '[0-9]+( files|[0-9]+)' | head -1 | grep -oE '[0-9]+' || echo 0)"
    if [[ $count -gt 10 ]]; then
      score=$((score + 10))
    fi
    
    if [[ $score -ge $AUTO_ISSUE_THRESHOLD ]]; then
      echo "[LEARNING] High-confidence signal ($score/100): $signal"
      echo "[LEARNING] Would create issue: $signal"
      
      # Log the recommendation (issue creation would go here in full mode)
      local issue_body
      issue_body="$(generate_issue_body "$signal")"
      echo "$issue_body" > "$LOGS_DIR/recommendation-$(date +%s).md"
      
      # In create mode, would do:
      # gh issue create --title "learning: $signal" --body-file "$LOGS_DIR/recommendation-$(date +%s).md" --label "$DEFAULT_LABELS"
      
      issues_created=$((issues_created + 1))
    else
      echo "[LEARNING] Low score ($score/100): $signal — logged but no issue created"
    fi
  done
  
  echo ""
  echo "=== Pipeline Complete: ${#signals[@]} signals analyzed, $issues_created recommendations generated ==="
  echo "Logs: $LOGS_DIR/"
}

main "$@"
