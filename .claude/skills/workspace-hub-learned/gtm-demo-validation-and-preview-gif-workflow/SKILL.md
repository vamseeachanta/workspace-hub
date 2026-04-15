---
name: gtm-demo-validation-and-preview-gif-workflow
description: Validate digitalmodel GTM demos end-to-end, recover from legacy Demo
  2 cache regressions, regenerate fresh artifacts, and produce lightweight preview
  GIFs for issue
version: 1.0.0
category: workspace-hub-learned
applies-to:
- hermes
- claude
- codex
- gemini
trigger: manual
auto_execute: false
tags:
- gtm
- digitalmodel
- validation
- playwright
- ffmpeg
- github
---

# GTM Demo Validation and Preview GIF Workflow

Use when validating the 5 GTM demos in `digitalmodel/examples/demos/gtm`, especially for GitHub issue #2118 / #1809 style work.

## When to use
- GTM demos need proof they actually run end-to-end
- `--from-cache` behavior is flaky or regressed
- reports need browser/render validation
- you need quick collateral GIFs from validated reports

## Key finding
Demo 2 (`demo_02_wall_thickness_multicode.py`) can fail in `--from-cache` mode if the committed cache is a legacy JSON containing only:
- `metadata`
- `results`
- `summary`

Newer chart builders expect intermediate keys:
- `lifecycle_phases`
- `min_wall_thickness`
- `weight_penalty`

If those keys are missing, `--from-cache` may crash indirectly when Chart 1 falls back into engineering-code paths and `PipeDefinition` / related symbols were never initialized.

## Verified fix pattern
In Demo 2:
1. Add a helper that checks whether the cache contains the required intermediate keys.
2. If `--from-cache` is requested but those keys are missing, print a warning and fall back to full recalculation.
3. In the true cache-fast path, still initialize code constants/modules needed by downstream chart builders.

### Minimal pattern
```python
CACHE_INTERMEDIATE_KEYS = (
    "lifecycle_phases",
    "min_wall_thickness",
    "weight_penalty",
)

def _cache_has_intermediate_data(cached):
    return all(cached.get(key) is not None for key in CACHE_INTERMEDIATE_KEYS)
```

Then in `main()`:
- compute `use_cache`
- load cache
- if missing intermediates: `use_cache = False`
- if `not use_cache`: do full recalc
- if `use_cache` but globals/constants are needed: call `_load_engineering_modules()` and `_init_code_constants()`

## Validation workflow
From `digitalmodel/`:

### 1. First run the suite
```bash
PYTHONPATH=examples/demos/gtm:src uv run pytest examples/demos/gtm/tests/test_gtm_demos.py -q
```

### 2. If Demo 2 cache path is suspect, isolate it
```bash
PYTHONPATH=examples/demos/gtm:src uv run pytest examples/demos/gtm/tests/test_gtm_demos.py -q -k wall_thickness
```

### 3. Run all 5 demos fresh
Use `--force` for approval-grade evidence:
```bash
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_01_dnv_freespan_viv.py --force
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_02_wall_thickness_multicode.py --force
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_03_deepwater_mudmat_installation.py --force
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_04_shallow_water_pipelay.py --force
PYTHONPATH=examples/demos/gtm:src uv run python examples/demos/gtm/demo_05_deepwater_rigid_jumper_installation.py --force
```

### 4. Verify regenerated JSON counts
Expected totals:
- Demo 1: 680
- Demo 2: 72
- Demo 3: 180
- Demo 4: 60
- Demo 5: 300

Use a small Python check against `metadata.total_cases` and the main data array length.

## Browser validation workflow
Use a local static server rooted at the GTM folder, not repo root.

### Correct server command
```bash
python -m http.server 8766 --directory /absolute/path/to/digitalmodel/examples/demos/gtm
```

Then open:
- `http://127.0.0.1:8766/output/demo_01_freespan_report.html`
- etc.

### What to verify
Per report:
- title renders
- `document.querySelectorAll('.chart-container').length == 5`
- `document.querySelectorAll('.js-plotly-plot').length == 5`
- browser console has no JS errors

## Hand-check pattern
Approval-grade evidence should include at least 2 simple spot checks.

### Good picks that matched well
1. Demo 3 landing phase:
- formula: `bearing_kpa = w_sub_kn / a_base_m2`
- utilisation: `bearing_kpa / bearing_limit_kpa`

2. Demo 5 in-air bending:
- moment: `M = w * L^2 / 8`
- utilisation: `bending_stress_mpa / allowable_stress_mpa`

These are easy to recompute from JSON results and usually match within rounding tolerance.

## Preview GIF workflow
This is useful for quick progress on #1809 before full workflow recordings exist.

### Preconditions
- validated HTML reports exist
- local HTTP server is running against `examples/demos/gtm`
- `npx playwright` works
- `ffmpeg` is installed

### Pattern
1. Use Playwright to open each report URL.
2. Scroll through the page in ~8 steps.
3. Capture PNG frames.
4. Convert frames to a compressed GIF with ffmpeg.
5. Clean up frame directories; keep GIFs only.

### Output location
Store GIFs under:
```text
examples/demos/gtm/media/
```

### Verified naming used for interim assets
- `demo_01_freespan_preview.gif`
- `demo_02_wall_thickness_preview.gif`
- `demo_03_mudmat_installation_preview.gif`
- `demo_04_shallow_pipelay_preview.gif`
- `demo_05_jumper_installation_preview.gif`

These were all kept under ~1 MB using Playwright screenshots + ffmpeg palette generation.

## Git hygiene
Running validation regenerates tracked HTML/JSON files. If the run is intended as evidence, commit and push the refreshed artifacts. If not, revert them before finishing.

Typical commit sequence used successfully:
1. bugfix commit for Demo 2 cache handling
2. artifact refresh commit after full validation
3. preview GIF commit

## GitHub issue choreography
If a previously closed issue is contradicted by live validation, reopen it immediately with evidence. After the verified fix lands, close it again and link the validation evidence.

Effective pattern used:
- reopen regression issue (#2087)
- comment with exact failing command and error
- fix + validate
- comment with commit + green test output
- close issue
- separately update umbrella/validation issue (#2118) and tracker (#2016)

## Pitfalls
- Serving from the repo root causes report URLs to 404 or point at the wrong directory.
- Legacy Demo 2 JSON may look valid because counts are present, but still be unusable for chart-only regeneration.
- Full validation runs modify tracked output artifacts; do not leave the nested repo dirty accidentally.
- Preview GIFs from reports are useful progress, but they are not automatically equivalent to a stricter “NL prompt -> agent navigation -> run -> report interaction” screencast spec.

## Exit condition
This workflow is complete when:
- GTM pytest suite is green
- all 5 demos were rerun with `--force`
- reports render in browser with 5 Plotly graphs each and no JS errors
- at least 2 hand-checks are documented
- refreshed artifacts are committed/pushed
- any interim GIF assets are committed/pushed if needed for GTM collateral
