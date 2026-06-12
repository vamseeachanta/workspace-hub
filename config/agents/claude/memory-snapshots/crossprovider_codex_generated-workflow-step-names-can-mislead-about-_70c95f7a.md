---
name: crossprovider codex generated-workflow-step-names-can-mislead-about-
description: Generated workflow step names can mislead about step order
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ci-cd, workflows, step-ordering]
---

A step named "Run smoke tests first" may actually run after linting, type checking, and security checks. Actual step order in a workflow determines execution sequence; names are hints only. Audit the step index, not the label.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
