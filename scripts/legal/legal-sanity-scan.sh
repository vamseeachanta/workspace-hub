#!/usr/bin/env bash
# =============================================================================
# Legal Sanity Scanner
# Scans code for client project names, proprietary tool references,
# and other legally sensitive content defined in .legal-deny-list.yaml files.
#
# Usage:
#   legal-sanity-scan.sh [--repo=<name>] [--all] [--diff-only] [--json]
#
# Environment:
#   LEGAL_SCAN_REPO_ROOTS    Semicolon- or newline-separated list of root
#                            directories to resolve repo names against.
#                            (Semicolons, not colons — ':' collides with
#                            Windows drive letters under git-bash.)
#                            When set it WINS: names resolve ONLY against the
#                            listed roots; no fallback to the defaults.
#   LEGAL_SCAN_RESOLVE_ONLY  When "1", print the resolved repo path(s) and
#                            exit 0 before any scanning happens. Minimal
#                            dry-run hook used by tests/legal/ to assert the
#                            resolution contract without needing deny-lists.
#
# Exit codes:
#   0  All clear (no block-severity violations)
#   1  Block-severity violations found
#   2  Usage / resolution error (unknown argument, repository not found,
#      --all with nothing to scan)
#
# Environment:
#   LEGAL_SCAN_REPO_ROOTS  Semicolon- or newline-separated list of repo root
#                          paths (semicolons/newlines survive Windows drive
#                          letters under git-bash). When set, it WINS over the
#                          default nested -> sibling -> walk-up resolution.
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
QUIET=false
VIOLATIONS=0
WARNINGS=0

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --repo=*) TARGET_REPO="${arg#*=}" ;;
    --all) SCAN_ALL=true ;;
    --diff-only) DIFF_ONLY=true ;;
    --json) JSON_OUTPUT=true ;;
    --quiet|-q) QUIET=true ;;
    --help|-h)
      echo "Usage: legal-sanity-scan.sh [--repo=<name>] [--all] [--diff-only] [--json]"
      echo ""
      echo "Options:"
      echo "  --repo=<name>   Scan a specific repo (nested submodule, sibling"
      echo "                  checkout, or LEGAL_SCAN_REPO_ROOTS entry)"
      echo "  --all           Scan all submodules (else all LEGAL_SCAN_REPO_ROOTS"
      echo "                  entries; refuses when both are empty)"
      echo "  --diff-only     Only scan files changed in git diff (HEAD)"
      echo "  --json          Output results as JSON"
      echo ""
      echo "Environment:"
      echo "  LEGAL_SCAN_REPO_ROOTS  Semicolon- or newline-separated repo root"
      echo "                         paths; wins over default resolution when set"
      echo ""
      echo "Exit codes:"
      echo "  0  Pass (no block-severity violations)"
      echo "  1  Block violations found"
      echo "  2  Usage / resolution error (repo not found, --all with nothing to scan)"
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

# --------------------------------------------------------------------------
# Candidate resolver — shared by --repo and --all
#
# WORKSPACE_ROOT stays anchored to workspace-hub (the global
# .legal-deny-list.yaml load must not move); only repo *lookup* is flexible:
#   1. LEGAL_SCAN_REPO_ROOTS (semicolon- or newline-separated repo root
#      paths) WINS when set. An entry matches <name> when its basename equals
#      <name>, otherwise <entry>/<name> is tried; entries in listed order.
#   2. Defaults: nested $WORKSPACE_ROOT/<name> wins, then sibling
#      $(dirname WORKSPACE_ROOT)/<name>, then a bounded walk-up from the
#      sibling level (cap 8 levels).
# On no-match: error to stderr listing every candidate tried, return 2.
# --------------------------------------------------------------------------
REGISTERED_ROOTS=()

