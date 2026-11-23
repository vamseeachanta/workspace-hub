# WRK-1059 Plan: Reference Documentation Quality Checks

## Context

WRK-1058 added `--docs` to `check-all.sh` covering: ruff D docstrings (warn-only),
README section validation (installation/usage/examples), and docs/ dir presence.

WRK-1059 extends this with three additional checks:
1. **Public symbol audit** (new `--api` flag): AST-enumerate public classes/functions per
   repo and compute docstring coverage % — surfaces API documentation gaps.
2. **docs/ structure** (extend `--docs`): beyond dir presence, verify index.md/rst and
   changelog files exist per repo.
3. **Build system detection** (extend `--docs`): detect Sphinx (docs/conf.py) or mkdocs
   (mkdocs.yml) or report "none".

## Files to Create / Modify

| File | Action | Notes |
|------|--------|-------|
| `scripts/quality/api-audit.py` | **Create** | AST-based public symbol + docstring scanner |
| `scripts/quality/check-all.sh` | **Modify** | Add `--api` flag; extend `--docs` sub-checks |
| `tests/quality/test_check_all.sh` | **Modify** | Add T15–T20 for new checks |

## Implementation Steps

### Step 1 — `scripts/quality/api-audit.py` (new, ~100 lines)

AST-walk a repo's `src/` directory:
- Collect all module-level and class-level public names (not starting with `_`)
- For each: check if the first statement in the body is a `ast.Constant` string (docstring)
- Output JSON: `{"repo": "<name>", "total": N, "with_docstring": M, "coverage_pct": X.X}`

CLI: `uv run --no-project python scripts/quality/api-audit.py <repo_name> <src_path>`

### Step 2 — Extend `check-all.sh --docs` (~30 lines added)

Add two new per-repo sub-checks called within the existing `if $OPT_DOCS` block:

**`check_docs_structure(repo_name, repo_path)`**
- Check for `docs/index.md` or `docs/index.rst` → PASS or WARN (missing)
- Check for `CHANGELOG.md`, `CHANGELOG.rst`, or `docs/changelog.md` → PASS or WARN
- Append to `DOCS_RESULTS[$repo_name]`

**`detect_build_system(repo_name, repo_path)`**
- `docs/conf.py` present → "build: sphinx"
- `mkdocs.yml` present → "build: mkdocs"
- Neither → "build: none"
- Append to `DOCS_RESULTS[$repo_name]`

### Step 3 — Add `--api` flag to `check-all.sh` (~30 lines added)

New flag `OPT_API=false` / `--api` in the parse loop.

**`run_api_audit(repo_name, repo_path)`**
- Finds `src/` dir within repo (skip if absent)
- Calls `uv run --no-project python scripts/quality/api-audit.py "$repo_name" "$src_path"`
- Parses output: prints `[repo_name] api: coverage X.X% (M/N symbols have docstrings)`
- Always warn-only (never fails build)

In the main loop: `if $OPT_API` → call `run_api_audit`.

check-all.sh line count after changes: ~335 (under 400L limit).

### Step 4 — Tests T15–T20 in `test_check_all.sh` (~60 lines added)

| Test | What it covers |
|------|----------------|
| T15 | `--docs` → `docs-index: WARN` when no index.md/rst |
| T16 | `--docs` → `docs-index: PASS` when index.md present |
| T17 | `--docs` → `changelog: WARN` when missing |
| T18 | `--docs` → `build: none` when no Sphinx/mkdocs files |
| T19 | `--api` → `api:` line appears in output |
| T20 | `--api` → `--help` mentions `--api` |

Tests use existing mock fixture pattern (temp dirs + mock `uv` binary with env var
`MOCK_API_AUDIT_OUTPUT` for T19).

test_check_all.sh line count after changes: ~308 (under 400L limit).

## Reuse

- Existing `run_ruff_docs()` pattern in check-all.sh → follow same warn-only idiom
- Existing mock `uv` binary pattern in test_check_all.sh → extend `MOCK_API_AUDIT_OUTPUT`
- `uv run --no-project python` — per python-runtime.md rules

## Verification

```bash
# Run new tests
bash tests/quality/test_check_all.sh

# Run against real repos
bash scripts/quality/check-all.sh --docs --api --repo assethold
bash scripts/quality/check-all.sh --docs --api  # all 5 repos

# Standalone api-audit.py
uv run --no-project python scripts/quality/api-audit.py assethold assethold/src
```

Expected outputs:
- `--docs` shows `docs-index: WARN`, `changelog: WARN`, `build: none` for most repos
- `--api` shows coverage % (e.g. `api: coverage 42.3% (87/206 symbols have docstrings)`)
- All tests pass (exit 0)
