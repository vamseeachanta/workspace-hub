# WRK-1058: Documentation Quality Checks Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend `scripts/quality/check-all.sh` with a `--docs` flag that runs ruff D (pydocstyle) rules, checks README required sections, and warns when `docs/` is absent.

**Architecture:** Add `run_ruff_docs()`, `check_readme_sections()`, and `check_docs_dir()` functions following the existing `run_ruff()`/`run_mypy()` pattern. Results stored in parallel `DOCS_RESULTS[]` map.

**Flag contract (explicit):**
- `--docs` is additive: always adds docs checks on top of whatever else runs. Alone → runs ruff + mypy + docs (default behaviour + docs). Combined with `--ruff-only` → runs ruff + docs only. Combined with `--mypy-only` → runs mypy + docs only. No `--docs-only` mode.
- All docs subchecks are warn-only: `run_ruff_docs` failure → `docstrings: WARN`; never raises exit code.
- README heading match: `grep -qEi "^#+[[:space:]]*${section}$"` — exact heading word match (e.g. `## Installation` passes, `## Installation Notes` does not).
- Output labels consistent across all subchecks: `PASS` / `WARN`.

**Tech Stack:** bash 4.0+ (already required by existing `declare -A` usage), `uv tool run ruff` (D rules), `uv run --no-project python` for JSON count (no bare python3).

**Runtime dependencies (inherited from check-all.sh — no new requirements):**

| Tool | Min version | Already required by | Behavior if absent |
|------|-------------|--------------------|--------------------|
| bash | 4.0+ | `declare -A RUFF_RESULTS` in existing check-all.sh | Script exits with syntax error |
| uv | 0.5.0+ | `uv tool run ruff` in existing run_ruff() | ruff_ver="(unavailable)", check skipped |
| ruff | any | `uv tool run ruff` in existing run_ruff() | Managed via uv tool; auto-installed |
| grep -E | POSIX | existing check-all.sh | system grep; present on all Linux targets |
| tr | POSIX | existing check-all.sh | system coreutils; present on all Linux targets |
| python (via uv) | 3.9+ | `uv run --no-project python` in hub scripts | If unavailable: count falls back to '?' |

`run_ruff_docs()` unavailability behavior: if `uv tool run ruff` fails, exit_code≠0 → `docstrings: WARN (? issues)`. Never hard-fails. All 5 target machines are ace-linux-1 (Linux, bash 5.x, uv 0.5+, all tools confirmed present per WRK-1066 env audit).

**Cross-review amendments applied:**
- v1 P2: README heading-level grep (not bare text match)
- v1 P3: exit code as primary signal; JSON count via `uv run --no-project python`
- v2 P1: `python3 -c` → `uv run --no-project python -c` (policy compliance)
- v2 P2: flag semantics clarified above; `--docs-only` dropped
- v2 P2: added T13 (ruff D WARN + exit 0) and T14 (missing README.md WARN)
- v2 P3: `docs-dir: OK` → `docs-dir: PASS` for label consistency

---

### Task 1: Add test fixtures for docs checks

**Files:**
- Modify: `tests/quality/test_check_all.sh` — add T8–T12 for `--docs` behaviour

**Step 1: Identify fixture gap**

The existing fixture repos (in `FIXTURE_ROOT`) have no `README.md` or `docs/`. Tests for `--docs` need:
- A repo with `README.md` containing all required sections → docs PASS
- A repo with `README.md` missing sections → docs WARN
- A repo with no `docs/` → docs WARN (different message)

**Step 2: Add README fixtures in test setup** (after the existing repo creation loop)

Find the line `run_check() {` in the test file and insert above it:

```bash
# Docs fixtures: assetutilities gets full README; worldenergydata gets partial README
cat > "${FIXTURE_ROOT}/assetutilities/README.md" <<'EOF'
# assetutilities
## Installation
Run `uv install`.
## Usage
Import the module.
## Examples
See tests/.
EOF

cat > "${FIXTURE_ROOT}/worldenergydata/README.md" <<'EOF'
# worldenergydata
## Overview
Energy data.
EOF
# No Installation / Examples sections — will trigger WARN

mkdir -p "${FIXTURE_ROOT}/assetutilities/docs"
# worldenergydata intentionally has no docs/

# Mock uv D-rules: controlled by MOCK_RUFF_DOCS_EXIT
# Amend the existing mock uv script to handle D-rule invocations:
```

**Step 3: Amend mock uv to handle D-rule args**

In the mock `uv` script, the `tool run ruff check` branch needs to distinguish D-rule runs.
Add before the closing `*) exit 0 ;;` in the mock:

```bash
  "tool run ruff check --select D"*)
    if [[ "${MOCK_RUFF_DOCS_EXIT:-0}" -ne 0 ]]; then
      echo "src/foo.py:1:1: D100 Missing docstring in public module"
      echo "Found 1 error."
      exit 1
    fi
    echo "All checks passed."
    exit 0
    ;;
```

