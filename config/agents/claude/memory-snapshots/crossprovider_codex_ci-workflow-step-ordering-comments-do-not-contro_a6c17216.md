---
name: crossprovider codex ci-workflow-step-ordering-comments-do-not-contro
description: CI workflow step ordering: comments do not control execution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-actions, ci-config]
---

In GitHub Actions, step execution order is determined by declaration position, not by comments like 'Run X first'. A step named 'Run smoke tests first' that appears after linting steps will still execute after lint. Reordering requires moving the step in the workflow YAML.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
