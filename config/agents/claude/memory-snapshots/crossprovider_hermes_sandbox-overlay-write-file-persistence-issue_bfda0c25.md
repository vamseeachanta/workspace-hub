---
name: crossprovider hermes sandbox-overlay-write-file-persistence-issue
description: Sandbox overlay write-file persistence issue
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tooling-quirk, file-io, hermes-agent]
---

execute_code's write_file writes to overlay not mounted filesystem; read_file embeds line numbers that create corrupted Python when re-written. Use terminal commands (cp, heredocs) or Python scripts generating clean content for actual mount writes. Affects multi-file edits in overnight agent batches.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
