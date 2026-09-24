---
name: crossprovider codex hardware-core-counts-require-measurement-of-all-
description: Hardware core counts require measurement of all sockets, not one
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hardware-measurement, tuning, windows-inventory]
---

Reading `NumberOfCores` from a single socket on a multi-socket system yields an incomplete picture (e.g., 32 cores from one socket when the system has 64 total). This error directly affects batch concurrency tuning. Verify `NUMBER_OF_PROCESSORS` (total logical) and measure each socket independently; document the result so later reviewers don't 'correct' it to a single socket's count.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
