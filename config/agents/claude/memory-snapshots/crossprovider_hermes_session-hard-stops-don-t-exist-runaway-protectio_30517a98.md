---
name: crossprovider hermes session-hard-stops-don-t-exist-runaway-protectio
description: Session hard-stops don't exist (runaway protection missing)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [session-governance, safety-gap, runaway-protection]
---

6.1M wasted tool calls across 3 work items show runaway sessions burn unchecked; no session-level ceiling (tool-call count, time limit, error loop detection) or auto-abort mechanism. AGENTS.md declares 'TDD mandatory' but no pre-commit hook enforces it (3-4% actual pairing). Harness has GSD workflow quality gates but no session-abort on quota exhaustion or loop detection.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