Note: The mock `uv` is written to a temp file at test startup — we need to regenerate it after this change. Easier: replace the whole mock block with one that handles all three cases.

**Step 4: Write T8–T12 tests at end of test file (before the Summary block)**

```bash
# ---------------------------------------------------------------------------
# T8: --docs flag appears in --help
# ---------------------------------------------------------------------------
echo "── T8: --help shows --docs ───────────────────────────────"
help_docs_out="$(run_check --help 2>&1)"
assert_contains "T8 --help shows --docs" "--docs" "$help_docs_out"

# ---------------------------------------------------------------------------
# T9: --docs runs docs check, not ruff/mypy lines unless combined
# ---------------------------------------------------------------------------
echo "── T9: --docs produces docs: lines ──────────────────────"
docs_out="$(MOCK_RUFF_DOCS_EXIT=0 run_check --docs --repo assetutilities 2>&1)" || true
assert_contains "T9 docs: line present" "docs:" "$docs_out"

# ---------------------------------------------------------------------------
# T10: README with all sections → PASS
# ---------------------------------------------------------------------------
echo "── T10: README all sections → PASS ───────────────────────"
t10_out="$(MOCK_RUFF_DOCS_EXIT=0 run_check --docs --repo assetutilities 2>&1)" || true
assert_contains "T10 readme: PASS" "readme: PASS" "$t10_out"

# ---------------------------------------------------------------------------
# T11: README missing sections → WARN (exit still 0)
# ---------------------------------------------------------------------------
echo "── T11: README missing sections → WARN, exit 0 ──────────"
t11_exit=0
t11_out="$(MOCK_RUFF_DOCS_EXIT=0 run_check --docs --repo worldenergydata 2>&1)" \
  || t11_exit=$?
assert_exit "T11 exit 0 on readme WARN" 0 "$t11_exit"
assert_contains "T11 readme: WARN" "readme: WARN" "$t11_out"

# ---------------------------------------------------------------------------
# T12: docs/ absent → WARN in output
# ---------------------------------------------------------------------------
echo "── T12: docs/ absent → WARN ──────────────────────────────"
t12_out="$(MOCK_RUFF_DOCS_EXIT=0 run_check --docs --repo worldenergydata 2>&1)" || true
assert_contains "T12 docs-dir: WARN" "docs-dir: WARN" "$t12_out"

# ---------------------------------------------------------------------------
# T13: ruff D failure → docstrings: WARN, but overall exit 0 (warn-only)
# ---------------------------------------------------------------------------
echo "── T13: ruff D failure → WARN, exit 0 ───────────────────"
t13_exit=0
t13_out="$(MOCK_RUFF_DOCS_EXIT=1 run_check --docs --repo assetutilities 2>&1)" \
  || t13_exit=$?
assert_exit "T13 exit 0 despite ruff D failure" 0 "$t13_exit"
assert_contains "T13 docstrings: WARN in output" "docstrings: WARN" "$t13_out"

# ---------------------------------------------------------------------------
# T14: missing README.md → readme: WARN (missing README.md)
# ---------------------------------------------------------------------------
echo "── T14: missing README.md → WARN ─────────────────────────"
# ogmanufacturing fixture has no README.md (not created in setup)
t14_out="$(MOCK_RUFF_DOCS_EXIT=0 run_check --docs --repo ogmanufacturing 2>&1)" || true
assert_contains "T14 readme: WARN (missing README.md)" "readme: WARN (missing README.md)" "$t14_out"
```

**Step 5: Run tests — expect T8–T14 to FAIL (red)**

```bash
bash tests/quality/test_check_all.sh 2>&1 | tail -20
```

Expected: T1–T7 PASS, T8–T14 FAIL with "not found in" messages.

**Step 6: Commit**

```bash
git add tests/quality/test_check_all.sh
git commit -m "test(WRK-1058): add T8-T14 for --docs flag (red)"
```

---

### Task 2: Add `--docs` flag and `run_ruff_docs()` to check-all.sh

**Files:**
- Modify: `scripts/quality/check-all.sh` — add flag, function, integration

**Step 1: Add `OPT_DOCS=false` with other flags**

After `OPT_MYPY_ONLY=false`, add:
```bash
OPT_DOCS=false
```

**Step 2: Add `--docs` to usage()**

In the `usage()` heredoc, add after `--mypy-only` line:
```
  --docs             Run ruff D (pydocstyle) rules + README + docs/ checks
```

**Step 3: Add `--docs` to argument parser**

After `--mypy-only) OPT_MYPY_ONLY=true; shift ;;`, add:
```bash
    --docs)       OPT_DOCS=true;         shift ;;
```

**Step 4: Add `DOCS_RESULTS` map with other result maps**

After `declare -A MYPY_RESULTS=()`, add:
```bash
declare -A DOCS_RESULTS=()
```

**Step 5: Add `run_ruff_docs()` function** (after `run_mypy()`)

