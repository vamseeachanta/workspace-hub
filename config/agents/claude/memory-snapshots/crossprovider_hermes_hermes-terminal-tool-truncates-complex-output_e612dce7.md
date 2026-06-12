---
name: crossprovider hermes hermes-terminal-tool-truncates-complex-output
description: Hermes terminal tool truncates complex output
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-tooling, debugging, output-handling]
---

Terminal tool output is truncated to '1 lines output' for verbose results, masking actual command exit codes and results. Use `set -o pipefail`, explicit `grep`/`wc` filters, and follow up with shorter verification commands to confirm completion rather than trusting truncated summaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
