---
name: crossprovider codex scoped-artifact-checks-outperform-repo-wide-lega
description: Scoped artifact checks outperform repo-wide legal/leak scans for code review
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [process, scanning, efficiency, code-review]
---

Repository-wide legal scans emit noise from pre-existing violations unrelated to the current diff, making regressions indistinguishable from baseline clutter. Use --diff-only modes or targeted artifact scans for reviews; reserve repo-wide sweeps for CI gates only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
