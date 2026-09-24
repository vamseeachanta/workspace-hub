---
name: crossprovider codex regex-assumptions-in-plan-scope-can-miss-half-th
description: Regex assumptions in plan scope can miss half the live system; verify against actual producer behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, regex, defect-class]
---

When a plan reuses existing code patterns (like `SKILL_PATH_RE` with exactly-two-segment match `[^/]+/[^/]+`), verify the regex captures the live system's actual output. #3138 plan missed 306 of 664 transcripts because the logger emits arbitrary-depth paths. Always enumerate live producer output before accepting path-matching assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
