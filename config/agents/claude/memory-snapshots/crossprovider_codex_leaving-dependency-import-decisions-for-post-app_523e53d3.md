---
name: crossprovider codex leaving-dependency-import-decisions-for-post-app
description: Leaving dependency/import decisions for post-approval review creates illusion of scope
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, dependencies, scope-creep]
---

Plans that identify a problem (e.g., `tests/unit/automation/test_cli.py` has stale import, or `assetutilities` is a sibling dep) but defer the fix to "phase 2 if needed" or "open for reviewer to decide" fail the approval gate. The plan must specify the concrete target (which import path, which install mechanism, which triggered files), not name the problem and ask reviewers to solve it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
