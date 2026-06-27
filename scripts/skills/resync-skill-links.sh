#!/usr/bin/env bash
# resync-skill-links.sh — verify (REPORT, default) + guard-gated re-sync (--apply) of the
# shared-skill links propagate-ecosystem.sh creates across ecosystem repos (#3251, epic #3248).
#
# REPORT mode (default) mutates NOTHING. It re-discovers every ecosystem repo (nested + flat-sibling
# layouts) and classifies each shared-skill link's WORKING-TREE state into one of:
#   HEALTHY            — link resolves to the canonical _internal/<dir> template
#   DANGLING           — symlink present but target unresolved / wrong (rotted link)
#   FLATTENED          — symlink materialized as a regular text file (Windows core.symlinks=false)
#   MISSING            — nothing there (new repo / never propagated)
#   MODIFIED-REAL-DIR  — a real dir whose content diverges from the template (benign, never auto-fixed)
#   TEMPLATE-ABSENT    — a SHARED_SKILL_DIRS entry with no _internal/<dir> template (surfaced, not healthy)
# It writes .claude/state/skill-link-health-<machine>.json with per-state COUNTS + a worst_state.
#
# --apply (guard-gated) re-propagates the repairable cells via propagate-ecosystem.sh --skills-only.
#
# Working-tree basis (NOT git tree): the shared dirs are gitignored, so link health can only be
# assessed against the filesystem.
#
# Usage: bash scripts/skills/resync-skill-links.sh [--apply] [--dry-run] [--only <repo>]
#                                                  [--machine <label>] [--json] [--verbose]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
# WORKSPACE_HUB env override is the test seam (sandbox); else resolve from the script location.
WS_HUB="${WORKSPACE_HUB:-$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)}"
STATE_DIR="$WS_HUB/.claude/state"
INTERNAL_DIR="$WS_HUB/.claude/skills/_internal"
PROPAGATE="$WS_HUB/scripts/propagate-ecosystem.sh"

# Discovery contract — replicated inline from propagate-ecosystem.sh (which CANNOT be sourced: it
# ends with both `main "$@"` and `exit 0`, either of which would hijack/terminate this script).
SHARED_SKILL_DIRS=("guidelines" "meta" "workflows")
EXCLUDE_DIRS=(".claude" "scripts" "specs" "docs" "node_modules" ".git"
              "_archive" "_temp" "config" "coordination" "data" "docker"
              "examples" "logs" "modules" "monitoring-dashboard" "reports"
              "skills" "src" "templates" "tests" "flow-nexus" "ruv-swarm" "claude-flow")

OPT_APPLY=false; OPT_DRY_RUN=false; OPT_ONLY=""; OPT_MACHINE=""; OPT_JSON=false; OPT_VERBOSE=false

usage() {
  cat <<'EOF'
Usage: bash scripts/skills/resync-skill-links.sh [OPTIONS]

Verify (REPORT, default) or re-sync (--apply) shared-skill links across ecosystem repos.

Options:
  --apply          Re-propagate repairable links via propagate-ecosystem.sh --skills-only (guard-gated)
  --dry-run        Under --apply, make no changes (no-op preview)
  --only <repo>    Limit to a single ecosystem repo (by directory name)
  --machine <lbl>  Override the machine label (else derived; EQ_MACHINE env also honored)
  --json           Also print the state JSON to stdout
  --verbose        Show the per-cell classification table
  --help, -h       Show this help
EOF
}

parse_arguments() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --apply)   OPT_APPLY=true;;
      --dry-run) OPT_DRY_RUN=true;;
      --only)    OPT_ONLY="${2:-}"; shift;;
      --machine) OPT_MACHINE="${2:-}"; shift;;
      --json)    OPT_JSON=true;;
      --verbose) OPT_VERBOSE=true;;
      --help|-h) usage; exit 0;;
      *) echo "Unknown option: $1" >&2; usage; exit 1;;
    esac; shift
  done
}

# ── platform + machine label ────────────────────────────────────────────────
# OS detection mirrors collect-equality.sh; EQ_*_OVERRIDE are TEST SEAMS ONLY (they affect the
# derived LABEL, never graded data — EQ_MACHINE already fully overrides the label).
case "$(uname -s 2>/dev/null)" in
  Linux) OS="linux";; Darwin) OS="macos";; MINGW*|MSYS*|CYGWIN*) OS="windows";; *) OS="unknown";;
esac
[[ -n "${EQ_OS_OVERRIDE:-}" ]] && OS="$EQ_OS_OVERRIDE"
HOST="${EQ_HOST_OVERRIDE:-$(hostname 2>/dev/null | tr '[:upper:]' '[:lower:]')}"
PLATFORM="unix"; [[ "$OS" == "windows" ]] && PLATFORM="windows"

