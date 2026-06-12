---
name: crossprovider codex result-schemas-need-all-output-channels-pre-plan
description: Result schemas need all output channels pre-planned
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, channels, result-types]
---

Plans assuming warning/info/status channels in output (like RunResult) will fail if only error_message exists. Channels must be added to schema and wired through before pseudocode assumes them; post-plan discovery forces redesign of the entire signaling path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
