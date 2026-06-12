---
name: crossprovider codex claude-cli-claude-p-unsuitable-for-automated-gat
description: Claude CLI (claude -p) unsuitable for automated gate reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tool-limitation, claude-cli, automation]
---

While interactive Claude orchestration is viable, non-interactive Claude CLI is unreliable as a review transport in shell scripts. Documented failure modes: payload size boundary (~2MB triggers timeout/NO_OUTPUT), positional-arg harness bug on full plans, and wrapper cleanup defects on 60s+ reviews. Current hard-gate is Codex, not Claude, for this reason.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
