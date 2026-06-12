---
name: crossprovider hermes symlinks-and-dotfiles-are-public-graph-attack-su
description: Symlinks and dotfiles are public-graph attack surfaces
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, knowledge-graph, path-validation]
---

In public knowledge-graph generators, reject all symlinks (or require resolved targets to remain inside approved corpus shape) and reject any path component starting with `.` (dotfiles), even under approved wiki directories. Both can bypass naive path validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
