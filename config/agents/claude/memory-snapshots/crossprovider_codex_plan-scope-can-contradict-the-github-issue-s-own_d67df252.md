---
name: crossprovider codex plan-scope-can-contradict-the-github-issue-s-own
description: Plan scope can contradict the GitHub issue's own acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, scope-boundaries, acceptance-criteria]
---

When a plan narrows scope (e.g., 'exclude new copy paths'), verify this doesn't exclude features that the issue's acceptance criteria explicitly require. This pattern recurs across issues #605, #608, #609: plan §Scope excludes required behavior, then acceptance criterion contradicts that scope. Reconcile plan scope against the issue before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
