---
name: crossprovider gemini tidy-script-is-living-test-harness-validates-lif
description: Tidy script is 'living test harness'—validates lifecycle via TDD red→green
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tdd-pattern, lifecycle-validation, self-testing]
---

tidy-agent-teams.sh starts as no-op stub (Red), then each WRK-1036 phase completion makes it green (e.g., deletes archived teams, preserves active). Passing tidy = phase validation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
