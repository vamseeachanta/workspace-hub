---
name: crossprovider codex state-machines-must-model-terminal-failure-and-r
description: State machines must model terminal, failure, and recovery states explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [state-machines, fault-tolerance, recovery, publication]
---

State machines lacking explicit quarantine/abort/mismatch/abandoned states or recovery paths create unrecoverable failure modes. Immutable corruption with no recovery path is a blocker. Systems relying on "just retry" semantics fail when the resource is immutable or permanently damaged. Example: publication acceptance system lacks abandoned candidate/attempt model and recovery from immutable HF corruption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