MACHINE=""
resolve_machine() {
  # Reuses the EXACT mapping collect-equality.sh uses, INCLUDING its fail-closed exit-1 for an
  # unrecognized Windows host (an unknown Windows box must NOT silently get a default label).
  # Set as a global (no command-substitution subshell) so the exit-1 actually terminates the script.
  if [[ -n "$OPT_MACHINE" ]]; then MACHINE="$OPT_MACHINE"; return; fi
  if [[ -n "${EQ_MACHINE:-}" ]]; then MACHINE="$EQ_MACHINE"; return; fi
  case "$HOST" in
    ace-linux-1*) MACHINE="dev-primary";;
    ace-linux-2*) MACHINE="dev-secondary";;
    *macbook*)    MACHINE="macbook-portable";;
    ace-win-1*|licensed-win-1*|acma-ansys05*) MACHINE="ace-win-1";;
    ace-win-2*|licensed-win-2*|acma-ws014*)   MACHINE="ace-win-2";;
    *)
      if [[ "$OS" == "windows" ]]; then
        echo "resync-skill-links.sh: unknown Windows host '$HOST'; pass --machine ace-win-1 or ace-win-2" >&2
        exit 1
      fi
      MACHINE="${HOST:-unknown}";;
  esac
}

# ── filesystem classification helpers ───────────────────────────────────────
is_link() {
  # symlink (unix) or junction+marker (windows) — minimal replica of propagate's is_link.
  local path="$1"
  if [[ "$PLATFORM" == "windows" ]]; then
    local marker; marker="$(dirname "$path")/.$(basename "$path")-link-marker"
    [[ -d "$path" && -f "$marker" ]] && return 0
    [[ -d "$path" ]] && fsutil reparsepoint query "$path" >/dev/null 2>&1 && return 0
    return 1
  fi
  [[ -L "$path" ]]
}

_strip_fm() {
  # Echo a file's body with a leading YAML frontmatter block (--- ... ---) removed, matching
  # propagate's directory_matches_template (internal copies carry metadata headers).
  awk 'NR==1 && $0=="---"{infm=1; next} infm && $0=="---"{infm=0; next} !infm{print}' "$1"
}

directory_matches_template() {
  # 0 if every template file is present in sub_dir with matching content (.md compared frontmatter-blind).
  local sub="$1" tmpl="$2" f rel
  [[ -d "$sub" && -d "$tmpl" ]] || return 1
  while IFS= read -r f; do
    rel="${f#"$tmpl"/}"
    [[ -f "$sub/$rel" ]] || return 1
    if [[ "$f" == *.md ]]; then
      [[ "$(_strip_fm "$f")" == "$(_strip_fm "$sub/$rel")" ]] || return 1
    else
      cmp -s "$f" "$sub/$rel" || return 1
    fi
  done < <(find "$tmpl" -type f)
  return 0
}

classify() {
  # classify <link_path> <target_dir> -> echoes one state token
  local link="$1" target="$2"
  if [[ ! -d "$target" ]]; then echo "TEMPLATE-ABSENT"; return; fi
  if is_link "$link"; then
    if [[ "$PLATFORM" == "windows" ]]; then echo "HEALTHY"; return; fi
    if [[ -d "$link" && "$(realpath "$link" 2>/dev/null)" == "$(realpath "$target" 2>/dev/null)" ]]; then
      echo "HEALTHY"; return
    fi
    echo "DANGLING"; return
  fi
  if [[ -e "$link" && ! -d "$link" ]]; then echo "FLATTENED"; return; fi
  if [[ -d "$link" ]]; then
    directory_matches_template "$link" "$target" && echo "HEALTHY" || echo "MODIFIED-REAL-DIR"
    return
  fi
  echo "MISSING"
}

