#!/usr/bin/env bash
# =============================================================================
# merge-submodule-skills.sh
#
# One-time script to discover unique skills in submodules and list/copy them
# to workspace-hub's centralized skill directory.
#
# Usage:
#   bash scripts/skills/merge-submodule-skills.sh              # dry-run
#   bash scripts/skills/merge-submodule-skills.sh --apply      # copy skills
#   bash scripts/skills/merge-submodule-skills.sh --diff       # show diffs
#
# Exit codes:
#   0  Success
#   1  Errors encountered during processing
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_WS_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
WS_HUB="${WORKSPACE_HUB_ROOT:-$DEFAULT_WS_HUB}"
SKILLS_ROOT="${WORKSPACE_HUB_SKILLS_ROOT:-${WS_HUB}/.claude/skills}"
REPO_MANIFEST="${WORKSPACE_HUB_SKILL_REPO_MANIFEST:-${SCRIPT_DIR}/skill-propagation-repos.txt}"

# ---------------------------------------------------------------------------
# CLI flags
# ---------------------------------------------------------------------------
MODE="dry-run"  # dry-run | apply | diff
REPORT_FILE=""

while [[ $# -gt 0 ]]; do
  arg="$1"
  case "$arg" in
    --apply)  MODE="apply"; shift ;;
    --diff)   MODE="diff"; shift ;;
    --report-file=*) REPORT_FILE="${arg#--report-file=}" ;;
    --report-file)
      shift
      if [[ $# -eq 0 ]]; then
        echo "error: --report-file requires a path" >&2
        exit 1
      fi
      REPORT_FILE="$1"
      shift
      ;;
    --report-file=)
      echo "error: --report-file requires a path" >&2
      exit 1
      ;;
    --help|-h)
      cat <<'USAGE'
Usage: bash scripts/skills/merge-submodule-skills.sh [--apply|--diff] [--report-file PATH]

Modes:
  (default)   Dry-run listing what would be merged
  --apply     Copy unique skills to workspace-hub
  --diff      Show content diffs for conflicts

Options:
  --report-file PATH  Write a machine-readable YAML propagation report
  --help, -h  Show this help message
USAGE
      exit 0
      ;;
    *)
      echo "error: unknown argument '${arg}'. Use --help for usage." >&2
      exit 1
      ;;
  esac
  if [[ "$arg" == --report-file=* ]]; then
    shift
  fi
done

# ---------------------------------------------------------------------------
# Terminal colors (disabled when piped)
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
  C_GREEN="\033[0;32m"
  C_YELLOW="\033[0;33m"
  C_RED="\033[0;31m"
  C_CYAN="\033[0;36m"
  C_DIM="\033[0;90m"
  C_BOLD="\033[1m"
  C_RESET="\033[0m"
else
  C_GREEN="" C_YELLOW="" C_RED="" C_CYAN="" C_DIM="" C_BOLD="" C_RESET=""
fi

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------
declare -i total_unique=0
declare -i already_exists=0
declare -i would_merge=0
declare -i merged=0
declare -i conflicts=0
declare -i errors=0
declare -i unmapped_count=0
declare -i skipped_repo_count=0
declare -i dirty_repo_count=0
declare -i skipped_skill_count=0

declare -a report_actions=()
declare -a report_skipped_repos=()
declare -a report_skipped_skills=()

# ---------------------------------------------------------------------------
# Shared/template directories to skip (propagated infrastructure, not skills)
# ---------------------------------------------------------------------------
SKIP_DIRS="guidelines|meta|workflows|session-logs|_internal|_core|_runtime"

# ---------------------------------------------------------------------------
# Mapping: submodule name -> associative routing rules
#
# Each mapping entry is: skill_pattern -> target_dir (relative to SKILLS_ROOT)
#
# Patterns are matched with bash globbing (case-insensitive prefix match).
# A special "*" pattern serves as the default for unmapped skills.
# ---------------------------------------------------------------------------

