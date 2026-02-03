#!/usr/bin/env bash
# sync-knowledge-work-plugins.sh
#
# Synchronize skills from anthropics/knowledge-work-plugins into the
# workspace-hub skill system.
#
# Usage:
#   ./scripts/skills/sync-knowledge-work-plugins.sh              # status report
#   ./scripts/skills/sync-knowledge-work-plugins.sh --dry-run     # show what would change
#   ./scripts/skills/sync-knowledge-work-plugins.sh --plugin=sales # sync one plugin
#   ./scripts/skills/sync-knowledge-work-plugins.sh --diff        # show content diffs
#   ./scripts/skills/sync-knowledge-work-plugins.sh --sync        # apply changes

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_OWNER="anthropics"
REPO_NAME="knowledge-work-plugins"
REPO_BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${REPO_BRANCH}"

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_ROOT="${WORKSPACE_ROOT}/.claude/skills"

# Plugin name -> local skill directory path (relative to SKILLS_ROOT)
declare -A PLUGIN_MAP=(
  ["sales"]="business/sales"
  ["customer-support"]="business/customer-support"
  ["product-management"]="business/product"
  ["marketing"]="business/marketing"
  ["legal"]="business/legal"
  ["finance"]="business/finance"
  ["data"]="data/analytics"
  ["enterprise-search"]="business/enterprise-search"
  ["productivity"]="business/productivity"
  ["bio-research"]="science/bio-research"
  ["cowork-plugin-management"]="development/plugin-management"
)

# Plugin name -> space-separated list of skill slugs
declare -A PLUGIN_SKILLS=(
  ["sales"]="account-research call-prep competitive-intelligence create-an-asset daily-briefing draft-outreach"
  ["customer-support"]="ticket-triage customer-research response-drafting escalation knowledge-management"
  ["product-management"]="feature-spec roadmap-management stakeholder-comms user-research-synthesis competitive-analysis metrics-tracking"
  ["marketing"]="brand-voice campaign-planning competitive-analysis content-creation performance-analytics"
  ["legal"]="contract-review nda-triage compliance canned-responses legal-risk-assessment meeting-briefing"
  ["finance"]="journal-entry-prep reconciliation financial-statements variance-analysis close-management audit-support"
  ["data"]="sql-queries data-exploration data-visualization statistical-analysis data-validation interactive-dashboard-builder data-context-extractor"
  ["enterprise-search"]="search-strategy source-management knowledge-synthesis"
  ["productivity"]="task-management memory-management"
  ["bio-research"]="single-cell-rna-qc scvi-tools nextflow-development clinical-trial-protocol instrument-data-to-allotrope scientific-problem-selection"
  ["cowork-plugin-management"]="cowork-plugin-customizer"
)

# ---------------------------------------------------------------------------
# CLI flags
# ---------------------------------------------------------------------------

DRY_RUN=false
SHOW_DIFF=false
DO_SYNC=false
FILTER_PLUGIN=""

for arg in "$@"; do
  case "$arg" in
    --dry-run)   DRY_RUN=true ;;
    --diff)      SHOW_DIFF=true ;;
    --sync)      DO_SYNC=true ;;
    --plugin=*)  FILTER_PLUGIN="${arg#--plugin=}" ;;
    --help|-h)
      echo "Usage: $(basename "$0") [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --dry-run         Show what would change without writing files"
      echo "  --diff            Show content diff for changed skills"
      echo "  --sync            Fetch and write updated skill files"
      echo "  --plugin=NAME     Operate on a single plugin only"
      echo "  --help, -h        Show this help message"
      echo ""
      echo "With no flags, reports the status of all plugins (OK / MISSING / OUTDATED)."
      exit 0
      ;;
    *)
      echo "error: unknown argument '${arg}'. Use --help for usage." >&2
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Colours (disabled when stdout is not a terminal)
if [[ -t 1 ]]; then
  C_GREEN="\033[0;32m"
  C_YELLOW="\033[0;33m"
  C_RED="\033[0;31m"
  C_CYAN="\033[0;36m"
  C_RESET="\033[0m"
