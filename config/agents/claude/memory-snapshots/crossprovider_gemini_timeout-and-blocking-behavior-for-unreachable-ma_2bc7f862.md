---
name: crossprovider gemini timeout-and-blocking-behavior-for-unreachable-ma
description: Timeout and blocking behavior for unreachable machines needs explicit test coverage
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, timeout-behavior, fault-tolerance, unreachable-machines]
---

Default silent omission or no-op behavior for remote probes that fail creates gaps in parity reports. Explicitly test timeout wrapping, blocked-status rendering, and fallback evidence paths; make unreachable machines visible in output, not invisible.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
