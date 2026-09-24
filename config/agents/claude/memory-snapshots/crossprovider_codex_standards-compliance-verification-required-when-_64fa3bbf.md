---
name: crossprovider codex standards-compliance-verification-required-when-
description: Standards compliance verification required when PRs touch already-violating files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, standards-enforcement, scope-verification]
---

When a PR modifies files with pre-existing violations (e.g., 79-line functions in a 50-line-limit repo), acceptance criteria including standards gates must explicitly verify the modification brings touched files into compliance, not just inherit the violation. Passing guards on unmodified violations is not sufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
