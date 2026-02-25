#!/usr/bin/env bash
# =============================================================================
# Legal Sanity Scanner
# Scans code for client project names, proprietary tool references,
# and other legally sensitive content defined in .legal-deny-list.yaml files.
#
# Usage:
#   legal-sanity-scan.sh [--repo=<name>] [--all] [--diff-only] [--json]
#
# Exit codes:
#   0  All clear (no block-severity violations)
#   1  Block-severity violations found
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# --------------------------------------------------------------------------
# Locate ripgrep — check PATH, common locations, fall back to grep
# --------------------------------------------------------------------------
RG_BIN=""
if command -v rg &>/dev/null; then
  RG_BIN="rg"
else
  # Check known vendor locations
  for candidate in \
    "$HOME/.npm-global/lib/node_modules/@anthropic-ai/claude-code/vendor/ripgrep/x64-linux/rg" \
    "$HOME/.cargo/bin/rg" \
    "/usr/local/bin/rg" \
    "/usr/bin/rg"; do
    if [[ -x "$candidate" ]]; then
      RG_BIN="$candidate"
      break
    fi
  done
fi

if [[ -z "$RG_BIN" ]]; then
  echo "WARNING: ripgrep (rg) not found — falling back to grep (slower)" >&2
fi

# --------------------------------------------------------------------------
# search_patterns: wrapper around rg or grep
#   Args: case_flag pattern [rg_extra_flags...] -- [files/dirs...]
# --------------------------------------------------------------------------
run_search() {
  local case_flag="$1"; shift
  local pattern="$1"; shift

  # Split extra flags and targets at "--"
  local extra_flags=()
  local targets=()
  local saw_sep=false
  for a in "$@"; do
    if [[ "$a" == "--" ]]; then saw_sep=true; continue; fi
    if $saw_sep; then targets+=("$a"); else extra_flags+=("$a"); fi
  done

  if [[ -n "$RG_BIN" ]]; then
    local rg_flags=("--no-heading" "--line-number" "--color" "never" "--no-ignore" "--max-filesize" "1M" "--fixed-strings")
    [[ "$case_flag" == "i" ]] && rg_flags+=("-i")
    rg_flags+=("${extra_flags[@]}")
    "$RG_BIN" "${rg_flags[@]}" "$pattern" "${targets[@]}" 2>/dev/null || true
  else
    local grep_flags=("-r" "-n" "--include=*" "-F")
    [[ "$case_flag" == "i" ]] && grep_flags+=("-i")
    grep "${grep_flags[@]}" "$pattern" "${targets[@]}" 2>/dev/null || true
  fi
}

# Defaults
TARGET_REPO=""
SCAN_ALL=false
DIFF_ONLY=false
JSON_OUTPUT=false
VIOLATIONS=0
WARNINGS=0

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --repo=*) TARGET_REPO="${arg#*=}" ;;
    --all) SCAN_ALL=true ;;
    --diff-only) DIFF_ONLY=true ;;
    --json) JSON_OUTPUT=true ;;
    --help|-h)
      echo "Usage: legal-sanity-scan.sh [--repo=<name>] [--all] [--diff-only] [--json]"
      echo ""
      echo "Options:"
      echo "  --repo=<name>   Scan a specific submodule"
      echo "  --all           Scan all submodules"
      echo "  --diff-only     Only scan files changed in git diff (HEAD)"
      echo "  --json          Output results as JSON"
      echo ""
      echo "Exit codes:"
      echo "  0  Pass (no block-severity violations)"
      echo "  1  Block violations found"
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

