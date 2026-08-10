---
name: crossprovider codex test-pytest-config-changes-with-o-flag-not-file-
description: Test pytest config changes with `-o` flag, not file edits
metadata:
  type: reference
  source: codex
  bridged: 2026-08-09
  tags: [pytest, testing, technique, adversarial-review]
---

When adversarially testing pytest config pre/post states, use `pytest -o key=value` inline to test alternate configurations without mutating pytest.ini, conftest.py, or lock files. This preserves a clean working tree and keeps measurements uncontaminated by side effects.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
