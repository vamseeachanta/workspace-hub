---
name: crossprovider codex issue-planning-dependencies-are-transitive-alway
description: Issue planning dependencies are transitive; always verify via live gate checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-planning, gates, dependencies]
---

Child issues depend on parent issue approval status before implementation is authorized. Never assume dependencies are ready; verify via live GitHub gate status + local artifact presence (plan file, approval marker, review artifacts) before proceeding.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
