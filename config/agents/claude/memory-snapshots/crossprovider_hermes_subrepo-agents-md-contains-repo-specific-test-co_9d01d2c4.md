---
name: crossprovider hermes subrepo-agents-md-contains-repo-specific-test-co
description: Subrepo AGENTS.md contains repo-specific test commands
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agents, subrepos, testing]
---

Each subrepo has custom test commands in AGENTS.md: assetutilities uses `uv run python -m pytest tests`, digitalmodel uses `PYTHONPATH=src uv run python -m pytest`, assethold uses `--noconftest` flag. These are not interchangeable; follow the repo's declared command to avoid fixture/context mismatches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
