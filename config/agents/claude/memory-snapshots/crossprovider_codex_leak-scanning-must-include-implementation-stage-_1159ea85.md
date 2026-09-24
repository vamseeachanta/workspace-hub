---
name: crossprovider codex leak-scanning-must-include-implementation-stage-
description: Leak scanning must include implementation-stage config files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, scanning, enforcement]
---

Security scanners that skip planned/configuration implementation files (e.g., config/*.example.json) create bypass opportunities. Include all configuration and implementation artifacts in private-value scanning; implementation stage has stricter requirements than test/script stage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
