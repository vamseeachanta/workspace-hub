---
name: gtm-demo-validation-cache-regression-repair
description: Diagnose and repair GTM demo validation failures caused by legacy cache files missing intermediate chart data, especially in nested digitalmodel demo scripts using --from-cache.
version: 1.0.0
category: workspace-hub-learned
tags: [gtm, digitalmodel, validation, cache, regression, pytest]
---

# GTM demo validation cache regression repair

Use when `digitalmodel/examples/demos/gtm/tests/test_gtm_demos.py` fails on a `--from-cache` smoke test after a demo script was retrofitted to cache more intermediate chart data.

## Trigger pattern

Typical symptom:
- `PYTHONPATH=examples/demos/gtm:src uv run pytest examples/demos/gtm/tests/test_gtm_demos.py -q`
- one failing demo, often Demo 2 wall thickness
- error from cached path like `NameError: PipeDefinition is not defined`

Root cause pattern:
- the script's cached mode assumes newly added intermediate keys exist in old committed JSON
- legacy cache only contains core keys like `metadata/results/summary`
- chart builders fall through into engineering-calculation code paths, which require symbols that cached mode never initialized

## Proven workflow

1. Reproduce in the nested repo, not only the outer workspace-hub repo.
   - `cd /mnt/local-analysis/workspace-hub/digitalmodel`
   - `PYTHONPATH=examples/demos/gtm:src uv run pytest examples/demos/gtm/tests/test_gtm_demos.py -q`

2. Inspect the failing script and the committed cache JSON together.
   - confirm which intermediate keys the script now expects
   - inspect the current results JSON to see whether those keys actually exist

3. Prefer a compatibility fix over forcing cache deletion.
   - add a helper like `_cache_has_intermediate_data(cached)`
   - if `--from-cache` loads a legacy JSON without required intermediate keys, log a clear message and fall back to full recalculation
   - also initialize any constants/imports still needed by downstream chart builders even in cache/regeneration mode

4. Re-run both:
   - full GTM test suite
   - targeted failing subset, e.g. `-k wall_thickness`

5. Clean generated artifact churn before committing.
   - GTM tests can rewrite tracked HTML/JSON outputs
   - revert unrelated regenerated files with `git checkout -- ...`
   - commit only the code fix unless output regeneration is intentionally part of the change

## Minimal repair pattern

In the script:
- define required cache keys
- detect whether loaded JSON has them
- if not, switch from cache mode to full-calc mode
- initialize code-name constants/imported enums for both cache and full modes when chart builders depend on them

## Verification standard

Required:
- `PYTHONPATH=examples/demos/gtm:src uv run pytest examples/demos/gtm/tests/test_gtm_demos.py -q` passes
- targeted regression subset passes
- nested repo `git status` is clean except for intended code changes before commit

## Important notes

- `digitalmodel` is a nested git repo under `workspace-hub`; status/history/commits must be checked there.
- A green GTM pytest suite clears the test-suite blocker for workspace-hub issue tracking, but does not by itself satisfy higher-level GTM approval gates like browser validation or hand checks.
