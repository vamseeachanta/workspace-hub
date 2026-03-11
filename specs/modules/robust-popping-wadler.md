# Plan: WRK-1117 — Windows/Git Bash: fix comprehensive-learning push path + signal generation

## Context

acma-ansys05 (Windows Git Bash) runs `comprehensive-learning.sh` at session exit
but contributes zero learnings to the pipeline. Two root causes:

1. `git add .claude/state/candidates/ ...` — bare git add fails with `fatal: pathspec
   did not match any files` when dirs are absent (first-run or sparse machine). The
   error is printed but not fatal (set -uo not set -e), so the script continues,
   `git diff --staged --quiet` returns 0, "No new learning state to push" is printed,
   and nothing reaches ace-linux-1.

2. `scripts/improve/lib/guard.sh:30` uses `bc -l` which is absent on Git Bash →
   fallback `|| echo "1"` always returns 1 → every improvement is rejected silently.

3. `scripts/improve/lib/classify.sh:27` calls bare `python3` which is not in PATH
   on Windows; violates the hard rule in `.claude/rules/python-runtime.md`.

The cross-platform patterns are now documented in
`.claude/skills/_core/bash/cross-platform-compat/SKILL.md` (created this session).

## Implementation Plan

### Step 1 — TDD: Write failing tests first

**New file:** `tests/unit/cross-platform/test_compat_wrk1117.sh`

Three tests using bash + `mktemp -d` + `trap cleanup EXIT` pattern (same as
`tests/hooks/`):

```
test_git_add_skips_missing_dirs()
  - Create temp git repo with NO .claude/state/candidates/
  - Source the patched push logic
  - Assert: exit 0, no fatal error in stderr, staged count = 0 ("nothing to push")

test_guard_score_without_bc()
  - Export PATH without bc (mock: PATH=/usr/bin minus bc via wrapper)
  - Call guard phase score check with score="0.5"
  - Assert: returns 1 (below threshold), no "bc: command not found" in stderr

test_classify_python_resolver()
  - Mock PATH with no python3 but python present
  - Source classify.sh
  - Assert: Python call succeeds using `python` fallback (uv run fallback last)
```

Run to confirm all three fail before implementation.

### Step 2 — Fix `comprehensive-learning.sh` (Windows push path)

**File:** `scripts/learning/comprehensive-learning.sh`
**Lines:** 29–52 (the non-ace-linux-1 branch)

Replace bare `git add` block with guarded loop:

```bash
# Before:
git add .claude/state/candidates/ \
        .claude/state/corrections/ \
        ...

# After:
STATE_PATHS=(
    ".claude/state/candidates/"
    ".claude/state/corrections/"
    ".claude/state/patterns/"
    ".claude/state/reflect-history/"
    ".claude/state/trends/"
    ".claude/state/session-signals/"
    ".claude/state/cc-insights/"
    ".claude/state/learned-patterns.json"
    ".claude/state/skill-scores.yaml"
    ".claude/state/cc-user-insights.yaml"
)
for path in "${STATE_PATHS[@]}"; do
    [[ -e "${WS_HUB}/${path}" ]] && git -C "$WS_HUB" add "$path"
done
```

Commit/push block unchanged — `git diff --staged --quiet` correctly detects nothing.
Add a diagnostic line: `echo "Learning state: $(git -C "$WS_HUB" diff --staged --name-only | wc -l | tr -d ' ') file(s) staged"`.

### Step 3 — Fix `guard.sh` (remove bc)

**File:** `scripts/improve/lib/guard.sh`
**Line:** 30

```bash
# Before:
if (( $(echo "$score < 0.6" | bc -l 2>/dev/null || echo "1") )); then

# After:
if awk "BEGIN {exit !($score < 0.6)}"; then
```

`awk` is already used in `ecosystem.sh` — consistent with existing codebase pattern.
No other bc usage exists in improve/lib/.

### Step 4 — Fix `classify.sh` (python3 → uv)

**File:** `scripts/improve/lib/classify.sh`
**Line:** 27

```bash
# Before:
if command -v python3 &>/dev/null; then
    python3 - <<PYEOF 2>/dev/null || true

# After:
if command -v uv &>/dev/null; then
    uv run --no-project python - <<PYEOF 2>/dev/null || true
```

`uv` is the hard-rule runtime. The existing `if command -v python3` guard is
replaced with `if command -v uv` — uv is required on all machines per
`.claude/rules/python-runtime.md`. No fallback needed (uv absence = skip, same
as before).

### Step 5 — Run tests (confirm green)

```bash
bash tests/unit/cross-platform/test_compat_wrk1117.sh
```

All 3 tests must pass.

### Step 6 — Update bash-script-framework SKILL.md

**File:** `.claude/skills/_core/bash/bash-script-framework/SKILL.md`

Update `DON'T USE when: Windows-only environment` → add a cross-reference line:
> For Windows/Git Bash-compatible scripts, see `_core/bash/cross-platform-compat`.

Bump version to 1.1.0 in frontmatter.

## Files Modified

| File | Change |
|------|--------|
| `scripts/learning/comprehensive-learning.sh` | Guarded git add loop (Step 2) |
| `scripts/improve/lib/guard.sh` | bc → awk (Step 3) |
| `scripts/improve/lib/classify.sh` | python3 → uv run (Step 4) |
| `tests/unit/cross-platform/test_compat_wrk1117.sh` | New TDD file (Step 1) |
| `.claude/skills/_core/bash/bash-script-framework/SKILL.md` | Cross-ref note (Step 6) |

## Files Already Done (This Session)

| File | Status |
|------|--------|
| `.claude/skills/_core/bash/cross-platform-compat/SKILL.md` | Created (186 lines) |
| `.claude/work-queue/pending/WRK-1117.md` | Multi-machine closure gate added |
| `.claude/work-queue/pending/WRK-1118.md` | Created with skill reference |

## Verification

```bash
# 1. TDD passes
bash tests/unit/cross-platform/test_compat_wrk1117.sh

# 2. No bc in improve pipeline
grep -rn "| bc\|bc -l" scripts/improve/

# 3. No python3 in classify.sh
grep "python3" scripts/improve/lib/classify.sh

# 4. Dry-run improve on Linux (regression check)
bash scripts/improve/improve.sh --quick --dry-run

# 5. Test Windows push path with missing dirs (simulate)
mkdir -p /tmp/test-wrk1117 && cd /tmp/test-wrk1117 && git init -q
# run comprehensive-learning.sh non-ace-linux-1 branch → should print
# "Learning state: 0 file(s) staged" and "No new learning state to push"
```

## Closure Gate (from WRK-1117)

| Machine | Required verification |
|---------|----------------------|
| ace-linux-1 | TDD passes + improve dry-run succeeds |
| acma-ansys05 | `bash comprehensive-learning.sh` exits 0, no fatal error |
