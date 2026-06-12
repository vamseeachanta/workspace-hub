---
name: crossprovider hermes pre-flight-check-defer-work-if-blocker-s-scope-c
description: Pre-flight check: defer work if blocker's scope changes affect you
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dependency-management, scope-drift, blocking-deps]
---

Before starting work dependent on in-flight sessions, check blocker's recent comments for routing/path/architectural changes. If blocker's landing would affect your scope, defer and post comment explaining why. Restart only after blocker fully merged. Avoids rework on stale assumptions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