```bash
run_ruff_docs() {
  local repo_name="$1" repo_path="$2"
  local exit_code=0 count=""
  # Use exit code as primary signal; JSON format for stable issue count
  (cd "$repo_path" && uv tool run ruff check --select D . --quiet 2>/dev/null) && exit_code=0 || exit_code=$?
  if [[ $exit_code -eq 0 ]]; then
    DOCS_RESULTS[$repo_name]+="docstrings: PASS  "
    return 0
  fi
  count="$(cd "$repo_path" && uv tool run ruff check --select D . --output-format json 2>/dev/null \
    | uv run --no-project python -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo '?')"
  DOCS_RESULTS[$repo_name]+="docstrings: WARN (${count} issues)  "
  return 0  # docs check is warn-only, never fails the build
}
```

**Step 6: Add `check_readme_sections()` function** (after `run_ruff_docs()`)

```bash
REQUIRED_README_SECTIONS=(installation usage examples)

check_readme_sections() {
  local repo_name="$1" repo_path="$2"
  local readme="${repo_path}/README.md"
  if [[ ! -f "$readme" ]]; then
    DOCS_RESULTS[$repo_name]+="readme: WARN (missing README.md)  "
    return 0
  fi
  local missing=() section
  for section in "${REQUIRED_README_SECTIONS[@]}"; do
    grep -qEi "^#+[[:space:]]*${section}$" "$readme" || missing+=("$section")
  done
  if [[ ${#missing[@]} -eq 0 ]]; then
    DOCS_RESULTS[$repo_name]+="readme: PASS  "
  else
    DOCS_RESULTS[$repo_name]+="readme: WARN (missing: ${missing[*]})  "
  fi
  return 0
}
```

**Step 7: Add `check_docs_dir()` function** (after `check_readme_sections()`)

```bash
check_docs_dir() {
  local repo_name="$1" repo_path="$2"
  if [[ -d "${repo_path}/docs" ]]; then
    DOCS_RESULTS[$repo_name]+="docs-dir: PASS"
  else
    DOCS_RESULTS[$repo_name]+="docs-dir: WARN (no docs/ directory)"
  fi
  return 0
}
```

**Step 8: Integrate into main loop**

After the `if ! $OPT_RUFF_ONLY` block (mypy section), add:
```bash
  if $OPT_DOCS; then
    DOCS_RESULTS[$repo_name]=""
    run_ruff_docs "$repo_name" "$repo_path"
    check_readme_sections "$repo_name" "$repo_path"
    check_docs_dir "$repo_name" "$repo_path"
    echo "${label} docs: ${DOCS_RESULTS[$repo_name]}"
  fi
```

**Step 9: Run tests — expect T8–T12 to PASS**

```bash
bash tests/quality/test_check_all.sh 2>&1 | tail -20
```

Expected: all 12 tests PASS.

**Step 10: Commit**

```bash
git add scripts/quality/check-all.sh
git commit -m "feat(WRK-1058): add --docs flag with ruff D rules + README + docs/ checks"
```

---

### Task 3: Integration smoke test + update README

**Files:**
- No new files — live smoke test only

**Step 1: Run live docs check against assethold (smallest repo)**

```bash
bash scripts/quality/check-all.sh --docs --repo assethold 2>&1
```

Expected: output shows `docs:` line with docstrings/readme/docs-dir results. Exit 0.

**Step 2: Run full docs check across all repos**

```bash
bash scripts/quality/check-all.sh --docs 2>&1
```

Expected: 5 repos, each with `docs:` line. Exit 0 (docs checks are warn-only).

**Step 3: Verify combined run (ruff + docs)**

```bash
bash scripts/quality/check-all.sh --ruff-only --docs --repo assetutilities 2>&1
```

Expected: both `ruff:` and `docs:` lines.

**Step 4: Commit smoke-test evidence in checkpoint**

No files to commit — evidence will go in stage YAML.

---

### Task 4: Write gate evidence and run Stage 12 TDD check

**Files:**
- Create: `.claude/work-queue/assets/WRK-1058/evidence/execute.yaml`
- Create: `.claude/work-queue/assets/WRK-1058/evidence/ac-test-matrix.md`

**Step 1: Verify all ACs against test outputs**

AC checklist:
- [ ] `--docs` flag runs ruff D rules → T9 + live smoke
- [ ] README section check reports missing sections → T10/T11
- [ ] `docs/` presence reported as warning → T12
- [ ] Output integrated into check-all.sh report table → T9
- [ ] Codex cross-review passes → Stage 13

**Step 2: Write `ac-test-matrix.md`**

```markdown
# WRK-1058 AC Test Matrix

| AC | Test | Result |
|----|------|--------|
| --docs runs ruff D rules | T9 + smoke | PASS |
| README section check (missing sections) | T11 | PASS |
| docs/ presence warning | T12 | PASS |
| Output integrated into report table | T9 | PASS |
| Codex cross-review passes | Stage 13 | PENDING |
```

**Step 3: Commit final**

```bash
git add tests/quality/test_check_all.sh scripts/quality/check-all.sh
git commit -m "feat(WRK-1058): docs quality checks complete — all 12 tests pass"
```
