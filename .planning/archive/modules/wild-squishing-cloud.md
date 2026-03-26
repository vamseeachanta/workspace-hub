# WRK-1085 Plan: Cross-Repo Search Indexing

## Context
Agents repeatedly run 3–5 Glob/Grep rounds to answer "where is X implemented?" across tier-1 repos.
A pre-built symbol index answers in one lookup. This plan adds a ripgrep wrapper for pattern search
and a Python AST symbol index for fast structural queries.

## Deliverables
1. `scripts/search/build-symbol-index.py` — AST walker, writes `config/search/symbol-index.jsonl`
2. `scripts/search/find-symbol.sh` — index lookup, <1s, no AST at query time
3. `scripts/search/cross-repo-search.sh` — ripgrep wrapper with ranked output (src > tests > docs)
4. Hook extension: `scripts/hooks/post-merge` — conditional rebuild when src/ changes
5. `tests/search/test-symbol-index.sh` — integration tests (≥6 cases)

## Existing patterns to reuse
- `scripts/readiness/build-specs-index.py` — direct model (walks repos, extracts metadata, writes YAML)
- `scripts/setup/install-all-hooks.sh` — copies `scripts/hooks/*` → `.git/hooks/`; post-merge source is `scripts/hooks/post-merge`
- `jq` at `/usr/bin/jq` — available for JSON filtering in shell scripts
- `ripgrep (rg)` — NOT installed; `grep -r` fallback required

## Tier-1 repos and src roots
| repo | submodule path | src root |
|------|----------------|----------|
| assethold | assethold/ | assethold/src/ |
| assetutilities | assetutilities/ | assetutilities/src/ |
| digitalmodel | digitalmodel/ | digitalmodel/src/ |
| OGManufacturing | OGManufacturing/ | OGManufacturing/src/ |
| worldenergydata | worldenergydata/ | worldenergydata/src/ |

## Symbol index schema (JSONL)
```
{"symbol": "Engine", "kind": "class", "repo": "assethold", "file": "assethold/src/assethold/engine.py", "line": 12}
{"symbol": "engine", "kind": "function", "repo": "assetutilities", "file": "assetutilities/src/assetutilities/engine.py", "line": 28}
{"symbol": "GRAVITY_MS2", "kind": "constant", "repo": "assetutilities", "file": "...", "line": 5}
```
File paths are relative to workspace-hub root.

## Phase 1 — build-symbol-index.py

```
build_symbol_index(repos_config) → symbol-index.jsonl   # walk repos, emit one JSONL per symbol
  1. For each repo in TIER1_REPOS (dict: name → src_root):
     a. Walk src_root recursively, select *.py files (skip __pycache__)
     b. Try ast.parse(source); except SyntaxError → log warning, continue
     c. Walk top-level AST nodes only (body of ast.Module):
        - ClassDef  → emit kind=class
        - FunctionDef / AsyncFunctionDef → emit kind=function
        - Assign where single target.id matches r'^[A-Z][A-Z0-9_]{2,}$' → emit kind=constant
     d. Also walk nested ClassDef bodies for method FunctionDef (kind=method)
  2. Write each record as JSON line to config/search/symbol-index.jsonl (create dir if absent)
  3. Print: "Indexed N symbols from M files across K repos"

emit_symbol(symbol, kind, repo, src_root, filepath, line) → dict
  1. rel_file = filepath relative to REPO_ROOT
  2. return {"symbol": symbol, "kind": kind, "repo": repo, "file": rel_file, "line": line}
```

## Phase 2 — find-symbol.sh

```
find_symbol(name, [kind], [repo]) → matching lines or "Symbol not found"
  1. Check SYMBOL_INDEX exists; else: error "Run build-symbol-index.py first"
  2. Build jq filter:  .symbol == $name  (exact match; add .kind/.repo if flags given)
  3. Stream SYMBOL_INDEX through jq; format: repo:file:line (kind)
  4. Fallback if jq absent: grep -F "\"$name\"" SYMBOL_INDEX | python3 -c "parse + format"
  5. If zero results → print "Symbol not found: $name" >&2; exit 1
```

## Phase 3 — cross-repo-search.sh

```
cross_repo_search(pattern, [type], [repo]) → ranked results
  1. Detect: USE_RG=true if which rg; else USE_RG=false (grep -r fallback, warn)
  2. Build SEARCH_REPOS list (all 5 if no --repo; else filter)
  3. For rank_dir in [src, tests, docs]:
     For each repo in SEARCH_REPOS:
       dir = repo_path/rank_dir (skip if absent)
       run: rg --no-heading -n --glob "*.{type}" pattern dir  (or grep equivalent)
       prefix each line: "repo:filepath:line:match"
  4. Output src_results first, then tests_results, then docs_results
  5. If no matches: "No matches found for: pattern"
```

## Phase 4 — post-merge hook extension

Edit `scripts/hooks/post-merge` (source file; `install-all-hooks.sh` copies to `.git/hooks/`):
- After the existing `install-all-hooks.sh` call, add:
  ```bash
  # Rebuild symbol index if src/ files changed (WRK-1085)
  if git diff --name-only ORIG_HEAD HEAD 2>/dev/null | grep -q '/src/'; then
    REPO_ROOT="$(git rev-parse --show-toplevel)"
    uv run --no-project python "$REPO_ROOT/scripts/search/build-symbol-index.py" --quiet
  fi
  ```
- `--quiet` flag suppresses per-symbol noise; still prints rebuild summary line.

## Phase 5 — tests/search/test-symbol-index.sh

| test | scenario | expected |
|------|----------|----------|
| build-symbol-index.py runs clean | happy path | exits 0; symbol-index.jsonl has ≥50 records |
| find-symbol.sh engine | happy path | ≥2 repo hits returned |
| find-symbol.sh NonExistentXYZ999 | miss | exits 1, "Symbol not found" in stderr |
| cross-repo-search.sh engine --type py | happy path | src/ lines appear before tests/ lines |
| build-symbol-index.py skips broken file | error path | warning logged; other files indexed; exits 0 |
| find-symbol.sh --kind class --repo assethold | filtered | all results have kind=class and repo=assethold |

Test script creates a temp broken .py file in a scratch dir for the error-path case.

## Risks
- R1 (medium): rg not installed → fallback grep; warn user to install rg for 10× speed
- R2 (medium): post-merge rebuild adds latency on digitalmodel (150 files ~300ms) → acceptable
- R3 (low): broken .py files → graceful skip; tested in test suite
- R4 (medium): `/work status WRK-NNN` symbol lookup deferred as stretch goal (not in ACs)

## Out of scope
- IDE integration
- Non-Python symbol indexing (JS/TS/YAML)
- Semantic / fuzzy search
- `/work status WRK-NNN` symbol cross-reference (stretch goal, not in ACs)

## Verification (end-to-end)
```bash
# 1. Build index
uv run --no-project python scripts/search/build-symbol-index.py
# → config/search/symbol-index.jsonl exists, >50 lines

# 2. Find a known symbol
bash scripts/search/find-symbol.sh engine
# → prints ≥2 repo:file:line results in <1s

# 3. Find a known class
bash scripts/search/find-symbol.sh Engine --kind class
# → assethold:assethold/src/assethold/engine.py:N (class)

# 4. Cross-repo search
bash scripts/search/cross-repo-search.sh "def engine" --type py
# → src/ hits ranked before tests/

# 5. Run test suite
bash tests/search/test-symbol-index.sh
# → 6/6 PASS

# 6. Simulate post-merge hook
bash scripts/hooks/post-merge
# → hook runs; symbol index rebuilt (or skipped if no src/ changes)
```
