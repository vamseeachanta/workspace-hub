---
name: crossprovider gemini atomic-writes-for-state-files-write-to-temp-rena
description: Atomic writes for state files: write to temp, rename to live
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [file-safety, atomic-operations, state-management]
---

Write portfolio-signals.yaml to .tmp, then mv atomically. Prevents partial/corrupted state if process crashes mid-write.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
