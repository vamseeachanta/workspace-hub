---
name: crossprovider gemini state-files-beat-manual-resume-from-for-batch-re
description: State files beat manual --resume-from for batch resumption
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [state-management, batch-processing, resumption]
---

For batch operations (1000+ items), store progress in .state.json (total/updated/skipped/errors) and implement automatic resumption logic. This beats manual `--resume-from N` flags: users forget the offset, and restarting always picks up correctly. Include per-item state (skipped reasons) for audit.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
