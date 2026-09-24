---
name: crossprovider gemini test-xfail-reason-marks-blocking-issue-explicitl
description: Test xfail reason marks blocking issue explicitly
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, dependencies]
---

When tests are written ahead of implementation, xfail reason should cite the blocking issue (`pending #2026 storage impl`). This signals what must be implemented before tests un-fail and enables parallel-work tracking without ambiguity.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
