---
name: crossprovider codex pre-push-hook-case-sensitivity-issue-with-repo-n
description: Pre-push hook case-sensitivity issue with repo names
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pre-push-hooks, git-hazards]
---

The pre-push hook references repo names case-sensitively (e.g., `OGManufacturing` vs `ogmanufacturing`). This can cause hook failures even with valid changes; verify the hook's exact naming expectations before diagnosing other causes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
