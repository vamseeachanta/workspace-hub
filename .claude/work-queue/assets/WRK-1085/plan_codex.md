# WRK-1085 Plan — Codex Review

## Verdict: MAJOR

## Blocking Issues

### 1. Tracked generated file + hook-driven rebuilds = worktree churn
`config/search/symbol-index.jsonl` is committed but also rebuilt from `post-merge`.
Every rebuild will dirty the working tree and cause merge noise.
**Fix**: gitignore the index or add `.cache/search/` to .gitignore.

### 2. Scope mismatch: mission says "all repos", plan hardcodes 5
Mission: "across all repos". Plan: 5 hardcoded tier-1 repos only.
Silent misses for any repo not in the hardcoded list.
**Fix**: Narrow mission/AC language to "selected tier-1 repos" OR drive discovery
from a canonical workspace registry.

### 3. Freshness under-specified
`post-merge` alone misses local edits, rebases, checkouts from other repo roots.
`find-symbol` can serve stale results with no signal to caller.
**Fix**: Add freshness check (index mtime vs src/ mtime) with warn/rebuild path.

### 4. Test gaps
Missing: duplicate symbol names across repos, deterministic output order,
jq-absent and rg-absent paths, unchanged-merge no-op, stale-index detection.

## Suggestions
- Move index to untracked cache or explicitly gitignore
- Use canonical repo registry (e.g., TIER1_REPOS from a config file)
- Add freshness check to find-symbol.sh
- Expand test suite for fallback paths
