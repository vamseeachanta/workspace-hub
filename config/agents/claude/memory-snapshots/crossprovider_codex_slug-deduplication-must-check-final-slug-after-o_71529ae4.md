---
name: crossprovider codex slug-deduplication-must-check-final-slug-after-o
description: Slug deduplication must check final slug after ordinal suffix
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [slug-deduplication, attachment-extraction, collision-detection]
---

In multi-attachment extraction, collision detection by `used_slugs.add(slug)` must happen AFTER ordinal suffix is appended, not before. The pattern prevents overwrites from same-stem attachments (Plan.pdf, Plan.pdf → plan, plan-1) but also catches cross-stem collisions where ordinal-generated slug collides with an earlier real stem (Plan.pdf, Plan-2.pdf, Plan.pdf → requires plan-2 check before assigning plan again).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
