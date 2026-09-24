---
name: crossprovider codex fixture-copy-consumers-break-when-scripts-source
description: Fixture-copy consumers break when scripts source new helpers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, script-libraries, testing]
---

If a widely-copied script converts to source a new helper, all external consumers fail. Either keep the helper self-contained, source conditionally if missing, or explicitly update and document the new bundle requirement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
