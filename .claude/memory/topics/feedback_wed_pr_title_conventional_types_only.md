> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-18
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_wed_pr_title_conventional_types_only.md

---
name: feedback_wed_pr_title_conventional_types_only
description: "worldenergydata PR titles must use a Conventional-Commits type; data(...)/chore-scope fail the required \"Validate PR Title\" check"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1f0e7090-8148-48cd-b224-90cfd2d5a453
---

**worldenergydata's `Validate PR Title` CI check (amann/action-semantic-pull-request) allows ONLY these types: `feat fix docs style refactor perf test build ci chore`. Subject must be ≤80 chars.**

`data(cost): ...` is NOT valid and fails the check → PR goes BLOCKED even with everything else green. Hit this THREE times (PR #1021, #1031-area, #1032) because "data" is the semantically natural prefix for dataset-only changes.

**Why:** the check is a required status; a bad type blocks merge regardless of test results.

**How to apply:** for a dataset/CSV change use `feat(cost):` (new data) or `fix(cost):` (corrections) — NOT `data(...)`. Keep the subject after the colon ≤80 chars. Verify title BEFORE opening, or expect a retitle round-trip. Related: [[feedback_required_check_must_not_skip]], [[feedback_non_required_checks_hide_regressions]].