# digitalmodel skill prefixes -> target directories
dm_route() {
  local skill="$1"
  case "$skill" in
    orcaflex-*)              echo "engineering/marine-offshore" ;;
    orcawave-*)              echo "engineering/marine-offshore" ;;
    aqwa-*)                  echo "engineering/marine-offshore" ;;
    bemrosetta*)             echo "engineering/marine-offshore" ;;
    diffraction-*)           echo "engineering/marine-offshore" ;;
    hydrodynamics*)          echo "engineering/marine-offshore" ;;
    mooring-*)               echo "engineering/marine-offshore" ;;
    fatigue-*)               echo "engineering/marine-offshore" ;;
    catenary-*)              echo "engineering/marine-offshore" ;;
    cathodic-*)              echo "engineering/marine-offshore" ;;
    structural-*)            echo "engineering/marine-offshore" ;;
    viv-*)                   echo "engineering/marine-offshore" ;;
    signal-*)                echo "engineering/marine-offshore" ;;
    cad-*)                   echo "engineering/cad" ;;
    freecad-*)               echo "engineering/cad" ;;
    gmsh-*)                  echo "eng/mesh-utilities" ;;
    data-analysis*)          echo "data/analysis" ;;
    documentation*)          echo "development/documentation" ;;
    devtools*)               echo "development/tools" ;;
    automation*)             echo "development/automation" ;;
    ai-prompting*)           echo "ai/prompting" ;;
    office-docs*)            echo "data/office" ;;
    context-management*)     echo "coordination/workspace" ;;
    optimization*)           echo "coordination/workspace" ;;
    product*)                echo "coordination/workspace" ;;
    productivity*)           echo "business/productivity" ;;
    communication*)          echo "business/communication" ;;
    *)                       echo "" ;;
  esac
}

# worldenergydata skill prefixes -> target directories
wed_route() {
  local skill="$1"
  case "$skill" in
    bsee-*)                  echo "data/energy" ;;
    metocean-*)              echo "data/energy" ;;
    energy-*)                echo "data/energy" ;;
    sodir-*)                 echo "data/energy" ;;
    web-scraper-energy*)     echo "data/energy" ;;
    field-*)                 echo "data/energy" ;;
    well-*)                  echo "data/energy" ;;
    production-*)            echo "data/energy" ;;
    npv-*)                   echo "data/energy" ;;
    fdas-*)                  echo "data/energy" ;;
    economic-*)              echo "data/energy" ;;
    api12-*)                 echo "data/energy" ;;
    hse-*)                   echo "data/energy" ;;
    marine-safety-*)         echo "data/energy" ;;
    context-management*)     echo "coordination/workspace" ;;
    optimization*)           echo "coordination/workspace" ;;
    product*)                echo "coordination/workspace" ;;
    *)                       echo "" ;;
  esac
}

# aceengineer-admin skill prefixes -> target directories
admin_route() {
  local skill="$1"
  case "$skill" in
    expense-*)               echo "business/admin" ;;
    invoice-*)               echo "business/admin" ;;
    tax-*)                   echo "business/admin" ;;
    quantification-*)        echo "business/admin" ;;
    modular-architecture-*)  echo "business/admin" ;;
    product-documentation*)  echo "business/admin" ;;
    technology-stack-*)      echo "business/admin" ;;
    workspace-hub-*)         echo "coordination/workspace" ;;
    context-management*)     echo "coordination/workspace" ;;
    optimization*)           echo "coordination/workspace" ;;
    product*)                echo "coordination/workspace" ;;
    *)                       echo "" ;;
  esac
}

# aceengineer-website skill prefixes -> target directories
website_route() {
  local skill="$1"
  case "$skill" in
    aceengineer-website-*)   echo "business/content-design" ;;
    *)                       echo "" ;;
  esac
}

# assetutilities skill prefixes -> target directories
asset_route() {
  local skill="$1"
  case "$skill" in
    data-management*)        echo "data/analysis" ;;
    pdf-*)                   echo "data/documents" ;;
    plotly-*)                echo "data/visualization" ;;
    context-management*)     echo "coordination/workspace" ;;
    optimization*)           echo "coordination/workspace" ;;
    product*)                echo "coordination/workspace" ;;
    *)                       echo "" ;;
  esac
}

