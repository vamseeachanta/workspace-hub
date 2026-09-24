---
name: crossprovider codex deployed-config-can-drift-behind-origin-detect-a
description: Deployed config can drift behind origin; detect and remediate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deployment, staleness-detection, machine-config]
---

Checkouts on deployed machines can be behind `origin/main`. Detect by comparing file line counts or commit SHAs. Deploy scripts must `git pull` before symlinking, and acceptance criteria must verify against `origin/main`, not hardcoded expectations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
