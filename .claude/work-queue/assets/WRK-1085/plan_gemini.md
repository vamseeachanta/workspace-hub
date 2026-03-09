# WRK-1085 Plan — Gemini Review

## Verdict: MAJOR

## Blocking Issues

### 1. Python-only AST walker misses other languages
Workspace has JS/TS files; Python-only AST walker silently misses them.
**Scoped response**: This WRK targets tier-1 Python repos only (explicitly Python).
Polyglot support is a follow-on WRK. Mission language should say "Python symbols".

### 2. Generated index in config/ (not cache)
`config/search/symbol-index.jsonl` is generated and will be accidentally committed.
Should live in an untracked cache location.
**Fix**: Add to .gitignore; rebuild on demand.

### 3. TDD violation
Plan puts tests last (Phase 5). Tests must come before or concurrently with
each implementation phase per workspace TDD rules.
**Note**: Implementation was already done. For future WRKs, tests first.

### 4. Hook insufficiency
`post-merge` alone is insufficient for freshness during active development.
Need `post-checkout` and `post-commit` hooks, or stale-index detection.
**Fix**: Add freshness check (mtime comparison) to find-symbol.sh.
