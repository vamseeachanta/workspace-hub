---
name: crossprovider hermes do-not-relaunch-existing-generated-prompts-witho
description: Do not relaunch existing generated prompts without unique names
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [autofeed, prompt-reuse, next-wave]
---

Generated prompt files with hardcoded result/log/session paths block or risk overwrites on rerun. For follow-up waves, clone prompt templates and create fresh files with unique session names and result paths (e.g., `-r1`, `-r2` suffixes), writing under `generated/launch-now/` before execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
