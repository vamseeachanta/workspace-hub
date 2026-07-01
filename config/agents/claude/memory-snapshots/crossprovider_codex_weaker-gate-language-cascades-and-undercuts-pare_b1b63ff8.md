---
name: crossprovider codex weaker-gate-language-cascades-and-undercuts-pare
description: Weaker gate language cascades and undercuts parent spec
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [governance, hierarchical-gates, specification-creep]
---

When parent epic specifies strong gates (approval + marker + canary + recorded result) but child plans/implementations use weaker language ('approved and canary passes'), the weaker version becomes the enforcement bottleneck. Each layer must enforce equal gate strength; any child using weaker language undercuts the entire parent specification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
