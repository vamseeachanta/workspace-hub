---
name: crossprovider codex defer-runtime-mutations-until-after-artifact-rev
description: Defer runtime mutations until after artifact review
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [review, lifecycle, gates]
---

Do not run setup/installation/registry edits before the plan passes adversarial review. Keep mutations (git commits, file changes) out of the artifact-under-review; instead, parameterize the plan so mutations become clear follow-on work items. This catches scope/gate/owner-authorization issues before they affect the running system.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
