---
name: crossprovider codex repo-specific-python-path-not-uv-run
description: Repo-specific Python path, not 'uv run'
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [python, environment, testing]
---

Use `/mnt/local-analysis/digitalmodel/.venv/bin/python` directly and prefix test runs with `PATH=.../.venv/bin:$PATH`. Never use 'uv run' in this setup; it bypasses repo conventions and test discovery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
