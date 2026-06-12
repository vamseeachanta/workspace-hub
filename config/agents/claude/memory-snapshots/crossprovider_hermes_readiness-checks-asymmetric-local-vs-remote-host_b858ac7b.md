---
name: crossprovider hermes readiness-checks-asymmetric-local-vs-remote-host
description: Readiness checks: asymmetric local vs remote host validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness, dispatch, host-detection, architecture]
---

Architectural design: local hosts perform live git + filesystem checks; remote hosts skip these when control surface cannot access evidence dir (expected behavior). Local host detection is case-sensitive socket.gethostname() match. Tests must distinguish local-only enforcement from remote-compatible warnings.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