# Generic route for submodules without specific mappings
generic_route() {
  local skill="$1"
  case "$skill" in
    context-management*)     echo "coordination/workspace" ;;
    optimization*)           echo "coordination/workspace" ;;
    product*)                echo "coordination/workspace" ;;
    *)                       echo "" ;;
  esac
}

# ---------------------------------------------------------------------------
# Route a skill from a given submodule to a target directory
# Arguments: $1=submodule_name  $2=skill_name
# Returns: target directory relative to SKILLS_ROOT, or empty if unmapped
# ---------------------------------------------------------------------------
route_skill() {
  local submodule="$1" skill="$2"
  case "$submodule" in
    digitalmodel)           dm_route "$skill" ;;
    worldenergydata)        wed_route "$skill" ;;
    aceengineer-admin)      admin_route "$skill" ;;
    aceengineer-website)    website_route "$skill" ;;
    assetutilities)         asset_route "$skill" ;;
    *)                      generic_route "$skill" ;;
  esac
}

# ---------------------------------------------------------------------------
# Check if a skill directory contains a SKILL.md file
# ---------------------------------------------------------------------------
has_skill_file() {
  local dir="$1"
  [[ -f "${dir}/SKILL.md" ]] || [[ -f "${dir}/README.md" ]]
}

# ---------------------------------------------------------------------------
# Find the primary skill file in a directory
# ---------------------------------------------------------------------------
skill_file() {
  local dir="$1"
  if [[ -f "${dir}/SKILL.md" ]]; then
    echo "${dir}/SKILL.md"
  elif [[ -f "${dir}/README.md" ]]; then
    echo "${dir}/README.md"
  else
    echo ""
  fi
}

# ---------------------------------------------------------------------------
# YAML report helpers
# ---------------------------------------------------------------------------
yaml_escape() {
  local value="$1"
  value="${value//\'/\'\'}"
  printf "'%s'" "$value"
}

add_action() {
  local repo="$1" skill="$2" action="$3" reason="$4" source_path="$5" target_path="$6"
  report_actions+=("${repo}|${skill}|${action}|${reason}|${source_path}|${target_path}")
}

add_skipped_repo() {
  local repo="$1" path="$2" reason="$3"
  skipped_repo_count+=1
  report_skipped_repos+=("${repo}|${path}|${reason}")
}

add_skipped_skill() {
  local repo="$1" path="$2" reason="$3"
  skipped_skill_count+=1
  report_skipped_skills+=("${repo}|${path}|${reason}")
}

