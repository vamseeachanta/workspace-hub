---
name: crossprovider gemini atomic-rename-2-is-the-definitive-race-guard-for
description: Atomic rename(2) is the definitive race guard for concurrent claims
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [concurrency, atomicity, race-conditions]
---

For concurrent WRK claims, pre-checks (is file in working/?) are fast-fail convenience; actual enforcement is rename(2) atomicity. Second session's mv fails because source gone. Pre-check gates first attempt; mv atomicity gates the race. Both layers needed; neither alone is sufficient.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
