#!/usr/bin/env bash
# sync-agent-memories.sh — Cross-pollinate memories between Hermes and Claude agents
#
# Reads Hermes MEMORY.md and USER.md (§-separated entries), categorizes them,
# and writes structured YAML into Claude's state directory. Also merges with
# existing Claude memory to produce a unified cross-agent-memory.yaml.
#
# Direction: Hermes -> Claude (read-only from Hermes side; never modifies Hermes files)
#
# Usage:
#   ./sync-agent-memories.sh              # normal sync
#   ./sync-agent-memories.sh --dry-run    # preview without writing
#
set -euo pipefail

# ── Paths ──────────────────────────────────────────────────────────────────
HERMES_MEMORY="${HOME}/.hermes/memories/MEMORY.md"
HERMES_USER="${HOME}/.hermes/memories/USER.md"
CLAUDE_STATE="/mnt/local-analysis/workspace-hub/.claude/state"
CLAUDE_PROJECT_MEMORY="${HOME}/.claude/projects/-mnt-local-analysis-workspace-hub/memory"
OUTPUT_HERMES="${CLAUDE_STATE}/hermes-insights.yaml"
OUTPUT_CROSS="${CLAUDE_STATE}/cross-agent-memory.yaml"

# ── Flags ──────────────────────────────────────────────────────────────────
DRY_RUN=false
VERBOSE=false
for arg in "$@"; do
  case "$arg" in
    --dry-run)  DRY_RUN=true ;;
    --verbose)  VERBOSE=true ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--verbose]"
      echo "  --dry-run   Preview output without writing files"
      echo "  --verbose   Print debug info during processing"
      exit 0
      ;;
  esac
done

log() { echo "[sync-agent-memories] $*"; }
debug() { $VERBOSE && echo "[DEBUG] $*" || true; }

# ── Validate sources exist ─────────────────────────────────────────────────
if [[ ! -f "$HERMES_MEMORY" ]]; then
  log "WARN: Hermes MEMORY.md not found at $HERMES_MEMORY — skipping memory entries"
  HERMES_MEMORY=""
fi
if [[ ! -f "$HERMES_USER" ]]; then
  log "WARN: Hermes USER.md not found at $HERMES_USER — skipping user entries"
  HERMES_USER=""
fi

if [[ -z "$HERMES_MEMORY" && -z "$HERMES_USER" ]]; then
  log "ERROR: No Hermes source files found. Nothing to sync."
  exit 1
fi

mkdir -p "$CLAUDE_STATE"

# ── Parse §-separated entries from a file into an array ────────────────────
# Reads file, splits on lines that are just "§", trims whitespace
parse_entries() {
  local file="$1"
  local -n arr=$2
  local current=""

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" == "§" ]]; then
      # Trim leading/trailing whitespace
      current="$(echo "$current" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
      if [[ -n "$current" ]]; then
        arr+=("$current")
      fi
      current=""
    else
      if [[ -n "$current" ]]; then
        current="${current} ${line}"
      else
        current="$line"
      fi
    fi
  done < "$file"

  # Don't forget the last entry (no trailing §)
  current="$(echo "$current" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  if [[ -n "$current" ]]; then
    arr+=("$current")
  fi
}

# ── Categorize a single entry ──────────────────────────────────────────────
# Returns: environment_facts | conventions | project_knowledge | user_preferences
categorize_entry() {
  local entry="$1"
  local source="$2"  # "memory" or "user"
  local lower
  lower="$(echo "$entry" | tr '[:upper:]' '[:lower:]')"

  # User source entries always go to user_preferences
  if [[ "$source" == "user" ]]; then
    echo "user_preferences"
    return
  fi

  # Convention patterns: tooling rules, "always use", "never", corrections
  if echo "$lower" | grep -qE '(always use|never bare|never use|corrected this|use.*instead|convention|must use|prefer )'; then
    echo "conventions"
    return
  fi

  # Environment facts: machine names, paths, mounts, filesystem, git repos
  if echo "$lower" | grep -qE '(ace-linux|mount|real workspace|overlay|write_file|/mnt/|filesystem|machine|kvm|edid|t400|sparse)'; then
    echo "environment_facts"
    return
  fi

  # Project knowledge: repos, features, specs, issues, architecture
  if echo "$lower" | grep -qE '(repo|feature|spec|issue|#[0-9]|pipeline|schema|catalog|orcaflex|orcawave|digitalmodel|aceengineer|solver|parachute|hull|diffraction|pydantic|yaml|registry|cron|scanner|nested|gitignore)'; then
    echo "project_knowledge"
    return
  fi

  # Default: environment_facts for memory source
  echo "environment_facts"
}

# ── YAML-safe string escaping ──────────────────────────────────────────────
yaml_escape() {
  local s="$1"
  # Replace backslashes first, then double quotes
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  echo "\"$s\""
}

