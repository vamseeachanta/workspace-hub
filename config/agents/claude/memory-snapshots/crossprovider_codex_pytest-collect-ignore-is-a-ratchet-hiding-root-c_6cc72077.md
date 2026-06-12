---
name: crossprovider codex pytest-collect-ignore-is-a-ratchet-hiding-root-c
description: pytest collect_ignore is a ratchet hiding root causes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, pytest, testing-strategy]
---

Adding files to conftest.py's collect_ignore list silences failing tests but does not fix them. Removing entries later requires concurrent fixes or tests fail. The ratchet creates a false sense of progress; prefer fixing root causes before removing ignore entries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
