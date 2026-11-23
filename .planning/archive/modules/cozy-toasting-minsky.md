# Plan: WRK-1112 — Limit Cross-Review Iterations to 3

## Context

Unbounded review loops waste AI quota and dilute feedback quality. This change caps all
cross-review cycles at 3 iterations per WRK, persists the count to a YAML file, and
injects a preamble into every review prompt that explicitly tells the reviewer agent:
- which iteration they're on (N of 3),
- that this is a hard budget (no more passes after 3),
- and what to prioritise at each tier (blockers → design → style).

The user specifically asked that the preamble communicate the constraint *to the reviewer
agent* so they put their best foot forward within those limits.

---

## Phase 1 — Enforce 3-iteration cap in cross-review scripts

### `scripts/review/cross-review.sh`

Add constant at top (after `set -euo pipefail`):
```bash
MAX_REVIEW_ITERATIONS=3
```

Add helper functions before `submit_review()`:
```bash
# Returns the current iteration number (1-based) for the given WRK, initialising if absent.
get_review_iteration() {
  local wrk_id="$1"
  local iter_file="${WS_HUB_ROOT}/.claude/work-queue/assets/${wrk_id}/review-iteration.yaml"
  if [[ ! -f "$iter_file" ]]; then echo 0; return; fi
  awk -F': ' '/^iteration:/ {print $2+0; exit}' "$iter_file"
}

# Increments iteration counter; writes review-iteration.yaml; returns new count.
increment_review_iteration() {
  local wrk_id="$1"
  local assets_dir="${WS_HUB_ROOT}/.claude/work-queue/assets/${wrk_id}"
  mkdir -p "$assets_dir"
  local iter_file="${assets_dir}/review-iteration.yaml"
  local current; current="$(get_review_iteration "$wrk_id")"
  local new_count=$(( current + 1 ))
  cat > "$iter_file" <<YAML
wrk_id: "${wrk_id}"
iteration: ${new_count}
first_review_at: "$(awk -F': ' '/^first_review_at:/ {print $2; exit}' "$iter_file" 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
last_review_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
YAML
  echo "$new_count"
}
```

Before the `submit_review` dispatch block (after PROMPT is loaded), add the cap check
and preamble injection:
```bash
# --- Iteration cap and preamble injection ---
CURRENT_ITER=0
if [[ -n "$WRK_ID" ]]; then
  CURRENT_ITER="$(get_review_iteration "$WRK_ID")"
  if [[ "$CURRENT_ITER" -ge "$MAX_REVIEW_ITERATIONS" ]]; then
    echo "✖ Review iteration cap reached: ${WRK_ID} has already had ${CURRENT_ITER}/${MAX_REVIEW_ITERATIONS} review passes." >&2
    echo "  No further review passes will be accepted for this WRK." >&2
    echo "  Resolve findings and close the WRK instead of requesting another review." >&2
    exit 1
  fi
  CURRENT_ITER="$(increment_review_iteration "$WRK_ID")"
  PROMPT="$(cat <<PREAMBLE
You are reviewing ${WRK_ID} — iteration ${CURRENT_ITER} of ${MAX_REVIEW_ITERATIONS} (maximum).

This is a hard budget. After iteration ${MAX_REVIEW_ITERATIONS} no further review passes will be
accepted. Plan your feedback to maximise impact within this constraint:
  • Iteration 1: blockers and security issues only — nothing else
  • Iteration 2: major design / correctness issues
  • Iteration 3: minor / style / nice-to-haves

Front-load your most critical finding first. If you have only one shot to prevent a
serious defect, this is it. Do not save critical issues for a later pass.

---
PREAMBLE
)
${PROMPT}"
fi
```

### `scripts/review/submit-to-codex.sh` — read-only guard

After the `WRK_ID` extraction block, add:
```bash
# Secondary iteration cap guard (prevents direct invocations bypassing cross-review.sh)
if [[ -n "$WRK_ID" && -n "$REPO_ROOT" ]]; then
  _iter_file="${REPO_ROOT}/.claude/work-queue/assets/${WRK_ID}/review-iteration.yaml"
  if [[ -f "$_iter_file" ]]; then
    _iter_count="$(awk -F': ' '/^iteration:/ {print $2+0; exit}' "$_iter_file")"
    if [[ "$_iter_count" -ge 3 ]]; then
      echo "# REVIEW_ITERATION_CAP_EXCEEDED: ${WRK_ID} has used ${_iter_count}/3 review passes." >&2
      echo "# No further review passes accepted. Resolve findings and close the WRK." >&2
      exit 1
    fi
  fi
fi
```

### `scripts/review/submit-to-gemini.sh` — same read-only guard

Identical block inserted after `WRK_ID` extraction.

---

## Phase 2 — Tests

New file: `scripts/review/tests/test-wrk1112-iteration-cap.sh`

5 tests (plain bash, assert_eq pattern matching existing tests):

1. `test_review_iteration_yaml_created_on_first_pass`
   — Run mock cross-review for WRK-9999; assert `review-iteration.yaml` exists with `iteration: 1`.

2. `test_review_iteration_increments_correctly`
   — Pre-seed yaml with `iteration: 1`; run again; assert `iteration: 2`.

3. `test_fourth_iteration_blocked_with_error`
   — Pre-seed yaml with `iteration: 3`; run cross-review; assert exit code 1 and error message contains "cap reached".

4. `test_preamble_includes_iteration_number_and_budget`
   — Mock submit-to-claude to capture PROMPT; assert preamble contains "iteration 2 of 3" and "Front-load".

5. `test_cap_applies_to_codex_and_gemini_wrappers`
   — Pre-seed yaml with `iteration: 3`; call submit-to-codex.sh and submit-to-gemini.sh directly; assert both exit 1 with cap message.

---

## Phase 3 — SKILL.md documentation

| File | Change |
|------|--------|
| `.claude/skills/coordination/workspace/work-queue/SKILL.md` §Cross-Review | Add: "Maximum 3 iterations per WRK. Enforced by `review-iteration.yaml` in assets." |
| `.claude/skills/coordination/workspace/work-queue-workflow/SKILL.md` Stage 13 | Add iteration-count gate: "cross-review iteration ≤ 3 (`review-iteration.yaml`)". |
| `.claude/skills/coordination/workspace/workflow-gatepass/SKILL.md` | Add R-28: "cross-review iteration count ≤ 3 (verified via review-iteration.yaml)". |

---

## Files to modify

| File | Change type |
|------|-------------|
| `scripts/review/cross-review.sh` | Add constant, two helper functions, cap check + preamble injection |
| `scripts/review/submit-to-codex.sh` | Add read-only iteration guard after WRK_ID extraction |
| `scripts/review/submit-to-gemini.sh` | Same read-only guard |
| `scripts/review/tests/test-wrk1112-iteration-cap.sh` | New — 5 TDD tests |
| `work-queue/SKILL.md` | §Cross-Review note |
| `work-queue-workflow/SKILL.md` | Stage 13 gate line |
| `workflow-gatepass/SKILL.md` | R-28 entry |

---

## Verification

```bash
# Run tests
bash scripts/review/tests/test-wrk1112-iteration-cap.sh

# Smoke test cap enforcement
mkdir -p .claude/work-queue/assets/WRK-SMOKE
echo -e "wrk_id: WRK-SMOKE\niteration: 3" > .claude/work-queue/assets/WRK-SMOKE/review-iteration.yaml
bash scripts/review/cross-review.sh /dev/null all --wrk-id WRK-SMOKE
# → should exit 1 with "cap reached" message
```
