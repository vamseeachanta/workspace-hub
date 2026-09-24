---
name: crossprovider codex silent-guard-blocks-create-false-success-appeara
description: Silent guard blocks create false-success appearance
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ux, guards, diagnostics]
---

Conditional blocks guarded by file-existence checks (e.g., `if-shell "[ -r ... ]"`) silently skip when prerequisites are absent, with no visible signal. Either add explicit warnings to the config file or add test coverage; silent success is a usability trap.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
