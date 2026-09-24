---
name: crossprovider codex pre-existing-repo-state-must-be-verified-at-plan
description: Pre-existing repo state must be verified at plan time, not discovered during implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, verification, artifacts]
---

Plans claiming artifacts will be created or first-run CI will be green must verify: existing test imports are correct, referenced files exist (e.g., `uv.lock`, `requirements.txt`), and module paths match package entry points. Claims like "repo has a committed uv.lock" that fail GitHub fetch verification invalidate the install strategy and acceptance criteria. Similarly, plans listing existing files as "Create" instead of "Update" signal incomplete grounding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
