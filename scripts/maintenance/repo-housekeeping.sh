#!/usr/bin/env bash
#
# repo-housekeeping.sh — Ecosystem-wide git housekeeping across all sibling repos.
#
# For every git repo found under --root (default: parent of workspace-hub), this:
#   1. COMMITS uncommitted work (onto a housekeeping branch if currently on main)
#   2. PUSHES topic branches to origin
#   3. Opens a PR to main for each branch ahead of main   (never auto-merges, never
#      pushes main — PR-for-everything model, per #2920 follow-on decision)
#   4. Prunes STALE state: branches merged into main (any age), pruneable worktrees,
#      and (optionally) untracked / ignored directories
#
# SAFETY MODEL
#   - DRY-RUN BY DEFAULT. Nothing is mutated without --apply. The dry-run prints
#     exactly what --apply would do.
#   - main / master is NEVER pushed and NEVER merged into locally. All integration
#     is via pull request, uniformly across protected and personal repos.
#   - Unmerged branches are never deleted.
#   - Untracked dirs are removed under --apply. IGNORED dirs (venvs, build, local
#     config) require the extra --prune-ignored flag, and a secret-file denylist
#     (.env, *.key, *.pem, auth.json, id_rsa, *secret*) is always preserved.
#   - Each repo is isolated: a failure in one repo is logged and the sweep continues.
#
# USAGE
#   scripts/maintenance/repo-housekeeping.sh [options]
#     --apply              Actually perform actions (default: dry-run / report only)
#     --root DIR           Directory whose git subdirs are swept (default: dirname of repo root)
#     --repos a,b,c        Limit to these repo names (default: all git subdirs)
#     --prune-ignored      Also remove git-ignored dirs (git clean -fdx, minus denylist)
#     --no-clean-dirs      Do NOT remove any untracked/ignored dirs (branches/worktrees only)
#     --no-pr              Skip PR creation (still commits/pushes branches)
#     --branch NAME        Housekeeping branch name for stray main-branch changes
#                          (default: housekeeping/YYYY-MM-DD)
#     --max-ahead N        Branches >N commits ahead are reported, not auto-PR'd (default 50)
#     --skip-branches RE   Regex of branch names to never auto-PR
#                          (default: backup/*, pre-rebase*, bare 4-6 digit year/month branches)
#     --pr-all             Override both guards: PR every ahead branch regardless
#     -h | --help          Show this help
#
# EXIT: 0 if the sweep completed (individual repo failures are non-fatal and summarized).

set -uo pipefail

# ── Options ───────────────────────────────────────────────────────────────────
APPLY=0
PRUNE_IGNORED=0
CLEAN_DIRS=1
MAKE_PR=1
ROOT=""
ONLY_REPOS=""
HK_BRANCH="housekeeping/$(date +%Y-%m-%d)"
MAX_AHEAD=50          # branches more than this many commits ahead are reported, not auto-PR'd
# Branch names that are archival/backup by convention — never auto-PR'd (regex, anchored per-branch).
SKIP_BRANCH_RE='^(backup/|wip/archive/)|pre-rebase|(^|/)[0-9]{4,6}$'

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)         APPLY=1 ;;
    --prune-ignored) PRUNE_IGNORED=1 ;;
    --no-clean-dirs) CLEAN_DIRS=0 ;;
    --no-pr)         MAKE_PR=0 ;;
    --root)          ROOT="${2:-}"; shift ;;
    --repos)         ONLY_REPOS="${2:-}"; shift ;;
    --branch)        HK_BRANCH="${2:-}"; shift ;;
    --max-ahead)     MAX_AHEAD="${2:-}"; shift ;;
    --skip-branches) SKIP_BRANCH_RE="${2:-}"; shift ;;
    --pr-all)        MAX_AHEAD=999999; SKIP_BRANCH_RE='^$' ;;  # override both guards
    -h|--help)       sed -n '2,45p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'

# Repo root → default sweep root is its parent (the sibling-repos directory).
REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || pwd)"
[[ -z "$ROOT" ]] && ROOT="$(dirname "$REPO_ROOT")"
GUARD="${REPO_ROOT}/scripts/lib/worktree_guard.py"  # #3143 deny-by-default worktree/branch ownership guard

# Secret-file denylist: never removed even under --prune-ignored.
SECRET_GLOBS=('.env' '.env.*' '*.key' '*.pem' 'auth.json' 'id_rsa' 'id_ed25519' '*secret*' '*.secret')

