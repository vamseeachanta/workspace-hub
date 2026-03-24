# WRK-643 Validation Results

## Bundle implementation

- Generator: `scripts/review/build-claude-plan-bundle.py`
- Claude prompt: `scripts/review/prompts/claude-compact-plan-review.md`
- Wrapper integration: `scripts/review/submit-to-claude.sh --compact-plan`
- Bundle test: `scripts/review/tests/test-claude-compact-bundle.sh`

## Bundle size

- Source plan (`WRK-624`): `20650` bytes
- Claude compact bundle v2: `5760` bytes
- Reduction: about `72%`

## Validation runs on WRK-624

| Run | Path | Result | Evidence |
|---|---|---|---|
| R1 | wrapper `submit-to-claude.sh --compact-plan` with 45s timeout | no usable review; wrapper path remained live past timeout window | `raw/wrk-624-claude-review.md` |
| R2 | direct `claude -p` on generated bundle, 35s timeout | no output | `raw/wrk-624-claude-direct-review.md` |
| R3 | direct `claude -p` on tighter generated bundle, 25s timeout | `NO_OUTPUT` | `raw/wrk-624-claude-direct-review-v2.md` |

## Interpretation

The Claude-specific bundle is now deterministic, scripted, and materially smaller than the full plan. That is a genuine improvement to the tooling surface. But Claude still does not produce substantive non-interactive review output on the real `WRK-624` plan-review target, even with the tighter bundle.

This narrows the boundary from `WRK-642`:
- Claude can review a trivial schema control.
- Claude cannot yet review a real plan-review target, even after a 72% payload reduction and provider-specific prompt shaping.

## Operational recommendation

Use the compact bundle path as the canonical Claude transport input for future experiments, but continue to classify real plan-review attempts as `NO_OUTPUT` until a still-smaller semantic bundle or different provider invocation path is proven.
