# WRK-1081 Plan (Final — post cross-review)
# feat(harness): extended static analysis — bandit, radon, vulture

## Route: B (Medium) | Workstation: ace-linux-1

## Cross-Review Changes (Codex + Gemini — REQUEST_CHANGES resolved)

| Issue | Resolution |
|-------|-----------|
| `-ll` suppresses LOW findings | Use `-f json` + parse severity in shell code |
| Count-only baseline too lossy | Use bandit native JSON baseline (`-b bandit-baseline.json`) |
| `.bandit` is YAML not TOML | Use `[tool.bandit]` in `pyproject.toml` (passed via `-c pyproject.toml`) |
| `[tool.radon]` wrong key | Use `.radon.cfg` per repo |
| vulture exits non-zero by default | Use `|| true`; capture output for warn display |
| Pre-commit staged-file path wrong | Pre-commit hook passes file args directly; `-r src/` only in full-suite |
| vulture false positives | Add `vulture_whitelist.py` stub per repo |

## Phase 1 — Baseline Capture
- Run `bandit -r src/ -f json -o config/quality/bandit-baseline-{repo}.json` per repo
- Each subsequent run: `bandit -r src/ -f json -b bandit-baseline-{repo}.json`
  - New MEDIUM/HIGH findings above baseline → exit 1
  - LOW findings always displayed as warnings only
- radon: no baseline needed (warn-only; output logged but never gates)
- vulture: `vulture_whitelist.py` per repo replaces count baseline

## Phase 2 — check-all.sh Extension

### Bandit (blocking on new MEDIUM/HIGH)
```bash
run_bandit() {
  bandit -r src/ -f json -b "${baseline}" 2>/dev/null | parse_bandit_severity
  # LOW → warn, MEDIUM/HIGH → exit 1
}
```

### Radon (warn-only)
```bash
run_radon() {
  radon cc src/ -n C 2>&1 || true  # always warn, never fail
}
```

### Vulture (warn-only)
```bash
run_vulture() {
  vulture src/ vulture_whitelist.py --min-confidence 80 2>&1 || true
}
```

New CLI flags: `--bandit`, `--radon`, `--vulture`, `--static` (all three)

## Phase 3 — Config Files (×5 repos)
- `pyproject.toml`: add `[tool.bandit]` section (skips list initially empty)
  - Passed via: `bandit -c pyproject.toml`
- `.radon.cfg` per repo: `[radon]\ncc_min = C`
- `vulture_whitelist.py` per repo: empty stub with comment on usage

## Phase 4 — Pre-commit Integration (×5 repos)
Local bandit hook with `pass_filenames: true`:
```yaml
- id: bandit-staged
  name: bandit security (staged files)
  language: system
  entry: bandit
  args: [-f, json, -c, pyproject.toml, -ll]  # -ll here is fine: staged = no baseline compare
  types: [python]
  pass_filenames: true
```
Note: staged-file hook uses simpler `-ll` (no baseline compare); full-suite uses JSON+baseline.

## Phase 5 — TDD (tests first)
File: `tests/quality/test_check_all_static.py` — 7 tests (was 6, adding pre-commit path test):
1. `test_bandit_medium_blocks` — MEDIUM finding in JSON → exit 1
2. `test_bandit_low_warns` — LOW only in JSON → exit 0 + warn line
3. `test_bandit_baseline_suppresses_existing` — existing MEDIUM in baseline → exit 0
4. `test_radon_nonblocking` — C-grade output → exit 0
5. `test_vulture_nonblocking` — dead code found → exit 0 + warn
6. `test_baseline_blocks_new_violations` — new MEDIUM not in baseline → exit 1
7. `test_static_flag_runs_all_three` — `--static` invokes bandit+radon+vulture

## Phase 6 — Cross-Review
Submit to Codex via `scripts/review/cross-review.sh`

## File Manifest
| File | Action |
|------|--------|
| `scripts/quality/check-all.sh` | Extend |
| `config/quality/bandit-baseline-{repo}.json` | Create ×5 |
| `{repo}/pyproject.toml` | Extend ×5 (`[tool.bandit]`) |
| `{repo}/.radon.cfg` | Create ×5 |
| `{repo}/vulture_whitelist.py` | Create ×5 (stub) |
| `{repo}/.pre-commit-config.yaml` | Extend ×5 (bandit-staged hook) |
| `tests/quality/test_check_all_static.py` | Create |

## Acceptance Criteria
- check-all.sh runs bandit/radon/vulture per repo
- bandit new MEDIUM/HIGH above baseline blocks; LOW warns
- radon C+ non-blocking; vulture 80%+ warning
- `[tool.bandit]` in pyproject.toml per repo; `.radon.cfg` per repo
- bandit JSON baseline per repo; vulture_whitelist.py stub per repo
- bandit in pre-commit (staged files only — no baseline compare, uses -ll)
- 7 TDD tests pass; Codex cross-review PASS
