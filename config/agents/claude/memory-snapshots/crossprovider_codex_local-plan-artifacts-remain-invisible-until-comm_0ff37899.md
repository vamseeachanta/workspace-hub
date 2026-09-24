---
name: crossprovider codex local-plan-artifacts-remain-invisible-until-comm
description: Local plan artifacts remain invisible until committed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [session-state, artifacts, git]
---

Draft plans created in docs/plans/ during a development session are not visible to GitHub until committed and pushed. Cross-document references between local draft plans (e.g., citing issue #601's plan as a precursor to #603) create unresolvable forward references; document 'local draft' status when citing interdependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
