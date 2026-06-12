---
name: crossprovider hermes bundle-terminal-state-conservative-classificatio
description: Bundle terminal state conservative classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex, bundle-monitoring, classification]
---

Classify outcomes as succeeded/failed/canceled/timed_out/blocked/blocked_partial based on objective evidence, not inference. Do not declare success without zero-exit-code or completion-signal evidence. Partial/blocked completions are distinct from failure and require documenting which sub-tasks succeeded vs which require human/governance decisions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