else
  C_GREEN="" C_YELLOW="" C_RED="" C_CYAN="" C_RESET=""
fi

status_ok()      { printf "${C_GREEN}OK${C_RESET}"; }
status_missing() { printf "${C_RED}MISSING${C_RESET}"; }
status_outdated(){ printf "${C_YELLOW}OUTDATED${C_RESET}"; }

# Build the remote URL for a skill inside a plugin.
# Arguments: $1=plugin $2=skill
remote_skill_url() {
  local plugin="$1" skill="$2"
  echo "${RAW_BASE}/${plugin}/${skill}/SKILL.md"
}

# Convert upstream content to local format.
#
# 1. Strip any "source table" frontmatter block that the upstream repo uses
#    (delimited by <!-- source-table --> markers or an HTML <table> at the top).
# 2. Prepend a YAML frontmatter block with provenance metadata.
convert_content() {
  local plugin="$1" skill="$2" raw_content="$3"
  local today
  today="$(date +%Y-%m-%d)"

  # --- Strip upstream source-table frontmatter ---
  # Remove everything between <!-- source-table --> ... <!-- /source-table -->
  local body
  body="$(echo "$raw_content" | sed '/^<!-- *source-table *-->$/,/^<!-- *\/source-table *-->$/d')"

  # Also strip a leading HTML <table>...</table> block if present (some plugins
  # use an HTML table instead of comment markers).
  body="$(echo "$body" | sed '/^<table>/,/^<\/table>/d')"

  # Trim leading blank lines
  body="$(echo "$body" | sed '/./,$!d')"

  # If upstream already has YAML frontmatter, strip it so we can add our own.
  if echo "$body" | head -1 | grep -q '^---$'; then
    body="$(echo "$body" | sed '1{/^---$/d}' | sed '1,/^---$/d')"
    body="$(echo "$body" | sed '/./,$!d')"
  fi

  # --- Build local YAML frontmatter ---
  cat <<EOF
---
name: ${skill}
description: "Skill synced from ${REPO_OWNER}/${REPO_NAME} plugin ${plugin}"
version: 1.0.0
category: ${PLUGIN_MAP[$plugin]}
last_updated: ${today}
source: ${REPO_OWNER}/${REPO_NAME}
source_plugin: ${plugin}
---

${body}
EOF
}

# Fetch remote content for a skill. Returns empty string on failure.
fetch_remote() {
  local url="$1"
  curl -fsSL --connect-timeout 10 --max-time 30 "$url" 2>/dev/null || true
}

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

declare -i total=0 ok=0 missing=0 outdated=0 synced=0 errors=0

plugins_to_process=()
if [[ -n "$FILTER_PLUGIN" ]]; then
  if [[ -z "${PLUGIN_MAP[$FILTER_PLUGIN]+x}" ]]; then
    echo "error: unknown plugin '${FILTER_PLUGIN}'" >&2
    echo "Available plugins: ${!PLUGIN_MAP[*]}" >&2
    exit 1
  fi
  plugins_to_process+=("$FILTER_PLUGIN")
else
  # Sort plugin names for deterministic output
  while IFS= read -r p; do
    plugins_to_process+=("$p")
  done < <(printf '%s\n' "${!PLUGIN_MAP[@]}" | sort)
fi

echo "================================================================"
echo " knowledge-work-plugins sync"
echo " source: ${REPO_OWNER}/${REPO_NAME} (${REPO_BRANCH})"
echo " target: ${SKILLS_ROOT}"
echo "================================================================"
echo ""

