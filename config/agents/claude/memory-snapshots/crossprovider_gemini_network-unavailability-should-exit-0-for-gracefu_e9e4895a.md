---
name: crossprovider gemini network-unavailability-should-exit-0-for-gracefu
description: Network unavailability should exit 0 for graceful degradation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [error-handling, orchestration, resilience]
---

Changed exit code from 3 to 0 when DNS/network checks fail (e.g., api.anthropic.com unreachable). Allows orchestrator to skip the agent cleanly rather than marking the session as failed.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
