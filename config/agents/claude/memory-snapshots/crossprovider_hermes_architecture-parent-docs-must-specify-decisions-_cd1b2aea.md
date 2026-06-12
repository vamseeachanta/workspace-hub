---
name: crossprovider hermes architecture-parent-docs-must-specify-decisions-
description: Architecture parent docs must specify decisions not defer vaguely
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, architecture, decisions, anti-pattern]
---

Parent architecture documents must make concrete decisions: canonical identity rule (sha256 vs path aliasing), layer owner names (not just 'someone'), allowed/forbidden information flows with specific exceptions. Vague deferral causes child-issue duplication and architectural divergence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