# ── repo discovery (inline replica of propagate's discover_submodules) ───────
discover_repos() {
  local hub_name hub_parent dir_name repo_dir ex excluded
  hub_name="$(basename "$WS_HUB")"
  hub_parent="$(dirname "$WS_HUB")"
  {
    for repo_dir in "$WS_HUB"/*/;     do echo "$repo_dir"; done
    for repo_dir in "$hub_parent"/*/; do echo "$repo_dir"; done
  } | while IFS= read -r repo_dir; do
    [[ ! -d "$repo_dir" ]] && continue
    dir_name="$(basename "$repo_dir")"
    [[ "$dir_name" == "$hub_name" ]] && continue
    excluded=false
    for ex in "${EXCLUDE_DIRS[@]}"; do [[ "$dir_name" == "$ex" ]] && excluded=true && break; done
    [[ "$excluded" == "true" ]] && continue
    # Skip git WORKTREES (but NOT submodules). A worktree's .git is a FILE whose gitdir points into a
    # ".../worktrees/<name>" path; a submodule's .git file points into ".../modules/<name>". We only
    # drop worktrees — they carry .claude/skills/ as transient checkouts, are not stable propagation
    # targets, and counting their un-linked shared dirs as MISSING would keep the cell permanently red
    # on every box with worktrees in flight. (propagate-ecosystem.sh may still touch a worktree
    # idempotently under --apply; we simply don't audit worktree link health here.)
    if [[ -f "$repo_dir/.git" ]] && grep -q '/worktrees/' "$repo_dir/.git" 2>/dev/null; then continue; fi
    [[ -d "$repo_dir/.claude/skills" ]] && echo "${repo_dir%/}"
  done | sort -u
}

# ── allowlist (repos that legitimately carry no shared-skill links) ──────────
read_allowlist() {
  # EQ_SKILL_LINK_ALLOWLIST (space/newline separated) is the test seam; else best-effort read of
  # harness-config.yaml::expected_skill_link_divergence (key may not exist yet — fail-soft to empty).
  if [[ -n "${EQ_SKILL_LINK_ALLOWLIST+x}" ]]; then
    printf '%s\n' ${EQ_SKILL_LINK_ALLOWLIST}
    return
  fi
  local cfg="$WS_HUB/scripts/readiness/harness-config.yaml"
  [[ -f "$cfg" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  python3 - "$cfg" <<'PY' 2>/dev/null || true
import sys
try:
    import yaml
except Exception:
    sys.exit(0)
try:
    data = yaml.safe_load(open(sys.argv[1])) or {}
except Exception:
    sys.exit(0)
allow = data.get("expected_skill_link_divergence") or []
if isinstance(allow, list):
    for a in allow:
        print(a)
PY
}

# ── classification pass (sets the count globals) ─────────────────────────────
C_HEALTHY=0; C_MISSING=0; C_DANGLING=0; C_FLATTENED=0; C_MODIFIED=0; C_TEMPLATE_ABSENT=0
REPOS_TOTAL=0
declare -a MISSING_REPOS=()       # basenames of repos with >=1 MISSING cell
declare -a TABLE=()               # verbose per-cell rows

run_classification() {
  C_HEALTHY=0; C_MISSING=0; C_DANGLING=0; C_FLATTENED=0; C_MODIFIED=0; C_TEMPLATE_ABSENT=0
  REPOS_TOTAL=0; MISSING_REPOS=(); TABLE=()
  local repo repo_name shared link target state repo_has_missing
  while IFS= read -r repo; do
    [[ -z "$repo" ]] && continue
    repo_name="$(basename "$repo")"
    if [[ -n "$OPT_ONLY" && "$repo_name" != "$OPT_ONLY" ]]; then continue; fi
    REPOS_TOTAL=$((REPOS_TOTAL + 1))
    repo_has_missing=false
    for shared in "${SHARED_SKILL_DIRS[@]}"; do
      link="$repo/.claude/skills/$shared"
      target="$INTERNAL_DIR/$shared"
      state="$(classify "$link" "$target")"
      case "$state" in
        HEALTHY)           C_HEALTHY=$((C_HEALTHY + 1));;
        MISSING)           C_MISSING=$((C_MISSING + 1)); repo_has_missing=true;;
        DANGLING)          C_DANGLING=$((C_DANGLING + 1));;
        FLATTENED)         C_FLATTENED=$((C_FLATTENED + 1));;
        MODIFIED-REAL-DIR) C_MODIFIED=$((C_MODIFIED + 1));;
        TEMPLATE-ABSENT)   C_TEMPLATE_ABSENT=$((C_TEMPLATE_ABSENT + 1));;
      esac
      TABLE+=("$(printf '%-22s %-10s %s' "$repo_name" "$shared" "$state")")
    done
    [[ "$repo_has_missing" == "true" ]] && MISSING_REPOS+=("$repo_name")
  done < <(discover_repos)
}

# ── JSON assembly (counts/bools/basenames only — no abs paths, no tokens) ────
json_escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

compute_unexpected_missing() {
  # echo basenames of MISSING repos NOT in the allowlist, one per line
  local allow repo a hit
  allow="$(read_allowlist)"
  for repo in "${MISSING_REPOS[@]:-}"; do
    [[ -z "$repo" ]] && continue
    hit=false
    while IFS= read -r a; do [[ -n "$a" && "$a" == "$repo" ]] && { hit=true; break; }; done <<< "$allow"
    [[ "$hit" == "false" ]] && echo "$repo"
  done
}

