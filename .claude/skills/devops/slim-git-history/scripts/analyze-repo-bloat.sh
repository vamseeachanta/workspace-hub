#!/usr/bin/env bash
# ABOUTME: READ-ONLY git bloat analysis — .git size, pack/loose counts, and the
# ABOUTME: largest blob PATHS in history, each classified TRACKED (still in HEAD,
# ABOUTME: do NOT strip without confirmation) vs GONE (already deleted, safe to strip).
#
# Usage: analyze-repo-bloat.sh [repo-path] [top-N]
# Never writes to the repo. Heavy on large repos (walks all history) — give it time.
set -euo pipefail
REPO="${1:-.}"
TOPN="${2:-30}"
cd "$REPO"
git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo: $REPO" >&2; exit 1; }

echo "== repo: $(git rev-parse --show-toplevel) =="
echo "== .git size (shared object store; worktrees share it) =="
# In a worktree, --absolute-git-dir is the per-worktree gitdir (tiny); the real
# object store is the COMMON dir. Resolve it to an absolute path robustly.
GITCOMMON="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
[ -z "$GITCOMMON" ] && GITCOMMON="$(cd "$(git rev-parse --git-common-dir)" && pwd)"
du -sh "$GITCOMMON" 2>/dev/null || true
echo "== object counts (high count/many packs/loose => run 'git gc') =="
git count-objects -vH | grep -E '^count:|^size:|^in-pack:|^packs:|^size-pack:'

echo "== reachable vs on-disk — decides the WHOLE approach =="
# reachable = bytes of objects reachable from any ref (what a fresh mirror clone keeps).
# If that is much smaller than the on-disk store, the rest is UNREACHABLE cruft
# (e.g. from auto-sync 'git reset --hard' churn) — reclaimable by a prune with NO
# history rewrite and NO force-push. If reachable ~= on-disk, the bloat is in
# reachable history and needs filter-repo (steps 3-6).
REACH="$(git rev-list --disk-usage --objects --all 2>/dev/null || echo 0)"
DISK="$(du -sb "$GITCOMMON" 2>/dev/null | cut -f1)"
awk -v r="$REACH" -v d="${DISK:-0}" 'BEGIN{
  printf "  reachable=%.2f GiB   on-disk=%.2f GiB\n", r/1073741824, d/1073741824;
  if (d>0 && r < d*0.6)
    print "  >> VERDICT: large UNREACHABLE cruft. Reclaim with NO force-push:\n     git reflog expire --expire=now --all && git gc --prune=now\n     (plain git gc keeps cruft <2 weeks old). filter-repo only for any reachable remainder below.";
  else
    print "  >> VERDICT: bloat is mostly REACHABLE history -> needs filter-repo + force-push (steps 3-6).";
}'

TRACKED="$(mktemp)"; BLOBS="$(mktemp)"
trap 'rm -f "$TRACKED" "$BLOBS"' EXIT

# Current working-tree paths (quotePath off so paths match rev-list output).
git -c core.quotePath=false ls-files | sort -u > "$TRACKED"

# Total historical bytes per path across ALL refs (a path may have many blob
# versions over time; we sum them — that is what stripping the path reclaims).
git -c core.quotePath=false rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $4!="" { sz[$4]+=$3 } END { for (p in sz) print sz[p] "\t" p }' \
  | sort -rn > "$BLOBS"

echo
echo "== top $TOPN paths by total historical blob bytes =="
echo "   TRACKED = still in current tree (KEEP unless confirmed) | GONE = safe to strip"
awk -F'\t' -v topn="$TOPN" '
  NR==FNR { tracked[$0]=1; next }
  {
    size=$1; path=$2;
    tag = (path in tracked) ? "TRACKED" : "GONE";
    if (tag=="GONE") gone+=size; else kept+=size;
    if (n < topn) { printf "  %12d  %-7s  %s\n", size, tag, path; n++ }
  }
  END {
    printf "\n== reclaim estimate (upper bound; real reclaim is less after delta/dedup) ==\n";
    printf "  GONE (safe to strip):     %.2f GiB\n", gone/1073741824;
    printf "  TRACKED (kept in tree):   %.2f GiB\n", kept/1073741824;
  }
' "$TRACKED" "$BLOBS"

echo
echo "Next: review GONE paths above. To plan a rewrite, see SKILL.md step 3."
echo "The history rewrite + force-push is OPERATOR-ONLY (see SKILL.md step 4)."
