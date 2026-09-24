---
name: crossprovider codex plan-revision-metadata-must-track-all-review-rou
description: Plan revision metadata must track all review rounds
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, adversarial-review]
---

When a plan is revised after an adversarial review, the Adversarial Review Summary, Artifact Map, and status fields often become stale—listing only prior rounds while incorporating fixes from new rounds. This causes reviewers to re-discover already-fixed issues. After each revision, explicitly update metadata to include the new review round, add its artifact to the Artifact Map, and update status to reflect post-round revisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