worst_state() {
  local s
  for s in DANGLING FLATTENED MISSING MODIFIED-REAL-DIR TEMPLATE-ABSENT; do
    case "$s" in
      DANGLING)          [[ $C_DANGLING -gt 0 ]] && { echo "$s"; return; };;
      FLATTENED)         [[ $C_FLATTENED -gt 0 ]] && { echo "$s"; return; };;
      MISSING)           [[ $C_MISSING -gt 0 ]] && { echo "$s"; return; };;
      MODIFIED-REAL-DIR) [[ $C_MODIFIED -gt 0 ]] && { echo "$s"; return; };;
      TEMPLATE-ABSENT)   [[ $C_TEMPLATE_ABSENT -gt 0 ]] && { echo "$s"; return; };;
    esac
  done
  echo "HEALTHY"
}

build_json() {
  local repairable unexpected arr first u worst stamp
  repairable=$((C_MISSING + C_DANGLING + C_FLATTENED))
  worst="$(worst_state)"
  stamp="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
  arr="["; first=1
  while IFS= read -r u; do
    [[ -z "$u" ]] && continue
    [[ $first -eq 1 ]] && first=0 || arr+=", "
    arr+="\"$(json_escape "$u")\""
  done < <(compute_unexpected_missing)
  arr+="]"
  cat <<EOF
{
  "machine": "$(json_escape "$MACHINE")",
  "audited_at": "$stamp",
  "platform": "$PLATFORM",
  "repos_total": $REPOS_TOTAL,
  "healthy": $C_HEALTHY,
  "missing": $C_MISSING,
  "dangling": $C_DANGLING,
  "flattened": $C_FLATTENED,
  "modified_real_dir": $C_MODIFIED,
  "template_absent": $C_TEMPLATE_ABSENT,
  "repairable": $repairable,
  "unexpected_missing_repos": $arr,
  "worst_state": "$worst",
  "schema_version": 1
}
EOF
}

write_state() {
  mkdir -p "$STATE_DIR"
  build_json > "$STATE_DIR/skill-link-health-$MACHINE.json"
}

print_report() {
  local repairable; repairable=$((C_MISSING + C_DANGLING + C_FLATTENED))
  if [[ "$OPT_VERBOSE" == "true" ]]; then
    printf '%s\n' "${TABLE[@]:-}"
    echo ""
  fi
  printf 'skill-link-health [%s]: repos=%d healthy=%d missing=%d dangling=%d flattened=%d modified=%d template-absent=%d (repairable=%d, worst=%s)\n' \
    "$MACHINE" "$REPOS_TOTAL" "$C_HEALTHY" "$C_MISSING" "$C_DANGLING" "$C_FLATTENED" \
    "$C_MODIFIED" "$C_TEMPLATE_ABSENT" "$repairable" "$(worst_state)"
}

guard_ok() {
  # Never let --apply run blind in a bad state.
  GUARD_REASON=""
  if [[ ! -d "$INTERNAL_DIR" ]]; then GUARD_REASON="_internal/ template root absent"; return 1; fi
  if [[ ! -f "$PROPAGATE" ]]; then GUARD_REASON="propagate-ecosystem.sh not found"; return 1; fi
  return 0
}

main() {
  parse_arguments "$@"
  resolve_machine

  run_classification
  write_state
  print_report
  [[ "$OPT_JSON" == "true" ]] && build_json

  if [[ "$OPT_APPLY" != "true" ]]; then
    return 0
  fi

  local repairable; repairable=$((C_MISSING + C_DANGLING + C_FLATTENED))
  if [[ $repairable -eq 0 ]]; then
    echo "apply: nothing to repair"
    return 0
  fi
  if ! guard_ok; then
    echo "apply: guard blocked apply ($GUARD_REASON) — no changes made"
    return 0
  fi
  if [[ "$OPT_DRY_RUN" == "true" ]]; then
    echo "apply: --dry-run — would re-propagate $repairable repairable cell(s); no changes made"
    return 0
  fi

  echo "apply: re-propagating $repairable repairable cell(s) via propagate-ecosystem.sh --skills-only"
  if [[ -n "$OPT_ONLY" ]]; then
    bash "$PROPAGATE" --skills-only --only "$OPT_ONLY" || true
  else
    bash "$PROPAGATE" --skills-only || true
  fi
  run_classification
  write_state
  print_report
  return 0
}

main "$@"