for plugin in "${plugins_to_process[@]}"; do
  local_dir="${SKILLS_ROOT}/${PLUGIN_MAP[$plugin]}"
  skills_list="${PLUGIN_SKILLS[$plugin]}"

  printf "${C_CYAN}[%s]${C_RESET} -> %s\n" "$plugin" "${PLUGIN_MAP[$plugin]}"

  for skill in $skills_list; do
    total+=1
    local_file="${local_dir}/${skill}/SKILL.md"
    remote_url="$(remote_skill_url "$plugin" "$skill")"

    # --- Determine status ---
    if [[ ! -f "$local_file" ]]; then
      printf "  %-40s %s\n" "$skill" "$(status_missing)"
      missing+=1

      if $DO_SYNC || $DRY_RUN; then
        remote_content="$(fetch_remote "$remote_url")"
        if [[ -z "$remote_content" ]]; then
          printf "    -> ${C_RED}fetch failed${C_RESET}: %s\n" "$remote_url"
          errors+=1
          continue
        fi

        converted="$(convert_content "$plugin" "$skill" "$remote_content")"

        if $DRY_RUN; then
          printf "    -> ${C_YELLOW}would create${C_RESET} %s\n" "$local_file"
          if $SHOW_DIFF; then
            echo "--- /dev/null"
            echo "+++ ${local_file}"
            echo "$converted" | sed 's/^/+ /'
            echo ""
          fi
        elif $DO_SYNC; then
          mkdir -p "$(dirname "$local_file")"
          echo "$converted" > "$local_file"
          printf "    -> ${C_GREEN}created${C_RESET} %s\n" "$local_file"
          synced+=1
        fi
      fi

    else
      # File exists -- check if content matches upstream
      if $DO_SYNC || $DRY_RUN || $SHOW_DIFF; then
        remote_content="$(fetch_remote "$remote_url")"
        if [[ -z "$remote_content" ]]; then
          # Cannot reach upstream; assume OK for status-only runs
          if $DO_SYNC || $DRY_RUN; then
            printf "  %-40s %s (${C_YELLOW}upstream unreachable${C_RESET})\n" "$skill" "$(status_ok)"
            errors+=1
          else
            printf "  %-40s %s\n" "$skill" "$(status_ok)"
            ok+=1
          fi
          continue
        fi

        converted="$(convert_content "$plugin" "$skill" "$remote_content")"

        # Compare ignoring the last_updated date line (which changes daily)
        local_normalized="$(sed '/^last_updated:/d' "$local_file")"
        remote_normalized="$(echo "$converted" | sed '/^last_updated:/d')"

        if [[ "$local_normalized" == "$remote_normalized" ]]; then
          printf "  %-40s %s\n" "$skill" "$(status_ok)"
          ok+=1
        else
          printf "  %-40s %s\n" "$skill" "$(status_outdated)"
          outdated+=1

          if $SHOW_DIFF; then
            diff --color=auto -u "$local_file" <(echo "$converted") || true
            echo ""
          fi

          if $DRY_RUN; then
            printf "    -> ${C_YELLOW}would update${C_RESET} %s\n" "$local_file"
          elif $DO_SYNC; then
            echo "$converted" > "$local_file"
            printf "    -> ${C_GREEN}updated${C_RESET} %s\n" "$local_file"
            synced+=1
          fi
        fi
      else
        # Status-only: file exists, skip upstream check
        printf "  %-40s %s\n" "$skill" "$(status_ok)"
        ok+=1
      fi
    fi
  done

  echo ""
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo "================================================================"
echo " Summary"
echo "================================================================"
printf " Total skills:  %d\n" "$total"
printf " OK:            ${C_GREEN}%d${C_RESET}\n" "$ok"
printf " Missing:       ${C_RED}%d${C_RESET}\n" "$missing"
printf " Outdated:      ${C_YELLOW}%d${C_RESET}\n" "$outdated"
if $DO_SYNC; then
  printf " Synced:        ${C_GREEN}%d${C_RESET}\n" "$synced"
fi
if (( errors > 0 )); then
  printf " Errors:        ${C_RED}%d${C_RESET}\n" "$errors"
fi
echo ""

if $DRY_RUN; then
  echo "(dry-run mode -- no files were modified)"
fi

# Exit non-zero when there are missing or outdated skills (useful for CI)
if (( missing + outdated > 0 )) && ! $DO_SYNC; then
  exit 1
fi

exit 0
