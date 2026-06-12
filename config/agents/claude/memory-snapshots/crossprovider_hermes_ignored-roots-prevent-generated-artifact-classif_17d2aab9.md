---
name: crossprovider hermes ignored-roots-prevent-generated-artifact-classif
description: Ignored roots prevent generated-artifact classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-structure, precedence-bug]
---

Repo-structure checkers apply `ignored_roots` with higher precedence than `generated_artifact_roots`, skipping validation entirely for ignored paths. If a tracked file accidentally appears in ignored+generated root (e.g., `dist/index.html`), checker silently allows it. Redesign: generated classification should override ignored for tracked files.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
