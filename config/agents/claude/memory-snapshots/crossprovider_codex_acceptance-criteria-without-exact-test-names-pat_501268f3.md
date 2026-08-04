---
name: crossprovider codex acceptance-criteria-without-exact-test-names-pat
description: Acceptance criteria without exact test names/paths are unverifiable
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [acceptance, testing, verification]
---

Acceptance statements like "behavior will remain covered" or "all settings effective" fail unless backed by specific test names and file paths (e.g. `tests/foo/test_bar.py::test_quoting_on_windows`). Broad coverage claims without test identity make acceptance subjective and prevent pre-merge verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
