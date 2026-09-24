---
name: crossprovider gemini issue-body-accuracy-drifts-verify-file-state-bef
description: Issue body accuracy drifts; verify file state before planning
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [issue-tracking, verification, investigation]
---

Issue descriptions can become stale (e.g., asserting "no pyproject.toml" when it exists). Ground-truth verification of file existence, tracked-file counts, and repo structure should precede plan design, not follow it. Use `git ls-files | grep -c pattern` and API calls to confirm current state.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
