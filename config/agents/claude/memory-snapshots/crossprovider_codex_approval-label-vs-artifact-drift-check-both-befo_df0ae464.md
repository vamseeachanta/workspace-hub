---
name: crossprovider codex approval-label-vs-artifact-drift-check-both-befo
description: Approval label vs artifact drift: check both before implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-gates, label-vs-artifact, verification]
---

GitHub issue labels (e.g., `status:plan-approved`) can diverge from linked plan artifacts. Found #2550 labeled approved on GitHub while its linked plan file still said 'not approval-ready' and 'NEEDS FRESH RE-REVIEW'. Always verify both sources; respect the artifact as ground truth if they conflict.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