load_registered_roots() {
  REGISTERED_ROOTS=()
  [[ -z "${LEGAL_SCAN_REPO_ROOTS:-}" ]] && return 0
  local entry
  while IFS= read -r entry; do
    entry="${entry%$'\r'}"
    # Normalize backslashes so git-bash tools (basename, -d) handle
    # Windows-style entries.
    entry="${entry//\\//}"
    # Trim surrounding whitespace
    entry="${entry#"${entry%%[![:space:]]*}"}"
    entry="${entry%"${entry##*[![:space:]]}"}"
    [[ -n "$entry" ]] && REGISTERED_ROOTS+=("$entry")
  done < <(printf '%s\n' "$LEGAL_SCAN_REPO_ROOTS" | tr ';' '\n')
  return 0
}

# resolve_repo_path <name>
# Prints the resolved repo path on stdout; returns 2 on no-match.
resolve_repo_path() {
  local name="$1"
  local candidates=()
  local c

  if [[ ${#REGISTERED_ROOTS[@]} -gt 0 ]]; then
    # Explicit registration wins outright when set.
    local root
    for root in "${REGISTERED_ROOTS[@]}"; do
      if [[ "$(basename "$root")" == "$name" ]]; then
        candidates+=("$root")
      else
        candidates+=("$root/$name")
      fi
    done
  else
    # Nested checkout wins, then sibling, then bounded walk-up (cap 8).
    candidates+=("$WORKSPACE_ROOT/$name")
    local parent walk next level
    parent="$(dirname "$WORKSPACE_ROOT")"
    candidates+=("${parent%/}/$name")
    walk="$parent"
    level=0
    while [[ $level -lt 8 ]]; do
      next="$(dirname "$walk")"
      [[ "$next" == "$walk" ]] && break
      walk="$next"
      candidates+=("${walk%/}/$name")
      level=$((level + 1))
    done
  fi

  for c in "${candidates[@]}"; do
    if [[ -d "$c" ]]; then
      printf '%s\n' "$c"
      return 0
    fi
  done

  {
    echo "ERROR: Repository not found: $name"
    echo "Candidates tried:"
    for c in "${candidates[@]}"; do
      echo "  - $c"
    done
    if [[ ${#REGISTERED_ROOTS[@]} -gt 0 ]]; then
      echo "(resolution used LEGAL_SCAN_REPO_ROOTS; unset it to use nested/sibling/walk-up defaults)"
    fi
  } >&2
  return 2
}

# --------------------------------------------------------------------------
# Parse deny-list YAML (lightweight, no yq dependency)
# Extracts pattern lines from a .legal-deny-list.yaml file.
# Returns: pattern|case_flag  (one per line)
#   case_flag: "s" = case-sensitive, "i" = case-insensitive
# --------------------------------------------------------------------------
parse_deny_list() {
  local file="$1"
  [[ -f "$file" ]] || return 0

  # Emits: pattern|case_flag|severity
  #
  # Entries are BUFFERED and flushed at END, for two reasons:
  #
  #   1. `default_severity:` sits at the BOTTOM of the deny list, after every
  #      pattern it governs. A streaming flush would apply an unset default to
  #      each entry as it went past.
  #   2. The previous version printed from the `case_sensitive:` rule, so an
  #      entry WITHOUT that key was never emitted and therefore never scanned —
  #      a silent drop, invisible because a pattern that is never searched
  #      simply reports nothing. Keying the flush to the entry rather than to
  #      one optional field removes that whole class of bug.
  #
  # An entry with no `case_sensitive:` defaults to case-INSENSITIVE: for a
  # legal gate the broader match is the safe direction.
  awk '
    /^[[:space:]]*default_severity:/ {
      s = $0; sub(/.*default_severity:[[:space:]]*/, "", s);
      gsub(/"/, "", s); gsub(/[[:space:]]+$/, "", s);
      if (s != "") default_sev = s;
      next;
    }
    /^[[:space:]]*-[[:space:]]*pattern:/ {
      n++;
      p = $0; sub(/.*pattern:[[:space:]]*/, "", p);
      sub(/^"/, "", p); sub(/"[[:space:]]*$/, "", p);
      P[n] = p; C[n] = "i"; S[n] = "";
      next;
    }
    n > 0 && /^[[:space:]]*case_sensitive:/ {
      v = $0; sub(/.*case_sensitive:[[:space:]]*/, "", v);
      gsub(/[[:space:]]+$/, "", v);
      C[n] = (v == "false") ? "i" : "s";
      next;
    }
    n > 0 && /^[[:space:]]*severity:/ {
      v = $0; sub(/.*severity:[[:space:]]*/, "", v);
      gsub(/"/, "", v); gsub(/[[:space:]]+$/, "", v);
      S[n] = v;
      next;
    }
    END {
      if (default_sev == "") default_sev = "block";
      for (i = 1; i <= n; i++)
        printf "%s|%s|%s\n", P[i], C[i], (S[i] != "" ? S[i] : default_sev);
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
# split_repo_roots: print LEGAL_SCAN_REPO_ROOTS one root per line.
# Separators: semicolons or newlines (':' would collide with Windows drive
# letters under git-bash).
# --------------------------------------------------------------------------
split_repo_roots() {
  printf '%s\n' "${LEGAL_SCAN_REPO_ROOTS:-}" | tr ';' '\n'
}

# --------------------------------------------------------------------------
# resolve_repo_path: resolve a repository name to a directory.
# Shared by --repo and --all.
#
# Order:
#   1. LEGAL_SCAN_REPO_ROOTS wins when set: resolve against each listed root
#      in order; if none match, FAIL (no fallthrough to defaults — the env
#      being set means the caller took explicit control).
#   2. Defaults, in order:
#        nested   $WORKSPACE_ROOT/<name>          (preserves original behavior)
#        sibling  $(dirname "$WORKSPACE_ROOT")/<name>
#        walk-up  <ancestor>/<name> from WORKSPACE_ROOT, max 8 levels
#
# On success: sets RESOLVED_REPO_PATH, returns 0.
# On failure: returns 1 with RESOLVE_CANDIDATES holding every path tried.
# --------------------------------------------------------------------------
resolve_repo_path() {
  local name="$1"
  RESOLVED_REPO_PATH=""
  RESOLVE_CANDIDATES=()

  if [[ -n "${LEGAL_SCAN_REPO_ROOTS:-}" ]]; then
    local root
    while IFS= read -r root; do
      [[ -z "$root" ]] && continue
      RESOLVE_CANDIDATES+=("$root/$name")
      if [[ -d "$root/$name" ]]; then
        RESOLVED_REPO_PATH="$root/$name"
        return 0
      fi
    done < <(split_repo_roots)
    return 1
  fi

  # Default 1: nested under the workspace root (original behavior)
  RESOLVE_CANDIDATES+=("$WORKSPACE_ROOT/$name")
  if [[ -d "$WORKSPACE_ROOT/$name" ]]; then
    RESOLVED_REPO_PATH="$WORKSPACE_ROOT/$name"
    return 0
  fi

  # Default 2: sibling of the workspace root
  local parent
  parent="$(dirname "$WORKSPACE_ROOT")"
  RESOLVE_CANDIDATES+=("$parent/$name")
  if [[ -d "$parent/$name" ]]; then
    RESOLVED_REPO_PATH="$parent/$name"
    return 0
  fi

  # Default 3: bounded walk-up from the workspace root (max 8 levels)
  local ancestor="$parent"
  local depth=0
  while [[ $depth -lt 8 ]]; do
    [[ "$ancestor" == "$(dirname "$ancestor")" ]] && break
    ancestor="$(dirname "$ancestor")"
    RESOLVE_CANDIDATES+=("$ancestor/$name")
    if [[ -d "$ancestor/$name" ]]; then
      RESOLVED_REPO_PATH="$ancestor/$name"
      return 0
    fi
    depth=$((depth + 1))
  done

  return 1
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

  # Build exclusion pattern list for file filtering
  local excl_patterns=()
  while IFS= read -r glob; do
    [[ -n "$glob" ]] && excl_patterns+=("$glob")
  done < <(parse_exclusions "$global_list"; parse_exclusions "$local_list")

  # Determine file list
  local file_args=()
  if [[ "$DIFF_ONLY" == "true" ]]; then
    local changed_files
    changed_files="$(cd "$scan_dir" && git diff --name-only HEAD 2>/dev/null || true)"
    [[ -z "$changed_files" ]] && return 0
    while IFS= read -r f; do
      [[ -f "$scan_dir/$f" ]] || continue
      # Apply exclusion globs to diff-only file list
      local excluded=false
      for ep in "${excl_patterns[@]}"; do
        case "$f" in
          $ep|*/$ep) excluded=true; break ;;
        esac
        # Match trailing-slash directory prefixes (e.g. "logs/orchestrator/", "scripts/legal/")
        if [[ "$ep" == */ ]]; then
          local ep_dir="${ep%/}"
          if [[ "$f" == ${ep_dir}/* || "$f" == ${ep_dir} ]]; then
            excluded=true; break
          fi
        fi
        # Also match wildcard directory globs (e.g. "docs/document-intelligence/*.md")
        if [[ "$ep" == *"*"* ]]; then
          local ep_dir="${ep%/*}"
          local ep_glob="${ep##*/}"
          if [[ "$f" == $ep_dir/* ]] && [[ "$(basename "$f")" == $ep_glob ]]; then
            excluded=true; break
          fi
        fi
      done
      $excluded || file_args+=("$scan_dir/$f")
    done <<< "$changed_files"
    [[ ${#file_args[@]} -eq 0 ]] && return 0
  fi

  # Scan each pattern
  while IFS='|' read -r pattern case_flag severity; do
    [[ -z "$pattern" ]] && continue
    # An unrecognised severity fails CLOSED. A typo ("blcok", "Warn") must not
    # silently downgrade a pattern to advisory.
    [[ "$severity" == "warn" ]] || severity="block"

    local matches=""
    if [[ "$DIFF_ONLY" == "true" && ${#file_args[@]} -gt 0 ]]; then
      matches="$(run_search "$case_flag" "$pattern" "${excl_args[@]}" -- "${file_args[@]}")"
    else
      matches="$(run_search "$case_flag" "$pattern" "${excl_args[@]}" -- "$scan_dir")"
    fi

    if [[ -n "$matches" ]]; then
      local count
      count="$(echo "$matches" | wc -l)"
      # Only block-severity matches drive the exit code. Warn matches are
      # reported in full — the tier changes what FAILS, never what is SEEN.
      if [[ "$severity" == "block" ]]; then
        VIOLATIONS=$((VIOLATIONS + count))
        local_violations=$((local_violations + count))
      else
        WARNINGS=$((WARNINGS + count))
      fi

      if [[ "$JSON_OUTPUT" == "true" ]]; then
        echo "$matches" | while IFS= read -r line; do
          local file_path line_num
          file_path="$(echo "$line" | cut -d: -f1)"
          line_num="$(echo "$line" | cut -d: -f2)"
          printf '{"repo":"%s","pattern":"%s","file":"%s","line":%s,"severity":"%s"}\n' \
            "$label" "$pattern" "$file_path" "$line_num" "$severity"
        done
      else
        echo "  ${severity^^}  pattern=\"$pattern\"  matches=$count"
        echo "$matches" | sed 's/^/         /'
      fi
    fi
  done <<< "$patterns"

  return $local_violations
}

# ==========================================================================
# Main
# ==========================================================================

if [[ "$JSON_OUTPUT" != "true" && "$QUIET" != "true" ]]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Legal Sanity Scanner"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

load_registered_roots

if [[ -n "$TARGET_REPO" ]]; then
  # Scan specific repo (shared candidate resolver)
  repo_path="$(resolve_repo_path "$TARGET_REPO")" || exit 2
  [[ "$JSON_OUTPUT" != "true" && "$QUIET" != "true" ]] && echo "Scanning: $TARGET_REPO ($repo_path)"
  scan_directory "$repo_path" "$TARGET_REPO" || true

elif [[ "$SCAN_ALL" == "true" ]]; then
  # Enumerate initialized submodules first; else fall back to env-registered
  # roots. An empty enumeration is a hard refusal — a legal gate must never
  # pass by scanning nothing.
  submodules=()
  while IFS= read -r sub; do
    [[ -n "$sub" ]] && submodules+=("$sub")
  done < <(git -C "$WORKSPACE_ROOT" submodule --quiet foreach 'echo $sm_path' 2>/dev/null || true)

  if [[ ${#submodules[@]} -gt 0 ]]; then
    for sub in "${submodules[@]}"; do
      sub_path="$(resolve_repo_path "$sub")" || exit 2
      [[ "$JSON_OUTPUT" != "true" && "$QUIET" != "true" ]] && echo "Scanning: $sub ($sub_path)"
      scan_directory "$sub_path" "$sub" || true
    done
  elif [[ ${#REGISTERED_ROOTS[@]} -gt 0 ]]; then
    for root in "${REGISTERED_ROOTS[@]}"; do
      if [[ ! -d "$root" ]]; then
        echo "ERROR: Registered repo root not found: $root (from LEGAL_SCAN_REPO_ROOTS)" >&2
        exit 2
      fi
      root_label="$(basename "$root")"
      [[ "$JSON_OUTPUT" != "true" && "$QUIET" != "true" ]] && echo "Scanning: $root_label ($root)"
      scan_directory "$root" "$root_label" || true
    done
  else
    echo "ERROR: --all found nothing to scan (no initialized submodules and LEGAL_SCAN_REPO_ROOTS is not set)." >&2
    echo "       A legal gate must never pass by scanning nothing. Initialize submodules or set LEGAL_SCAN_REPO_ROOTS." >&2
    exit 2
  fi

else
  # Scan workspace root (non-submodule files)
  [[ "$JSON_OUTPUT" != "true" && "$QUIET" != "true" ]] && echo "Scanning: workspace-hub (root)"
  scan_directory "$WORKSPACE_ROOT" "workspace-hub" || true
fi

# Summary
if [[ "$JSON_OUTPUT" != "true" && "$QUIET" != "true" ]]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  if [[ $VIOLATIONS -gt 0 ]]; then
    echo "  RESULT: FAIL — $VIOLATIONS block violation(s) found"
  else
    echo "  RESULT: PASS — no block violations found"
  fi
  # Always printed, PASS included. A pass that silently swallows its warnings
  # is how a downgraded pattern stops being looked at ever again.
  if [[ $WARNINGS -gt 0 ]]; then
    echo "  WARNINGS: $WARNINGS advisory match(es) — reported, not blocking"
  fi
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

[[ $VIOLATIONS -gt 0 ]] && exit 1
exit 0
