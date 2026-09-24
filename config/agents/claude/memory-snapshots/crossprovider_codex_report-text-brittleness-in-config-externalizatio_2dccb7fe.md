---
name: crossprovider codex report-text-brittleness-in-config-externalizatio
description: Report text brittleness in config externalization refactors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [golden-testing, config-externalization, report-generation, behavioral-regression]
---

When refactoring to externalize config and verifying golden baseline tests pass, numeric output often stays correct but human-facing report (chart subtitles, methodology, assumptions text) still hardcode old baseline values. This creates output that lies to users when config changes. Requires explicit testing that report content propagates resolved config values, not just numeric verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