# ── Compute content hash for idempotency ───────────────────────────────────
compute_source_hash() {
  local hash=""
  if [[ -n "$HERMES_MEMORY" && -f "$HERMES_MEMORY" ]]; then
    hash+="$(md5sum "$HERMES_MEMORY" | cut -d' ' -f1)"
  fi
  if [[ -n "$HERMES_USER" && -f "$HERMES_USER" ]]; then
    hash+="$(md5sum "$HERMES_USER" | cut -d' ' -f1)"
  fi
  echo "$hash" | md5sum | cut -d' ' -f1
}

# ── Check if sync is needed (idempotency) ─────────────────────────────────
SOURCE_HASH="$(compute_source_hash)"

if [[ -f "$OUTPUT_HERMES" ]] && ! $DRY_RUN; then
  EXISTING_HASH="$(grep -oP 'source_hash: "\K[^"]+' "$OUTPUT_HERMES" 2>/dev/null || echo "")"
  if [[ "$EXISTING_HASH" == "$SOURCE_HASH" ]]; then
    log "Sources unchanged (hash: ${SOURCE_HASH:0:8}...). Skipping sync."
    exit 0
  fi
  debug "Hash changed: $EXISTING_HASH -> $SOURCE_HASH"
fi

# ── Parse all entries ──────────────────────────────────────────────────────
declare -a MEMORY_ENTRIES=()
declare -a USER_ENTRIES=()

if [[ -n "$HERMES_MEMORY" ]]; then
  parse_entries "$HERMES_MEMORY" MEMORY_ENTRIES
  debug "Parsed ${#MEMORY_ENTRIES[@]} entries from MEMORY.md"
fi

if [[ -n "$HERMES_USER" ]]; then
  parse_entries "$HERMES_USER" USER_ENTRIES
  debug "Parsed ${#USER_ENTRIES[@]} entries from USER.md"
fi

# ── Categorize entries ─────────────────────────────────────────────────────
declare -a CAT_ENV=()
declare -a CAT_CONV=()
declare -a CAT_PROJ=()
declare -a CAT_USER=()

for entry in "${MEMORY_ENTRIES[@]}"; do
  cat="$(categorize_entry "$entry" "memory")"
  case "$cat" in
    environment_facts)  CAT_ENV+=("$entry") ;;
    conventions)        CAT_CONV+=("$entry") ;;
    project_knowledge)  CAT_PROJ+=("$entry") ;;
    user_preferences)   CAT_USER+=("$entry") ;;
  esac
  debug "  [$cat] ${entry:0:60}..."
done

for entry in "${USER_ENTRIES[@]}"; do
  CAT_USER+=("$entry")
  debug "  [user_preferences] ${entry:0:60}..."
done

log "Categorized: env=${#CAT_ENV[@]} conv=${#CAT_CONV[@]} proj=${#CAT_PROJ[@]} user=${#CAT_USER[@]}"

# ── Generate hermes-insights.yaml ──────────────────────────────────────────
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HERMES_YAML=""