# ── Helpers ───────────────────────────────────────────────────────────────────
act() {
  # act "<description>" <command...> — run if --apply, else just narrate.
  local desc="$1"; shift
  if (( APPLY )); then
    echo -e "    ${GREEN}DO${NC}    ${desc}"
    "$@"
  else
    echo -e "    ${YELLOW}WOULD${NC} ${desc}"
  fi
}

main_branch_of() {
  # Resolve the repo's main branch name (origin/HEAD → main → master).
  local b
  b="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')"
  if [[ -z "$b" ]]; then
    for cand in main master; do
      git show-ref --verify --quiet "refs/heads/$cand" && { b="$cand"; break; }
    done
  fi
  echo "${b:-main}"
}

mid_operation() {
  # True if a rebase/merge/cherry-pick is in progress — skip such repos.
  local g; g="$(git rev-parse --git-dir 2>/dev/null)" || return 1
  [[ -d "$g/rebase-merge" || -d "$g/rebase-apply" || -f "$g/MERGE_HEAD" || -f "$g/CHERRY_PICK_HEAD" ]]
}

# ── Counters ──────────────────────────────────────────────────────────────────
declare -a SUMMARY=()
swept=0; committed=0; pushed=0; prs=0; branches_deleted=0; skipped=0

echo -e "${BOLD}${CYAN}=== repo-housekeeping ===${NC}"
echo "  Mode      : $( ((APPLY)) && echo 'APPLY (mutating)' || echo 'DRY-RUN (report only)')"
echo "  Sweep root: ${ROOT}"
echo "  PR mode   : $( ((MAKE_PR)) && echo 'open PRs for ahead branches' || echo 'disabled (--no-pr)')"
if (( CLEAN_DIRS )); then
  echo "  Prune dirs: untracked=$( ((APPLY)) && echo yes || echo 'dry' ) ignored=$( ((PRUNE_IGNORED)) && echo yes || echo no )"
else
  echo "  Prune dirs: DISABLED (--no-clean-dirs) — branches/worktrees only"
fi
echo "  HK branch : ${HK_BRANCH}"
command -v gh >/dev/null 2>&1 || { MAKE_PR=0; echo -e "  ${YELLOW}gh not found — PR creation disabled${NC}"; }
echo ""

