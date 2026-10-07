---
name: gtm-demo-workflow-gif-generation
description: Generate GTM demo GIF assets from validated HTML reports, including both report-scroll GIFs and one higher-fidelity workflow-style GIF, while avoiding Playwright/Python environment traps.
version: 1.0.0
category: workspace-hub-learned
---

# GTM Demo Workflow GIF Generation

Use when working on `digitalmodel/examples/demos/gtm/media/` to produce GIF deliverables for GTM/demo issues like #1809.

## When to use
- You already have validated HTML reports under `examples/demos/gtm/output/`
- You need GIF assets in `examples/demos/gtm/media/`
- You want either:
  1. simple report-scroll GIFs, or
  2. a richer workflow GIF showing prompt -> setup -> execution -> report -> browser walkthrough

## Proven approach

### 1. Validate reports first
Do not generate GIFs from stale or unvalidated outputs.

Run from `digitalmodel/`:
```bash
PYTHONPATH=examples/demos/gtm:src uv run pytest examples/demos/gtm/tests/test_gtm_demos.py -q
```

If you need fresh artifacts, rerun demos with `--force` before GIF work.

### 2. For report-scroll GIFs, keep it simple
For issue-aligned deliverable names, keep files in:
```text
examples/demos/gtm/media/
```

If preview GIFs already exist and are acceptable, normalize by renaming/copying to final names instead of regenerating.

### 3. For comparison-matrix GIFs, use a generator script
Pattern that worked:
- build a lightweight HTML page from comparison JSON files
- render via Playwright
- capture full-page screenshot
- slice into viewport-height frames
- assemble with Pillow or ffmpeg into GIF

Good source files:
- `examples/demos/gtm/results/vessel_comparison_matrix.json`
- `examples/demos/gtm/results/structure_comparison_matrix.json`

### 4. For workflow-style GIFs, compose staged scenes
Best reusable structure:
1. prompt scene
2. setup/command scene
3. execution/progress scene
4. report generation/open scene
5. browser walkthrough scene

Implementation pattern:
- render the first 4 scenes as synthetic HTML slides styled like terminal/UI panels
- then append a real scroll-through of the validated HTML report
- use Playwright for rendering and Pillow for assembly

This gives a deterministic asset without requiring flaky live desktop capture.

## Critical pitfalls discovered

### Pitfall 1: Python environment mismatch for Playwright
A script with `playwright.sync_api` may fail under `uv run python` or the default `python3` even though Playwright is installed elsewhere.

What happened:
- Playwright was not available in the default interpreter path used by one run
- it was available in `python3.12`

Verification command:
```bash
python3.12 -c "from playwright.sync_api import sync_playwright; print('OK')"
```

Fix:
- use an explicit shebang like:
```python
#!/usr/bin/env python3.12
```
- or run the generator explicitly with `python3.12`

### Pitfall 2: `networkidle` can hang on local HTML reports using Plotly CDN
For local file-based HTML reports that load Plotly from CDN, this pattern can fail:
```python
page.goto(...)
page.wait_for_load_state("networkidle")
```

Why:
- CDN fetches / background activity prevent a clean `networkidle` state

Fix that worked:
```python
page.goto(url, wait_until="domcontentloaded")
page.wait_for_timeout(5000)
```

Use a timed wait after `domcontentloaded` to let Plotly render.

### Pitfall 3: External verification matters more than Claude's claim
When using interactive Claude Code in tmux:
- let Claude implement
- then independently verify with:
```bash
git status --short --branch
git log --oneline -3
ls -lh examples/demos/gtm/media/*
```

Do not trust completion claims without checking the actual files and commit.

## Recommended workflow with interactive Claude Code

When the user explicitly wants Claude Code:
1. write a tight prompt to `/tmp/...txt`
2. launch tmux + Claude with:
```bash
claude --setting-sources user --dangerously-skip-permissions "$(cat /tmp/prompt.txt)"
```
3. monitor with `tmux capture-pane`
4. if Claude gets stuck, interrupt and send a narrower corrective prompt
5. after completion, verify externally and update GitHub yourself if needed

## Good outputs to leave behind
- final GIF assets in `examples/demos/gtm/media/`
- reproducible generator script(s) in the same folder
- `media/README.md` documenting what each asset is and how to regenerate it

## Workflow-upgrade wave pattern that proved reusable
After the first true workflow exemplar works, upgrade the remaining demos one-by-one instead of trying to regenerate all five in a single fragile run.

Recommended pattern:
1. one tmux/Claude session per demo
2. one generator script per demo, e.g.:
   - `generate_demo_01_workflow_gif.py`
   - `generate_demo_03_workflow_gif.py`
   - `generate_demo_04_workflow_gif.py`
   - `generate_demo_05_workflow_gif.py`
3. update `media/README.md` after each successful asset
4. verify file size and visual output externally before closing the issue

This isolates failures and makes it easy to salvage finished files even if one interactive Claude session later hits an upstream API error.

## Size-control finding for workflow GIFs
A workflow GIF can easily exceed a practical sharing limit if you keep too many colors or frames.

Recovery pattern that worked:
- re-open the generated GIF with Pillow
- quantize/re-save at lower color count (128 colors worked)
- verify the optimized output still looks acceptable

Use this when a workflow GIF lands over the target size threshold. In the validated run, this was necessary for Demo 4 and brought the file under 5 MB without regenerating the whole asset from scratch.

## Suggested follow-up issue split
If a parent issue asked for all GIFs but you only produced one true workflow exemplar plus simpler report-scroll GIFs:
- close parent if named deliverables exist
- create follow-up issue for upgrading remaining demos to workflow-style format

This avoids scope creep while preserving momentum.

If the follow-up issue is approved, execute the remaining upgrades as a wave of small, independent demo-specific tasks rather than reopening the original issue.

## Downstream website/gallery packaging finding
Do not automatically publish the large workflow GIFs on a public gallery page.

Better pattern for a marketing/gallery surface:
- copy the 5 lightweight primary demo GIFs plus `demo_comparison_matrix.gif`
- exclude the larger `_workflow.gif` files from the page bundle
- use `loading="lazy"` on below-the-fold media

Why:
- the lightweight set stayed around ~5.3 MB total for the gallery
- including all workflow GIFs would have pushed the page toward ~25 MB+
- workflow GIFs are excellent proof assets, but not ideal default web-gallery payloads

For `aceengineer-website`, the working implementation pattern was:
- add page source at `content/demos/index.html`
- copy gallery assets into `assets/img/demos/`
- run the site build so `dist/demos/index.html` is produced
- locally serve `dist/` and browser-verify the built page, not just the source file