# --------------------------------------------------------------------------
# Parse deny-list YAML (lightweight, no yq dependency)
# Extracts pattern lines from a .legal-deny-list.yaml file.
# Returns: pattern|case_flag  (one per line)
#   case_flag: "s" = case-sensitive, "i" = case-insensitive
# --------------------------------------------------------------------------
parse_deny_list() {
  local file="$1"
  [[ -f "$file" ]] || return 0

  awk '
    /^[[:space:]]*- pattern:/ {
      gsub(/.*pattern:[[:space:]]*"?/, "");
      gsub(/"[[:space:]]*$/, "");
      pattern = $0;
    }
    /^[[:space:]]*case_sensitive:/ {
      gsub(/.*case_sensitive:[[:space:]]*/, "");
      gsub(/[[:space:]]*$/, "");
      if ($0 == "false") {
        print pattern "|i";
      } else {
        print pattern "|s";
      }
    }
  ' "$file"
}

# --------------------------------------------------------------------------
# Build exclusion args for ripgrep from the exclusions list
# --------------------------------------------------------------------------
parse_exclusions() {
  local file="$1"
  [[ -f "$file" ]] || return 0

  awk '
    /^exclusions:/ { in_exc=1; next }
    in_exc && /^[^[:space:]#-]/ { in_exc=0; next }
    in_exc && /^[[:space:]]*- / {
      val = $0;
      gsub(/^[[:space:]]*- "?/, "", val);
      gsub(/"[[:space:]]*$/, "", val);
      print val;
      next;
    }
  ' "$file"
}

# --------------------------------------------------------------------------
# Scan a single directory against merged patterns
# --------------------------------------------------------------------------
scan_directory() {
  local scan_dir="$1"
  local label="$2"
  local local_violations=0

  # Merge global + local deny lists
  local global_list="$WORKSPACE_ROOT/.legal-deny-list.yaml"
  local local_list="$scan_dir/.legal-deny-list.yaml"

  local patterns
  patterns="$(parse_deny_list "$global_list"; parse_deny_list "$local_list")"
  [[ -z "$patterns" ]] && return 0

  # Build exclusion globs
  local excl_args=()
  while IFS= read -r glob; do
    [[ -n "$glob" ]] && excl_args+=("--glob" "!$glob")
  done < <(parse_exclusions "$global_list"; parse_exclusions "$local_list")

  # Determine file list
  local file_args=()
  if [[ "$DIFF_ONLY" == "true" ]]; then
    local changed_files
    changed_files="$(cd "$scan_dir" && git diff --name-only HEAD 2>/dev/null || true)"
    [[ -z "$changed_files" ]] && return 0
    while IFS= read -r f; do
      [[ -f "$scan_dir/$f" ]] && file_args+=("$scan_dir/$f")
    done <<< "$changed_files"
    [[ ${#file_args[@]} -eq 0 ]] && return 0
  fi

  # Scan each pattern
  while IFS='|' read -r pattern case_flag; do
    [[ -z "$pattern" ]] && continue

    local matches=""
    if [[ "$DIFF_ONLY" == "true" && ${#file_args[@]} -gt 0 ]]; then
      matches="$(run_search "$case_flag" "$pattern" "${excl_args[@]}" -- "${file_args[@]}")"
    else
      matches="$(run_search "$case_flag" "$pattern" "${excl_args[@]}" -- "$scan_dir")"
    fi

    if [[ -n "$matches" ]]; then
      local count
      count="$(echo "$matches" | wc -l)"
      VIOLATIONS=$((VIOLATIONS + count))
      local_violations=$((local_violations + count))

      if [[ "$JSON_OUTPUT" == "true" ]]; then
        echo "$matches" | while IFS= read -r line; do
          local file_path line_num
          file_path="$(echo "$line" | cut -d: -f1)"
          line_num="$(echo "$line" | cut -d: -f2)"
          printf '{"repo":"%s","pattern":"%s","file":"%s","line":%s,"severity":"block"}\n' \
            "$label" "$pattern" "$file_path" "$line_num"
        done
      else
        echo "  BLOCK  pattern=\"$pattern\"  matches=$count"
        echo "$matches" | sed 's/^/         /'
      fi
    fi
  done <<< "$patterns"

  return $local_violations
}

# ==========================================================================
# Main
# ==========================================================================

if [[ "$JSON_OUTPUT" != "true" ]]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Legal Sanity Scanner"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

if [[ -n "$TARGET_REPO" ]]; then
  # Scan specific repo
  repo_path="$WORKSPACE_ROOT/$TARGET_REPO"
  if [[ ! -d "$repo_path" ]]; then
    echo "ERROR: Repository not found: $repo_path" >&2
    exit 2
  fi
  [[ "$JSON_OUTPUT" != "true" ]] && echo "Scanning: $TARGET_REPO"
  scan_directory "$repo_path" "$TARGET_REPO" || true

elif [[ "$SCAN_ALL" == "true" ]]; then
  # Scan all submodules
  while IFS= read -r sub; do
    [[ -z "$sub" ]] && continue
    sub_path="$WORKSPACE_ROOT/$sub"
    [[ "$JSON_OUTPUT" != "true" ]] && echo "Scanning: $sub"
    scan_directory "$sub_path" "$sub" || true
  done < <(git -C "$WORKSPACE_ROOT" submodule --quiet foreach 'echo $sm_path' 2>/dev/null)

else
  # Scan workspace root (non-submodule files)
  [[ "$JSON_OUTPUT" != "true" ]] && echo "Scanning: workspace-hub (root)"
  scan_directory "$WORKSPACE_ROOT" "workspace-hub" || true
fi

# Summary
if [[ "$JSON_OUTPUT" != "true" ]]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  if [[ $VIOLATIONS -gt 0 ]]; then
    echo "  RESULT: FAIL — $VIOLATIONS block violation(s) found"
  else
    echo "  RESULT: PASS — no violations found"
  fi
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

[[ $VIOLATIONS -gt 0 ]] && exit 1
exit 0