# ── Discover repos ────────────────────────────────────────────────────────────
mapfile -t REPO_DIRS < <(
  for d in "$ROOT"/*/; do
    # Primary repos only: a .git DIRECTORY. A .git FILE is a linked worktree —
    # it shares refs/remote with its parent and is handled inside that repo's
    # `git worktree` pass below, so sweeping it standalone would double-process.
    [[ -d "$d/.git" ]] || continue
    name="$(basename "$d")"
    if [[ -n "$ONLY_REPOS" ]]; then
      [[ ",$ONLY_REPOS," == *",$name,"* ]] || continue
    fi
    echo "$d"
  done | sort
)

if [[ ${#REPO_DIRS[@]} -eq 0 ]]; then
  echo -e "${RED}No git repos found under ${ROOT}.${NC}"; exit 0
fi

# ── Per-repo sweep ────────────────────────────────────────────────────────────
for dir in "${REPO_DIRS[@]}"; do
  name="$(basename "$dir")"
  echo -e "${BOLD}── ${name}${NC}  (${dir})"
  swept=$((swept+1))
  pushd "$dir" >/dev/null || { echo -e "  ${RED}cannot enter${NC}"; continue; }

  # Guard: mid-operation or detached HEAD → report and skip mutations.
  if mid_operation; then
    echo -e "  ${YELLOW}SKIP: rebase/merge in progress${NC}"; SUMMARY+=("$name: skipped (mid-op)"); skipped=$((skipped+1)); popd >/dev/null; continue
  fi
  cur="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo '')"
  if [[ -z "$cur" ]]; then
    echo -e "  ${YELLOW}SKIP: detached HEAD${NC}"; SUMMARY+=("$name: skipped (detached)"); skipped=$((skipped+1)); popd >/dev/null; continue
  fi
  mainb="$(main_branch_of)"
  has_remote="$(git remote | head -1)"

  # 1) COMMIT uncommitted work ------------------------------------------------
  if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
    target="$cur"
    if [[ "$cur" == "$mainb" || "$cur" == "master" ]]; then
      target="$HK_BRANCH"
      echo "  on ${mainb} with changes → divert to ${target}"
      act "git checkout -b ${target}" git checkout -b "$target" 2>/dev/null || act "git checkout ${target}" git checkout "$target" 2>/dev/null
    fi
    echo "  uncommitted changes ($(git status --porcelain | wc -l | tr -d ' ') paths) on ${target}"
    act "git add -A" git add -A
    act "git commit -m 'chore(housekeeping): commit WIP $(date +%F)'" \
        git commit -q -m "chore(housekeeping): commit WIP $(date +%F)" -m "Auto-committed by repo-housekeeping.sh"
    committed=$((committed+1))
  else
    echo "  clean working tree"
  fi

  # 1b) COMMIT WIP in linked worktrees (shared refs flow into the PR loop below)
  while IFS= read -r wt; do
    [[ -z "$wt" || "$wt" == "$(pwd)" ]] && continue
    [[ -n "$(git -C "$wt" status --porcelain 2>/dev/null)" ]] || continue
    # #3143: only auto-commit WIP in a worktree housekeeping OWNS (.wt-owner marker).
    # NEVER sweep a foreign/active session's uncommitted work into a commit.
    if ! python3 "$GUARD" is-owned "$wt" repo-housekeeping 2>/dev/null; then
      echo "  worktree ${wt}: foreign/unowned — skipping WIP commit (#3143)"
      continue
    fi
    wbr="$(git -C "$wt" symbolic-ref --quiet --short HEAD 2>/dev/null || echo '?')"
    echo "  worktree ${wt} (${wbr}): uncommitted changes"
    act "git -C ${wt} add -A && commit" \
        bash -c "git -C '$wt' add -A && git -C '$wt' commit -q -m 'chore(housekeeping): commit WIP $(date +%F)'"
    committed=$((committed+1))
  done < <(git worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}')

  # 2+3) PUSH ahead branches + open PRs --------------------------------------
  # Integrate against the REMOTE main (origin/main) when available — a stale local
  # main would otherwise hide already-merged branches and trigger duplicate PRs.
  base="$mainb"
  if [[ -n "$has_remote" ]] && git rev-parse --verify --quiet "origin/${mainb}" >/dev/null 2>&1; then
    base="origin/${mainb}"
  fi
  if [[ -n "$has_remote" ]]; then
    while IFS= read -r br; do
      [[ -z "$br" || "$br" == "$mainb" || "$br" == "master" ]] && continue
      # Ahead of (remote) main?
      ahead="$(git rev-list --count "${base}..${br}" 2>/dev/null || echo 0)"
      [[ "$ahead" -gt 0 ]] || continue
      # Already merged (patch-id equivalent — catches squash/rebase merges where the
      # branch still shows commits "ahead")? Prune it instead of opening a stale PR.
      if [[ -z "$(git cherry "$base" "$br" 2>/dev/null | grep '^+')" ]]; then
        if [[ "$br" == "$cur" ]]; then
          echo -e "  branch ${br}: already merged into ${base} — ${YELLOW}current branch, not deleting${NC}"
        else
          echo -e "  branch ${br}: ${ahead} ahead but all commits already in ${base} — ${GREEN}merged; pruning${NC}"
          if python3 "$GUARD" safe-delete-branch "$br" 2>/dev/null; then
            act "git branch -D ${br}" git branch -D "$br" 2>/dev/null && branches_deleted=$((branches_deleted+1))
          else
            echo -e "  branch ${br}: checked out in a live worktree — ${YELLOW}skipping delete (#3143)${NC}"
          fi
        fi
        continue
      fi
      # Guard 1: archival/backup branch names → report only, never PR.
      if [[ "$br" =~ $SKIP_BRANCH_RE ]]; then
        echo -e "  branch ${br}: ${ahead} ahead — ${YELLOW}skipped (archival/backup name; --skip-branches / --pr-all to override)${NC}"; continue
      fi
      # Guard 2: very large diff → report only, never auto-PR (avoids monster PRs).
      if [[ "$ahead" -gt "$MAX_AHEAD" ]]; then
        echo -e "  branch ${br}: ${ahead} ahead — ${YELLOW}skipped (> --max-ahead=${MAX_AHEAD}; review manually or --pr-all)${NC}"; continue
      fi
      echo "  branch ${br}: ${ahead} commit(s) ahead of ${base}"
      act "git push -u origin ${br}" git push -u origin "$br" 2>/dev/null && pushed=$((pushed+1))
      if (( MAKE_PR )); then
        existing="$(gh pr list --head "$br" --json number --jq '.[0].number' 2>/dev/null || echo '')"
        if [[ -n "$existing" ]]; then
          echo "    PR #${existing} already open"
        else
          act "gh pr create --base ${mainb} --head ${br}" \
              gh pr create --base "$mainb" --head "$br" \
                --title "chore(housekeeping): merge ${br}" \
                --body "Opened by repo-housekeeping.sh. Review and merge — this script never auto-merges to ${mainb}." \
              && prs=$((prs+1))
        fi
      fi
    done < <(git for-each-ref --format='%(refname:short)' refs/heads/)
  else
    echo "  (no remote — skip push/PR)"
  fi

  # 4) PRUNE stale branches whose tip is an ancestor of (remote) main. The cherry
  # check above already pruned patch-equivalent (squash/rebase) merges; this catches
  # plain ancestor merges and is a no-op for branches handled above.
  while IFS= read -r mb; do
    mb="$(echo "$mb" | sed 's/^[* +]*//;s/ *$//')"
    [[ -z "$mb" || "$mb" == "$mainb" || "$mb" == "master" || "$mb" == "$cur" ]] && continue
    echo "  stale branch (merged into ${base}): ${mb}"
    if python3 "$GUARD" safe-delete-branch "$mb" 2>/dev/null; then
      act "git branch -d ${mb}" git branch -d "$mb" 2>/dev/null && branches_deleted=$((branches_deleted+1))
    else
      echo "  branch ${mb}: checked out in a live worktree — skipping delete (#3143)"
    fi
  done < <(git branch --merged "$base" 2>/dev/null)

  # 4b) PRUNE worktrees (merged or missing) -----------------------------------
  if git worktree list >/dev/null 2>&1; then
    act "git worktree prune -v" git worktree prune -v 2>/dev/null || true
  fi

  # 4c) PRUNE untracked dirs (under --apply), ignored dirs (--prune-ignored).
  #     Skipped entirely under --no-clean-dirs (branch/worktree cleanup only).
  if (( CLEAN_DIRS )); then
  untracked="$(git clean -nd 2>/dev/null | sed 's/^Would remove //')"
  if [[ -n "$untracked" ]]; then
    echo "  untracked dirs/files to remove:"; echo "$untracked" | sed 's/^/      /'
    act "git clean -fd" git clean -fd >/dev/null 2>&1
  fi
  if (( PRUNE_IGNORED )); then
    # Build exclude args for the secret denylist so secrets survive.
    excludes=(); for g in "${SECRET_GLOBS[@]}"; do excludes+=(-e "$g"); done
    ignored="$(git clean -ndx "${excludes[@]}" 2>/dev/null | sed 's/^Would remove //')"
    if [[ -n "$ignored" ]]; then
      echo -e "  ${YELLOW}ignored dirs/files to remove (secrets preserved):${NC}"; echo "$ignored" | sed 's/^/      /'
      act "git clean -fdx (denylist-protected)" git clean -fdx "${excludes[@]}" >/dev/null 2>&1
    fi
  fi
  fi  # CLEAN_DIRS

  SUMMARY+=("$name: ok (branch=${cur})")
  popd >/dev/null
  echo ""
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "${BOLD}${CYAN}================ Summary ================${NC}"
printf '  %-42s %s\n' "swept repos" "$swept"
printf '  %-42s %s\n' "repos committed" "$committed"
printf '  %-42s %s\n' "branches pushed" "$pushed"
printf '  %-42s %s\n' "PRs opened" "$prs"
printf '  %-42s %s\n' "merged branches deleted" "$branches_deleted"
printf '  %-42s %s\n' "repos skipped (mid-op / detached)" "$skipped"
echo ""
if (( APPLY )); then
  echo -e "${GREEN}Applied.${NC} Review opened PRs; nothing was merged to ${BOLD}main${NC} (PR-only by design)."
else
  echo -e "${YELLOW}Dry-run only — no changes made.${NC} Re-run with ${BOLD}--apply${NC} to act$( ((PRUNE_IGNORED)) || echo ', and --prune-ignored to also clear ignored dirs')."
fi
exit 0