write_report() {
  [[ -n "$REPORT_FILE" ]] || return 0
  mkdir -p "$(dirname "$REPORT_FILE")"
  {
    printf "generated_at: %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf "mode: %s\n" "$(yaml_escape "$MODE")"
    printf "source: %s\n" "$(yaml_escape "workspace submodule skills")"
    printf "workspace: %s\n" "$(yaml_escape "$WS_HUB")"
    printf "manifest: %s\n" "$(yaml_escape "$REPO_MANIFEST")"
    echo "actions:"
    if [[ ${#report_actions[@]} -eq 0 ]]; then
      echo "  []"
    else
      local entry repo skill action reason source_path target_path
      for entry in "${report_actions[@]}"; do
        IFS='|' read -r repo skill action reason source_path target_path <<<"$entry"
        echo "  - repo: $(yaml_escape "$repo")"
        echo "    skill: $(yaml_escape "$skill")"
        echo "    action: $(yaml_escape "$action")"
        echo "    reason: $(yaml_escape "$reason")"
        echo "    source_path: $(yaml_escape "$source_path")"
        echo "    target_path: $(yaml_escape "$target_path")"
      done
    fi
    echo "skipped_repos:"
    if [[ ${#report_skipped_repos[@]} -eq 0 ]]; then
      echo "  []"
    else
      local entry repo path reason
      for entry in "${report_skipped_repos[@]}"; do
        IFS='|' read -r repo path reason <<<"$entry"
        echo "  - repo: $(yaml_escape "$repo")"
        echo "    path: $(yaml_escape "$path")"
        echo "    reason: $(yaml_escape "$reason")"
      done
    fi
    echo "skipped_skills:"
    if [[ ${#report_skipped_skills[@]} -eq 0 ]]; then
      echo "  []"
    else
      local entry repo path reason
      for entry in "${report_skipped_skills[@]}"; do
        IFS='|' read -r repo path reason <<<"$entry"
        echo "  - repo: $(yaml_escape "$repo")"
        echo "    path: $(yaml_escape "$path")"
        echo "    reason: $(yaml_escape "$reason")"
      done
    fi
    echo "summary:"
    printf "  total_unique: %d\n" "$total_unique"
    printf "  already_exists: %d\n" "$already_exists"
    printf "  would_merge: %d\n" "$would_merge"
    printf "  merged: %d\n" "$merged"
    printf "  unmapped: %d\n" "$unmapped_count"
    printf "  skipped_repos: %d\n" "$skipped_repo_count"
    printf "  dirty_repos: %d\n" "$dirty_repo_count"
    printf "  skipped_skills: %d\n" "$skipped_skill_count"
    printf "  conflicts: %d\n" "$conflicts"
    printf "  errors: %d\n" "$errors"
  } >"$REPORT_FILE"
}

# ---------------------------------------------------------------------------
# Check if a skill already exists in workspace-hub's centralized directory
# Arguments: $1=target_dir (relative)  $2=skill_name
# Returns: 0 if exists, 1 if not
# ---------------------------------------------------------------------------
hub_skill_exists() {
  local target_dir="$1" skill_name="$2"
  local full_path="${SKILLS_ROOT}/${target_dir}/${skill_name}"
  [[ -d "$full_path" ]] && has_skill_file "$full_path"
}

# ---------------------------------------------------------------------------
# Discover submodules with .claude/skills/
# ---------------------------------------------------------------------------
discover_submodules() {
  local submodules=()
  if [[ -f "$REPO_MANIFEST" ]]; then
    local line
    while IFS= read -r line || [[ -n "$line" ]]; do
      line="${line%%#*}"
      line="${line#"${line%%[![:space:]]*}"}"
      line="${line%"${line##*[![:space:]]}"}"
      [[ -n "$line" ]] || continue
      submodules+=("$line")
    done <"$REPO_MANIFEST"
  else
    for dir in "${WS_HUB}"/*/; do
      local name
      name="$(basename "$dir")"
      # Skip non-submodule directories
      case "$name" in
        _archive|_temp|config|coordination|data|docker|docs|examples|\
        flow-nexus|logs|modules|monitoring-dashboard|node_modules|\
        reports|ruv-swarm|scripts|skills|specs|src|templates|tests)
          continue ;;
      esac
      if [[ -d "${dir}.claude/skills" ]]; then
        submodules+=("$name")
      fi
    done
  fi
  printf '%s\n' "${submodules[@]}" | sort
}

# ---------------------------------------------------------------------------
# Check whether a repo has uncommitted changes. Untracked files count because
# propagation should not overwrite or reason about a moving source tree.
# ---------------------------------------------------------------------------
repo_is_dirty() {
  local repo_dir="$1"
  [[ -d "${repo_dir}/.git" ]] || return 1
  [[ -n "$(git -C "$repo_dir" status --porcelain 2>/dev/null || true)" ]]
}

# ---------------------------------------------------------------------------
# Enumerate unique skill directories in a submodule, including nested trees.
# Arguments: $1=submodule_name
# Emits tab-separated records:
#   SKILL <relative_skill_dir> <skill_name>
#   SKIP  <relative_skipped_dir> <reason>
# ---------------------------------------------------------------------------
enumerate_skill_records() {
  local submodule="$1"
  local skills_dir="${WS_HUB}/${submodule}/.claude/skills"
  [[ -d "$skills_dir" ]] || return 0

  local skipped_roots="|"
  while IFS= read -r skill_dir; do
    [[ "$skill_dir" != "$skills_dir" ]] || continue
    local rel_path first_component skill_name skip_root
    rel_path="${skill_dir#"$skills_dir"/}"
    first_component="${rel_path%%/*}"

    if echo "$first_component" | grep -qE "^(${SKIP_DIRS})$"; then
      skip_root="${skills_dir}/${first_component}"
      if [[ "$skipped_roots" != *"|${skip_root}|"* ]]; then
        skipped_roots+="${skip_root}|"
        printf 'SKIP\t%s\tmatched shared/template skip pattern: %s\n' \
          "$first_component" "$first_component"
      fi
      continue
    fi

    if has_skill_file "$skill_dir"; then
      skill_name="$(basename "$skill_dir")"
      printf 'SKILL\t%s\t%s\n' "$rel_path" "$skill_name"
    fi
  done < <(find "$skills_dir" -type d | sort)
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

printf "${C_BOLD}[%s]${C_RESET} Scanning submodules for unique skills...\n\n" \
  "$(echo "$MODE" | tr '[:lower:]' '[:upper:]')"

# Collect unmapped skills for final report
declare -a unmapped_list=()

# Discover all submodules
mapfile -t submodules < <(discover_submodules)

if [[ ${#submodules[@]} -eq 0 ]]; then
  echo "No submodules with .claude/skills/ found."
  exit 0
fi

for submodule in "${submodules[@]}"; do
  skills_dir="${WS_HUB}/${submodule}/.claude/skills"

  if [[ ! -d "$skills_dir" ]]; then
    add_skipped_repo "$submodule" "$skills_dir" "expected repo missing .claude/skills directory"
    printf "${C_YELLOW}%s${C_RESET}: skipped, missing .claude/skills directory\n" "$submodule"
    continue
  fi

  if repo_is_dirty "${WS_HUB}/${submodule}"; then
    dirty_repo_count+=1
    add_skipped_repo "$submodule" "$skills_dir" "repo has uncommitted changes"
    printf "${C_YELLOW}%s${C_RESET}: skipped, repo has uncommitted changes\n" "$submodule"
    continue
  fi

  # Enumerate unique skills for this submodule
  records=()
  while IFS= read -r record; do
    records+=("$record")
  done < <(enumerate_skill_records "$submodule")

  skill_records=()
  for record in "${records[@]}"; do
    IFS=$'\t' read -r record_type rel_path reason_or_name <<<"$record"
    if [[ "$record_type" == "SKIP" ]]; then
      add_skipped_skill "$submodule" "${skills_dir}/${rel_path}" "$reason_or_name"
    elif [[ "$record_type" == "SKILL" ]]; then
      skill_records+=("${rel_path}"$'\t'"${reason_or_name}")
    fi
  done

  if [[ ${#skill_records[@]} -eq 0 ]]; then
    continue
  fi

  printf "${C_CYAN}${C_BOLD}%s${C_RESET} (%d unique skills):\n" \
    "$submodule" "${#skill_records[@]}"

  for skill_record in "${skill_records[@]}"; do
    IFS=$'\t' read -r skill_rel_path skill_name <<<"$skill_record"
    total_unique+=1
    src_dir="${skills_dir}/${skill_rel_path}"
    src_file="$(skill_file "$src_dir")"

    # Route the skill
    target_dir="$(route_skill "$submodule" "$skill_name")"

    if [[ -z "$target_dir" ]]; then
      # Unmapped skill
      unmapped_count+=1
      unmapped_list+=("${submodule}/${skill_name}")
      add_action "$submodule" "$skill_name" "skip" "no route mapping for skill" "$src_dir" ""
      printf "  %-45s ${C_DIM}-> unmapped (manual review)${C_RESET}\n" \
        "$skill_name"
      continue
    fi

    target_path="${SKILLS_ROOT}/${target_dir}/${skill_name}"

    if hub_skill_exists "$target_dir" "$skill_name"; then
      # Already exists in workspace-hub
      already_exists+=1
      add_action "$submodule" "$skill_name" "skip" "already exists in workspace-hub" "$src_dir" "$target_path"
      printf "  %-45s -> ${C_DIM}%s/${C_RESET} ${C_GREEN}(exists)${C_RESET}\n" \
        "$skill_name" "$target_dir"

      # In diff mode, show differences
      if [[ "$MODE" == "diff" && -n "$src_file" ]]; then
        hub_file="$(skill_file "$target_path")"
        if [[ -n "$hub_file" ]]; then
          local_diff="$(diff -u "$hub_file" "$src_file" 2>/dev/null || true)"
          if [[ -n "$local_diff" ]]; then
            conflicts+=1
            printf "    ${C_YELLOW}^ content differs:${C_RESET}\n"
            echo "$local_diff" | head -30 | sed 's/^/    /'
            local_lines="$(echo "$local_diff" | wc -l)"
            if (( local_lines > 30 )); then
              printf "    ${C_DIM}... (%d more lines)${C_RESET}\n" \
                "$((local_lines - 30))"
            fi
            echo ""
          fi
        fi
      fi
    else
      # New skill to merge
      would_merge+=1
      add_action "$submodule" "$skill_name" "create" "skill does not exist in workspace-hub" "$src_dir" "$target_path"
      printf "  %-45s -> ${C_BOLD}%s/${C_RESET} ${C_YELLOW}(NEW)${C_RESET}\n" \
        "$skill_name" "$target_dir"

      if [[ "$MODE" == "apply" && -n "$src_file" ]]; then
        # Create target directory and copy
        if mkdir -p "$target_path" 2>/dev/null; then
          if cp "$src_file" "${target_path}/SKILL.md" 2>/dev/null; then
            merged+=1
            printf "    ${C_GREEN}-> copied${C_RESET} %s\n" \
              "${target_dir}/${skill_name}/SKILL.md"
          else
            errors+=1
            printf "    ${C_RED}-> copy failed${C_RESET}\n" >&2
          fi
        else
          errors+=1
          printf "    ${C_RED}-> mkdir failed${C_RESET}: %s\n" \
            "$target_path" >&2
        fi
      fi

      if [[ "$MODE" == "diff" && -n "$src_file" ]]; then
        printf "    ${C_CYAN}(new file, no diff to show)${C_RESET}\n"
      fi
    fi
  done

  echo ""
done

# ---------------------------------------------------------------------------
# Unmapped skills report
# ---------------------------------------------------------------------------
if [[ ${#unmapped_list[@]} -gt 0 ]]; then
  printf "${C_YELLOW}${C_BOLD}Unmapped skills (%d) — manual review needed:${C_RESET}\n" \
    "${#unmapped_list[@]}"
  for entry in "${unmapped_list[@]}"; do
    printf "  %s\n" "$entry"
  done
  echo ""
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "================================================================"
printf "${C_BOLD} Summary${C_RESET}\n"
echo "================================================================"
printf " Total unique skills:   %d\n" "$total_unique"
printf " Already in hub:        ${C_GREEN}%d${C_RESET}\n" "$already_exists"
printf " Would be merged:       ${C_YELLOW}%d${C_RESET}\n" "$would_merge"
printf " Unmapped:              ${C_DIM}%d${C_RESET}\n" "$unmapped_count"
printf " Skipped repos:         ${C_DIM}%d${C_RESET}\n" "$skipped_repo_count"
printf " Skipped skill dirs:    ${C_DIM}%d${C_RESET}\n" "$skipped_skill_count"

if [[ "$MODE" == "apply" ]]; then
  printf " Merged (copied):       ${C_GREEN}%d${C_RESET}\n" "$merged"
fi

if [[ "$MODE" == "diff" ]] && (( conflicts > 0 )); then
  printf " Content conflicts:     ${C_YELLOW}%d${C_RESET}\n" "$conflicts"
fi

if (( errors > 0 )); then
  printf " Errors:                ${C_RED}%d${C_RESET}\n" "$errors"
fi
echo ""

if [[ -n "$REPORT_FILE" ]]; then
  write_report
  printf "Wrote propagation report: %s\n" "$REPORT_FILE"
fi

case "$MODE" in
  dry-run)
    echo "(dry-run mode -- no files were modified)"
    echo "Use --apply to copy new skills, --diff to compare existing ones."
    ;;
  apply)
    printf "Merged %d skill(s) into %s\n" "$merged" "$SKILLS_ROOT"
    ;;
  diff)
    if (( conflicts > 0 )); then
      printf "%d skill(s) have content differences with the hub version.\n" \
        "$conflicts"
    else
      echo "All existing skills match their submodule sources."
    fi
    ;;
esac

# Exit non-zero if there were errors
(( errors > 0 )) && exit 1
exit 0
