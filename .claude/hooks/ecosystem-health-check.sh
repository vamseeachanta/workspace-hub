#!/usr/bin/env bash
# Ecosystem health check — runs as Stop hook, writes signals for /improve
# Checks: skill counts, memory sizes, category balance, stale skills

set -euo pipefail

WORKSPACE_HUB="${WORKSPACE_HUB:-$(git rev-parse --show-superproject-working-tree 2>/dev/null | grep . || git rev-parse --show-toplevel 2>/dev/null || echo "/mnt/local-analysis/workspace-hub")}"
STATE_DIR="$WORKSPACE_HUB/.claude/state"
SIGNALS_FILE="$STATE_DIR/pending-reviews/ecosystem-review.jsonl"
SKILLS_DIR="$WORKSPACE_HUB/.claude/skills"
MEMORY_DIR="$WORKSPACE_HUB/.claude/memory"
USER_MEMORY_DIR="$HOME/.claude/projects/-mnt-local-analysis-workspace-hub/memory"

mkdir -p "$STATE_DIR/pending-reviews"

# Timestamp
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

emit_signal() {
  local type="$1" signal="$2" severity="$3"
  printf '{"timestamp":"%s","type":"%s","signal":"%s","severity":"%s","source":"ecosystem-health-check"}\n' \
    "$TS" "$type" "$signal" "$severity" >> "$SIGNALS_FILE"
}

# --- Skill counts (info only — no count-based warn thresholds) ---
# Policy (improve SKILL.md v1.4.0): a large, well-indexed library is not a problem.
# Stale and unreferenced skills are. Count-based thresholds removed — staleness
# detection uses SKILLS_GRAPH.yaml (WRK-205) rather than raw counts.
active_skills=$(find "$SKILLS_DIR" -type f -name "SKILL.md" ! -path "*/_archive/*" 2>/dev/null | wc -l)
archived_skills=$(find "$SKILLS_DIR/_archive" -type f -name "SKILL.md" 2>/dev/null | wc -l)
emit_signal "ecosystem" "Skill library: ${active_skills} active, ${archived_skills} archived" "info"

# --- Memory file sizes ---
if [ -d "$USER_MEMORY_DIR" ]; then
  for f in "$USER_MEMORY_DIR"/*.md; do
    [ -f "$f" ] || continue
    lines=$(wc -l < "$f")
    fname=$(basename "$f")
    if [ "$lines" -gt 200 ]; then
      emit_signal "memory" "Memory bloat: $fname is $lines lines (limit 200) — needs archival or split" "warn"
    fi
  done
fi

if [ -d "$MEMORY_DIR" ]; then
  for f in "$MEMORY_DIR"/*.md; do
    [ -f "$f" ] || continue
    lines=$(wc -l < "$f")
    fname=$(basename "$f")
    if [ "$lines" -gt 200 ]; then
      emit_signal "memory" "Repo memory bloat: $fname is $lines lines (limit 200)" "warn"
    fi
  done
fi

# --- Stale pending signals ---
if [ -d "$STATE_DIR/pending-reviews" ]; then
  stale_count=0
  for f in "$STATE_DIR/pending-reviews"/*.jsonl; do
    [ -f "$f" ] || continue
    lines=$(wc -l < "$f")
    stale_count=$((stale_count + lines))
  done
  if [ "$stale_count" -gt 50 ]; then
    emit_signal "ecosystem" "Signal backlog: $stale_count pending signals unprocessed — run /improve" "info"
  fi
fi

# --- Skills without recent git activity (proxy for staleness) ---
# Only check if we have enough git history
if git -C "$WORKSPACE_HUB" log --oneline -1 -- ".claude/skills/" >/dev/null 2>&1; then
  last_skill_commit=$(git -C "$WORKSPACE_HUB" log -1 --format="%ct" -- ".claude/skills/" 2>/dev/null || echo "0")
  now=$(date +%s)
  days_since=$(( (now - last_skill_commit) / 86400 ))
  if [ "$days_since" -gt 30 ]; then
    emit_signal "ecosystem" "Skills stale: no skill changes in $days_since days" "info"
  fi
fi

# --- Provider adapter symlinks ---
for provider in codex gemini; do
  if [[ ! -L "$WORKSPACE_HUB/.$provider/skills" ]]; then
    emit_signal "warn" "provider_adapter_missing" ".$provider/skills symlink absent — run scripts/operations/compliance/generate_provider_adapters.sh"
  fi
done

# --- Summary line (visible in session output) ---
echo "Ecosystem health: ${active_skills} active skills, ${archived_skills} archived"
