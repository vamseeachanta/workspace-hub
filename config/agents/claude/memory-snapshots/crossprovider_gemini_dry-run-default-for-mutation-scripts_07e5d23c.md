---
name: crossprovider gemini dry-run-default-for-mutation-scripts
description: Dry-run default for mutation scripts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cli-design, safety-first, user-preference]
---

Python scripts default to `--dry-run` with `--apply` flag to write changes. No side effects without explicit user approval. Pattern spans `verify_checklist.py`, `fix-unresolved-refs.py`, and other tooling.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
