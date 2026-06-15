---
name: crossprovider codex output-sanitizers-must-maintain-exhaustive-path-
description: Output sanitizers must maintain exhaustive path-prefix lists with adversarial test coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, sanitization, testing, output-validation]
---

Path blacklist sanitizers (e.g., filtering `/mnt/` and `/home/`) silently leak other absolute paths like `/tmp/`. Maintain a comprehensive list of forbidden prefixes and test with adversarial inputs that expose gaps. Tests using only repo-relative paths won't catch these regressions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