generate_hermes_yaml() {
  local yaml=""
  yaml+="# hermes-insights.yaml — Auto-generated by sync-agent-memories.sh\n"
  yaml+="# DO NOT EDIT — this file is overwritten on each sync\n"
  yaml+="# Source: Hermes MEMORY.md + USER.md\n"
  yaml+="\n"
  yaml+="metadata:\n"
  yaml+="  generated: \"${TIMESTAMP}\"\n"
  yaml+="  source_hash: \"${SOURCE_HASH}\"\n"
  yaml+="  hermes_memory: \"${HERMES_MEMORY:-none}\"\n"
  yaml+="  hermes_user: \"${HERMES_USER:-none}\"\n"
  yaml+="  entry_count: $(( ${#CAT_ENV[@]} + ${#CAT_CONV[@]} + ${#CAT_PROJ[@]} + ${#CAT_USER[@]} ))\n"
  yaml+="\n"

  yaml+="environment_facts:\n"
  if (( ${#CAT_ENV[@]} == 0 )); then
    yaml+="  []\n"
  else
    for entry in "${CAT_ENV[@]}"; do
      yaml+="  - $(yaml_escape "$entry")\n"
    done
  fi
  yaml+="\n"

  yaml+="conventions:\n"
  if (( ${#CAT_CONV[@]} == 0 )); then
    yaml+="  []\n"
  else
    for entry in "${CAT_CONV[@]}"; do
      yaml+="  - $(yaml_escape "$entry")\n"
    done
  fi
  yaml+="\n"

  yaml+="project_knowledge:\n"
  if (( ${#CAT_PROJ[@]} == 0 )); then
    yaml+="  []\n"
  else
    for entry in "${CAT_PROJ[@]}"; do
      yaml+="  - $(yaml_escape "$entry")\n"
    done
  fi
  yaml+="\n"

  yaml+="user_preferences:\n"
  if (( ${#CAT_USER[@]} == 0 )); then
    yaml+="  []\n"
  else
    for entry in "${CAT_USER[@]}"; do
      yaml+="  - $(yaml_escape "$entry")\n"
    done
  fi

  echo -e "$yaml"
}

HERMES_YAML="$(generate_hermes_yaml)"

# ── Generate cross-agent-memory.yaml ───────────────────────────────────────
# Merges Hermes insights with Claude project memory topics
generate_cross_yaml() {
  local yaml=""
  yaml+="# cross-agent-memory.yaml — Unified cross-agent memory index\n"
  yaml+="# DO NOT EDIT — this file is overwritten on each sync\n"
  yaml+="# Merges: Hermes (MEMORY.md/USER.md) + Claude (project memory files)\n"
  yaml+="\n"
  yaml+="metadata:\n"
  yaml+="  generated: \"${TIMESTAMP}\"\n"
  yaml+="  source_hash: \"${SOURCE_HASH}\"\n"
  yaml+="  agents:\n"
  yaml+="    hermes:\n"
  yaml+="      memory_file: \"${HERMES_MEMORY:-none}\"\n"
  yaml+="      user_file: \"${HERMES_USER:-none}\"\n"
  yaml+="      entry_count: $(( ${#MEMORY_ENTRIES[@]} + ${#USER_ENTRIES[@]} ))\n"
  yaml+="    claude:\n"
  yaml+="      project_memory_dir: \"${CLAUDE_PROJECT_MEMORY}\"\n"

  # Count Claude memory files
  local claude_count=0
  local claude_files=()
  if [[ -d "$CLAUDE_PROJECT_MEMORY" ]]; then
    while IFS= read -r -d '' f; do
      claude_files+=("$(basename "$f")")
      ((claude_count++))
    done < <(find "$CLAUDE_PROJECT_MEMORY" -maxdepth 1 -name '*.md' ! -name '*.bak' -print0 2>/dev/null || true)
  fi
  yaml+="      memory_file_count: ${claude_count}\n"
  yaml+="\n"

  # ── Hermes section ─────────────────────────────────────────────────────
  yaml+="hermes_insights:\n"
  yaml+="  environment_facts:\n"
  if (( ${#CAT_ENV[@]} == 0 )); then
    yaml+="    []\n"
  else
    for entry in "${CAT_ENV[@]}"; do
      yaml+="    - $(yaml_escape "$entry")\n"
    done
  fi
  yaml+="  conventions:\n"
  if (( ${#CAT_CONV[@]} == 0 )); then
    yaml+="    []\n"
  else
    for entry in "${CAT_CONV[@]}"; do
      yaml+="    - $(yaml_escape "$entry")\n"
    done
  fi
  yaml+="  project_knowledge:\n"
  if (( ${#CAT_PROJ[@]} == 0 )); then
    yaml+="    []\n"
  else
    for entry in "${CAT_PROJ[@]}"; do
      yaml+="    - $(yaml_escape "$entry")\n"
    done
  fi
  yaml+="  user_preferences:\n"
  if (( ${#CAT_USER[@]} == 0 )); then
    yaml+="    []\n"
  else
    for entry in "${CAT_USER[@]}"; do
      yaml+="    - $(yaml_escape "$entry")\n"
    done
  fi
  yaml+="\n"

  # ── Claude section (index of memory files + key topics) ────────────────
  yaml+="claude_memory_index:\n"
  if (( claude_count == 0 )); then
    yaml+="  files: []\n"
  else
    yaml+="  files:\n"
    for f in "${claude_files[@]}"; do
      local topic
      # Extract topic from filename: project_foo_bar.md -> foo bar
      topic="$(echo "${f%.md}" | sed 's/^feedback_//;s/^project_//;s/^reference_//;s/_/ /g')"
      yaml+="    - file: $(yaml_escape "$f")\n"
      yaml+="      topic: $(yaml_escape "$topic")\n"
    done
  fi
  yaml+="\n"

  # ── Shared facts (entries that appear relevant to both agents) ─────────
  yaml+="shared_conventions:\n"
  yaml+="  # These conventions from Hermes should be honored by all agents\n"
  if (( ${#CAT_CONV[@]} == 0 )); then
    yaml+="  []\n"
  else
    for entry in "${CAT_CONV[@]}"; do
      yaml+="  - $(yaml_escape "$entry")\n"
    done
  fi

  echo -e "$yaml"
}

CROSS_YAML="$(generate_cross_yaml)"

# ── Output ─────────────────────────────────────────────────────────────────
if $DRY_RUN; then
  log "=== DRY RUN — would write to $OUTPUT_HERMES ==="
  echo "$HERMES_YAML"
  echo ""
  log "=== DRY RUN — would write to $OUTPUT_CROSS ==="
  echo "$CROSS_YAML"
  log "=== DRY RUN complete — no files written ==="
else
  echo "$HERMES_YAML" > "$OUTPUT_HERMES"
  echo "$CROSS_YAML" > "$OUTPUT_CROSS"
  log "Wrote $OUTPUT_HERMES ($(wc -c < "$OUTPUT_HERMES") bytes)"
  log "Wrote $OUTPUT_CROSS ($(wc -c < "$OUTPUT_CROSS") bytes)"
  log "Sync complete at $TIMESTAMP (hash: ${SOURCE_HASH:0:8}...)"
fi
