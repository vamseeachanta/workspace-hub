# WRK-1058: Documentation Quality Checks Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend `scripts/quality/check-all.sh` with a `--docs` flag that runs ruff D (pydocstyle) rules, checks README required sections, and warns when `docs/` is absent.

**Architecture:** Add `run_ruff_docs()`, `check_readme_sections()`, and `check_docs_dir()` functions following the existing `run_ruff()`/`run_mypy()` pattern. Results stored in parallel `DOCS_RESULTS[]` map. `--docs` flag is additive (runs alongside ruff/mypy unless `--docs-only` is specified).

**Tech Stack:** bash, `uv tool run ruff` (D rules), grep for README section matching.

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
```

**Step 5: Run tests — expect T8–T12 to FAIL (red)**

```bash
bash tests/quality/test_check_all.sh 2>&1 | tail -20
```

Expected: T1–T7 PASS, T8–T12 FAIL with "not found in" messages.

**Step 6: Commit**

```bash
git add tests/quality/test_check_all.sh
git commit -m "test(WRK-1058): add T8-T12 for --docs flag (red)"
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
  local exit_code=0 output=""
  output="$(cd "$repo_path" && uv tool run ruff check --select D . 2>&1)" || exit_code=$?
  if [[ $exit_code -eq 0 ]]; then
    DOCS_RESULTS[$repo_name]+="docstrings: PASS  "
    return 0
  fi
  local count
  count="$(printf '%s\n' "$output" | grep -c '^\s*[0-9]' || true)"
  DOCS_RESULTS[$repo_name]+="docstrings: WARN (${count:-?} issues)  "
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
  local missing=() section content
  content="$(tr '[:upper:]' '[:lower:]' < "$readme")"
  for section in "${REQUIRED_README_SECTIONS[@]}"; do
    grep -q "$section" <<< "$content" || missing+=("$section")
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
    DOCS_RESULTS[$repo_name]+="docs-dir: OK"
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
