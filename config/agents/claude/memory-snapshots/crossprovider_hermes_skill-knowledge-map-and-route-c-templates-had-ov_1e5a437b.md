---
name: crossprovider hermes skill-knowledge-map-and-route-c-templates-had-ov
description: Skill-knowledge-map and route-c templates had overlapping stale references to parse-session-logs.sh
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [stale-paths, templates, maintenance]
---

skill-knowledge-map.md line 102 referenced deleted scripts/work-queue/parse-session-logs.sh; route-c templates line 1 all referenced deleted scripts/work-queue/new-spec.sh. Both patched to point to current surfaces (orchestrator audit ecosystem, issue+plan workflow). Check these templates quarterly during ecosystem drift audits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
