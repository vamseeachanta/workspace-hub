---
name: gtm-workflow-gif-generation
description: Generate workflow-style GTM GIFs from validated HTML demo reports using synthetic scene slides plus Playwright/Pillow scroll capture, with Python 3.12 fallback and GIF size optimization.
version: 1.0.0
category: workspace-hub-learned
tags: [gtm, gif, playwright, pillow, demo, workflow, digitalmodel]
---

# GTM Workflow GIF Generation

Use when a demo/report already has a validated HTML artifact and you need a reusable GIF that tells the full story:
prompt -> setup -> execution -> report -> browser walkthrough.

## When to use
- A report-scroll GIF already exists but is not enough for GTM
- You need one deterministic, reproducible workflow GIF per demo
- The HTML report is already validated and present under `examples/demos/gtm/output/`

## Core pattern
1. Keep the generator local to `examples/demos/gtm/media/`.
2. Reuse the existing workflow generator structure from another demo if available.
3. Build 5 synthetic HTML scenes with shared dark-theme CSS:
   - prompt
   - repo/code setup
   - analysis execution/progress
   - report/artifact output
   - browser walkthrough label
4. Render those scenes with Playwright headless Chromium.
5. Append a scroll-through of the real validated HTML report by taking a full-page screenshot and cropping viewport-sized frames.
6. Assemble frames into a GIF with Pillow.
7. Update `examples/demos/gtm/media/README.md` with:
   - deliverable row
   - generation note
   - regeneration command
8. Commit/push the GIF, generator script, and README together.

## Important implementation details
- Prefer `python3.12` directly if the script imports `playwright.sync_api`; `uv run python` may use a Python without Playwright installed.
- For local HTML reports with external Plotly CDN assets, use:
  - `page.goto(..., wait_until="domcontentloaded")`
  - then `page.wait_for_timeout(5000)`
  instead of `networkidle`, which can hang or fail.
- Keep constants aligned across demos:
  - `WIDTH = 1024`
  - `HEIGHT = 640`
  - `FRAME_DURATION_MS = 120`
  - `SCROLL_STEP = 80`
- Hold each synthetic slide for several duplicate frames, then insert a few dark transition frames.
- For the walkthrough, do one full-page screenshot and crop it into scrolling frames rather than driving interactive scrolling in real time.

## Size-control lesson
If the generated GIF exceeds the repo hook threshold (5 MB), re-quantize it after generation:
- reopen GIF with Pillow
- quantize frames to ~128 colors
- resave with `optimize=True`
This was enough to shrink a 5.4 MB workflow GIF to ~3.6 MB without changing the underlying scene logic.

## Minimal file set per demo
- `examples/demos/gtm/media/<demo>_workflow.gif`
- `examples/demos/gtm/media/generate_<demo>_workflow_gif.py`
- `examples/demos/gtm/media/README.md`

## Recovery / orchestration lessons
- In tmux/interactive Codex sessions, the useful files may already exist even if the session later hits an Anthropic API 500.
- After any interactive failure, verify externally before retrying:
  - `git status --short --branch`
  - `ls -lh examples/demos/gtm/media/...`
- If the artifact exists and only commit/push remains, finish that outside the Codex session instead of rerunning the whole generation.

## Good commit pattern
- `feat(gtm): add Demo N end-to-end workflow GIF for #2288`

## Closeout rule
Once all demos in scope have workflow GIFs and README regeneration notes, close the follow-up issue and move downstream to gallery/embed work rather than continuing asset generation.