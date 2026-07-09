---
name: crossprovider codex optional-tooling-gates-bitrot-silently
description: Optional tooling gates bitrot silently
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [CI, governance, enforcement]
---

A gate like `if [ -x scripts/legal/legal-sanity-scan.sh ]; then ... else echo MISSING; fi` allows enforcement to silently disappear if the script is never created. Sibling repos may have the tool, but conditional invocation masks that a repo lacks its own enforcement. Solution: fail closed (error) if required enforcement is unavailable, don't silently skip.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
