## Parent: #1668 (retroactive review)

## Problem
Codex adversarial review (2026-04-02) found shell injection vulnerability:
- `submit-batch.sh` uses `python3 -c "with open('${MANIFEST}')"` with unsanitized shell interpolation
- `queue-health.sh` has the same pattern with `${job_dir}result.yaml`
- A manifest path containing `'` breaks parsing; a crafted path can become Python code injection

## Severity: HIGH (S2)

## Fix Options
1. Replace `python3 -c` with standalone Python scripts called with arguments
2. Use `uv run` (repo convention) with proper argument passing
3. At minimum, shell-quote the interpolated paths

## Acceptance Criteria
- [ ] No raw shell interpolation inside `python3 -c` strings
- [ ] All Python invocations use `uv run` per repo convention
- [ ] Paths passed as CLI arguments, not embedded in source
- [ ] Tests cover paths with special characters (spaces, quotes, etc.)

## Source
Review: `scripts/review/results/2026-04-02T132222Z-retroactive-review-codex.md`