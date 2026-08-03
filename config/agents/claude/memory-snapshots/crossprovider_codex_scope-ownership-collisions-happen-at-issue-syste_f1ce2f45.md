---
name: crossprovider codex scope-ownership-collisions-happen-at-issue-syste
description: Scope ownership collisions happen at issue/system boundaries and require explicit separation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [scope, ownership, design]
---

Issues #662 (bridge), #640 (reusable pipeline), and #153 (geometry orchestration) overlap in responsibility. Blurred ownership leads to unverified requirements and duplicated work. Plans must explicitly state who owns what, not let responsibility emerge. Collision detection is part of design review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
