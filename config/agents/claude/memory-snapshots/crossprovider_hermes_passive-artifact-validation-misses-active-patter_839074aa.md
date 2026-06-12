---
name: crossprovider hermes passive-artifact-validation-misses-active-patter
description: Passive artifact validation misses active patterns
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, public-safety, validation]
---

Doc/checklist-only validation ('contains section X') fails to catch forbidden patterns. Active scanning via legal denylist and explicit grep (e.g., 'no `/mnt/ace` paths') is required for public-safe outputs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
