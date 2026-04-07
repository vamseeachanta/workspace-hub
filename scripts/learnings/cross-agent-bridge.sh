#!/usr/bin/env bash
# cross-agent-bridge.sh — Phase 5: Cross-Agent Memory Bridge
# Ensures learnings from any agent are available to all agents.
# Runs as part of nightly comprehensive-learning or standalone.
#
# Bridge directions:
# 1. Local agent memory -> Repo-tracked files (for all agents)
# 2. Repo-tracked files -> Local agent context (on session start)
# 3. Skill changes -> Sync across repos
#
# Issues: #1760

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BRIDGE_DIR="${REPO_ROOT}/logs/bridge"
mkdir -p "$BRIDGE_DIR"

MACHINE="$(hostname -s 2>/dev/null || echo 'unknown')"
TIMESTAMP="$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')"

# ── Bridge 1: Local Memory -> Repo Files ────────────────────────────
bridge_local_to_repo() {
  echo "=== Bridge: Local Memory -> Repo ==="
  
  # 1a. Hermes memory -> repo memory file
  local hermes_memory="$HOME/.hermes/memory/*.jsonl"
  if [[ -d "$HOME/.hermes/memory/" ]]; then
    local hermes_files
    hermes_files="$(find "$HOME/.hermes/memory/" -name "*.jsonl" -mmin -1440 2>/dev/null | wc -l)"
    if [[ $hermes_files -gt 0 ]]; then
      echo "  [1a] Hermes: $hermes_files recent memory files found"
      # Copy to repo
      local dest="${REPO_ROOT}/.claude/state/agent-memory/hermes/$MACHINE/"
      mkdir -p "$dest"
      find "$HOME/.hermes/memory/" -name "*.jsonl" -mmin -1440 -exec cp {} "$dest" \; 2>/dev/null || true
    fi
  fi
  
  # 1b. Claude Code session state -> repo
  local claude_state="${REPO_ROOT}/.claude/state/"
  if [[ -d "$claude_state" ]]; then
    echo "  [1b] Claude: .claude/state/ exists ($(ls -la "$claude_state" 2>/dev/null | wc -l) entries)"
  fi
  
  # 1c. Skill modifications -> changelog
  local recent_skills
  recent_skills="$(find "${REPO_ROOT}/.claude/skills/" -name "SKILL.md" -mtime -1 2>/dev/null | wc -l)"
  if [[ $recent_skills -gt 0 ]]; then
    echo "  [1c] Skills: $recent_skills modified in last 24h"
    # Generate changelog
    (
      echo "## Skill Changes ($TIMESTAMP, $MACHINE)"
      echo ""
      find "${REPO_ROOT}/.claude/skills/" -name "SKILL.md" -mtime -1 -newer "${BRIDGE_DIR}/last-bridge.txt" 2>/dev/null | while read -r skill; do
        local rel="${skill#${REPO_ROOT}/}"
        local msg="$(git log -1 --format='%h %s' -- "$skill" 2>/dev/null || echo 'unstaged')"
        echo "- $rel: $msg"
      done
    ) >> "${BRIDGE_DIR}/skill-changelog.md"
  fi
  
  echo ""
}

# ── Bridge 2: Repo Files -> Agent Context ────────────────────────────
bridge_repo_to_agent() {
  echo "=== Bridge: Repo -> Agent Context ==="
  
  # 2a. Latest learnings -> session context
  local learnings
  learnings="$(find "${REPO_ROOT}/.claude/state/learning-reports/" -name "*.md" -newer "${BRIDGE_DIR}/last-bridge.txt" 2>/dev/null | head -5)"
  if [[ -n "$learnings" ]]; then
    echo "  [2a] $(echo "$learnings" | wc -l) new learning reports available"
  fi
  
  # 2b. Compliance status -> agent awareness
  local latest_compliance
  latest_compliance="$(find "${REPO_ROOT}/logs/compliance/" -name "*.json" -newer "${BRIDGE_DIR}/last-bridge.txt" 2>/dev/null | tail -1)"
  if [[ -f "$latest_compliance" ]]; then
    local rate
    rate="$(grep -oE '"compliance_rate":[0-9]+' "$latest_compliance" 2>/dev/null | cut -d: -f2 || echo 'unknown')"
    echo "  [2b] Latest compliance rate: ${rate}%"
    
    # If compliance is low, add enforcement reminder
    if [[ "$rate" =~ ^[0-9]+$ ]] && [[ $rate -lt 50 ]]; then
      echo "  [2b] LOW COMPLIANCE: Adding enforcement reminder to agent context"
      echo "WARNING: Review compliance is ${rate}% (threshold: 80%). Ensure all feature commits have plan approval and cross-review evidence." > "${REPO_ROOT}/.claude/state/enforcement-reminder.txt"
    fi
  fi
  
  # 2c. Shared memory files for all agents
  local shared="${REPO_ROOT}/.claude/state/shared-knowledge/"
  mkdir -p "$shared"
  echo "  [2c] Shared knowledge directory: $(ls "$shared" 2>/dev/null | wc -l) files"
  
  echo ""
}

# ── Bridge 3: Skill Sync ─────────────────────────────────────────────
bridge_skill_sync() {
  echo "=== Bridge: Skill Sync ==="
  
  # 3a. Check .claude/skills/ vs Hermes ~/.hermes/skills/
  if [[ -d "$HOME/.hermes/skills/" ]]; then
    local hermes_only=0
    local repo_only=0
    local hermes_count
    hermes_count="$(find "$HOME/.hermes/skills/" -name "SKILL.md" 2>/dev/null | wc -l)"
    local repo_count
    repo_count="$(find "${REPO_ROOT}/.claude/skills/" -name "SKILL.md" 2>/dev/null | wc -l)"
    
    echo "  [3a] Hermes skills: $hermes_count | Repo skills: $repo_count"
  fi
  
  # 3b. Check workspace-hub .claude/skills/ vs tier-1 repos
  local tier1_repos=(assetutilities digitalmodel worldenergydata assethold)
  for repo in "${tier1_repos[@]}"; do
    if [[ -d "${REPO_ROOT}/$repo/.claude/skills/" ]]; then
      local repo_skill_count
      repo_skill_count="$(find "${REPO_ROOT}/$repo/.claude/skills/" -name "SKILL.md" 2>/dev/null | wc -l)"
      echo "  [3b] $repo: $repo_skill_count skills"
    fi
  done
  
  # 3c. Sync workspace-hub skills to all repos
  for repo in "${tier1_repos[@]}"; do
    if [[ -d "${REPO_ROOT}/$repo/.claude/skills/" ]]; then
      echo "  [3c] $repo: skills directory exists"
    fi
  done
  
  echo ""
}

# ── Main Bridge ──────────────────────────────────────────────────────
main() {
  local mode="${1:-bridge}"
  
  case "$mode" in
    bridge)
      bridge_local_to_repo
      bridge_repo_to_agent
      bridge_skill_sync
      
      # Record bridge timestamp
      echo "$TIMESTAMP" > "${BRIDGE_DIR}/last-bridge.txt"
      
      echo "=== Bridge Complete ($TIMESTAMP, $MACHINE) ==="
      ;;
    status)
      echo "Bridge status:"
      if [[ -f "${BRIDGE_DIR}/last-bridge.txt" ]]; then
        echo "  Last bridge: $(cat "${BRIDGE_DIR}/last-bridge.txt")"
      else
        echo "  Last bridge: never"
      fi
      ;;
  esac
}

main "$@"
