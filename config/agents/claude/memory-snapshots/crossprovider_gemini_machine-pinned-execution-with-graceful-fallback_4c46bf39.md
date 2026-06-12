---
name: crossprovider gemini machine-pinned-execution-with-graceful-fallback
description: Machine-pinned execution with graceful fallback
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [execution-guard, multi-machine, user-guidance]
---

When a task only makes sense on one machine (e.g., comprehensive-learning on ace-linux-1), implement an explicit machine guard at entry that exits early with clear guidance on what the current machine should do instead (commit state, push, let the coordinator handle it).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
